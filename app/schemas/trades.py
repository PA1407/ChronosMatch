
from decimal import Decimal

from pydantic import BaseModel, Field


class TradeResponse(BaseModel):
    trade_id: str
    symbol: str
    buy_order_id: str
    sell_order_id: str
    execution_price: Decimal = Field(gt=0)
    quantity: int = Field(gt=0)
    executed_at: str
