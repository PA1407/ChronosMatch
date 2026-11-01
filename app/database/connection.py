
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "chronosmatch.db"

# Allows tests to use a separate database.
_test_db_path = None


def set_database_path(path):
    global _test_db_path
    _test_db_path = Path(path) if path is not None else None


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    db_path = _test_db_path or DB_PATH

    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
