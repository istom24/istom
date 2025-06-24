from functools import wraps
import logging


def db_connection_decorator(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with cls() as db:
                return func(db, *args, **kwargs)

        return wrapper

    return decorator


def error_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Error: %s", e)
            return f"Error: {e}"

    return wrapper
