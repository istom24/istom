import sqlite3
import logging
from abc import ABC, abstractmethod
from constants import DB_PATH


class Shape(ABC):
    def __init__(self, db_connection=None):
        self._db_connection = db_connection
        self._logger = logging.getLogger()

    def log_info(self, message: str):
        self._logger.info(message)

    def log_error(self, message: str):
        self._logger.error(message)

    @abstractmethod
    def insert(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, record_id, **kwargs):
        pass

    @abstractmethod
    def delete(self, record_id):
        pass

    @abstractmethod
    def import_from_csv(self, filepath: str):
        pass

    def __enter__(self):
        self._db_connection = sqlite3.connect(DB_PATH)
        self._cursor = self._db_connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._db_connection.commit()
        self._cursor.close()
        self._db_connection.close()

    @property
    def cursor(self):
        return self._cursor
