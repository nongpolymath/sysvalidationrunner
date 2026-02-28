"""
Sample test file — tests/strings/test_strings.py
"""


def test_upper():
    assert "hello".upper() == "HELLO"


def test_strip():
    assert "  trimmed  ".strip() == "trimmed"


def test_join():
    assert ", ".join(["a", "b", "c"]) == "a, b, c"


def test_intentional_error():
    """Raises an unexpected exception (not AssertionError)."""
    raise ValueError("Something went very wrong inside test logic")
