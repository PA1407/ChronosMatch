
from decimal import Decimal

from app.engine.matching_engine import MatchingEngine
from app.engine.models import Order, OrderSide, OrderStatus



def make_order(order_id, side, price, quantity, symbol="TEST"):
    return Order(
        order_id=order_id,
        symbol=symbol,
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


import pytest


def test_duplicate_order_id_is_rejected():
    engine = MatchingEngine()

    first = make_order("B1", OrderSide.BUY, 100, 5)
    duplicate = make_order("B1", OrderSide.BUY, 99, 3)

    engine.process_order(first)

    with pytest.raises(ValueError, match="Duplicate order_id"):
        engine.process_order(duplicate)


def test_duplicate_order_id_across_symbols_is_rejected():
    engine = MatchingEngine()

    first = make_order("B1", OrderSide.BUY, 100, 5)
    engine.process_order(first)

    duplicate = Order(
        order_id="B1",
        symbol="OTHER",
        side=OrderSide.BUY,
        price=Decimal("99"),
        quantity=3,
    )

    with pytest.raises(ValueError, match="Duplicate order_id"):
        engine.process_order(duplicate)



def test_zero_quantity_order_is_rejected():
    with pytest.raises(ValueError, match="quantity must be positive"):
        make_order("B_ZERO", OrderSide.BUY, 100, 0)


def test_negative_price_order_is_rejected():
    with pytest.raises(
        ValueError,
        match="price must be a positive finite Decimal",
    ):
        make_order("B_NEG", OrderSide.BUY, -10, 5)



def test_cancel_open_buy_order():
    engine = MatchingEngine()
    buy = make_order("B_CANCEL", OrderSide.BUY, 100, 5)

    engine.process_order(buy)

    result = engine.cancel_order("TEST", "B_CANCEL")

    assert result is True
    assert buy.order_status == OrderStatus.CANCELLED
    assert engine.get_order("TEST", "B_CANCEL") is None


def test_cancel_unknown_order_returns_false():
    engine = MatchingEngine()

    result = engine.cancel_order("TEST", "UNKNOWN")

    assert result is False


def test_filled_order_cannot_be_cancelled():
    engine = MatchingEngine()

    buy = make_order("B_FILLED", OrderSide.BUY, 100, 5)
    sell = make_order("S_FILLED", OrderSide.SELL, 100, 5)

    engine.process_order(buy)
    engine.process_order(sell)

    result = engine.cancel_order("TEST", "B_FILLED")

    assert result is False
    assert buy.order_status == OrderStatus.FILLED


def test_cancel_partially_filled_order():
    engine = MatchingEngine()

    buy = make_order("B_PARTIAL", OrderSide.BUY, 100, 10)
    sell = make_order("S_PARTIAL", OrderSide.SELL, 100, 6)

    engine.process_order(buy)
    trades = engine.process_order(sell)

    assert len(trades) == 1
    assert buy.filled_quantity == 6
    assert buy.remaining_quantity == 4
    assert buy.order_status == OrderStatus.PARTIALLY_FILLED

    result = engine.cancel_order("TEST", "B_PARTIAL")

    assert result is True
    assert buy.order_status == OrderStatus.CANCELLED
    assert buy.filled_quantity == 6
    assert buy.remaining_quantity == 4
    assert engine.get_order("TEST", "B_PARTIAL") is None


def test_cancel_open_sell_order():
    engine = MatchingEngine()
    sell = make_order("S_CANCEL", OrderSide.SELL, 105, 5)

    engine.process_order(sell)

    result = engine.cancel_order("TEST", "S_CANCEL")

    assert result is True
    assert sell.order_status == OrderStatus.CANCELLED
    assert sell.remaining_quantity == 5
    assert sell.filled_quantity == 0
    assert engine.get_order("TEST", "S_CANCEL") is None


def test_cancelling_partial_order_preserves_trade_history():
    engine = MatchingEngine()

    buy = make_order("B_HISTORY", OrderSide.BUY, 100, 10)
    sell = make_order("S_HISTORY", OrderSide.SELL, 100, 6)

    engine.process_order(buy)
    trades_before_cancel = engine.process_order(sell)

    assert len(trades_before_cancel) == 1
    assert trades_before_cancel[0].quantity == 6

    result = engine.cancel_order("TEST", "B_HISTORY")

    assert result is True
    assert buy.order_status == OrderStatus.CANCELLED
    assert buy.filled_quantity == 6
    assert buy.remaining_quantity == 4

    # Cancelling the remaining quantity must not erase executed trades.
    all_trades = engine.get_trades("TEST")
    assert len(all_trades) == 1
    assert all_trades[0].trade_id == trades_before_cancel[0].trade_id
    assert all_trades[0].quantity == 6


def test_cancelling_one_order_preserves_other_orders():
    engine = MatchingEngine()

    first = make_order("B_FIRST", OrderSide.BUY, 100, 5)
    second = make_order("B_SECOND", OrderSide.BUY, 99, 8)

    engine.process_order(first)
    engine.process_order(second)

    assert engine.cancel_order("TEST", "B_FIRST") is True

    book = engine.get_order_book("TEST")

    assert book.get_best_buy() is second
    assert book.get_order("B_FIRST") is None
    assert book.get_order("B_SECOND") is second
    assert second.remaining_quantity == 8
    assert second.order_status == OrderStatus.OPEN


def test_cancelling_same_order_twice():
    engine = MatchingEngine()
    buy = make_order("B_TWICE", OrderSide.BUY, 100, 5)

    engine.process_order(buy)

    assert engine.cancel_order("TEST", "B_TWICE") is True
    assert buy.order_status == OrderStatus.CANCELLED

    assert engine.cancel_order("TEST", "B_TWICE") is False
    assert buy.order_status == OrderStatus.CANCELLED
    assert buy.remaining_quantity == 5


def test_one_order_matches_multiple_resting_orders():
    engine = MatchingEngine()

    first_buy = make_order("B1", OrderSide.BUY, 100, 4)
    second_buy = make_order("B2", OrderSide.BUY, 98, 6)
    incoming_sell = make_order("S1", OrderSide.SELL, 95, 10)

    assert engine.process_order(first_buy) == []
    assert engine.process_order(second_buy) == []

    trades = engine.process_order(incoming_sell)

    assert len(trades) == 2

    assert trades[0].buy_order_id == "B1"
    assert trades[0].quantity == 4
    assert trades[0].price == Decimal("100")

    assert trades[1].buy_order_id == "B2"
    assert trades[1].quantity == 6
    assert trades[1].price == Decimal("98")

    assert incoming_sell.filled_quantity == 10
    assert incoming_sell.remaining_quantity == 0
    assert incoming_sell.order_status == OrderStatus.FILLED

    assert first_buy.order_status == OrderStatus.FILLED
    assert second_buy.order_status == OrderStatus.FILLED

    assert engine.get_order("TEST", "B1") is None
    assert engine.get_order("TEST", "B2") is None
    assert engine.get_order("TEST", "S1") is None



def test_orders_with_different_symbols_do_not_match():
    engine = MatchingEngine()

    buy = make_order("B_SYMBOL", OrderSide.BUY, 100, 5, symbol="ABC")
    sell = make_order("S_SYMBOL", OrderSide.SELL, 90, 5, symbol="XYZ")

    assert engine.process_order(buy) == []
    assert engine.process_order(sell) == []

    assert buy.filled_quantity == 0
    assert sell.filled_quantity == 0

    assert buy.remaining_quantity == 5
    assert sell.remaining_quantity == 5

    assert buy.order_status == OrderStatus.OPEN
    assert sell.order_status == OrderStatus.OPEN

    assert engine.get_order("ABC", "B_SYMBOL") is buy
    assert engine.get_order("XYZ", "S_SYMBOL") is sell
