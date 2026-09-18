---
name: meeting-debrief
description: >-
  Ingests a meeting transcript, extracts compliance-relevant decisions and
  actions, writes memory immediately, and stages run JSON changes for
  confirmation. Use when the user runs /meeting-debrief, asks to debrief a
  meeting, or process meeting notes into program state.
---

# Meeting debrief

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/meeting-debrief.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/meeting-debrief.md` in full. Apply workspace path resolution to every path that file references.
