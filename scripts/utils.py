#!/usr/bin/env python3
"""
Shared Script Utilities
========================
Canonical helpers used across scripts/*.py validators and generators.
Import from here instead of redefining — resolve_repo_root() alone was
independently duplicated (with drifting logic) in 5+ scripts before this
module existed. See config/tool-requirements.md.

Usage:
    from utils import resolve_repo_root
    repo_root = resolve_repo_root()

This module has no side effects on import and requires no arguments.

Style: PEP 8
Deviations: None
"""

from __future__ import annotations

from pathlib import Path

# Directories that must be present (as siblings, in the same candidate
# directory) for a candidate to be considered the repo root. Requiring a
# majority (not just one) avoids false-positive matches on nested
# directories that happen to contain exactly one of these names.
_ROOT_ANCHORS: frozenset[str] = frozenset({"config", "engine", "functions", "scripts"})
_ROOT_ANCHOR_THRESHOLD = 3


def resolve_repo_root(start: Path | None = None) -> Path:
    """Walk up from a starting path to find the compliance repo root.

    A directory qualifies as the root if at least _ROOT_ANCHOR_THRESHOLD of
    _ROOT_ANCHORS exist as direct children. Checks the caller's parent, the
    caller's own directory, and the grandparent, in that order — covers
    scripts run directly, via symlink, or from a nested subdirectory.

    Falls back to Path.cwd() if no candidate qualifies — callers should
    treat that as "best effort," not a guarantee the cwd is actually root.
    """
    here = (start or Path(__file__).resolve()).parent
    for candidate in (here.parent, here, here.parent.parent):
        if sum(1 for a in _ROOT_ANCHORS if (candidate / a).exists()) >= _ROOT_ANCHOR_THRESHOLD:
            return candidate
    return Path.cwd()
