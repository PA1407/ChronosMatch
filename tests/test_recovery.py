
from uuid import uuid4

from app.database.repository import create_order, save_trade
from app.engine.matching_engine import MatchingEngine


def test_restore_open_order_from_database():
    order_id = str(uuid4())

    # Save a partially filled order in SQLite.
    create_order({
        "order_id": order_id,
        "symbol": "RECOVERY",
        "side": "BUY",
        "limit_price": "150.00",
        "quantity": 10,
        "remaining_quantity": 6,
        "status": "PARTIALLY_FILLED",
    })

    # Simulate a fresh matching engine after restart.
    new_engine = MatchingEngine()

    assert new_engine.get_order("RECOVERY", order_id) is None

    # Restore previous state from SQLite.
    new_engine.restore_from_database()

    # Verify that the order has been recovered.
    restored_order = new_engine.get_order("RECOVERY", order_id)

    assert restored_order is not None
    assert restored_order.order_id == order_id
    assert restored_order.remaining_quantity == 6
    assert restored_order.filled_quantity == 4
    assert restored_order.order_status.value == "PARTIALLY_FILLED"


def test_restore_trade_history_from_database():
    buy_id = str(uuid4())
    sell_id = str(uuid4())
    trade_id = str(uuid4())

    # Create the two orders required by the trade's foreign keys.
    create_order({
        "order_id": buy_id,
        "symbol": "RECOVERY",
        "side": "BUY",
        "limit_price": "150.00",
        "quantity": 5,
        "remaining_quantity": 0,
        "status": "FILLED",
    })

    create_order({
        "order_id": sell_id,
        "symbol": "RECOVERY",
        "side": "SELL",
        "limit_price": "150.00",
        "quantity": 5,
        "remaining_quantity": 0,
        "status": "FILLED",
    })

    # Save an executed trade.
    save_trade({
        "trade_id": trade_id,
        "symbol": "RECOVERY",
        "buy_order_id": buy_id,
        "sell_order_id": sell_id,
        "execution_price": "150.00",
        "quantity": 5,
    })

    # Simulate a fresh engine after restart.
    new_engine = MatchingEngine()
    new_engine.restore_from_database()

    # Verify that trade history was recovered.
    restored_trades = new_engine.get_trades("RECOVERY")

    assert len(restored_trades) == 1
    assert restored_trades[0].trade_id == trade_id
    assert restored_trades[0].quantity == 5
    assert str(restored_trades[0].price) == "150.00"
