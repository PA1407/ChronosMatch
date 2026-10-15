
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_order():
    response = client.post(
        "/orders",
        json={
            "symbol": "TEST",
            "side": "BUY",
            "limit_price": "100.00",
            "quantity": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["order_id"]
    assert data["symbol"] == "TEST"
    assert data["side"] == "BUY"
    assert data["limit_price"] == "100.00"
    assert data["quantity"] == 10
    assert data["remaining_quantity"] == 10
    assert data["status"] == "NEW"


def test_get_nonexistent_order():
    response = client.get(
        "/orders/nonexistent-order-id"
    )

    assert response.status_code == 404


def test_get_created_order():
    create_response = client.post(
        "/orders",
        json={
            "symbol": "TEST",
            "side": "BUY",
            "limit_price": "100.00",
            "quantity": 10,
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["order_id"]

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["symbol"] == "TEST"
    assert data["status"] == "NEW"


def test_cancel_order():
    create_response = client.post(
        "/orders",
        json={
            "symbol": "TEST",
            "side": "SELL",
            "limit_price": "105.00",
            "quantity": 5,
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["order_id"]

    response = client.delete(f"/orders/{order_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["status"] == "CANCELLED"
    assert data["remaining_quantity"] == 0


def test_cancel_nonexistent_order():
    response = client.delete(
        "/orders/nonexistent-order-id"
    )

    assert response.status_code == 404
