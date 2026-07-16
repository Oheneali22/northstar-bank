import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def decimal_to_cents(value: Decimal) -> int:
    return int((value * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID
    account_number: str
    account_type: str
    currency: str
    balance_cents: int
    status: str
    created_at: datetime


class TransferCreate(BaseModel):
    source_account_id: uuid.UUID
    destination_account_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    description: str = Field(default="Account transfer", min_length=1, max_length=255)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class TransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    idempotency_key: str
    source_account_id: uuid.UUID
    destination_account_id: uuid.UUID
    amount_cents: int
    currency: str
    description: str
    status: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
