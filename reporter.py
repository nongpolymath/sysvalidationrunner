"""
Reporter
  Consumes List[TestResult] and formats human / machine output.
"""
import json
from typing import List

from .models import TestResult, Status


# ANSI colours (fall back gracefully on Windows)
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def report_console(results: List[TestResult], verbose: bool = False) -> int:
    """
    Print results to stdout.
    Returns exit code: 0 if all passed/skipped, 1 if any failures.
    """
    print()
    for r in results:
        _print_result(r, verbose)

    # ── Summary ──
    total   = len(results)
    passed  = sum(1 for r in results if r.status == Status.PASS)
    failed  = sum(1 for r in results if r.status == Status.FAIL)
    errors  = sum(1 for r in results if r.status == Status.ERROR)
    skipped = sum(1 for r in results if r.status == Status.SKIP)

    print("\n" + "─" * 60)
    print(
        f"{BOLD}Results:{RESET} "
        f"{GREEN}{passed} passed{RESET}  "
        f"{RED}{failed} failed{RESET}  "
        f"{YELLOW}{errors} errors{RESET}  "
        f"{CYAN}{skipped} skipped{RESET}  "
        f"({total} total)"
    )

    total_time = sum(r.duration_s for r in results)
    print(f"Time: {total_time:.3f}s")
    print("─" * 60)

    return 0 if (failed + errors) == 0 else 1


def report_json(results: List[TestResult], path: str = "results.json"):
    """Write results as JSON (useful for CI systems)."""
    data = []
    for r in results:
        data.append({
            "name":       r.case.name,
            "file":       r.case.file_path,
            "module":     r.case.module_name,
            "status":     r.status.value,
            "duration_s": r.duration_s,
            "message":    r.message,
            "traceback":  r.traceback,
        })
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nJSON report written to {path}")


# ── private ──────────────────────────────────────────────────────────

def _print_result(r: TestResult, verbose: bool):
    icon = {
        Status.PASS:  f"{GREEN}✓{RESET}",
        Status.FAIL:  f"{RED}✗{RESET}",
        Status.ERROR: f"{YELLOW}E{RESET}",
        Status.SKIP:  f"{CYAN}s{RESET}",
    }[r.status]

    label = f"{r.case.module_name}::{r.case.name}"
    time  = f"({r.duration_s*1000:.1f}ms)"

    print(f"  {icon}  {label:<55} {time}")

    if r.status in (Status.FAIL, Status.ERROR):
        if r.message:
            print(f"       {RED}{r.message}{RESET}")
        if verbose and r.traceback:
            for line in r.traceback.strip().splitlines():
                print(f"         {line}")

    if verbose and r.status == Status.SKIP:
        print(f"       {CYAN}Skipped: {r.message}{RESET}")

    if verbose and r.stdout:
        print(f"       stdout: {r.stdout.strip()}")
