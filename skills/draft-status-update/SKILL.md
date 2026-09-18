---
name: draft-status-update
description: >-
  Drafts a stakeholder status communication calibrated by audience (executive,
  technical, auditor, vendor, all-hands), routed through the comms spec; output
  is always a reviewable draft, never sent automatically. Use when the user
  runs /draft-status-update, asks for a status update draft, or stakeholder comms.
---

# Draft status update

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/draft-status-update.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/draft-status-update.md` in full. Apply workspace path resolution to every path that file references.
