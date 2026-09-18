---
name: auditor-view
description: >-
  Generates a read-only auditor compliance posture dashboard as static HTML
  (provenance, coverage, risks, evidence calendar). Use when the user runs
  /auditor-view, asks for an auditor dashboard, or auditor-facing posture view.
---

# Auditor view

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/auditor-view.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/auditor-view.md` in full. Apply workspace path resolution to every path that file references.
