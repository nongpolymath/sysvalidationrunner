"""
Discovery Engine
  1. Walk the directory tree
  2. Filter files matching the pattern (default: test_*.py or *_test.py)
  3. Dynamically import each file as a module
  4. Inspect the module for callables whose name starts with 'test_'
  5. Yield TestCase objects
"""
import fnmatch
import importlib.util
import inspect
import os
import sys
from typing import Iterator, List

from .models import TestCase


SKIP_MARKER = "__test_skip__"   # set by @skip decorator


def discover(root: str, pattern: str = "test_*.py") -> List[TestCase]:
    cases = []
    for filepath in _walk_files(root, pattern):
        module = _import_file(filepath)
        if module is None:
            continue
        for case in _collect_tests(module, filepath):
            cases.append(case)
    return cases


# ── private helpers ──────────────────────────────────────────────────

def _walk_files(root: str, pattern: str) -> Iterator[str]:
    """Yield absolute paths of files matching pattern under root."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs and __pycache__
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "_"))]
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(dirpath, filename)


def _import_file(filepath: str):
    """
    Dynamically import a .py file as a module.
    We derive a unique module name from the path to avoid collisions.
    """
    # Build a dotted name like "tests.subdir.test_math"
    module_name = filepath.replace(os.sep, ".").rstrip(".py").lstrip(".")
    module_name = module_name.replace("..", ".").strip(".")

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
        print(f"[discovery] WARNING: could not load {filepath}")
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # register so relative imports work
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"[discovery] ERROR importing {filepath}: {exc}")
        return None

    return module


def _collect_tests(module, filepath: str) -> Iterator[TestCase]:
    """Yield one TestCase per test_* function found in the module."""
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("test_"):
            continue
        skip_reason = getattr(obj, SKIP_MARKER, None)
        yield TestCase(
            name=name,
            fn=obj,
            module_name=module.__name__,
            file_path=filepath,
            skip_reason=skip_reason,
        )
