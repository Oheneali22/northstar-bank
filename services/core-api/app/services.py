import uuid

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.metrics import TRANSFER_AMOUNT, TRANSFERS
from app.models import Account, LedgerEntry, Transfer
from app.schemas import TransferCreate, decimal_to_cents


def list_accounts(db: Session) -> list[Account]:
    return list(db.scalars(select(Account).order_by(Account.created_at)))


def list_transfers(db: Session, account_id: uuid.UUID | None = None) -> list[Transfer]:
    query = select(Transfer).order_by(Transfer.created_at.desc()).limit(100)
    if account_id:
        query = query.where(
            or_(
                Transfer.source_account_id == account_id,
                Transfer.destination_account_id == account_id,
            )
        )
    return list(db.scalars(query))


def create_transfer(db: Session, payload: TransferCreate, idempotency_key: str) -> Transfer:
    existing = db.scalar(select(Transfer).where(Transfer.idempotency_key == idempotency_key))
    if existing:
        return existing

    amount_cents = decimal_to_cents(payload.amount)
    account_ids = sorted([payload.source_account_id, payload.destination_account_id], key=str)
    locked = list(
        db.scalars(select(Account).where(Account.id.in_(account_ids)).order_by(Account.id).with_for_update())
    )
    accounts = {account.id: account for account in locked}
    source = accounts.get(payload.source_account_id)
    destination = accounts.get(payload.destination_account_id)

    if not source or not destination:
        TRANSFERS.labels(outcome="account_not_found").inc()
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Source or destination account not found")
    if source.status != "active" or destination.status != "active":
        TRANSFERS.labels(outcome="inactive_account").inc()
        raise HTTPException(status.HTTP_409_CONFLICT, "Both accounts must be active")
    if source.currency != payload.currency or destination.currency != payload.currency:
        TRANSFERS.labels(outcome="currency_mismatch").inc()
        raise HTTPException(status.HTTP_409_CONFLICT, "Account currency does not match transfer")
    if source.balance_cents < amount_cents:
        TRANSFERS.labels(outcome="insufficient_funds").inc()
        raise HTTPException(status.HTTP_409_CONFLICT, "Insufficient funds")

    transfer = Transfer(
        idempotency_key=idempotency_key,
        source_account_id=source.id,
        destination_account_id=destination.id,
        amount_cents=amount_cents,
        currency=payload.currency,
        description=payload.description,
    )
    source.balance_cents -= amount_cents
    destination.balance_cents += amount_cents
    db.add(transfer)
    db.flush()
    db.add_all(
        [
            LedgerEntry(
                transfer_id=transfer.id,
                account_id=source.id,
                amount_cents=-amount_cents,
                entry_type="debit",
            ),
            LedgerEntry(
                transfer_id=transfer.id,
                account_id=destination.id,
                amount_cents=amount_cents,
                entry_type="credit",
            ),
        ]
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(Transfer).where(Transfer.idempotency_key == idempotency_key))
        if existing:
            return existing
        raise
    db.refresh(transfer)
    TRANSFERS.labels(outcome="completed").inc()
    TRANSFER_AMOUNT.observe(amount_cents)
    return transfer
