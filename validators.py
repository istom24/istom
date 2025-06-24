import re
from datetime import datetime


def validate_user_full_name(full_name):
    result_split = re.sub(r"[^a-zA-Z\s]", " ", full_name).strip().split()
    if len(result_split) < 2:
        raise Exception("User full name must contain at least name and surname")
    name = result_split[0]
    surname = result_split[1]
    return name, surname

def check_allowed(field_name, value, allowed_values):
    if value not in allowed_values:
        raise Exception(f"Inadmissible value {value} for field {field_name} !")
    return value


def validate_datetime(dt):
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_account_number(account_number):
    account_number = re.sub(r"[#%_?&]", "-", account_number)

    if len(account_number) != 18:
        raise ValueError(f"Invalid account number length: expected 18 characters, got {len(account_number)}.")

    if not account_number.startswith("ID--"):
        raise ValueError("Account number must start with 'ID--'.")

    pattern = r"[a-zA-Z]{1,3}-\d+-"
    if not re.search(pattern, account_number):
        raise ValueError("Account number must contain pattern: 1-3 letters, a dash, digits, and a dash.")

    return account_number

print(validate_user_full_name("John Smith"))
print(validate_user_full_name("Anna-Maria Petrova"))
print(check_allowed("currency", "USD", ["USD", "EUR"]))
print(check_allowed("type", "crypto", ["credit", "debit"]))

