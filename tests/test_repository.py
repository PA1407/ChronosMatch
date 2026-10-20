
from uuid import uuid4

from app.database.repository import (
    create_order,
    get_order,
    update_order,
    save_trade,
    get_trade,
    list_trades,
)


def make_order(side="BUY", quantity=10):
    return {
        "order_id": str(uuid4()),
        "symbol": "ABC",
        "side": side,
        "limit_price": "100.00",
        "quantity": quantity,
        "remaining_quantity": quantity,
        "status": "NEW",
    }


def test_create_and_get_order():
    order = make_order()

    create_order(order)
    result = get_order(order["order_id"])

    assert result is not None
    assert result["order_id"] == order["order_id"]


def test_update_order():
    order = make_order()
    create_order(order)

    result = update_order(
        order["order_id"],
        {"status": "CANCELLED", "remaining_quantity": 0},
    )

    assert result["status"] == "CANCELLED"
    assert result["remaining_quantity"] == 0


def test_get_nonexistent_order():
    assert get_order(f"missing-{uuid4()}") is None


def test_save_and_get_trade():
    buy_order = make_order("BUY", 10)
    sell_order = make_order("SELL", 5)

    create_order(buy_order)
    create_order(sell_order)

    trade = {
        "trade_id": str(uuid4()),
        "symbol": "ABC",
        "buy_order_id": buy_order["order_id"],
        "sell_order_id": sell_order["order_id"],
        "execution_price": "100.00",
        "quantity": 5,
    }

    save_trade(trade)
    result = get_trade(trade["trade_id"])

    assert result is not None
    assert result["trade_id"] == trade["trade_id"]
    assert result["quantity"] == 5


def test_list_trades():
    result = list_trades(limit=10)

    assert isinstance(result, list)
    assert len(result) <= 10
