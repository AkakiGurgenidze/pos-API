import os

from infra.sqlite.database_connect import Database


def test_database_initial_and_close_successful() -> None:
    db = Database(":memory:", os.path.abspath("../infra/sqlite/start_up.sql"))
    db.initial()
    db.close_database()
