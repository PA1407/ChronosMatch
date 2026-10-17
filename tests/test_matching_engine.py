
from decimal import Decimal

from app.engine.matching_engine import MatchingEngine
from app.engine.models import Order, OrderSide, OrderStatus


def make_order(order_id, side, price, quantity):
    return Order(
        order_id=order_id,
        symbol="TEST",
        side=side,
        price=Decimal(str(price)),
        quantity=quantity,
    )


def test_partial_fill():
    engine = MatchingEngine()

    buy = make_order("B1", OrderSide.BUY, 100, 10)
    sell = make_order("S1", OrderSide.SELL, 100, 6)

    # The first order should rest in the book.
    assert engine.process_order(buy) == []

    # The sell order should match 6 units of the buy order.
    trades = engine.process_order(sell)

    assert len(trades) == 1
    assert trades[0].quantity == 6
    assert trades[0].price == Decimal("100")

    assert buy.filled_quantity == 6
    assert buy.remaining_quantity == 4
    assert buy.order_status == OrderStatus.PARTIALLY_FILLED

    assert sell.filled_quantity == 6
    assert sell.remaining_quantity == 0
    assert sell.order_status == OrderStatus.FILLED

    assert engine.get_order("TEST", "B1") is buy
    assert engine.get_order("TEST", "S1") is None


def test_non_crossing_orders_remain_in_book():
    engine = MatchingEngine()

    buy = make_order("B1", OrderSide.BUY, 100, 5)
    sell = make_order("S1", OrderSide.SELL, 105, 5)

    assert engine.process_order(buy) == []
    assert engine.process_order(sell) == []

    book = engine.get_order_book("TEST")

    assert book.get_best_buy() is buy
    assert book.get_best_sell() is sell
    assert buy.remaining_quantity == 5
    assert sell.remaining_quantity == 5


def test_fully_filled_buy_order_is_removed():
    engine = MatchingEngine()

    buy = make_order("B1", OrderSide.BUY, 100, 5)
    sell = make_order("S1", OrderSide.SELL, 100, 5)

    engine.process_order(buy)
    trades = engine.process_order(sell)

    assert len(trades) == 1
    assert trades[0].quantity == 5
    assert buy.order_status == OrderStatus.FILLED
    assert buy.remaining_quantity == 0
    assert engine.get_order("TEST", "B1") is None


def test_best_buy_uses_highest_price_first():
    engine = MatchingEngine()

    buy_100 = make_order("B1", OrderSide.BUY, 100, 5)
    buy_105 = make_order("B2", OrderSide.BUY, 105, 5)
    buy_103 = make_order("B3", OrderSide.BUY, 103, 5)

    engine.process_order(buy_100)
    engine.process_order(buy_105)
    engine.process_order(buy_103)

    book = engine.get_order_book("TEST")

    assert book.get_best_buy().order_id == "B2"
    assert book.buy_orders[1].order_id == "B3"
    assert book.buy_orders[2].order_id == "B1"


def test_same_price_uses_earlier_order_first():
    engine = MatchingEngine()

    first = make_order("B1", OrderSide.BUY, 100, 5)
    second = make_order("B2", OrderSide.BUY, 100, 5)

    engine.process_order(first)
    engine.process_order(second)

    book = engine.get_order_book("TEST")

    assert book.get_best_buy().order_id == "B1"
    assert book.buy_orders[1].order_id == "B2"


def test_best_sell_uses_lowest_price_first():
    engine = MatchingEngine()

    sell_110 = make_order("S1", OrderSide.SELL, 110, 5)
    sell_105 = make_order("S2", OrderSide.SELL, 105, 5)
    sell_108 = make_order("S3", OrderSide.SELL, 108, 5)

    engine.process_order(sell_110)
    engine.process_order(sell_105)
    engine.process_order(sell_108)

    book = engine.get_order_book("TEST")

    assert book.get_best_sell().order_id == "S2"
    assert book.sell_orders[1].order_id == "S3"
    assert book.sell_orders[2].order_id == "S1"


def test_same_sell_price_uses_earlier_order_first():
    engine = MatchingEngine()

    first = make_order("S1", OrderSide.SELL, 105, 5)
    second = make_order("S2", OrderSide.SELL, 105, 5)

    engine.process_order(first)
    engine.process_order(second)

    book = engine.get_order_book("TEST")

    assert book.get_best_sell().order_id == "S1"
    assert book.sell_orders[1].order_id == "S2"
