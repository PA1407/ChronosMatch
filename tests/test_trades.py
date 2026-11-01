
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_trades_returns_list():
    response = client.get("/trades")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_trades_with_limit():
    response = client.get("/trades?limit=10")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 10


def test_get_trades_with_invalid_limit():
    response = client.get("/trades?limit=0")

    assert response.status_code == 422
