
import requests

API_BASE_URL = "http://127.0.0.1:8000"


def check_api_health():
    """Check whether the backend API is reachable."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/docs",
            timeout=5
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def submit_order(symbol, side, limit_price, quantity):
    """Submit a new buy or sell order."""
    payload = {
        "symbol": symbol,
        "side": side,
        "limit_price": str(limit_price),
        "quantity": quantity
    }

    response = requests.post(
        f"{API_BASE_URL}/orders",
        json=payload,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_order(order_id):
    """Retrieve order details."""
    response = requests.get(
        f"{API_BASE_URL}/orders/{order_id}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def cancel_order(order_id):
    """Cancel an existing order."""
    response = requests.delete(
        f"{API_BASE_URL}/orders/{order_id}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_orderbook(symbol):
    """Retrieve buy and sell orders."""
    response = requests.get(
        f"{API_BASE_URL}/orderbook/{symbol}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_orderbook_summary(symbol):
    """Retrieve order-book summary."""
    response = requests.get(
        f"{API_BASE_URL}/orderbook/{symbol}/summary",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_trades(symbol=None, limit=100):
    """Retrieve recent executed trades."""
    params = {"limit": limit}

    if symbol:
        params["symbol"] = symbol

    response = requests.get(
        f"{API_BASE_URL}/trades",
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_stats():
    """Retrieve matching-engine statistics."""
    response = requests.get(
        f"{API_BASE_URL}/stats",
        timeout=10
    )
    response.raise_for_status()
    return response.json()
