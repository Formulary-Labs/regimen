---
name: control-assessment
description: >-
  Fills auditor templates, STIG/CIS/IEC 62443/functional test plans from
  framework and product documentation in validated, resumable batches; produces
  filled template, markdown artifact, and gap report. Use when the user runs
  /control-assessment, asks to fill a control template, STIG, or benchmark from
  product docs.
---

# Control assessment

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/control-assessment.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/control-assessment.md` in full. Apply workspace path resolution to every path that file references.
