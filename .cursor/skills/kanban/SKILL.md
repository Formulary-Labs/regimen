---
description: >
  View, initialize, and update per-program kanban boards backed by
  data/[program]/kanban.yaml. Surfaces blocked and overdue cards across
  all programs, supports card add/update/move operations, generates Jira
  import files, and routes to the Jira MCP when available.
  Use when the user runs /kanban, asks about task status or blocked work,
  wants to create Jira tickets, update a card, initialize a board, or get
  a cross-program work-in-progress view.
---

# Kanban Skill

## When to invoke

- User runs `/kanban`, `/kanban [program]`, or any kanban sub-command
- User asks what tasks are blocked, overdue, or in progress
- User asks to create, move, or update a task/card/ticket
- User asks to generate Jira tickets or export to Jira
- User asks for a project or task board view
- User asks to initialize a new board for a program

## How to execute

### Step 1 — Load this skill's spec

Read `functions/kanban-spec.md` in full before taking any action. That spec defines all four operations (init, update, add, export) and the Jira MCP detection rule. Do not improvise kanban operations.

### Step 2 — Check Jira MCP availability

At the start of any write operation, check whether `plugin-atlassian-atlassian` MCP is available in session and whether `data/[program]/kanban.yaml` has a non-null `jira_project_key`. If both are true, route write operations through the Jira MCP instead of writing YAML directly, then update `jira_key` in YAML after Jira confirms.

### Step 3 — Detect operation

| User intent | Operation |
|-------------|-----------|
| No program or "all blocked" | Cross-program status summary |
| "show board" / "status" | Operation: status — read and surface board state |
| "init" / "set up board" | Operation: init — scaffold from run JSON |
| "add card" / "create ticket" / "new task" | Operation: add |
| "move PM-NNN" / "update PM-NNN" / "close PM-NNN" | Operation: update |
| "export to Jira" / "generate Jira tickets" | Operation: export |
| "sprint" / "close sprint" / "new sprint" | Sprint management |

### Step 4 — Execute per spec

Follow `functions/kanban-spec.md` for the detected operation exactly. Key constraints:
- Always show current state before proposing a change
- Require confirmation before any write
- Flag one-way door moves (done/canceled on POA&M-linked cards) explicitly
- Never delete a card — move to `canceled`
- Append-only on `progress_notes` — never edit existing entries

### Step 5 — Render board if useful

After a board init or major update, offer to render the HTML board:
```
python scripts/kanban_renderer.py --program [program] --open
```

### Step 6 — Log provenance

After every successful write, log to `logs/provenance.jsonl` via `scripts/provenance_log.py` with `output_type: kanban_update` or `jira_export` as appropriate.

## File locations

| File | Purpose |
|------|---------|
| `data/[program]/kanban.yaml` | Board — source of truth |
| `config/schemas/kanban.schema.json` | Schema |
| `functions/kanban-spec.md` | Full operation spec (read before acting) |
| `agents/project-manager.md` | Agent definition |
| `scripts/kanban_renderer.py` | HTML board renderer |
| `drafts/[program]-jira-import-[date].csv` | Jira bulk export |
| `drafts/[program]-jira-import-[date].json` | Jira REST export |

## Quality gate

All outputs pass through `engine/quality-gate-spec.md` before being presented. One-way door actions (done/canceled moves on POA&M items, Jira MCP writes) require explicit lead program manager confirmation regardless of trust level.
