---
name: portfolio-qbr
description: >-
  Synthesizes a quarterly business review across all active programs: cross-program
  patterns, health trajectory, shared vendor exposure, ownership signals, and
  forward-looking priorities. Produces a dated narrative artifact and updates
  data/portfolio/qbr/latest.md. Use when the user runs /portfolio-qbr, asks for a
  quarterly review, QBR, portfolio retrospective, or cross-program synthesis report.
---

# Portfolio QBR

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/portfolio-qbr.md` and in specs (`config/`, `engine/`, `data/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository's root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/portfolio-qbr.md` in full. Apply workspace path resolution to every path that file references.
