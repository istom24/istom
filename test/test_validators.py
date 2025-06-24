from lab4.validators import validate_user_full_name
from lab4.validators import validate_check_allowed
from lab4.validators import validate_datetime
from lab4.validators import validate_account_number


def test_validate_user_full_name():
    input_param = "Marco Polo"
    actual_name, actual_surname = validate_user_full_name(input_param)
    expected_name = "Marco"
    expected_surname = "Polo"
    assert actual_name == expected_name
    assert actual_surname == expected_surname

    input_param = "  Marco    Polo       "
    actual_name, actual_surname = validate_user_full_name(input_param)
    expected_name = "Marco"
    expected_surname = "Polo"
    assert actual_name == expected_name
    assert actual_surname == expected_surname


def test_validate_check_allowed():
    param_name = 'surname'
    value = 'Shevchenko'
    allowed_values = ['Shevchenko', 'Franko', 'Lesya Ukrainka']

    actual = validate_check_allowed(param_name, value, allowed_values)
    expected = 'Shevchenko'

    assert actual == expected


def test_validate_datetime_with_valid_date():
    actual = "2025-06-23 15:30:00"
    expected = validate_datetime(actual)
    assert actual == expected


def test_validate_account_number_valid():
    param = "ID##ab_12345?xyz&7"
    expected = "ID--ab-12345-xyz-7"
    actual = validate_account_number(param)
    assert expected == actual
