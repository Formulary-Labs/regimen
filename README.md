# Regimen

Principal-level compliance program management agent. Governs program intake through audit closure, orchestrates [Formulary](https://github.com/Formulary-Labs) CLI tools for all deterministic work, and applies judgment where tools cannot.

Part of the [Formulary-Labs](https://github.com/Formulary-Labs) ecosystem.

---

## What it does

Regimen is the AI agent layer above Formulary's deterministic CLI tools. It handles:

- **Program intake and monitoring** — classifies incoming work, routes to the right spec, and maintains program state across sessions
- **Orchestration** — when a matching Formulary CLI is installed, prefers it for computation-heavy work and synthesizes the structured output into decisions and communications; executes via function specs when CLIs are not available
- **Memory management** — maintains per-program hot memory, decision logs, and workflow state across sessions
- **Quality gate** — every output passes `engine/quality-gate-spec.md` before delivery
- **Portfolio view** — cross-program health, QBR synthesis, and shared risk patterns
- **Stakeholder communications** — drafts calibrated by audience (executive, technical, auditor)
- **Post-audit processing** — lessons learned, corrective actions, feed-forward artifacts

## Architecture

```
Lead Program Manager
        │
        │  slash commands / natural language
        ▼
   ┌──────────┐
   │  regimen │  ◄── config/constitution.md (governance)
   │  (agent) │  ◄── engine/ (orchestrators, quality gate)
   │          │  ◄── functions/ (19 function specs)
   └────┬─────┘
        │  structured invocation (when CLIs installed)
        ▼
   Formulary CLI tools — optional; any subset
   (assay · titer · specimen · dose · exhibit · challenge
    decay · scan · compound · formula · probe · bind)
        │
        ▼
   gemara artifacts  ·  run JSON  ·  provenance log
```

The split is explicit: Formulary tools handle anything that can be reduced to a deterministic function. Regimen handles everything that requires judgment, context, or reasoning across heterogeneous inputs.

---

## Setup

### Required

**Cursor or Claude Code** — this framework is designed for use with an AI coding agent that can read the repo structure, invoke slash commands, and run scripts.

**Python 3.10+** — for provenance logging, validation scripts, and HTML renderers:

```bash
pip install -r runtime/requirements.txt
```

### Optional Formulary CLIs

Regimen works without any Formulary CLI installed — the function specs contain enough guidance to execute manually. When a CLI is available for a function, regimen prefers it for deterministic work. Install only the tools you use:

```bash
# Example — install only what your workflow needs
go install github.com/Formulary-Labs/probe/cmd/probe@latest
go install github.com/Formulary-Labs/assay/cmd/assay@latest
go install github.com/Formulary-Labs/titer/cmd/titer@latest
go install github.com/Formulary-Labs/bind/cmd/bind@latest   # cross-framework mapping
```

See [FORMULARY.md](./FORMULARY.md) for the full spec → CLI map and install commands for every tool.

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/Formulary-Labs/regimen.git
cd regimen

# 2. Read the constitution (required before any action)
# The agent loads this at session start automatically.
# Read it yourself to understand the governance model.
cat config/constitution.md

# 3. Add a program to the catalog
# Edit config/program-catalog.json — copy the template entry and fill in your slug.

# 4. Create program memory and run structure
mkdir -p runs/your-program-slug memory
cp memory/program-state-template.md memory/your-program-slug-memory.md
cp memory/program-decisions-log-template.log memory/your-program-slug-decisions.log

# 5. Open in Cursor (or Claude Code) and run:
#   /init   — session initialization, constitution load, orientation
```

---

## Repository layout

```
regimen/
├── config/              # Constitution, JSON schemas, program catalog, tool requirements
├── engine/              # Session init, pipeline orchestrator, quality gate, portfolio specs
├── functions/           # 19 function specs (each maps to a Formulary CLI where applicable)
├── agents/              # Agent role definitions (coordinator, program, intelligence, review, evidence, frameworks)
├── commands/            # Slash command specs (/init, /daily-brief, /kanban, /post-audit, …)
├── skills/              # Cursor skill implementations for each command
├── rules/               # Cursor .mdc rules (identity, lazy-load, path conventions)
├── memory/              # Templates only — program memory files are gitignored
├── scripts/             # Python utilities: provenance log, integrity check, validators, renderers
├── runtime/             # Containerized fleet runtime for multi-PM / deployed mode
├── tests/               # Test suite
├── docs/                # Reference documentation
├── runs/                # Per-program pipeline run JSONs (gitignored)
├── data/                # Per-program materials and checkpoints (gitignored)
├── logs/                # Provenance log (gitignored)
├── CLAUDE.md            # Agent identity, boot sequence, routing table (loaded by the AI at session start)
└── FORMULARY.md         # Full spec → Formulary CLI cross-reference map
```

---

## Commands

| Command | What it does |
|---|---|
| `/init` | Session initialization — constitution load, directory discovery, classify or orient |
| `/daily-brief` | Morning briefing across all active programs |
| `/program-status` | One-page status snapshot for a single program |
| `/due-this-week` | Cross-program digest of items due in the next seven days |
| `/evidence-due` | Upcoming and overdue evidence collection windows |
| `/kanban` | View, update, and manage per-program kanban boards |
| `/log-decision` | Capture a decision into the program decision log |
| `/meeting-debrief` | Ingest a transcript; extract decisions and actions |
| `/meeting-prep` | Focused briefing for a 1:1 or team sync |
| `/draft-status-update` | Draft a stakeholder communication calibrated by audience |
| `/control-assessment` | Fill auditor templates, STIGs, or benchmarks |
| `/intel-scan` | External intelligence monitoring: source scan, risk deltas |
| `/portfolio-qbr` | Quarterly narrative synthesis across all programs |
| `/auditor-view` | Read-only auditor compliance posture dashboard |
| `/provenance-query` | Query what the system has produced for a program |
| `/update-item` | Update status, owner, or notes on a POA&M item |
| `/doc-review` | Language scan for AI writing tells and format standards |
| `/post-audit` | Lessons learned, corrective actions, feed-forward artifact |
| `/validate` | Run all structural validators in one pass |

---

## Relationship to Formulary

Regimen is the judgment layer. Formulary is the computation layer. They are designed to work together but neither requires the other to function.

- **Formulary tools run without regimen** — any Formulary CLI can be invoked directly from a terminal or CI pipeline.
- **Regimen works without Formulary** — the function specs contain enough guidance for a capable agent to execute manually if the CLIs are unavailable. Formulary tools reduce token overhead and increase determinism when present.

See `FORMULARY.md` for the full integration map.

---

## Governance

All behavior is governed by `config/constitution.md`. The constitution supersedes all other specs and instructions in cases of conflict.

Before modifying the constitution, the pipeline orchestrator, or the quality gate spec, run:

```bash
python scripts/integrity_check.py
```

---

## License

Apache License 2.0
