"""Create core banking tables."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("customer_id", sa.Uuid(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("account_number", sa.String(16), nullable=False, unique=True),
        sa.Column("account_type", sa.String(32), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("balance_cents", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("balance_cents >= 0", name="ck_accounts_nonnegative_balance"),
    )
    op.create_index("ix_accounts_customer_id", "accounts", ["customer_id"])
    op.create_table(
        "transfers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("source_account_id", sa.Uuid(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column(
            "destination_account_id",
            sa.Uuid(),
            sa.ForeignKey("accounts.id"),
            nullable=False,
        ),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_cents > 0", name="ck_transfers_positive_amount"),
        sa.CheckConstraint(
            "source_account_id <> destination_account_id",
            name="ck_transfers_distinct_accounts",
        ),
    )
    op.create_index("ix_transfers_source", "transfers", ["source_account_id", "created_at"])
    op.create_index(
        "ix_transfers_destination", "transfers", ["destination_account_id", "created_at"]
    )
    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("transfer_id", sa.Uuid(), sa.ForeignKey("transfers.id"), nullable=False),
        sa.Column("account_id", sa.Uuid(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False),
        sa.Column("entry_type", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_cents <> 0", name="ck_ledger_nonzero_amount"),
    )
    op.create_index("ix_ledger_account", "ledger_entries", ["account_id", "created_at"])
    op.create_index("ix_ledger_transfer", "ledger_entries", ["transfer_id"])


def downgrade() -> None:
    op.drop_table("ledger_entries")
    op.drop_table("transfers")
    op.drop_table("accounts")
    op.drop_table("customers")
