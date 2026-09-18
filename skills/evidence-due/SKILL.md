---
name: evidence-due
description: >-
  Surfaces upcoming and overdue evidence collection windows for a program
  within a configurable day horizon. Use when the user runs /evidence-due,
  asks what evidence is due, or needs the evidence calendar view for a program.
---

# Evidence due

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/evidence-due.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/evidence-due.md` in full. Apply workspace path resolution to every path that file references.
