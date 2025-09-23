import warnings
from functools import wraps

def deprecated(replacement: str = None):
    """
    Decorator to mark functions as deprecated.

    Args:
        replacement (str, optional): Name of the function to use instead.

    Usage:
        @deprecated("new_function")
        def old_function(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = f"Function '{func.__name__}' is deprecated and will be removed in future versions."
            if replacement:
                message += f" Use '{replacement}' instead."
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator