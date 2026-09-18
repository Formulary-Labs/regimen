---
name: validate
description: >-
  Runs the system's structural validators (integrity_check, frontmatter,
  schema drift, spec coverage, script execution-safety, and program-specific
  validators) in one pass and summarizes pass/fail. Use when the user runs
  /validate, asks to check system health, validate specs, or check for
  schema/frontmatter/routing/script-safety drift.
---

# Validate

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/validate.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository's root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/validate.md` in full. Apply workspace path resolution to every path that file references.
