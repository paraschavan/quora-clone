# Make test directory a Python package

from functools import wraps

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f'\nFailed: {func.__name__}')
            raise e
        else:
            print(f'\nPassed: {func.__name__}')

    return wrapper
