---
name: due-this-week
description: >-
  Produces a cross-program digest of items due or overdue in the next seven
  days: evidence windows, POA&M dates, urgent decisions, pipeline runs, and
  escalations. Use when the user runs /due-this-week, asks what is due this
  week, or needs a deadline-focused portfolio view.
---

# Due this week

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/due-this-week.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/due-this-week.md` in full. Apply workspace path resolution to every path that file references.
