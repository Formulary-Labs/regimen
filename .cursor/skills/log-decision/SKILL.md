---
name: log-decision
description: >-
  Captures a decision made outside a pipeline run: appends to the program
  decision log in memory and logs provenance. Use when the user runs
  /log-decision, asks to record a decision, or log something to program memory.
---

# Log decision

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/log-decision.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/log-decision.md` in full. Apply workspace path resolution to every path that file references.
