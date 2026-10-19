
from uuid import uuid4

from app.database.repository import create_order, get_order, update_order

# Create sample order data
order_id = str(uuid4())

order_data = {
    "order_id": order_id,
    "symbol": "ABC",
    "side": "BUY",
    "limit_price": "100.00",
    "quantity": 10,
    "remaining_quantity": 10,
    "status": "NEW",
}

# 1. Save the order to SQLite
saved_order = create_order(order_data)
print("1. Order saved:")
print(saved_order)

# 2. Retrieve the order from SQLite
retrieved_order = get_order(order_id)
print("\n2. Order retrieved:")
print(retrieved_order)

# 3. Update the order status
updated_order = update_order(
    order_id,
    {"status": "CANCELLED", "remaining_quantity": 0},
)
print("\n3. Order after update:")
print(updated_order)

# 4. Verify the update
assert retrieved_order is not None
assert updated_order["status"] == "CANCELLED"
assert updated_order["remaining_quantity"] == 0

print("\nSUCCESS: Repository tests passed!")

def test_save_and_get_trade():
    from uuid import uuid4

    from app.database.repository import (
        create_order,
        save_trade,
        get_trade,
    )

    buy_id = str(uuid4())
    sell_id = str(uuid4())
    trade_id = str(uuid4())

    create_order({
        "order_id": buy_id,
        "symbol": "ABC",
        "side": "BUY",
        "limit_price": "100.00",
        "quantity": 10,
        "remaining_quantity": 5,
        "status": "PARTIALLY_FILLED",
    })

    create_order({
        "order_id": sell_id,
        "symbol": "ABC",
        "side": "SELL",
        "limit_price": "100.00",
        "quantity": 5,
        "remaining_quantity": 0,
        "status": "FILLED",
    })

    trade = {
        "trade_id": trade_id,
        "symbol": "ABC",
        "buy_order_id": buy_id,
        "sell_order_id": sell_id,
        "execution_price": "100.00",
        "quantity": 5,
    }

    save_trade(trade)
    result = get_trade(trade_id)

    assert result is not None
    assert result["trade_id"] == trade_id
    assert result["quantity"] == 5


def test_list_trades():
    from app.database.repository import list_trades

    result = list_trades(limit=10)

    assert isinstance(result, list)
    assert len(result) <= 10

