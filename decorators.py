"""
Decorators available to test authors.
"""
from .discovery import SKIP_MARKER


def skip(reason: str = ""):
    """Mark a test function to be skipped.

    Usage:
        @skip("not implemented yet")
        def test_something():
            ...
    """
    def decorator(fn):
        setattr(fn, SKIP_MARKER, reason or "no reason given")
        return fn
    return decorator
