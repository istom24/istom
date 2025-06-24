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
            logging.error(f"Error: {e}")
            return f"Error: {e}"
    return wrapper

# def db_connection_decorator(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         with Shape() as db:
#             return func(db, *args, **kwargs)
#     return wrapper

# def db_connection_decorator(func):
#     def wrapper(*args, **kwargs):
#         with Shape() as db:
#             return func(db, *args, **kwargs)
#
#     return wrapper
#
# def with_connection(f):
#     @wraps(f)
#     def wrapped(*args, **kwargs):
#         conn = sqlite3.connect('dec.db')
#         cursor = conn.cursor()
#         f_ret = f(cursor, *args, **kwargs)
#         conn.commit()
#         conn.close()
#         return f_ret
#     return wrapped



