from .base import Shape
import csv
from .decorators import error_decorator
from datetime import datetime, timedelta
from .decorators import db_connection_decorator

class User(Shape):
    @error_decorator
    def import_from_csv(self, filepath: str):
        users = []
        with open(filepath, newline='', encoding='utf8') as file:
            reader = csv.reader(file)
            for row in reader:
                users.append(row)
        return self.insert(*users, as_list=True)

    @error_decorator
    def insert(self, *users, as_list=False):
        users_temp = users[0] if as_list else users
        new_data = []

        for user in users_temp:
            if isinstance(user, dict):
                name, surname = self._parse_full_name(user["user_full_name"])
                birth_day = user.get("birth_day", None)
                accounts = user.get("accounts", None)
            else:
                name, surname, birth_day, accounts = user

            new_data.append((name, surname, birth_day, accounts))

        self.cursor.executemany('''
            INSERT OR IGNORE INTO User (
                name, surname, birth_day, accounts
            ) VALUES (?, ?, ?, ?)''', new_data)
        self._db_connection.commit()

        self.log_info(f"Add {self.cursor.rowcount} users.")
        return f"Add {self.cursor.rowcount} users."

    @error_decorator
    def update(self, record_id, **kwargs):

        allowed_fields = {"name", "surname", "birth_day", "accounts"}
        update_fields = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                update_fields.append(f"{key} = ?")
                values.append(value)
            else:
                self.log_error(f"The {key} field cannot be updated.")

        if not update_fields:
            self.log_info("There are no fields to update.")
            return "There are no fields to update."

        sql = f"UPDATE User SET {', '.join(update_fields)} WHERE id = ?"
        values.append(record_id)

        self.cursor.execute(sql, tuple(values))
        self._db_connection.commit()

        if self.cursor.rowcount == 0:
            self.log_info(f"User with id={record_id} not found.")
            return f"User with id={record_id} not found."

        self.log_info(f"The user with id={record_id} has been updated.")
        return f"The user with id={record_id} has been updated."

    @error_decorator
    def delete(self, record_id):
        self.cursor.execute("SELECT id FROM User WHERE id = ?", (record_id,))
        result = self.cursor.fetchone()

        if result is None:
            self.log_info(f"User with id={record_id} not found.")
            return f"User with id={record_id} not found."

        self._db_connection.commit()
        self.cursor.execute("DELETE FROM User WHERE id = ?", (record_id,))
        self.log_info(f"User with id={record_id} deleted.")
        return f"User with id={record_id} deleted."

    @error_decorator
    def transfer_money(self, from_currency: str, to_currency: str, summa: float):

        self.cursor.execute("SELECT amount, currency FROM Account WHERE account_number = ?", (from_currency,))
        sender = self.cursor.fetchone()
        if not sender:
            self.log_error(f"Sender account {from_currency} not found.")
            return f"Sender account {from_currency} not found."
        sender_amount, sender_currency = sender

        if sender_amount < summa:
            self.log_error("Insufficient funds for transfer.")
            return "Insufficient funds for transfer."

        self.cursor.execute("SELECT amount, currency FROM Account WHERE account_number = ?", (to_currency,))
        receiver = self.cursor.fetchone()
        if not receiver:
            self.log_error(f"Receiver account {to_currency} not found.")
            return f"Receiver account {to_currency} not found."
        _, receiver_currency = receiver

        if sender_currency != receiver_currency:
            rate = self.get_exchange_course(sender_currency.upper(), receiver_currency.upper())
            if rate is None:
                self.log_error("Cannot get exchange rate.")
                return "Cannot get exchange rate."
            converted_summa = summa * rate
        else:
            converted_summa = summa

        self.cursor.execute("UPDATE Account SET amount = amount - ? WHERE account_number = ?", (summa, from_currency))
        self.cursor.execute("UPDATE Account SET amount = amount + ? WHERE account_number = ?",
                            (converted_summa, to_currency))
        self._db_connection.commit()

        self.log_info(f"Transferred {summa} {sender_currency} from {from_currency} to {to_currency} "
                      f"({converted_summa} {receiver_currency}")
        return f"Transferred {summa} {sender_currency} from {from_currency} to {to_currency} {converted_summa} {receiver_currency}"

    @staticmethod
    def _parse_full_name(full_name):
        parts = full_name.strip().split()
        name = parts[0] if len(parts) > 0 else None
        surname = parts[1] if len(parts) > 1 else None
        return name, surname

    @db_connection_decorator
    def get_users_with_debts(self):
        self.cursor.execute("""
            SELECT u.name, u.surname
            FROM User u
            JOIN Account a ON u.id = a.user_id
            WHERE a.amount < 0""")
        users = []
        for row in self.cursor.fetchall():
            full_name = f"{row[0]} {row[1]}"
            users.append(full_name)
        return users

    # Банк, який обслуговує найстарішого клієнта.
    @db_connection_decorator
    def get_bank_with_oldest_client(self):
        self.cursor.execute("""
            SELECT b.name, u.surname, u.birth_day 
            FROM Bank b
            JOIN Account a ON b.id = a.bank_id
            JOIN User u ON a.user_id = u.id
            ORDER BY u.birth_day ASC
            LIMIT 1""")
        result = self.cursor.fetchone()
        if result:
            bank_name, surname, birth_day = result
            return bank_name, surname, birth_day
        return None

    # Банк з найбільшою кількістю унікальних користувачів, які здійснювали вихідні транзакції.

    def get_bank_with_most_unique_outbound_users(self):
        self.cursor.execute("""
        SELECT b.name, COUNT(DISTINCT a.user_id) AS unique_users_count
        FROM Transactions t
        JOIN Account a ON t.account_sender_id = a.id
        JOIN Bank b ON a.bank_id = b.id
        GROUP BY b.id
        ORDER BY unique_users_count DESC
        LIMIT 1""")
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Видаляти користувачів і рахунки, які не мають повної інформації.
    def delete_incomplete_users_and_accounts(self):
        self.cursor.execute("DELETE FROM Account WHERE account_number IS NULL OR user_id IS NULL")
        self.cursor.execute("DELETE FROM User WHERE name IS NULL OR surname IS NULL")
        self._db_connection.commit()

    # Транзакції конкретного користувача за останні 3 місяці
    def get_user_transactions_last_3_months(self, user_id):
        three_months_ago = datetime.now() - timedelta(days=90)
        date_str = three_months_ago.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            SELECT t.*
            FROM Transactions t
            WHERE (
                t.account_sender_id IN (
                    SELECT id FROM Account WHERE user_id = ?
                )
                OR t.account_receiver_id IN (
                    SELECT id FROM Account WHERE user_id = ?
               )
            )
            AND t.datetime >= ?
            ORDER BY t.datetime DESC""", (user_id, user_id, date_str))
        return self.cursor.fetchall()

    # (Якщо ви хочете потренувати деякі з вивчених навичок, створіть власний функціонал для себе)

    def get_accounts_of_under_18(self):
        eighteen_years_ago = datetime.now() - timedelta(days=18 * 365)
        date_str = eighteen_years_ago.strftime("%Y-%m-%d")
        self.cursor.execute("""
            SELECT a.account_number, u.id, u.name, u.birth_day
            FROM Account a
            JOIN User u ON a.user_id = u.id
            WHERE u.birth_day > ? """, (date_str,))
        return self.cursor.fetchall()
