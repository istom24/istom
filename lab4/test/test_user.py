import pytest
from unittest.mock import MagicMock, patch
from lab4.user import User


@pytest.fixture
def mocked_user():
    user = User()
    user._cursor = MagicMock()
    user.cursor.executemany = MagicMock()
    user._db_connection = MagicMock()
    user._db_connection.commit = MagicMock()
    user.log_info = MagicMock()
    user.log_error = MagicMock()
    user.log_info.assert_called_with = MagicMock()
    return user

    def delete(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):

        pass


def test_insert_from_list_of_lists(mocked_user):
    mocked_user.cursor.rowcount = 2
    data = [
        ("John", "Doe", "1990-01-01", "1234"),
        ("Jane", "Smith", "1991-02-02", "3456")
    ]
    actual = mocked_user.insert(data, as_list=True)

    assert mocked_user.cursor.executemany.call_count == 1
    sql, params = mocked_user.cursor.executemany.call_args[0]

    normalized_sql = ' '.join(sql.strip().split())
    expected_sql = 'INSERT OR IGNORE INTO User ( name, surname, birth_day, accounts ) VALUES (?, ?, ?, ?)'

    assert normalized_sql == expected_sql
    assert params == data
    assert actual == "Add 2 users."
    mocked_user._db_connection.commit.assert_called_once()


def test_insert_multiple_dicts(mocked_user):
    mocked_user.cursor.rowcount = 2
    mocked_user._parse_full_name = lambda x: (x.split()[0], x.split()[1])

    user_dicts = [
        {
            "user_full_name": "Anna Ivanova",
            "birth_day": "1995-01-01",
            "accounts": "678564"
        },
        {
            "user_full_name": "Ivan Petrov",
            "birth_day": "1988-12-12",
            "accounts": "123456"
        }
    ]

    actual = mocked_user.insert(user_dicts, as_list=True)

    mocked_user.cursor.executemany.assert_called_once()

    sql, params = mocked_user.cursor.executemany.call_args[0]

    normalized_sql = ' '.join(sql.strip().split())
    assert "INSERT OR IGNORE INTO User" in normalized_sql
    assert "VALUES (?, ?, ?, ?)" in normalized_sql

    assert params == [
        ("Anna", "Ivanova", "1995-01-01", "678564"),
        ("Ivan", "Petrov", "1988-12-12", "123456")
    ]

    mocked_user._db_connection.commit.assert_called_once()
    assert actual == "Add 2 users."


def test_insert_from_args(mocked_user):
    mocked_user.cursor.rowcount = 2
    actual = mocked_user.insert(
        ("John", "Doe", "1990-01-01", "1234"),
        ("Jane", "Smith", "1991-02-02", "3456"),
        as_list=False
    )
    mocked_user.cursor.executemany.assert_called_once()
    sql, params = mocked_user.cursor.executemany.call_args[0]

    normalized_sql = ' '.join(sql.strip().split())
    assert "INSERT OR IGNORE INTO User" in normalized_sql
    assert "VALUES (?, ?, ?, ?)" in normalized_sql

    assert params == [
        ("John", "Doe", "1990-01-01", "1234"),
        ("Jane", "Smith", "1991-02-02", "3456")
    ]

    assert actual == "Add 2 users."


def test_delete_user_not_found_simple(mocked_user):
    mocked_user.cursor.fetchone.return_value = None
    actual = mocked_user.delete(record_id=24)
    assert mocked_user.cursor.execute.call_count == 1
    mocked_user._db_connection.commit.assert_not_called()
    mocked_user.log_info.assert_called_once_with("User with id=24 not found.")
    assert actual == "User with id=24 not found."


def test_transfer_money_insufficient_funds(mocked_user):
    mocked_user.cursor.fetchone.side_effect = [
        (100, "USD"),
    ]
    actual = mocked_user.transfer_money("acc1", "acc2", 200)
    mocked_user.log_error.assert_called_once_with("Insufficient funds for transfer.")
    assert actual == "Insufficient funds for transfer."

def test_transfer_money_sender_not_found(mocked_user):
    mocked_user.cursor.fetchone.return_value = None
    actual = mocked_user.transfer_money("acc1", "acc2", 100)
    mocked_user.log_error.assert_called_once_with("Sender account acc1 not found.")
    assert actual == "Sender account acc1 not found."

def test_parse_full_name():
    parse = User._parse_full_name
    assert parse("Anna Ivanova") == ("Anna", "Ivanova")
    assert parse("SingleName") == ("SingleName", None)
    assert parse("") == (None, None)

def test_get_accounts_of_under_18(mocked_user):
    mocked_user.cursor.fetchall.return_value = [("acc1", 1, "Anna", "2007-05-05")]
    result = mocked_user.get_accounts_of_under_18()
    mocked_user.cursor.execute.assert_called_once()
    assert result == [("acc1", 1, "Anna", "2007-05-05")]
