"""
CLI Entry Point

Usage:
    python -m sysvalidationrunner [directory] [options]

Options:
    --pattern   FILE    File glob pattern       (default: test_*.py)
    --timeout   SECS    Per-test timeout        (default: 10)
    --workers   N       Parallel workers        (default: 1)
    --verbose   -v      Show tracebacks/stdout
    --json      PATH    Write JSON report to PATH
"""
import argparse
import sys
import os

from .discovery import discover
from .executor  import run_all
from .reporter  import report_console, report_json


def main():
    parser = argparse.ArgumentParser(
        prog="sysvalidationrunner",
        description="Minimal test runner — discovers and runs test_* functions"
    )
    parser.add_argument("directory", nargs="?", default=".",
                        help="Root directory to search for tests (default: .)")
    parser.add_argument("--pattern",  default="test_*.py",
                        help="Filename glob pattern (default: test_*.py)")
    parser.add_argument("--timeout",  type=float, default=10.0,
                        help="Per-test timeout in seconds (default: 10)")
    parser.add_argument("--workers",  type=int,   default=1,
                        help="Number of parallel workers (default: 1)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show tracebacks and captured stdout")
    parser.add_argument("--json",     default=None,
                        help="Write JSON report to this file path")

    args = parser.parse_args()
    root = os.path.abspath(args.directory)

    # ── 1. Add root to sys.path so imports inside test files work ──
    if root not in sys.path:
        sys.path.insert(0, root)

    print(f"🔍  Discovering tests in: {root}")
    print(f"    pattern={args.pattern}  timeout={args.timeout}s  workers={args.workers}")

    # ── 2. Discovery ──
    cases = discover(root, pattern=args.pattern)
    if not cases:
        print("\nNo tests found.")
        sys.exit(0)

    print(f"    Found {len(cases)} test(s)\n")

    # ── 3. Execution ──
    results = run_all(cases, timeout=args.timeout, workers=args.workers)

    # ── 4. Reporting ──
    exit_code = report_console(results, verbose=args.verbose)

    if args.json:
        report_json(results, path=args.json)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
