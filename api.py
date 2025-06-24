import requests
from .constants import API_URL, API_KEY
from .decorators import error_decorator


@error_decorator
def get_exchange_course(from_currency: str, to_currency: str):
    response = requests.get(
        API_URL,
        params={
            "apikey": API_KEY,
            "base_currency": from_currency.upper(),
            "currencies": to_currency.upper()
        },
    timeout = 3
    )
    data = response.json()
    return data.get("data", {}).get(to_currency.upper())
