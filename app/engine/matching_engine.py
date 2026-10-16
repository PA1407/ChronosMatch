
from uuid import uuid4

from app.engine.models import (
    Order,
    OrderSide,
    OrderStatus,
    Trade,
    utc_now,
)
from app.engine.order_book import OrderBook


class MatchingEngine:
    """Match buy and sell orders using price-time priority."""

    def __init__(self):
        self.order_books: dict[str, OrderBook] = {}
        self.trades: list[Trade] = []

    def get_order_book(self, symbol: str) -> OrderBook:
        """Return the order book for a symbol, creating it if needed."""
        if not symbol.strip():
            raise ValueError("symbol cannot be empty")

        if symbol not in self.order_books:
            self.order_books[symbol] = OrderBook(symbol)

        return self.order_books[symbol]

    def process_order(self, order: Order) -> list[Trade]:
        """Match an incoming order and return the trades it generates."""
        if order.order_status != OrderStatus.OPEN:
            raise ValueError("Only new OPEN orders can be processed")

        if order.remaining_quantity is None or order.remaining_quantity <= 0:
            raise ValueError("Order must have remaining quantity")

        book = self.get_order_book(order.symbol)

        if book.get_order(order.order_id) is not None:
            raise ValueError("Duplicate order_id")

        if any(
            existing.order_id == order.order_id
            for existing_book in self.order_books.values()
            for existing in existing_book.orders_by_id.values()
        ):
            raise ValueError("Duplicate order_id")

        generated_trades: list[Trade] = []

        while order.remaining_quantity > 0:
            if order.side == OrderSide.BUY:
                resting_order = book.get_best_sell()
                if resting_order is None:
                    break
                if order.price < resting_order.price:
                    break
            else:
                resting_order = book.get_best_buy()
                if resting_order is None:
                    break
                if order.price > resting_order.price:
                    break

            executed_quantity = min(
                order.remaining_quantity,
                resting_order.remaining_quantity,
            )

            # The resting order's price determines the execution price.
            trade = Trade(
                trade_id=str(uuid4()),
                buy_order_id=(
                    order.order_id
                    if order.side == OrderSide.BUY
                    else resting_order.order_id
                ),
                sell_order_id=(
                    order.order_id
                    if order.side == OrderSide.SELL
                    else resting_order.order_id
                ),
                symbol=order.symbol,
                price=resting_order.price,
                quantity=executed_quantity,
            )

            order.filled_quantity += executed_quantity
            order.remaining_quantity -= executed_quantity

            resting_order.filled_quantity += executed_quantity
            resting_order.remaining_quantity -= executed_quantity

            now = utc_now()
            order.updated_at = now
            resting_order.updated_at = now

            if order.remaining_quantity == 0:
                order.order_status = OrderStatus.FILLED
            else:
                order.order_status = OrderStatus.PARTIALLY_FILLED

            if resting_order.remaining_quantity == 0:
                resting_order.order_status = OrderStatus.FILLED
                book.remove_order(resting_order.order_id)
            else:
                resting_order.order_status = OrderStatus.PARTIALLY_FILLED

            generated_trades.append(trade)
            self.trades.append(trade)

        # Keep any unfilled quantity in the order book.
        if order.remaining_quantity > 0:
            if order.filled_quantity > 0:
                order.order_status = OrderStatus.PARTIALLY_FILLED
            else:
                order.order_status = OrderStatus.OPEN

            book.add_order(order)

        return generated_trades

    def get_order(self, symbol: str, order_id: str) -> Order | None:
        """Find an order currently resting in the order book."""
        book = self.order_books.get(symbol)
        if book is None:
            return None
        return book.get_order(order_id)

    def get_trades(self, symbol: str | None = None) -> list[Trade]:
        """Return all trades, optionally filtered by symbol."""
        if symbol is None:
            return list(self.trades)

        return [
            trade for trade in self.trades
            if trade.symbol == symbol
        ]
