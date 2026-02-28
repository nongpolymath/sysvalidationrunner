"""
Execution Engine
  - Runs each TestCase in isolation
  - Captures stdout/stderr
  - Enforces a per-test timeout
  - Supports parallel execution via ThreadPoolExecutor
"""
import io
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stdout, redirect_stderr
from typing import List

from .models import TestCase, TestResult, Status


def run_all(
    cases: List[TestCase],
    timeout: float = 10.0,
    workers: int = 1,
) -> List[TestResult]:
    """
    Execute all test cases. Returns results in completion order.
    workers=1  → serial (easier to debug)
    workers>1  → parallel via threads
    """
    if workers == 1:
        return [_run_one(case, timeout) for case in cases]

    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run_one, case, timeout): case for case in cases}
        for future in as_completed(futures):
            results.append(future.result())
    return results


# ── private ──────────────────────────────────────────────────────────

def _run_one(case: TestCase, timeout: float) -> TestResult:
    """Run a single TestCase and return a TestResult."""

    # ── SKIP ──
    if case.skip_reason is not None:
        return TestResult(case=case, status=Status.SKIP, message=case.skip_reason)

    # ── SETUP (optional: module-level setup()) ──
    setup    = getattr(sys.modules.get(case.module_name), "setup",    None)
    teardown = getattr(sys.modules.get(case.module_name), "teardown", None)

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    start      = time.perf_counter()

    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            if setup:
                setup()
            _call_with_timeout(case.fn, timeout)
            if teardown:
                teardown()

        duration = time.perf_counter() - start
        return TestResult(
            case=case,
            status=Status.PASS,
            duration_s=duration,
            stdout=stdout_buf.getvalue(),
            stderr=stderr_buf.getvalue(),
        )

    except AssertionError as exc:
        duration = time.perf_counter() - start
        return TestResult(
            case=case,
            status=Status.FAIL,
            duration_s=duration,
            message=str(exc),
            traceback=traceback.format_exc(),
            stdout=stdout_buf.getvalue(),
            stderr=stderr_buf.getvalue(),
        )

    except TimeoutError:
        return TestResult(
            case=case,
            status=Status.ERROR,
            duration_s=timeout,
            message=f"Test exceeded timeout of {timeout}s",
        )

    except Exception as exc:
        duration = time.perf_counter() - start
        return TestResult(
            case=case,
            status=Status.ERROR,
            duration_s=duration,
            message=str(exc),
            traceback=traceback.format_exc(),
            stdout=stdout_buf.getvalue(),
            stderr=stderr_buf.getvalue(),
        )


def _call_with_timeout(fn, timeout: float):
    """
    Run fn() with a timeout enforced via a background thread + event.
    Raises TimeoutError if the function doesn't complete in time.
    """
    import threading
    result    = [None]
    exception = [None]
    finished  = threading.Event()

    def target():
        try:
            fn()
        except Exception as exc:
            exception[0] = exc
        finally:
            finished.set()

    t = threading.Thread(target=target, daemon=True)
    t.start()
    completed = finished.wait(timeout=timeout)

    if not completed:
        raise TimeoutError()
    if exception[0] is not None:
        raise exception[0]
