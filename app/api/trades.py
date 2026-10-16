
from fastapi import APIRouter, Query

from app.database.repositories import list_trades
from app.schemas.trades import TradeResponse

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("", response_model=list[TradeResponse])
def get_trades(
    limit: int = Query(default=100, ge=1, le=1000),
):
    return list_trades(limit=limit)
