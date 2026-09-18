---
resource_type: spec
version: "1.0"
domain: compliance
triggers:
  - auditor_view
  - generate_auditor_dashboard
  - audit_prep
inputs:
  - program_run_json
  - provenance_log
  - control_coverage_matrix
  - risk_register
  - evidence_calendar
outputs:
  - auditor_dashboard_html
governed_by: config/constitution.md
standalone: true
entry_point: true
structured_output: true
structured_output_schema: config/schemas/auditor-view-output.schema.json
depends_on:
  - runs/[PROGRAM]/latest.json
  - logs/provenance.jsonl
---

# Auditor View Spec
**Version:** 1.0
**Purpose:** Generate a read-only, per-program compliance posture dashboard suitable for auditor review. Demonstrates continuous monitoring activity, control coverage status, risk register posture, and evidence collection cadence. Does not expose internal program management detail, decision queues, or session-level operational data.
**Governed by:** `/config/constitution.md`
**Output:** Static HTML file — generated on demand via this spec OR automatically on every CI push to main via `scripts/build_pages.py` (Step 1, sub-step 4).
**Audience:** Third-party auditors, compliance reviewers, oversight stakeholders.
**Maintainer:** `[your name/handle]`

---

## Constitutional Guidance

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

---

## What This View Shows

Four sections, nothing more:

1. **Monitoring Activity Log** — provenance entries for this program, full detail: timestamp, spec invoked, artifact type produced, quality gate result. Proves continuous monitoring is occurring on cadence.

2. **Control Coverage Status** — percentage of controls evidenced, implemented without evidence, and gap by control family. Derived from the most recent coverage matrix in the run JSON or coverage spec output.

3. **Risk Register Summary** — open item count by severity, closure rate, POA&M item status. Does not expose individual risk descriptions beyond severity classification unless explicitly included in the run JSON's auditor-visible fields.

4. **Evidence Collection Calendar** — upcoming and completed collection windows with status. Shows that evidence collection is planned and tracked.

## What This View Does Not Show

- Internal decision queues or deferred items
- Session-level operational notes or memory content
- Draft communications or staged outputs
- Watch list items or internal health classifications
- Any field tagged `internal_only: true` in the run JSON
- Lead program manager name or organizational chart detail beyond program ownership fields

---

## Parameters

```
PROGRAM:          [program slug]
REPORT_DATE:      [YYYY-MM-DD — defaults to today]
LOOKBACK_DAYS:    [90 | 180 | 365 — provenance window, default 90]
OUTPUT_PATH:      [ui/[program]-auditor-[date].html — default]
```

---

## Execution

Use the `exhibit` CLI (see Formulary Tool section below). It handles all data loading, section assembly, and HTML rendering from `runs/[PROGRAM]/latest.json` and `logs/provenance.jsonl`.

After the run, log provenance:

```bash
python scripts/provenance_log.py write \
  --spec "functions/auditor-view-spec.md" \
  --output "ui/[PROGRAM]-auditor-[DATE].html" \
  --output-type auditor_dashboard \
  --program "[PROGRAM]" \
  --purpose "Auditor view generated for [context]" \
  --reusability artifact \
  --quality-gate pass
```

---

## Trigger

```
PROGRAM: [slug]
REPORT_DATE: [YYYY-MM-DD]
LOOKBACK_DAYS: [90]

BEGIN AUDITOR VIEW
```

---

## Formulary Tool

**CLI:** [`exhibit`](https://github.com/Formulary-Labs/exhibit) — `github.com/Formulary-Labs/exhibit`

Handles the deterministic execution layer of this spec:
- Loads `runs/[PROGRAM]/latest.json` and `logs/provenance.jsonl`
- Renders a clean, no-JavaScript static HTML auditor posture view
- Outputs to stdout or a file path; CI-safe exit codes

```bash
exhibit --run runs/[PROGRAM]/latest.json --provenance logs/provenance.jsonl --out ui/[PROGRAM]-auditor.html
```

This spec governs routing, data assembly across passes, and quality gate. `exhibit` handles the HTML render step (replaces Pass 6 / `scripts/auditor_view_renderer.py` invocation).

> See [`FORMULARY.md`](../FORMULARY.md) for the full integration map.

---

## Suggested Repo Path
`/functions/auditor-view-spec.md`

## Companion Specs
- Governed by: `/config/constitution.md`
- Reads: `/runs/[PROGRAM]/latest.json`, `/logs/provenance.jsonl`
- Writes: `/ui/[PROGRAM]-auditor-[DATE].html`
- Rendered by: `scripts/auditor_view_renderer.py`
- Auto-invoked by: `scripts/build_pages.py` on every push to main (Step 1, sub-step 4)
