from sqlalchemy import select

from app.database import SessionLocal
from app.models import Account, Customer


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Customer).where(Customer.email == "grace@example.test")):
            print("Seed data already exists")
            return
        grace = Customer(full_name="Grace Johnson", email="grace@example.test")
        alex = Customer(full_name="Alex Morgan", email="alex@example.test")
        db.add_all([grace, alex])
        db.flush()
        db.add_all(
            [
                Account(
                    customer_id=grace.id,
                    account_number="100000004821",
                    account_type="checking",
                    balance_cents=2_478_264,
                ),
                Account(
                    customer_id=grace.id,
                    account_number="100000006800",
                    account_type="savings",
                    balance_cents=680_000,
                ),
                Account(
                    customer_id=alex.id,
                    account_number="100000007714",
                    account_type="checking",
                    balance_cents=950_000,
                ),
            ]
        )
        db.commit()
        print("Created synthetic customers and accounts")


if __name__ == "__main__":
    seed()
