
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class OrderCreate(BaseModel):
    """Fields supplied by a client when placing an order."""

    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(
        min_length=1,
        max_length=20,
        description="Instrument symbol, for example ABC",
    )
    side: OrderSide
    limit_price: Decimal = Field(gt=0)
    quantity: int = Field(gt=0)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        value = value.upper()
        if not value.isalnum():
            raise ValueError("Symbol must contain only letters and numbers")
        return value


class OrderResponse(BaseModel):
    """Order details returned by the backend."""

    order_id: str
    symbol: str
    side: OrderSide
    limit_price: Decimal
    quantity: int
    remaining_quantity: int
    status: OrderStatus
