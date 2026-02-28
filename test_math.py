"""
Sample test file — tests/test_math.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sysvalidationrunner.decorators import skip


def setup():
    """Optional: runs before each test in this module."""
    pass


def teardown():
    """Optional: runs after each test in this module."""
    pass


def test_addition():
    assert 1 + 1 == 2


def test_subtraction():
    assert 10 - 3 == 7


def test_multiplication():
    assert 6 * 7 == 42


def test_division_by_zero():
    """This test intentionally fails."""
    result = 10 / 2
    assert result == 6, f"Expected 6 but got {result}"  # wrong expected value


def test_string_ops():
    s = "hello world"
    assert s.upper() == "HELLO WORLD"
    assert s.split() == ["hello", "world"]


@skip("not yet implemented")
def test_future_feature():
    assert False  # never runs


def test_slow_but_ok():
    import time
    time.sleep(0.05)
    assert True


def test_with_stdout():
    print("This is captured stdout")
    assert 2 ** 8 == 256
