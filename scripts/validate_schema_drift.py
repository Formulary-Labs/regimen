#!/usr/bin/env python3
"""
Schema Drift Detector
=====================
Validates that the renderer scripts only access JSON keys that are declared
in the canonical JSON schemas. Catches drift between what the pipeline
produces (the schema) and what the renderers consume (the code).

Checks each renderer against the schema it should conform to:
  - scripts/dashboard.py           → config/schemas/run-output.schema.json
  - scripts/auditor_view_renderer.py → config/schemas/run-output.schema.json
  - scripts/portfolio_renderer.py  → config/schemas/portfolio-state.schema.json

Reports two categories:
  ERROR   — renderer reads a key not declared anywhere in the schema
  WARNING — schema declares a property that no renderer reads (dead property)

Only ERRORs cause a non-zero exit. WARNINGs are informational.

Usage:
    python scripts/validate_schema_drift.py
    python scripts/validate_schema_drift.py --repo /path/to/compliance
    python scripts/validate_schema_drift.py --renderers scripts/dashboard.py

Style: PEP 8
Deviations: None
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from utils import resolve_repo_root


# ---------------------------------------------------------------------------
# Renderer → schema mapping
# ---------------------------------------------------------------------------

RENDERER_SCHEMA_MAP: list[tuple[str, str]] = [
    ("scripts/dashboard.py",              "config/schemas/run-output.schema.json"),
    ("scripts/auditor_view_renderer.py",  "config/schemas/run-output.schema.json"),
    ("scripts/portfolio_renderer.py",     "config/schemas/portfolio-state.schema.json"),
]

# Keys that are injected by the loaders themselves (not from JSON) or are
# Python built-ins — exclude from undeclared-key reporting.
LOADER_INJECTED_KEYS: frozenset[str] = frozenset({
    "_source",
    "_program_slug",
    "_program",
})

# Keys that a renderer genuinely reads, but from a data source OTHER than the
# schema it's mapped to in RENDERER_SCHEMA_MAP — e.g. a kanban.yaml board
# dict, or a *different* run JSON file loaded ad hoc inside a helper
# function. This whole-file regex scan cannot track which variable a .get()
# call is applied to, so it cannot distinguish "reads from the mapped
# run/portfolio JSON" from "reads from some other dict with the same key
# name." Maintain manually with a comment naming the real source — do not
# add an entry here just to silence a finding without checking where the
# key is actually read from.
RENDERER_EXTRA_EXCLUSIONS: dict[str, frozenset[str]] = {
    # scripts/dashboard.py's render_kanban_summary()/`_kanban_summary_rows()
    # read these exclusively from data/[program]/kanban.yaml board dicts
    # (loaded via load_kanban_boards()), never from the run JSON that this
    # renderer is otherwise mapped to. Kanban boards have their own format
    # (functions/kanban-spec.md) — not run-output.schema.json.
    "scripts/dashboard.py": frozenset({
        "cards", "column", "blocked", "overdue", "total_active",
        "jira_project_key", "in_progress", "id", "title",
    }),
    # scripts/portfolio_renderer.py's _lookup_program_name() reads this from
    # runs/[slug]/latest.json directly (a fallback path, not the aggregated
    # portfolio.json this renderer is mapped to). run_manifest IS declared
    # in run-output.schema.json — just not in portfolio-state.schema.json,
    # which is correct, since it isn't a portfolio-state field.
    "scripts/portfolio_renderer.py": frozenset({"run_manifest"}),
}

# Generic keys that appear in utility calls but do not represent schema fields.
# Also includes renderer-computed display/UI values that are built at render
# time from schema data and are never read directly from a JSON document.
GENERIC_EXCLUSIONS: frozenset[str] = frozenset({
    # Python / file-open kwargs
    "default",
    "encoding",
    "errors",
    "mode",
    # JSON Schema meta-keywords picked up as string literals
    "type",
    "format",
    "items",
    "properties",
    "required",
    # Renderer-computed display/UI values — not JSON data fields
    "bg",
    "color",
    "icon",
    "label",
    "text",
    # Dict key used as a status bucket label in display mappings, not a JSON key
    "Unknown",
})


# ---------------------------------------------------------------------------
# Schema flattening
# ---------------------------------------------------------------------------

def collect_schema_keys(node: Any, result: set[str] | None = None) -> set[str]:
    """Recursively collect all property names declared in a JSON Schema node.

    Walks ``properties``, ``$defs``, ``items``, ``allOf``, ``anyOf``,
    ``oneOf``, and ``if``/``then``/``else`` branches.
    """
    if result is None:
        result = set()

    if not isinstance(node, dict):
        return result

    if "properties" in node and isinstance(node["properties"], dict):
        for key, child in node["properties"].items():
            result.add(key)
            collect_schema_keys(child, result)

    for container_key in ("$defs", "definitions"):
        if container_key in node and isinstance(node[container_key], dict):
            for child in node[container_key].values():
                collect_schema_keys(child, result)

    for array_key in ("allOf", "anyOf", "oneOf"):
        if array_key in node and isinstance(node[array_key], list):
            for child in node[array_key]:
                collect_schema_keys(child, result)

    for branch in ("if", "then", "else", "items", "contains"):
        if branch in node and isinstance(node[branch], dict):
            collect_schema_keys(node[branch], result)

    return result


def load_schema(schema_path: Path) -> tuple[set[str], str | None]:
    """Load a JSON schema and return (set_of_property_names, error_or_None)."""
    if not schema_path.exists():
        return set(), f"Schema file not found: {schema_path}"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return set(), f"Cannot load {schema_path}: {exc}"
    return collect_schema_keys(data), None


# ---------------------------------------------------------------------------
# Renderer key extraction
# ---------------------------------------------------------------------------

# Patterns that indicate a dict key access in renderer code:
#   safe_get(obj, "key1", "key2")  →  captures each quoted arg after position 0
#   obj.get("key")
#   obj.get("key", default)
#   obj["key"]
#   data.get("key")

_SAFE_GET_ARGS = re.compile(
    r'safe_get\s*\([^)]*?(?:"([^"]+)"|\'([^\']+)\')',
)
_DOT_GET = re.compile(
    r'\.get\s*\(\s*(?:"([^"]+)"|\'([^\']+)\')',
)
_BRACKET = re.compile(
    r'\[\s*(?:"([^"]+)"|\'([^\']+)\')\s*\]',
)

# Capture ALL quoted string args inside safe_get(...) — the first positional
# arg is the dict object, subsequent strings are key names.
_SAFE_GET_FULL = re.compile(
    r'safe_get\s*\(([^)]+)\)',
)
_QUOTED_STRING = re.compile(r'(?:"([^"]+)"|\'([^\']+)\')')


def extract_key_accesses(source: str) -> set[str]:
    """Extract string literal dict key accesses from Python source code."""
    keys: set[str] = set()

    # safe_get(obj, "k1", "k2", ...) — skip the first token (the dict arg)
    for full_match in _SAFE_GET_FULL.finditer(source):
        args_str = full_match.group(1)
        string_matches = list(_QUOTED_STRING.finditer(args_str))
        # First token might be a variable, skip it; collect remaining strings
        for m in string_matches:
            key = m.group(1) or m.group(2)
            if key:
                keys.add(key)

    # .get("key") calls
    for m in _DOT_GET.finditer(source):
        key = m.group(1) or m.group(2)
        if key:
            keys.add(key)

    # ["key"] bracket access
    for m in _BRACKET.finditer(source):
        key = m.group(1) or m.group(2)
        if key:
            keys.add(key)

    return keys


def load_renderer_keys(renderer_path: Path, renderer_rel: str = "") -> tuple[set[str], str | None]:
    """Load a renderer script and return (set_of_key_names, error_or_None)."""
    if not renderer_path.exists():
        return set(), f"Renderer not found: {renderer_path}"
    try:
        source = renderer_path.read_text(encoding="utf-8")
    except OSError as exc:
        return set(), f"Cannot read {renderer_path}: {exc}"

    raw_keys = extract_key_accesses(source)
    extra_exclusions = RENDERER_EXTRA_EXCLUSIONS.get(renderer_rel, frozenset())
    # Remove loader-injected and generic exclusions; keep only identifiers
    # that look like schema field names (no spaces, reasonable length)
    filtered = {
        k for k in raw_keys
        if k not in LOADER_INJECTED_KEYS
        and k not in GENERIC_EXCLUSIONS
        and k not in extra_exclusions
        and " " not in k
        and len(k) <= 64
    }
    return filtered, None


# ---------------------------------------------------------------------------
# Resolve helpers
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect drift between renderer key accesses and JSON schemas.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo",
        help="Repo root path. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--renderers",
        nargs="+",
        metavar="PATH",
        help="Check only these renderer paths (relative to repo root). "
             "Checks all mapped renderers if omitted.",
    )
    parser.add_argument(
        "--warn-dead",
        action="store_true",
        default=True,
        help="Report schema properties not read by any renderer (default: on).",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Report undeclared keys as warnings rather than errors (exit 0). "
             "Use in CI until baseline drift is resolved.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve() if args.repo else resolve_repo_root()

    # Determine which renderer→schema pairs to check
    if args.renderers:
        # Map user-supplied renderer paths to their schema using the table
        schema_map = {r: s for r, s in RENDERER_SCHEMA_MAP}
        pairs = []
        for r in args.renderers:
            rel = r.lstrip("/")
            if rel not in schema_map:
                print(
                    f"WARNING: {rel} not in renderer→schema map; skipping.",
                    file=sys.stderr,
                )
                continue
            pairs.append((rel, schema_map[rel]))
    else:
        pairs = RENDERER_SCHEMA_MAP

    # Load schemas (deduplicated)
    schema_cache: dict[str, set[str]] = {}
    schema_errors: dict[str, str] = {}
    for _, schema_rel in pairs:
        if schema_rel in schema_cache:
            continue
        keys, err = load_schema(repo_root / schema_rel)
        if err:
            schema_errors[schema_rel] = err
        else:
            schema_cache[schema_rel] = keys

    if schema_errors:
        for path, err in schema_errors.items():
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    all_errors: list[tuple[str, list[str]]] = []
    all_warnings: list[tuple[str, list[str]]] = []

    # Track which schema keys are read by any renderer (for dead-property check)
    schema_usage: dict[str, set[str]] = {s: set() for s in schema_cache}

    for renderer_rel, schema_rel in pairs:
        renderer_path = repo_root / renderer_rel
        renderer_keys, err = load_renderer_keys(renderer_path, renderer_rel)
        if err:
            all_errors.append((renderer_rel, [err]))
            continue

        schema_keys = schema_cache[schema_rel]
        schema_usage[schema_rel].update(renderer_keys & schema_keys)

        undeclared = sorted(renderer_keys - schema_keys)
        if undeclared:
            all_errors.append((renderer_rel, [
                f'reads undeclared key "{k}" (not in {schema_rel})'
                for k in undeclared
            ]))

    # Dead schema properties: declared but never read by any mapped renderer
    for schema_rel, used_keys in schema_usage.items():
        schema_keys = schema_cache[schema_rel]
        dead = sorted(schema_keys - used_keys)
        if dead and args.warn_dead:
            all_warnings.append((schema_rel, [
                f'property "{k}" declared but not read by any renderer'
                for k in dead
            ]))

    # Report
    print(f"\nSchema Drift — {repo_root.name}")
    print(f"{'─' * 50}")
    print(f"  Schemas checked:   {len(schema_cache)}")
    print(f"  Renderers checked: {len(pairs)}")

    if not all_errors and not all_warnings:
        print("\n  No drift detected.")
        print("\nAll renderers conform to their schemas.")
        return 0

    if all_errors:
        print(f"\n  ERRORS ({sum(len(e) for _, e in all_errors)}):")
        for source, findings in all_errors:
            for finding in findings:
                print(f"    ✗ [{source}] {finding}")

    if all_warnings:
        print(f"\n  WARNINGS ({sum(len(w) for _, w in all_warnings)}):")
        for source, findings in all_warnings:
            for finding in findings:
                print(f"    ⚠ [{source}] {finding}")

    print()
    if all_errors:
        if args.warn_only:
            print("Schema drift detected (--warn-only: not failing CI).")
            print("Run without --warn-only to enforce. Fix drift to clear this report.")
            return 0
        print("Schema drift check FAILED — undeclared key accesses detected.")
        return 1

    print("Schema drift check passed with warnings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
