# SysValidationRunner

A minimal, zero-dependency test runner for Python. Discovers and executes `test_*` functions across your project with parallel execution, timeouts, and JSON reporting.

## Features

- **Auto-discovery** — recursively finds all `test_*` functions in `test_*.py` files
- **Parallel execution** — run tests concurrently with a configurable worker pool
- **Per-test timeouts** — enforce time limits using a threading-based mechanism (Windows compatible)
- **Module hooks** — automatically calls `setup()` / `teardown()` if defined in a test module
- **Output capture** — captures stdout/stderr per test; shown in verbose mode
- **Console reporting** — colorized output with pass/fail/error/skip indicators
- **JSON reporting** — structured output for CI/CD integration
- **`@skip` decorator** — mark tests to skip with an optional reason
- **Zero dependencies** — standard library only, Python 3.12+

## Project Structure

```
sysvalidationrunner/
├── __main__.py      # CLI entry point
├── models.py        # Shared data contracts (TestCase, TestResult, Status)
├── discovery.py     # Walks directories and collects test_* functions
├── executor.py      # Runs tests with isolation, timeouts, and parallel support
├── reporter.py      # Console and JSON output
├── decorators.py    # @skip decorator
├── test_math.py     # Example tests
└── test_strings.py  # Example tests
```

## Usage

```bash
python -m sysvalidationrunner [directory] [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `directory` | `.` | Root directory to search for tests |
| `--pattern FILE` | `test_*.py` | Glob pattern for test files |
| `--timeout SECS` | `10` | Per-test timeout in seconds |
| `--workers N` | `1` | Number of parallel workers (1 = serial) |
| `--verbose, -v` | off | Show tracebacks, stdout, and skip reasons |
| `--json PATH` | — | Write a JSON report to the specified file |

### Examples

```bash
# Run all tests in the current directory
python -m sysvalidationrunner .

# Run with 4 parallel workers and a 5-second timeout
python -m sysvalidationrunner . --workers 4 --timeout 5

# Verbose output with a JSON report
python -m sysvalidationrunner . --verbose --json results.json

# Match a custom file pattern
python -m sysvalidationrunner ./tests --pattern "*_test.py"
```

## Writing Tests

Any function whose name starts with `test_` in a file matching the discovery pattern is automatically collected and run.

```python
# test_example.py

def test_addition():
    assert 1 + 1 == 2

def test_string_upper():
    assert "hello".upper() == "HELLO"
```

### Setup and Teardown

Define module-level `setup()` and `teardown()` functions to run before and after each test in that module:

```python
def setup():
    print("runs before each test")

def teardown():
    print("runs after each test")

def test_something():
    assert True
```

### Skipping Tests

```python
from decorators import skip

@skip("not implemented yet")
def test_pending():
    pass
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All tests passed or skipped |
| `1` | One or more failures or errors |

## Architecture

Execution follows a three-stage pipeline:

1. **Discovery** (`discovery.py`) — imports test files dynamically and collects `test_*` functions into `TestCase` objects
2. **Execution** (`executor.py`) — runs each test in isolation, capturing output and enforcing timeouts via daemon threads
3. **Reporting** (`reporter.py`) — formats results for the console and/or a JSON file

Data flows through shared dataclasses defined in `models.py` (`TestCase`, `TestResult`, `Status`).