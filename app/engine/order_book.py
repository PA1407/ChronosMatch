
from app.engine.models import Order, OrderSide


class OrderBook:
    """Maintain outstanding buy and sell orders for one symbol."""

    def __init__(self, symbol: str):
        if not symbol.strip():
            raise ValueError("symbol cannot be empty")

        self.symbol = symbol
        self.buy_orders: list[Order] = []
        self.sell_orders: list[Order] = []
        self.orders_by_id: dict[str, Order] = {}

    def add_order(self, order: Order) -> None:
        """Add an order while preserving price-time priority."""
        if order.symbol != self.symbol:
            raise ValueError("Order symbol does not match this order book")

        if order.order_id in self.orders_by_id:
            raise ValueError("Duplicate order_id")

        if order.remaining_quantity <= 0:
            raise ValueError("Order must have remaining quantity")

        if order.side == OrderSide.BUY:
            self.buy_orders.append(order)
            self.buy_orders.sort(
                key=lambda item: (-item.price, item.created_at)
            )
        else:
            self.sell_orders.append(order)
            self.sell_orders.sort(
                key=lambda item: (item.price, item.created_at)
            )

        self.orders_by_id[order.order_id] = order

    def get_best_buy(self) -> Order | None:
        """Return the highest-priority buy order."""
        if not self.buy_orders:
            return None
        return self.buy_orders[0]

    def get_best_sell(self) -> Order | None:
        """Return the highest-priority sell order."""
        if not self.sell_orders:
            return None
        return self.sell_orders[0]

    def get_order(self, order_id: str) -> Order | None:
        """Find an order by its ID."""
        return self.orders_by_id.get(order_id)

    def remove_order(self, order_id: str) -> bool:
        """Remove an order from the book. Return whether it existed."""
        order = self.orders_by_id.get(order_id)

        if order is None:
            return False

        if order.side == OrderSide.BUY:
            self.buy_orders.remove(order)
        else:
            self.sell_orders.remove(order)

        del self.orders_by_id[order_id]
        return True
