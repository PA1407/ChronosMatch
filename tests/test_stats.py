
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_stats_returns_success():
    response = client.get("/stats")

    assert response.status_code == 200


def test_get_stats_contains_expected_fields():
    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "total_orders",
        "active_orders",
        "filled_orders",
        "cancelled_orders",
        "total_trades",
    }

    assert expected_fields.issubset(data.keys())


def test_stats_values_are_non_negative_integers():
    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    for field in (
        "total_orders",
        "active_orders",
        "filled_orders",
        "cancelled_orders",
        "total_trades",
    ):
        assert isinstance(data[field], int)
        assert data[field] >= 0
