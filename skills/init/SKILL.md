---
name: init
description: >-
  Runs the Session Initialization Spec end-to-end (constitution, directory
  discovery, classify input or session orientation, load-on-demand routing,
  quality gate). Use when the user runs /init, asks for session initialization
  or orientation, session start, “what should I work on,” or routing at open.
---

# Init (session start)

## Workspace paths

**Default:** Workspace root is this repository (e.g. the `prompt` checkout). Use paths exactly as written in `commands/init.md` and in any spec it loads (e.g. `engine/session-init-spec.md`, `config/constitution.md`).

**Nested layout:** If this repo lives inside a larger tree (e.g. a company monorepo), prefix every repo-relative path with the path from the workspace root to this repository’s root. Do not reuse path prefixes from older nested-repo layouts.

## Authority

Read and execute `commands/init.md` in full. It defers to `engine/session-init-spec.md` for procedural detail.

## Related

Canonical procedure: `commands/init.md`.
