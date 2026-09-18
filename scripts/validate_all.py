#!/usr/bin/env python3
"""
Unified Validation Runner
==========================
Runs all system-wide structural validators in one pass and prints the
summary table defined in commands/validate.md. This is a repo-health
check, not a compliance-content check — it validates that the
spec/schema/renderer system itself is internally consistent, not that any
program's compliance posture is correct.

Read-only: this script only invokes other read-only validators as
subprocesses and prints their results. It writes nothing.

Usage:
    python scripts/validate_all.py
    python scripts/validate_all.py --program iso42001
    python scripts/validate_all.py --quiet   # summary table only, no raw output on failure

Style: PEP 8
Deviations: None
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

from utils import resolve_repo_root

# (script relative path, display label)
SYSTEM_VALIDATORS: list[tuple[str, str]] = [
    ("scripts/integrity_check.py", "integrity_check.py"),
    ("scripts/validate_frontmatter.py", "validate_frontmatter.py"),
    ("scripts/validate_schema_drift.py", "validate_schema_drift.py"),
    ("scripts/spec_coverage.py", "spec_coverage.py"),
    ("scripts/validate_script_safety.py", "validate_script_safety.py"),
    ("scripts/eval_routing.py", "eval_routing.py"),
]

# program slug -> (script relative path, display label, extra CLI args)
PROGRAM_VALIDATORS: dict[str, tuple[str, str, list[str]]] = {
    "iso42001": ("scripts/validate_aims_xlsx.py", "validate_aims_xlsx.py", ["--all"]),
    "62443": ("scripts/test_guide_urls.py", "test_guide_urls.py", []),
}


def run_validator(repo_root: Path, rel_path: str, extra_args: list[str] | None = None) -> tuple[int, str]:
    """Run one validator script and return (exit_code, combined_output)."""
    script_path = repo_root / rel_path
    if not script_path.exists():
        return 1, f"Validator not found: {rel_path}"
    result = subprocess.run(
        [sys.executable, str(script_path), *(extra_args or [])],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    output = result.stdout
    if result.stderr:
        output += ("\n" if output else "") + result.stderr
    return result.returncode, output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all system-wide validators and print a summary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--program",
        help="Program slug — additionally run that program's validator if one exists.",
    )
    parser.add_argument(
        "--repo",
        help="Repo root path. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only the summary table — suppress raw output for failing validators.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve() if args.repo else resolve_repo_root()

    validators: list[tuple[str, str, list[str]]] = [
        (rel_path, label, []) for rel_path, label in SYSTEM_VALIDATORS
    ]
    if args.program:
        program_validator = PROGRAM_VALIDATORS.get(args.program)
        if program_validator:
            validators.append(program_validator)
        else:
            print(
                f"NOTE: no dedicated validator registered for program "
                f"'{args.program}' — running system validators only.",
                file=sys.stderr,
            )

    print(f"VALIDATION RUN — {date.today().isoformat()}\n")

    results: list[tuple[str, int, str]] = []
    for rel_path, label, extra_args in validators:
        code, output = run_validator(repo_root, rel_path, extra_args)
        results.append((label, code, output))

    label_width = max(len(label) for label, _, _ in results) + 2
    for label, code, _ in results:
        status = "PASS" if code == 0 else "FAIL"
        print(f"{label:<{label_width}} {status}")

    overall_pass = all(code == 0 for _, code, _ in results)
    print(f"\nOVERALL: {'PASS' if overall_pass else 'FAIL'}")

    if not overall_pass and not args.quiet:
        print("\n" + "─" * 60)
        for label, code, output in results:
            if code != 0:
                print(f"\n--- {label} output ---")
                print(output.strip())

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
