---
resource_type: reference
version: "2.0"
scope: all programs
governed_by: config/constitution.md
---

# Formulary — Compliance Micro-Tools Ecosystem

**Organization:** [github.com/Formulary-Labs](https://github.com/Formulary-Labs)
**Purpose:** Open-source Go CLI tools that implement the deterministic execution layer for functions defined in this repo. Each tool is independently useful — run one alone, pipe a few together, or skip any tool entirely. No Formulary CLI is required for regimen to function.

> **Optionality:** Every Formulary binary is independent. When a CLI is installed and a matching function spec exists, regimen prefers it for deterministic work. When a CLI is not installed, the function spec provides enough guidance to execute manually. Install only the tools your workflow uses.

---

## Design Relationship

This repo (`regimen`) is the **AI agent orchestration layer** — specs, memory, run state, and quality gates that govern how compliance work gets done and routed.

Formulary tools are the **execution layer** — deterministic, testable CLI binaries that do the compute-heavy, artifact-heavy, or structured-output work that would otherwise be done inline by an LLM.

```
regimen (this repo)
  ├── config/constitution.md    AI agent behavior and values
  ├── engine/                   Orchestration, routing, quality gates
  ├── functions/                Per-domain work specs (what to do, when, how to judge)
  └── scripts/                  Python execution layer (renderers, validators, provenance)

Formulary-Labs org (github.com/Formulary-Labs)
  ├── substrate                 Shared Go library (exit codes, flags, provenance, gemara)
  └── <tool>                    One repo per CLI tool — see table below
```

**Rule:** When a Formulary CLI exists for a function, prefer it over inline LLM execution for the deterministic steps. The spec still governs routing, judgment, flagging, and quality gate.

---

## Spec → Formulary Tool Map

| Function Spec | Formulary Tool | Repo | What the CLI handles | What the spec adds |
|---|---|---|---|---|
| `functions/auditor-view-spec.md` | `exhibit` | [Formulary-Labs/exhibit](https://github.com/Formulary-Labs/exhibit) | Static HTML auditor posture view from run state + provenance | Routing, quality gate, program context |
| `functions/calendar-output-spec.md` | `dose` | [Formulary-Labs/dose](https://github.com/Formulary-Labs/dose) | `.ics` + Markdown evidence calendar with shift-left scheduling | Pipeline context |
| `functions/compliance-doc-generator-spec.md` | `formula` | [Formulary-Labs/formula](https://github.com/Formulary-Labs/formula) | Deterministic SOA CSV, risk CSV, evidence registry, system card scaffolds | Multi-pass narrative generation, XLSX, quality gate |
| `functions/compliance-entropy-spec.md` | `decay` | [Formulary-Labs/decay](https://github.com/Formulary-Labs/decay) | 13-pattern longitudinal drift detection between program snapshots | Narrative synthesis, finding validation, behavioral constraints |
| `functions/compliance-redteam-spec.md` | `challenge` | [Formulary-Labs/challenge](https://github.com/Formulary-Labs/challenge) | 10-pattern deterministic artifact interrogation | SME judgment, severity classification, reviewer guidance |
| `functions/control-assessment-spec.md` | `assay` | [Formulary-Labs/assay](https://github.com/Formulary-Labs/assay) | Resumable batch control assessment with 7-criterion validation and state management | Narrative response generation, quality gate, gap review |
| `functions/control-coverage-spec.md` | `titer` | [Formulary-Labs/titer](https://github.com/Formulary-Labs/titer) | Coverage matrix, gap analysis (coverage/owner/evidence), SOA CSV from gemara Layer 2 | Framework interpretation, control narrative, pipeline writes |
| `functions/control-mapping-spec.md` | `bind` | [Formulary-Labs/bind](https://github.com/Formulary-Labs/bind) | Cross-framework MappingDocument resolution — mapped/unmapped entries, title resolution, conflict flags | Routing to downstream specs (risk register, compound, audit package) |
| `functions/external-intel-spec.md` | `scan` | [Formulary-Labs/scan](https://github.com/Formulary-Labs/scan) | External source fetch (CISA, NVD, RSS), relevance scoring, structured output | Source judgment, risk delta narrative, stakeholder draft routing |
| `functions/management-system-assembler-spec.md` | `compound` | [Formulary-Labs/compound](https://github.com/Formulary-Labs/compound) | Annex SL-structured ISMS/AIMS/CSMS document scaffold with deterministic clause population | Narrative generation (marked `[DATA NEEDED: narrative]`), quality gate, review |
| `functions/program-dashboard-spec.md` | `vital` | [Formulary-Labs/vital](https://github.com/Formulary-Labs/vital) | Program health snapshot JSON/Markdown from run state, coverage, risk data | Full HTML render (renderers still active), portfolio aggregation |
| `functions/risk-register-spec.md` | `specimen` | [Formulary-Labs/specimen](https://github.com/Formulary-Labs/specimen) | Risk register and POA&M CRUD, feed-forward ingestion, status filtering | Risk scoring judgment, owner assignment, pipeline write |

---

## Shared Library

| Repo | Purpose |
|---|---|
| [Formulary-Labs/substrate](https://github.com/Formulary-Labs/substrate) | Shared Go module: standard exit codes, format types, CLI flags, provenance writer, gemara artifact wrappers. All tools import this. |

---

## Function Specs Without a Formulary Tool (handled by agent/LLM)

| Function Spec | Reason no CLI tool needed |
|---|---|
| `functions/kanban-spec.md` | YAML state + HTML render; Python renderer active; Jira sync is agent work |
| `functions/post-audit-spec.md` | Narrative-heavy process; feed-forward artifact consumed by `specimen` |
| `functions/product-evidence-spec.md` | Document ingestion and mapping; LLM judgment is the core capability |
| `functions/product-onboarding-intake-spec.md` | Intake validation and merge; agent-mediated |
| `functions/program-comms-spec.md` | Communications drafting; LLM is the execution layer |
| `functions/program-intake-spec.md` | Program scaffolding; orchestrator-driven |
| `functions/program-monitoring-spec.md` | Continuous oversight; orchestrator-driven |
| `functions/vendor-management-spec.md` | Vendor scoring and remediation; judgment-heavy |

---

## Scripts in This Repo

Python scripts in `scripts/` remain the active execution layer for rendering, validation, and provenance logging. Formulary tools use gemara artifacts as their primary input; scripts use `runs/*/latest.json`. Both run in parallel until a data layer bridge is established.

| Script | Purpose | Formulary overlap |
|---|---|---|
| `provenance_log.py` | Append-only provenance log writer and query tool | None — core infrastructure |
| `integrity_check.py` | Protected file heading verification | None — core infrastructure |
| `validate_all.py` + `validate_*.py` | Frontmatter, schema drift, spec coverage, script safety | None — framework validators |
| `spec_coverage.py` | Spec coverage audit | None |
| `utils.py` | Shared utilities | None |
| `program_dashboard_renderer.py` | Full HTML program dashboard from run state | `vital` produces JSON/MD; this renders HTML |
| `portfolio_renderer.py` | Portfolio health page | `vital` partial overlap |
| `kanban_renderer.py` | Kanban HTML view | None |
| `briefing_renderer.py` | Daily brief HTML rendering | None |
| `draft_formatter.py` | Stakeholder communication formatting | None |
| `build_pages.py` | CI/CD page build orchestration | None |

---

## Gemara Schema Compatibility

Formulary tools read and write [gemara](https://github.com/gemaraproj/gemara)-compatible artifacts (CUE schema, Go bindings via `go-gemara`). The [gemara-mcp](https://github.com/gemaraproj/gemara-mcp) server provides AI agent access to the same schema — Formulary tools and gemara-mcp are complementary, not competing.

Data flow:
```
gemara artifacts (Layer 2)
  → probe (validate)
  → assay / titer / specimen (assess / cover / register)
  → formula / compound (generate documents)
  → exhibit (auditor view)
  → vital / decay / challenge (health / drift / interrogate)
```

---

## complytime Integration

See [complytime-integration-design.md](https://github.com/Formulary-Labs/.github/blob/main/complytime-integration-design.md) for proposed contributions and integration points with [complytime](https://github.com/complytime).

---

## Optional Installs

Each binary is independent — install only the tools your workflow uses:

```bash
go install github.com/Formulary-Labs/probe/cmd/probe@latest
go install github.com/Formulary-Labs/assay/cmd/assay@latest
go install github.com/Formulary-Labs/titer/cmd/titer@latest
go install github.com/Formulary-Labs/specimen/cmd/specimen@latest
go install github.com/Formulary-Labs/dose/cmd/dose@latest
go install github.com/Formulary-Labs/exhibit/cmd/exhibit@latest
go install github.com/Formulary-Labs/challenge/cmd/challenge@latest
go install github.com/Formulary-Labs/decay/cmd/decay@latest
go install github.com/Formulary-Labs/scan/cmd/scan@latest
go install github.com/Formulary-Labs/compound/cmd/compound@latest
go install github.com/Formulary-Labs/formula/cmd/formula@latest
go install github.com/Formulary-Labs/bind/cmd/bind@latest
```
