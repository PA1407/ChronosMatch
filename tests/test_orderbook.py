
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_orderbook():
    response = client.get("/orderbook/ABC")

    assert response.status_code == 200

    data = response.json()
    assert data["symbol"] == "ABC"
    assert data["buy_orders"] == []
    assert data["sell_orders"] == []


def test_orderbook_normalizes_symbol():
    response = client.get("/orderbook/abc")

    assert response.status_code == 200
    assert response.json()["symbol"] == "ABC"
