from unittest.mock import MagicMock, patch
import sqlite3
from lab4.base import Shape


class TestShape(Shape):
    def __init__(self):
        self._logger = MagicMock()

    def insert(self, *args, **kwargs): pass
    def update(self, record_id, **kwargs): pass
    def delete(self, record_id): pass
    def import_from_csv(self, filepath: str): pass

    def log_info(self, message):
        self._logger.info(message)

    def log_error(self, message: str):
        self._logger.error(message)

    def __enter__(self):
        self._db_connection = sqlite3.connect('my_database.db')
        self._cursor = self._db_connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._db_connection.commit()
        self._cursor.close()
        self._db_connection.close()

def test_log_info():
    shape = TestShape()
    shape.log_info("Test message")
    shape._logger.info.assert_called_once_with("Test message")

def test_log_error():
    shape = TestShape()
    shape.log_error("Test error")
    shape._logger.error.assert_called_once_with("Test error")

def test_cursor_property():
    shape = TestShape()
    shape._cursor = "test_cursor"
    assert shape.cursor == "test_cursor"

def test_insert():
    shape = TestShape()
    shape.insert = MagicMock()
    shape.insert(123, 234)
    shape.insert.assert_called_once_with(123, 234)

def test_database():
    with TestShape() as db:
        db._cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")
        db._cursor.execute("INSERT INTO test_table (name) VALUES ('Alice')")
        db._cursor.execute("SELECT * FROM test_table")
        rows = db._cursor.fetchall()
        print(rows)

