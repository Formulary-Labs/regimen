---
name: daily-brief
description: >-
  Produces a concise morning briefing across active programs: portfolio health,
  due today and this week, pending decisions, blockers, and recent provenance
  activity. Use when the user runs /daily-brief, asks for a morning brief,
  daily briefing, or start-of-day portfolio orientation.
---

# Daily brief

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/daily-brief.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/daily-brief.md` in full. Apply workspace path resolution to every path that file references.
