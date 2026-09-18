---
resource_type: spec
version: "2.0"
domain: program-management
triggers:
  - calendar_export
  - monitoring_run
  - new_program
inputs:
  - pipeline_run_json
  - calendar_events_array
outputs:
  - ics_file
  - markdown_event_list
governed_by: config/constitution.md
invoked_by: engine/program-pipeline-orchestrator.md
depends_on: functions/program-monitoring-spec.md
---

# Calendar Output Spec
**Version:** 2.0
**Purpose:** Transform the `calendar_events` array from a pipeline run JSON into a portable `.ics` file and human-readable event list.
**Governed by:** `config/constitution.md`

---

## Constitutional Guidance

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

---

## Parameters

```
TIMEZONE:      [IANA timezone string — default: America/New_York]
WORK_START:    [HH:MM — default: 09:00]
WORK_END:      [HH:MM — default: 17:00]
GAP_MINUTES:   [minutes between events — default: 15]
HOLIDAYS:      [us_federal_plus_observed — default, only supported value currently]
```

---

## Formulary Tool

**CLI:** [`dose`](https://github.com/Formulary-Labs/dose) — `github.com/Formulary-Labs/dose`

Handles all calendar generation:
- Reads `calendar_events` from a run JSON file
- Produces RFC 5545-compliant `.ics` and Markdown event list
- Working-day-aware scheduling with US federal holiday awareness
- Shift-left scheduling, conflict resolution, intelligent batching
- CI-safe exit codes

```bash
dose --run runs/[PROGRAM]/latest.json --out data/[PROGRAM]/[date]-calendar.ics
dose --run runs/[PROGRAM]/latest.json --markdown-only
dose --run runs/[PROGRAM]/latest.json --timezone America/Chicago
```

> See [`FORMULARY.md`](../FORMULARY.md) for the full integration map.

---

## Provenance

```bash
python scripts/provenance_log.py write \
  --spec "functions/calendar-output-spec.md" \
  --output "data/[PROGRAM]/[DATE]-calendar.ics" \
  --output-type calendar \
  --program "[PROGRAM]" \
  --purpose "Calendar generated: [n] events" \
  --reusability artifact \
  --quality-gate pass
```

---

## Companion Specs
- Governed by: `config/constitution.md`
- Invoked by: `engine/program-pipeline-orchestrator.md`
- Reads: `runs/[PROGRAM]/latest.json` → `calendar_events`
- Writes: `data/[PROGRAM]/[date]-calendar.ics`, `data/[PROGRAM]/[date]-calendar.md`
- Depends on: `functions/program-monitoring-spec.md`
