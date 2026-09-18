---
name: doc-review
description: >-
  Two-tier language scan for AI writing tells and format standards on a
  document or passage, per engine/doc-style-guide.md. Use when the user runs
  /doc-review, asks to check a document for AI-sounding language, style
  issues, or wants a credibility/tone pass on a compliance artifact.
---

# Doc review

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/doc-review.md` and in specs (`config/`, `engine/`, …).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository's root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/doc-review.md` in full. Apply workspace path resolution to every path that file references.
