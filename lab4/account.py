from base import Shape
from .decorators import error_decorator
import csv


class Account(Shape):
    @error_decorator
    def import_from_csv(self, filepath: str):
        accounts = []

        with open(filepath, newline='', encoding='utf8') as file:
            reader = csv.reader(file)
            for row in reader:
                accounts.append(row)

        return self.insert(accounts, as_list=True)

    @error_decorator
    def insert(self, *accounts, as_list=False):
        accounts_temp = accounts[0] if as_list else accounts
        new_data = []

        for account in accounts_temp:
            if isinstance(account, dict):
                account_number = account.get("account_number")
                user_id = account.get("user_id")
                acc_type = account.get("type")
                bank_id = account.get("bank_id")
                currency = account.get("currency")
                amount = account.get("amount")
                status = account.get("status")
            else:
                account_number, user_id, acc_type, bank_id, currency, amount, status = account

            new_data.append((
                account_number, user_id, acc_type, bank_id, currency, amount, status
            ))

        self.cursor.executemany('''
            INSERT OR IGNORE INTO Account (
                account_number, user_id, type, bank_id, currency, amount, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)''', new_data)
        self._db_connection.commit()
        self.log_info(f"Added {self.cursor.rowcount} account(s).")
        return f"Added {self.cursor.rowcount} account(s)."

    @error_decorator
    def update(self, record_id, **kwargs):
        fields = {
            "account_number", "user_id", "type", "bank_id", "currency", "amount", "status"
        }
        update_fields = []
        values = []

        for key, value in kwargs.items():
            if key in fields:
                update_fields.append(f"{key} = ?")
                values.append(value)
            else:
                self.log_error(f"The {key} field cannot be updated.")

        if not update_fields:
            self.log_info("No fields to update..")
            return "No fields to update."

        sql = f"UPDATE Account SET {', '.join(update_fields)} WHERE id = ?"
        values.append(record_id)

        self.cursor.execute(sql, tuple(values))
        self._db_connection.commit()
        if self.cursor.rowcount == 0:
            self.log_info(f"Account with id={record_id} not found.")
            return f"Account with id={record_id} not found."

        self.log_info(f"Account with id={record_id} updated.")
        return f"Account with id={record_id} updated."

    @error_decorator
    def delete(self, record_id):
        self.cursor.execute("SELECT id FROM Account WHERE id = ?", (record_id,))
        result = self.cursor.fetchone()

        if result is None:
            self.log_info(f"Account with id={record_id} not found.")
            return f"Account with id={record_id} not found."

        self.cursor.execute("DELETE FROM Account WHERE id = ?", (record_id,))
        self._db_connection.commit()
        self.log_info(f"Account with id={record_id} deleted.")
        return f"Account with id={record_id} deleted."
