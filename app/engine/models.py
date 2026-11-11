from dataclasses import dataclass, field 
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    price: Decimal
    quantity: int 
    filled_quantity: int = 0
    remaining_quantity: int | None = None
    order_status: OrderStatus = OrderStatus.OPEN
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    

    def __post_init__(self):
        if not self.order_id.strip():
            raise ValueError("order_id cannot be empty")
        if not self.symbol.strip():
            raise ValueError("symbol cannot be empty")
        if not isinstance(self.side, OrderSide):
            raise ValueError("side must be an OrderSide")
        if not isinstance(self.price, Decimal) or not self.price.is_finite() or self.price <= 0:
            raise ValueError("price must be a positive finite Decimal")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.filled_quantity < 0 or self.filled_quantity > self.quantity:
            raise ValueError("filled_quantity is invalid")

        if self.remaining_quantity is None:
            self.remaining_quantity = self.quantity - self.filled_quantity

        if self.remaining_quantity != self.quantity - self.filled_quantity:
            raise ValueError("quantity must equal filled_quantity + remaining_quantity")

        if self.remaining_quantity == 0:
            self.order_status = OrderStatus.FILLED
        elif self.filled_quantity > 0:
            self.order_status = OrderStatus.PARTIALLY_FILLED


@dataclass(frozen=True)
class Trade:
    trade_id: str
    buy_order_id: str
    sell_order_id: str
    symbol: str
    price: Decimal
    quantity: int
    executed_at: datetime = field(default_factory=utc_now)
