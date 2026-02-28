"""
Core data contracts passed between pipeline stages.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class Status(Enum):
    PASS  = "PASS"
    FAIL  = "FAIL"
    ERROR = "ERROR"
    SKIP  = "SKIP"


@dataclass
class TestCase:
    """Output of Discovery. Input to Execution."""
    name:        str            # "test_addition"
    fn:          Callable       # the actual function object
    module_name: str            # "tests.test_math"
    file_path:   str            # "/project/tests/test_math.py"
    skip_reason: Optional[str] = None


@dataclass
class TestResult:
    """Output of Execution. Input to Reporter."""
    case:       TestCase
    status:     Status
    duration_s: float           = 0.0
    message:    str             = ""
    traceback:  Optional[str]   = None
    stdout:     str             = ""
    stderr:     str             = ""
