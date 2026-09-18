---
name: post-audit
description: >-
  Processes audit closure into structured lessons learned, corrective action
  plans, program improvement items, and a feed-forward artifact for the next
  program cycle, per functions/post-audit-spec.md. Use when the user runs
  /post-audit, an audit just closed, or asks for lessons learned / corrective
  actions / a post-audit retrospective for a program.
---

# Post audit

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/post-audit.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository's root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/post-audit.md` in full. Apply workspace path resolution to every path that file references.
