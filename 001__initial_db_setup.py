import sqlite3
import argparse
from constants import DB_PATH


def create_database(unique_name_surname=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    conn.execute('''CREATE TABLE IF NOT EXISTS Bank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )''')

    user_table_sql = '''CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        birth_day DATE,
        accounts TEXT NOT NULL'''

    if unique_name_surname:
        user_table_sql += ''',
        UNIQUE(name, surname)'''

    user_table_sql += ')'
    conn.execute(user_table_sql)

    conn.execute('''CREATE TABLE IF NOT EXISTS Account (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT CHECK(type IN ('credit', 'debit')) NOT NULL,
        account_number TEXT NOT NULL UNIQUE,
        bank_id INTEGER NOT NULL,
        currency TEXT CHECK(currency IN ('USD', 'EUR', 'UAH')) NOT NULL,
        amount INTEGER NOT NULL,
        status TEXT CHECK(status IN ('gold', 'silver', 'platinum')),
        FOREIGN KEY (user_id) REFERENCES User(id),
        FOREIGN KEY (bank_id) REFERENCES Bank(id)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank_sender_name TEXT NOT NULL,
        account_sender_id INTEGER NOT NULL,
        bank_receiver_name TEXT NOT NULL,
        account_receiver_id INTEGER NOT NULL,
        sent_currency TEXT CHECK(sent_currency IN ('USD', 'EUR', 'UAH')) NOT NULL,
        sent_amount INTEGER NOT NULL,
        datetime TEXT,
        FOREIGN KEY (account_sender_id) REFERENCES Account(id),
        FOREIGN KEY (account_receiver_id) REFERENCES Account(id)
    )''')

    banks = [
        ('MONO Bank',),
        ('Privat24 Bank',)
    ]
    cursor.executemany('''INSERT OR IGNORE INTO Bank (name) VALUES (?)''', banks)

    users = [
        ('Alice', 'Martin', '2001-05-10', '123344'),
        ('Elizabeth', 'Miller', '2004-08-22', '3545456'),
        ('Barbara', 'Lopez', '1999-02-11', '34535345')
    ]
    cursor.executemany('''INSERT OR IGNORE INTO User (
        name, surname, birth_day, accounts
    ) VALUES (?, ?, ?, ?)''', users)

    accounts = [
        (1, 'debit', 'ID--j3-q-432547-u9', 1, 'USD', 1000, 'gold'),
        (2, 'credit', 'ID--j3-q-432597-u9', 2, 'EUR', 500, 'silver')
    ]
    cursor.executemany('''INSERT OR IGNORE INTO Account (
        user_id, type, account_number, 
        bank_id, currency, amount, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?)''', accounts)

    transactions_data = [
        ('MONO Bank', 1, 'MONO Bank', 2, 'USD', 1500, '2025-05-28 10:30:00'),
        ('Privat24 Bank', 2, 'MONO Bank', 1, 'EUR', 500, '2025-05-27 15:45:00'),
        ('MONO Bank', 1, 'Privat24 Bank', 3, 'UAH', 2500, '2025-05-26 09:20:00'),
    ]
    cursor.executemany('''
        INSERT INTO Transactions (
            bank_sender_name, account_sender_id,
            bank_receiver_name, account_receiver_id,
            sent_currency, sent_amount, datetime
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', transactions_data)

    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-unique', action='store_false', dest='unique_name_surname')

    args = parser.parse_args()
    create_database(unique_name_surname=args.unique_name_surname)
    print(f"A database has been created with a uniqueness constraint: {args.unique_name_surname}")


if __name__ == "__main__":
    main()
