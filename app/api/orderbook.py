
from fastapi import APIRouter

router = APIRouter(prefix="/orderbook", tags=["Order Book"])


@router.get("/{symbol}")
def get_orderbook(symbol: str):
    return {
        "symbol": symbol.upper(),
        "buy_orders": [],
        "sell_orders": [],
    }
