


from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_order():
    response = client.post(
        "/orders",
        json={
            "symbol": "ABC",
            "side": "BUY",
            "limit_price": "100.00",
            "quantity": 10,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "ABC"
    assert data["side"] == "BUY"
    assert data["quantity"] == 10
    assert data["remaining_quantity"] == 10


def test_get_nonexistent_order():
    response = client.get("/orders/nonexistent-id")
    assert response.status_code == 404


def test_get_created_order():
    create_response = client.post(
        "/orders",
        json={
            "symbol": "GETTEST",
            "side": "BUY",
            "limit_price": "100.00",
            "quantity": 5,
        },
    )

    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200
    assert response.json()["order_id"] == order_id


def test_cancel_order():
    create_response = client.post(
        "/orders",
        json={
            "symbol": "CANCELTEST",
            "side": "BUY",
            "limit_price": "100.00",
            "quantity": 5,
        },
    )

    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    response = client.delete(f"/orders/{order_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
    assert response.json()["remaining_quantity"] == 5


def test_cancel_nonexistent_order():
    response = client.delete("/orders/nonexistent-id")
    assert response.status_code == 404


def test_zero_quantity_invalid():
    response = client.post(
        "/orders",
        json={
            "symbol": "INVALIDTEST",
            "side": "BUY",
            "limit_price": "100.00",
            "quantity": 0,
        },
    )

    assert response.status_code == 422


def test_negative_price_invalid():
    response = client.post(
        "/orders",
        json={
            "symbol": "INVALIDTEST",
            "side": "BUY",
            "limit_price": "-10.00",
            "quantity": 5,
        },
    )

    assert response.status_code == 422


def test_cancel_partially_filled_order():
    # Create a BUY order for 10 units.
    buy_response = client.post(
        "/orders",
        json={
            "symbol": "PARTIALCANCELTEST",
            "side": "BUY",
            "limit_price": "100.00",
            "quantity": 10,
        },
    )

    assert buy_response.status_code == 201
    buy_order_id = buy_response.json()["order_id"]

    # Match 2 units using a SELL order.
    sell_response = client.post(
        "/orders",
        json={
            "symbol": "PARTIALCANCELTEST",
            "side": "SELL",
            "limit_price": "100.00",
            "quantity": 2,
        },
    )

    assert sell_response.status_code == 201

    # Confirm the BUY order is partially filled.
    get_response = client.get(f"/orders/{buy_order_id}")

    assert get_response.status_code == 200
    assert get_response.json()["status"] == "PARTIALLY_FILLED"
    assert get_response.json()["remaining_quantity"] == 8

    # Cancel the remaining 8 units.
    cancel_response = client.delete(f"/orders/{buy_order_id}")

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"
    assert cancel_response.json()["remaining_quantity"] == 8

    # Confirm the cancelled order is no longer in the active order book.
    orderbook_response = client.get("/orderbook/PARTIALCANCELTEST")

    assert orderbook_response.status_code == 200

    buy_orders = orderbook_response.json()["buy_orders"]
    assert all(order["order_id"] != buy_order_id for order in buy_orders)
