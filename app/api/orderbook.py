
from fastapi import APIRouter

from app.services.order_service import matching_engine

router = APIRouter(prefix="/orderbook", tags=["Order Book"])


def serialize_order(order):
    return {
        "order_id": order.order_id,
        "symbol": order.symbol,
        "side": order.side.value,
        "price": str(order.price),
        "quantity": order.quantity,
        "filled_quantity": order.filled_quantity,
        "remaining_quantity": order.remaining_quantity,
        "status": order.order_status.value,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }


@router.get("/{symbol}")
def get_orderbook(symbol: str):
    symbol = symbol.strip().upper()

    if not symbol:
        return {
            "symbol": symbol,
            "buy_orders": [],
            "sell_orders": [],
        }

    book = matching_engine.order_books.get(symbol)

    if book is None:
        return {
            "symbol": symbol,
            "buy_orders": [],
            "sell_orders": [],
        }

    return {
        "symbol": symbol,
        "buy_orders": [
            serialize_order(order)
            for order in book.buy_orders
        ],
        "sell_orders": [
            serialize_order(order)
            for order in book.sell_orders
        ],
    }
