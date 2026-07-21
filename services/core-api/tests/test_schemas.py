from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import TransferCreate, decimal_to_cents


def test_money_is_converted_to_integer_cents() -> None:
    assert decimal_to_cents(Decimal("42.19")) == 4219


def test_transfer_rejects_non_positive_amount(account_ids) -> None:
    source, destination = account_ids
    with pytest.raises(ValidationError):
        TransferCreate(
            source_account_id=source,
            destination_account_id=destination,
            amount=Decimal("0"),
        )


@pytest.fixture
def account_ids():
    import uuid

    return uuid.uuid4(), uuid.uuid4()
