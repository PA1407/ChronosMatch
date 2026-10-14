
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
