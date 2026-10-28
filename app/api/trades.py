from fastapi import APIRouter, Query
from app.database.repository import list_trades
from app.schemas.trades import TradeResponse

router = APIRouter(prefix="/trades", tags=["Trades"])

@router.get("", response_model=list[TradeResponse])
def get_trades(
    symbol: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=100, ge=1, le=1000),
):
    trades = list_trades(limit=1000)

    if symbol is not None:
        symbol = symbol.strip().upper()
        trades = [
            trade for trade in trades
            if trade["symbol"].upper() == symbol
        ]

    return trades[:limit]