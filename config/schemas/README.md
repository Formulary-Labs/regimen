# Schemas

Versioned JSON Schemas for the compliance fleet data types. These schemas define the contracts between agents and are validated at runtime and in CI.

**Path:** `config/schemas`

## Contents

| File | Version | Purpose |
|------|---------|---------|
| **portfolio-state.schema.json** | 1.0 | Cross-program portfolio state produced by the coordinator. Used by `engine/portfolio-orchestrator.md`. |
| **run-output.schema.json** | 1.1 | Pipeline run output envelope, nested shape (runs/[PROGRAM]/*.json). Used by `engine/program-pipeline-orchestrator.md`. |
| **run-output-v2.schema.json** | 2.0 | Pipeline run output envelope, flat shape. Used by `functions/program-intake-spec.md`. Extends with optional `vendor_output`/`monitoring_output`/`program_extensions` — see OPTIMIZATION-ROADMAP.md Phase 3 for the schema-strategy decision behind these. |
| **kanban.schema.json** | 1.0 | Per-program Jira-aligned kanban board (`data/[program]/kanban.yaml`). Used by `functions/kanban-spec.md`. |
| **control-assessment-state.schema.json** | 1.0 | Control assessment batch state (`data/[program]/assessments/[RUN_ID]-state.json`). Used by `functions/control-assessment-spec.md`. |
| **briefing-output.schema.json** | 1.0 | Structured shape of the daily cross-program brief. Companion to `commands/daily-brief.md`'s prose format, not a replacement for it. |
| **qbr-output.schema.json** | 1.0 | Structured shape of the quarterly business review. Companion to `engine/portfolio-qbr-spec.md`'s markdown narrative. |
| **auditor-view-output.schema.json** | 1.0 | Structured shape of the auditor posture dashboard data, pre-HTML-render. Used conceptually by `functions/auditor-view-spec.md` / `scripts/auditor_view_renderer.py`. |
| **agent-message.schema.json** | 1.0 | Inter-agent message envelope for the message bus (37 types) |
| **audit-entry.schema.json** | 1.0 | Append-only audit log entry (provenance.jsonl) |
| **common-control-catalog.schema.json** | 1.0 | Cross-framework control mappings (CCC) |
| **evidence-record.schema.json** | 1.0 | Evidence lifecycle tracking per program |
| **trust-state.schema.json** | 1.0 | Agent trust levels and promotion/demotion history |
| **fleet-metrics.schema.json** | 1.0 | Fleet operational metrics (agents, programs, costs) |
| **work-checkpoint.schema.json** | 1.0 | Generic resumability checkpoint (`data/[program]/checkpoints/*.json`) |

## Structured Output Contracts

Specs whose output has a declared schema set `structured_output: true` and `structured_output_schema: config/schemas/[name].schema.json` in their frontmatter (see `config/spec-frontmatter-schema.yaml`). For specs whose canonical output is prose/markdown (QBR, daily brief, auditor view), the schema is a companion contract for structured consumption — it does not change or relax the prose format's own quality-gate requirements. `scripts/validate_frontmatter.py` checks that `structured_output_schema` paths exist and live under `config/schemas/`.

## Versioning

Schemas are versioned independently from specs. Schema version is embedded in the data (`schema_version` field). Breaking changes require a major version bump and a migration path.

## Validation

Schemas can be validated using any JSON Schema 2020-12 compatible validator. In Python:

```python
import json
import jsonschema

with open("config/schemas/run-output.schema.json") as f:
    schema = json.load(f)

with open("runs/program/latest.json") as f:
    data = json.load(f)

jsonschema.validate(data, schema)
```
