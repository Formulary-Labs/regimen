# Multi-PM Cursor identity — shared repo, personal context

**Audience:** Program managers and engineers who share this Portfolio repo and use Cursor Agent on program files.  
**Goal:** Same agent behavior and file layout for everyone, without overwriting shared config or blurring **who** is asking.

Cursor does **not** authenticate you as a specific PM. Identity is **you-declared** (User rules + first message) plus **repo conventions** below.

---

## 1. Use Cursor **User rules** (recommended)

User rules live in your Cursor account, **not** in Git — each person maintains their own. They apply across workspaces unless scoped.

**Copy-paste template** (replace brackets):

```
When working in the Portfolio compliance repo:
- My role: [paste "Session identity tag" from config/pm-roster.md for your row]
- Programs I may change workflow state for (runs/, decision logs): [slug1, slug2] — if unsure, ask before writing runs/*.json
- Programs I read for status: [same or "all assigned by lead PM"]
- Put personal scratch notes only under local/pm/<my-handle>/ (gitignored)
- Do not modify config/constitution.md, engine/program-pipeline-orchestrator.md, or engine/quality-gate-spec.md unless I explicitly ask and integrity_check has been run
- Prefer slash commands (/program-status, /meeting-debrief, etc.) per docs/cursor-agent-use-guide.md
```

Roster table: `config/pm-roster.md`.

---

## 2. Start each Agent chat with a one-line preamble

Even with User rules, the first message helps routing:

```
Session: cohort: [Your Name] ([Title]). Program: [slug or "portfolio"]. Task: [what you want].
```

The agent should **classify program** before loading `memory/` and `runs/` per `.cursorrules` lazy-load table.

---

## 3. Keep personal notes out of Git

| Location | Committed? | Use for |
|----------|--------------|---------|
| `memory/[program]-memory.md` | Yes | Session narrative, decision log table — team visibility |
| `runs/[program]/latest.json` | Yes | Workflow state — treat as **shared**; prefer PR for changes |
| `local/pm/<your-handle>/` | **No** (gitignored) | Drafts, paste buffer, experiment prompts |

See `local/pm/README.md` for the folder convention.

---

## 4. What counts as “stomping” shared config

Avoid casual edits to:

- `config/constitution.md`, `engine/program-pipeline-orchestrator.md`, `engine/quality-gate-spec.md` (integrity check + principal approval per repo rules)
- Another person’s **sole-owned** program `latest.json` without coordination — use PR or explicit handoff
- `.cursorrules` / `.cursor/rules/*.mdc` unless the team agreed a change (affects everyone)

Safe frequent edits (when **your** program is classified):

- `memory/[your-program]-memory.md` session entries and decision log rows (follow meeting-debrief / log-decision flows)
- `runs/[your-program]/latest.json` when you are the owner and follow confirmation flows for destructive changes

---

## 5. Enforcing identity in Cursor (what is and is not possible)

| Mechanism | Enforces identity? |
|-----------|-------------------|
| User rules | Soft — you set it; model should follow |
| Workspace rules (`.cursor/rules`) | Soft — shared team guardrails; request **`pm-cohort`** rule when onboarding |
| `config/pm-roster.md` | Reference only — update assignments with lead PM |
| Git branch protection / CODEOWNERS | **Hard** (on Git host) — optional for `runs/` / `config/` |
| `.gitignore` + `local/pm/` | Prevents accidental **commit** of personal noise |

There is no Cursor feature that blocks file edits by LDAP identity. Combine **User rules + roster + PR process** for real enforcement on shared files.

---

## 6. Related docs

- `docs/cursor-agent-use-guide.md` — slash commands and collaborator roles
- `config/pm-roster.md` — names, titles, session tags
- `.cursor/rules/pm-cohort.mdc` — agent behavior when multiple PMs use the repo
