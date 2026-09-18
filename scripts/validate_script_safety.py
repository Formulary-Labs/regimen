#!/usr/bin/env python3
"""
Validate Script Safety
=======================
Static check that every script in scripts/ follows the Execution Safety
rules in config/tool-requirements.md:
  1. No file-mutating call at module top level (must live inside a function)
  2. A `def main()` entry point requires an `if __name__ == "__main__":` guard
  3. Any script with file-mutating calls requires an argparse-based
     confirm/yes gate so bare invocation and --help are safe no-ops

This is a heuristic static check, not a type-checker — it looks for common
write patterns (open(..., "w"/"a"/"x"), Path.write_text/write_bytes,
workbook.save(), os.remove/unlink, shutil.rmtree/move) and common confirm-gate
patterns (--confirm/--yes flags checked before calling into mutating logic).
It will not catch every possible mutation, and can produce false positives
for unusual patterns — treat findings as a starting point for review, not
an infallible verdict.

Triggered by the 2026-07-29 incident (see OPTIMIZATION-ROADMAP.md Phase 4 —
Tool Creation Guardrails): 10 scripts ran file-mutating side effects on bare
invocation or --help because they had no confirm gate, and two had no
if __name__ == "__main__" guard at all.

Usage:
    python scripts/validate_script_safety.py
    python scripts/validate_script_safety.py --dir scripts
    python scripts/validate_script_safety.py --verbose

Style: PEP 8
Deviations: None
"""

import argparse
import ast
import sys
from pathlib import Path

WRITE_ATTR_NAMES = {"write_text", "write_bytes", "save", "unlink", "rmtree", "move", "remove"}
WRITE_MODULE_CALLS = {
    ("os", "remove"),
    ("os", "unlink"),
    ("os", "rename"),
    ("shutil", "rmtree"),
    ("shutil", "move"),
}
WRITE_FILE_MODES = {"w", "a", "x", "w+", "a+", "wb", "ab", "xb", "wb+", "ab+"}

# Scripts that are legitimately read-only (reports, audits, network checks)
# and are therefore exempt from the confirm-gate requirement, but still need
# the __main__ guard if they define main(). Maintain manually — do not infer.
READ_ONLY_EXEMPT = {
    "test_guide_urls.py",
    "validate_frontmatter.py",
    "validate_schema_drift.py",
    "spec_coverage.py",
    "integrity_check.py",
    "validate_script_safety.py",
    "provenance_log.py",  # append-only via a dedicated, reviewed writer path
}

# Renderer/generator tools that only ever write to their own dedicated,
# derived-output path (ui/*.html, a report file, a regenerated dashboard) —
# never to hand-authored source content. Re-running them regenerates a
# derived artifact deterministically from current source data, the same
# risk class as a build script writing to dist/. This is a different, lower
# risk category than the 2026-07-29 incident (one-shot scripts editing
# source-of-truth compliance documents in place) and is exempt from the
# --confirm gate for that reason. Maintain manually — do not infer; if a
# script's write target ever becomes hand-authored/source content, remove
# it from this list and add a --confirm gate.
DESIGNATED_OUTPUT_EXEMPT = {
    "build_pages.py",
    "calendar_exporter.py",
    "dashboard.py",
    "fleet_dashboard.py",
    "iso42001_ingest_standard_pdf.py",  # also gated by a not-committed licensed-PDF default path
    "kanban_renderer.py",
    "portfolio_renderer.py",
    "predictive_health.py",
    "validate_aims_xlsx.py",  # only writes when --output is explicitly passed
}


