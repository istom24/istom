from .base import Shape
from .decorators import error_decorator
import csv


class Bank(Shape):
    @error_decorator
    def import_from_csv(self, filepath: str):
        banks = []

        with open(filepath, newline='', encoding='utf8') as file:
            reader = csv.reader(file)
            for row in reader:
                banks.append(row)

        return self.insert(*banks, as_list=True)

    @error_decorator
    def insert(self, *banks, as_list=False):
        banks_temp = banks[0] if as_list else banks
        new_data = []

        for bank in banks_temp:
            if isinstance(bank, dict):
                bank_name = bank.get("bank_name")
            else:
                bank_name = bank

            new_data.append((bank_name,))

        self.cursor.executemany('''
            INSERT OR IGNORE INTO Bank (name) VALUES (?)
        ''', new_data)

        self._db_connection.commit()
        self.log_info(f"Added {self.cursor.rowcount} banks.")
        return f"Added {self.cursor.rowcount} banks."

    @error_decorator
    def update(self, record_id, **kwargs):
        allowed_fields = {"name"}
        update_fields = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                update_fields.append(f"{key} = ?")
                values.append(value)
            else:
                self.log_error(f"The {key} field cannot be updated.")

        if not update_fields:
            self.log_info("No fields to update.")
            return "No fields to update."

        sql = f"UPDATE Bank SET {', '.join(update_fields)} WHERE id = ?"
        values.append(record_id)

        self.cursor.execute(sql, tuple(values))
        self._db_connection.commit()

        if self.cursor.rowcount == 0:
            self.log_info(f"Bank with id={record_id} not found.")
            return f"Bank with id={record_id} not found."

        self.log_info(f"Bank with id={record_id} updated.")
        return f"Bank with id={record_id} updated."

    @error_decorator
    def delete(self, record_id):
        self.cursor.execute("SELECT id FROM Bank WHERE id = ?", (record_id,))
        result = self.cursor.fetchone()

        if result is None:
            self.log_info(f"Bank with id={record_id} not found.")
            return f"Bank with id={record_id} not found."

        self.cursor.execute("DELETE FROM Bank WHERE id = ?", (record_id,))
        self._db_connection.commit()
        self.log_info(f"Bank with id={record_id} deleted.")
        return f"Bank with id={record_id} deleted."
