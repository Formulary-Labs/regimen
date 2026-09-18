---
name: provenance-query
description: >-
  Queries the provenance log for what the system has produced for a program,
  with optional output-type and date filters, and surfaces reusable artifacts.
  Use when the user runs /provenance-query, asks what was generated for a
  program, or wants deliverable history from logs/provenance.jsonl.
---

# Provenance query

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/provenance-query.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/provenance-query.md` in full. Apply workspace path resolution to every path that file references.
