
from fastapi import APIRouter, HTTPException, Query

from app.database.repository import list_trades
from app.schemas.trades import TradeResponse

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("", response_model=list[TradeResponse])
def get_trades(
    symbol: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=100, ge=1, le=1000),
):
    """Return recent trades, optionally filtered by symbol."""
    trades = list_trades(limit=1000)

    if symbol is not None:
        symbol = symbol.strip().upper()

        if not symbol:
            raise HTTPException(
                status_code=422,
                detail="Symbol cannot be empty",
            )

        trades = [
            trade for trade in trades
            if trade["symbol"].upper() == symbol
        ]

    return trades[:limit]
