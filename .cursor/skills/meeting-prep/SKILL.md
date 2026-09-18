---
name: meeting-prep
description: >-
  Prepares a focused 1:1 or team meeting briefing filtered by owner and program,
  with open items, progress, evidence windows, blockers, and suggested talking
  points. Use when the user runs /meeting-prep, asks for meeting prep, or a
  briefing before a sync scoped to a person and program.
---

# Meeting prep

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/meeting-prep.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/meeting-prep.md` in full. Apply workspace path resolution to every path that file references.
