
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.database.connection import get_connection


def _now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _value(value: Any) -> Any:
    """Convert enums and Decimal values to SQLite-friendly values."""
    if isinstance(value, Decimal):
        return str(value)

    if hasattr(value, "value"):
        return value.value

    return value


def create_order(order: dict) -> dict:
    """Insert a new order and return the saved record."""
    now = _now()

    record = {
        "order_id": order["order_id"],
        "symbol": order["symbol"],
        "side": _value(order["side"]),
        "limit_price": str(order["limit_price"]),
        "quantity": order["quantity"],
        "remaining_quantity": order.get(
            "remaining_quantity", order["quantity"]
        ),
        "status": _value(order.get("status", "NEW")),
        "created_at": order.get("created_at", now),
        "updated_at": order.get("updated_at", now),
    }

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO orders (
                order_id, symbol, side, limit_price,
                quantity, remaining_quantity, status,
                created_at, updated_at
            )
            VALUES (
                :order_id, :symbol, :side, :limit_price,
                :quantity, :remaining_quantity, :status,
                :created_at, :updated_at
            )
            """,
            record,
        )

    return record


def get_order(order_id: str) -> dict | None:
    """Retrieve an order by its ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()

    return dict(row) if row else None


def list_orders() -> list[dict]:
    """Retrieve all orders in creation order."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM orders
            ORDER BY created_at ASC, order_id ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def update_order(order_id: str, updates: dict) -> dict | None:
    """Update allowed order fields and return the updated record."""
    allowed_fields = {
        "remaining_quantity",
        "status",
        "limit_price",
        "quantity",
    }

    updates = {
        key: _value(value)
        for key, value in updates.items()
        if key in allowed_fields
    }

    if not updates:
        return get_order(order_id)

    updates["updated_at"] = _now()

    assignments = ", ".join(
        f"{field} = :{field}" for field in updates
    )
    updates["order_id"] = order_id

    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            UPDATE orders
            SET {assignments}
            WHERE order_id = :order_id
            """,
            updates,
        )

        if cursor.rowcount == 0:
            return None

    return get_order(order_id)


def save_trade(trade: dict) -> dict:
    """Persist one successfully executed trade."""
    record = {
        "trade_id": trade["trade_id"],
        "symbol": trade["symbol"],
        "buy_order_id": trade["buy_order_id"],
        "sell_order_id": trade["sell_order_id"],
        "execution_price": str(trade["execution_price"]),
        "quantity": trade["quantity"],
        "executed_at": trade.get("executed_at", _now()),
    }

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO trades (
                trade_id, symbol, buy_order_id, sell_order_id,
                execution_price, quantity, executed_at
            )
            VALUES (
                :trade_id, :symbol, :buy_order_id, :sell_order_id,
                :execution_price, :quantity, :executed_at
            )
            """,
            record,
        )

    return record


def get_trade(trade_id: str) -> dict | None:
    """Retrieve a trade by its ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM trades WHERE trade_id = ?",
            (trade_id,),
        ).fetchone()

    return dict(row) if row else None


def list_trades(limit: int = 100) -> list[dict]:
    """Retrieve the most recent trades, limited by count."""
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM trades
            ORDER BY executed_at DESC, trade_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def list_all_trades() -> list[dict]:
    """Retrieve all persisted trades in execution order."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM trades
            ORDER BY executed_at ASC, trade_id ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_order_stats() -> dict:
    """Return aggregate order and trade statistics."""
    with get_connection() as connection:
        total_orders = connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

        active_orders = connection.execute(
            """
            SELECT COUNT(*) FROM orders
            WHERE status IN ('NEW', 'PARTIALLY_FILLED')
            """
        ).fetchone()[0]

        filled_orders = connection.execute(
            """
            SELECT COUNT(*) FROM orders
            WHERE status = 'FILLED'
            """
        ).fetchone()[0]

        cancelled_orders = connection.execute(
            """
            SELECT COUNT(*) FROM orders
            WHERE status = 'CANCELLED'
            """
        ).fetchone()[0]

        total_trades = connection.execute(
            "SELECT COUNT(*) FROM trades"
        ).fetchone()[0]

    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "filled_orders": filled_orders,
        "cancelled_orders": cancelled_orders,
        "total_trades": total_trades,
    }
