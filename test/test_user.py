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

    result = mocked_user.insert(user_dicts, as_list=True)

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
    assert result == "Add 2 users."


def test_insert_from_args(mocked_user):
    mocked_user.cursor.rowcount = 2
    result = mocked_user.insert(
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

    assert result == "Add 2 users."


def test_update(mocked_user):
    mocked_user.cursor.rowcount = 1
    actual = mocked_user.update(
        user_id=1,
        name="NewName",
        surname="NewSurname",
        birth_day="2000-01-01"
    )
    mocked_user.cursor.execute.assert_called_once()
    sql, params = mocked_user.cursor.execute.call_args[0]

    assert "UPDATE User SET" in sql
    assert "name = ?" in sql
    assert "surname = ?" in sql
    assert "birth_day = ?" in sql
    assert "WHERE id = ?" in sql
    assert params == ("NewName", "NewSurname", "2000-01-01", 1)

    mocked_user._db_connection.commit.assert_called_once()
    mocked_user.log_info.assert_called_with(f"The user with id=1 has been updated.")
    assert actual == f"The user with id=1 has been updated."


def test_delete_user_success(mocked_user):
    mocked_user.cursor.fetchone.return_value = (24,)
    mocked_user.cursor.rowcount = 1
    result = mocked_user.delete(user_id=24)
    assert mocked_user.cursor.execute.call_count == 2
    select_call = mocked_user.cursor.execute.call_args_list[0]
    assert "SELECT id FROM User WHERE id = ?" in select_call[0][0]
    assert select_call[0][1] == (24,)

    delete_call = mocked_user.cursor.execute.call_args_list[1]
    assert "DELETE FROM User WHERE id = ?" in delete_call[0][0]
    assert delete_call[0][1] == (24,)

    mocked_user.log_info.assert_called_once_with("User with id=24 deleted.")

    assert result == "User with id=24 deleted."

    mocked_user._db_connection.commit.assert_called_once()


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

def test_get_bank_with_oldest_client_found(mocked_user):
    mocked_user.cursor.fetchone.return_value = ("BankA", "Ivanova", "1950-01-01")
    actual = mocked_user.get_bank_with_oldest_client()
    mocked_user.cursor.execute.assert_called_once()
    assert actual == ("BankA", "Ivanova", "1950-01-01")

def test_get_accounts_of_under_18(mocked_user):
    mocked_user.cursor.fetchall.return_value = [("acc1", 1, "Anna", "2007-05-05")]
    result = mocked_user.get_accounts_of_under_18()
    mocked_user.cursor.execute.assert_called_once()
    assert result == [("acc1", 1, "Anna", "2007-05-05")]
