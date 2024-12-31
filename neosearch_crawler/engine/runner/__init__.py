from functools import wraps

# custom modules
from .base import BaseRunner


def step(index):
    """Decorator to mark a method as a DAG step."""
    def decorator(func):
        setattr(func, "_step_index", index)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


__all__ = [
    'BaseRunner',
    'step'
]