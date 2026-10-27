
from fastapi import APIRouter

from app.services.order_service import matching_engine

router = APIRouter(prefix="/orderbook", tags=["Order Book"])


def serialize_order(order):
    """Convert an engine order into a JSON-friendly dictionary."""
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
    """Return resting buy and sell orders for a symbol."""
    symbol = symbol.strip().upper()
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


@router.get("/{symbol}/summary")
def get_orderbook_summary(symbol: str):
    """Return order counts and total remaining quantities."""
    symbol = symbol.strip().upper()
    book = matching_engine.order_books.get(symbol)

    if book is None:
        return {
            "symbol": symbol,
            "buy_order_count": 0,
            "sell_order_count": 0,
            "buy_remaining_quantity": 0,
            "sell_remaining_quantity": 0,
        }

    return {
        "symbol": symbol,
        "buy_order_count": len(book.buy_orders),
        "sell_order_count": len(book.sell_orders),
        "buy_remaining_quantity": sum(
            order.remaining_quantity
            for order in book.buy_orders
        ),
        "sell_remaining_quantity": sum(
            order.remaining_quantity
            for order in book.sell_orders
        ),
    }
