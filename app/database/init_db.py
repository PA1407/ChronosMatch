
from app.database.connection import get_connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
                limit_price TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                remaining_quantity INTEGER NOT NULL
                    CHECK (remaining_quantity >= 0),
                status TEXT NOT NULL CHECK (
                    status IN (
                        'NEW',
                        'PARTIALLY_FILLED',
                        'FILLED',
                        'CANCELLED'
                    )
                ),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                buy_order_id TEXT NOT NULL,
                sell_order_id TEXT NOT NULL,
                execution_price TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                executed_at TEXT NOT NULL,
                FOREIGN KEY (buy_order_id) REFERENCES orders(order_id),
                FOREIGN KEY (sell_order_id) REFERENCES orders(order_id)
            )
        """)


if __name__ == "__main__":
    initialize_database()
    print("ChronosMatch database initialized successfully.")
