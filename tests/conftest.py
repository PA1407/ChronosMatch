
import pytest

from app.database.connection import set_database_path
from app.database.init_db import initialize_database


@pytest.fixture(autouse=True)
def isolated_database(tmp_path):
    db_path = tmp_path / "test_chronosmatch.db"
    set_database_path(db_path)

    initialize_database()

    yield

    set_database_path(None)