class ScriptFindings:
    def __init__(self, path: Path):
        self.path = path
        self.has_main_func = False
        self.has_main_guard = False
        self.top_level_writes: list[int] = []
        self.function_writes: list[int] = []
        self.imports_argparse = False
        self.has_required_arg = False

    @property
    def is_mutating(self) -> bool:
        return bool(self.top_level_writes or self.function_writes)

    @property
    def failures(self) -> list[str]:
        out = []
        if self.top_level_writes:
            lines = ", ".join(str(n) for n in self.top_level_writes)
            out.append(f"top-level write call(s) outside any function at line(s) {lines}")
        if self.has_main_func and not self.has_main_guard:
            out.append('defines main() but has no `if __name__ == "__main__":` guard')
        exempt = self.path.name in READ_ONLY_EXEMPT or self.path.name in DESIGNATED_OUTPUT_EXEMPT
        if self.is_mutating and not exempt and not self._is_gated():
            out.append(
                "mutates files but has no --confirm/--yes gate and no required argument "
                "before execution — bare invocation would write files"
            )
        return out

    def _is_gated(self) -> bool:
        """A mutating script is safe if it has an explicit confirm flag, OR a
        required argument that makes accidental bare invocation fail before
        any write occurs (argparse errors out before main() runs)."""
        return self._has_confirm_gate() or self.has_required_arg

    def _has_confirm_gate(self) -> bool:
        if not self.imports_argparse:
            return False
        text = self.path.read_text(encoding="utf-8", errors="replace")
        flag_defined = ("--confirm" in text) or ("--yes" in text)
        flag_checked = ("args.confirm" in text) or ("args.yes" in text)
        return flag_defined and flag_checked


def _is_write_call(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr in WRITE_ATTR_NAMES:
        return True
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        if (func.value.id, func.attr) in WRITE_MODULE_CALLS:
            return True
    if isinstance(func, ast.Name) and func.id == "open":
        mode = None
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            mode = node.args[1].value
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                mode = kw.value.value
        if isinstance(mode, str) and mode in WRITE_FILE_MODES:
            return True
    return False


def _is_required_add_argument(node: ast.Call) -> bool:
    """True for parser.add_argument(...) calls that are positional (no leading
    '-') or explicitly required=True — either makes bare invocation error out
    via argparse before any code (including a write) runs."""
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr == "add_argument"):
        return False
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and not arg.value.startswith("-"):
            return True
    for kw in node.keywords:
        if kw.arg == "required" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
            return True
    return False


def _is_main_guard(node: ast.If) -> bool:
    test = node.test
    if not isinstance(test, ast.Compare):
        return False
    values = [test.left, *test.comparators]
    names = {v.id for v in values if isinstance(v, ast.Name)}
    consts = {v.value for v in values if isinstance(v, ast.Constant)}
    return "__name__" in names and "__main__" in consts


def analyze(path: Path) -> ScriptFindings:
    findings = ScriptFindings(path)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError as exc:
        findings.top_level_writes = [-1]
        findings._syntax_error = str(exc)  # noqa: SLF001 - internal debug field
        return findings

    def walk(node: ast.AST, in_function: bool) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Import):
                if any(alias.name == "argparse" for alias in child.names):
                    findings.imports_argparse = True
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name == "main":
                    findings.has_main_func = True
                walk(child, in_function=True)
                continue
            elif isinstance(child, ast.Call) and _is_write_call(child):
                if in_function:
                    findings.function_writes.append(child.lineno)
                else:
                    findings.top_level_writes.append(child.lineno)
            elif isinstance(child, ast.Call) and _is_required_add_argument(child):
                findings.has_required_arg = True
            elif isinstance(child, ast.If) and not in_function and _is_main_guard(child):
                findings.has_main_guard = True
            walk(child, in_function)

    walk(tree, in_function=False)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--dir", default="scripts", help="Directory to scan (default: scripts)")
    parser.add_argument("--verbose", action="store_true", help="Print PASS lines too, not just failures")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    scan_dir = (repo_root / args.dir).resolve()
    if not scan_dir.is_dir():
        print(f"ERROR: directory not found: {scan_dir}", file=sys.stderr)
        return 2

    py_files = sorted(scan_dir.glob("*.py"))
    if not py_files:
        print(f"No Python scripts found under {scan_dir}")
        return 0

    print(f"\nScript Safety Validation — {scan_dir}")
    print("─" * 60)

    total_failures = 0
    for path in py_files:
        findings = analyze(path)
        failures = findings.failures
        if failures:
            total_failures += 1
            print(f"  {path.name:45s} ✗ FAIL")
            for f in failures:
                print(f"      - {f}")
        elif args.verbose:
            print(f"  {path.name:45s} ✓ PASS")

    print("─" * 60)
    if total_failures:
        print(f"{total_failures} of {len(py_files)} scripts failed execution-safety checks.")
        print('See config/tool-requirements.md "Execution Safety" section for the fix pattern.')
        return 1

    print(f"All {len(py_files)} scripts passed execution-safety checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
