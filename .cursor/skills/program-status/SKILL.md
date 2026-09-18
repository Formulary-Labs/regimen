---
name: program-status
description: >-
  Produces a one-page status summary for a single program: health, scope, control
  coverage, risks, decisions, blockers, deadlines, and next pipeline run
  recommendation. Use when the user runs /program-status, asks for program
  status, or a snapshot of one compliance program.
---

# Program status

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/program-status.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/program-status.md` in full. Apply workspace path resolution to every path that file references.
