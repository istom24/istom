from bank import Bank
from decorators import db_connection_decorator
import logging
from user import User
from account import Account


def main():
    logging.basicConfig(
        filename='app.log', filemode='a', level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def demo_insert_banks():
    with Bank() as bank:
        result = bank.insert(
            "My Bank",
            "Your Bank",
            as_list=False
        )
        print(result)


@db_connection_decorator(Bank)
def demo_update_bank(bank_obj):
    return bank_obj.update(1, name="Updated Bank Name")


@db_connection_decorator(User)
def demo_transfer_money(user_obj):
    return user_obj.transfer_money("123456", "234567", 50.0)


@db_connection_decorator(User)
def demo_update_user(user_obj):
    return user_obj.update(
        user_id=1,
        name="Oksana",
        surname="Kovalenko",
        birth_day="1995-04-21",
        accounts="ID--g5-k-934871-p1"
    )


@db_connection_decorator(User)
def demo_create_users(user_obj):
    sample_users = [
        ("Anna", "Ivanova", "2001-05-12", "ID--a1-12345-x"),
        ("Dmytro", "Shevchenko", "2000-03-15", "ID--d3-45678-y"),
        ("Olena", "Tkachenko", "1999-11-09", "ID--o2-23456-z"),
        ("Ihor", "Bondar", "2002-07-21", "ID--i9-98765-w"),
        ("Kateryna", "Melnyk", "2004-01-01", "ID--k7-11111-v"),
        ("Taras", "Kovalenko", "2003-12-30", "ID--t4-22222-u"),
        ("Yulia", "Kravchenko", "2005-04-17", "ID--y5-33333-t"),
        ("Oleh", "Pavlenko", "2006-09-14", "ID--o8-44444-s"),
        ("Larysa", "Moroz", "2007-02-28", "ID--l1-55555-r"),
        ("Petro", "Hnatyuk", "2005-08-08", "ID--p3-66666-q")
    ]
    result = user_obj.insert(sample_users, as_list=True)

@db_connection_decorator(User)
def demo_call_all_methods(user_obj):

    print(user_obj.get_users_with_debts())
    print( user_obj.get_bank_with_oldest_client())
    print(user_obj.get_bank_with_most_unique_outbound_users())
    print(user_obj.get_user_transactions_last_3_months(1))
    print(user_obj.get_accounts_of_under_18())

@db_connection_decorator(Account)
def demo_account_operations(account_obj):
    accounts = [
        (7, 'debit', 123476, 1, 'USD', 1000, 'gold'),
        (8, 'credit', 237567, 2, 'EUR', 5070, 'silver')
    ]

    insert_accounts = account_obj.insert(accounts, as_list=True)
    print(insert_accounts)

    update_result = account_obj.update(
        account_id=1,
        balance=1200,
        currency='USD'
    )





if __name__ == "__main__":
    main()
    demo_insert_banks()
    print(demo_update_bank())
    print(demo_transfer_money())
    print(demo_update_user())
    print(demo_create_users())
    print(demo_call_all_methods())
    print(demo_account_operations())
