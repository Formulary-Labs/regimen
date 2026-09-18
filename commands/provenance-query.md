# Provenance Query

Show what the system has produced for a program by querying the append-only provenance log. Surface reusable artifacts when present.

## Input required

If not provided after the command, ask before proceeding:

- **Program** — program slug (required for a focused query)
- **Output type filter** (optional) — narrow results; map user-facing labels to `scripts/provenance_log.py` `--output-type` when possible:
  - `run_json` → `run_json`
  - `status_report` / stakeholder drafts → `draft_communication` or query without type and filter by `purpose` / `spec`
  - `auditor_dashboard` → `dashboard`
  - `intel_report` → `entropy_report`, `red_team_report`, or query broadly and filter
  - `decision_log` / `item_update` → often `other` or no `--output-type`; scan matching `spec` / `purpose` in results
- **Since date** (optional) — `YYYY-MM-DD` for `query --since`

## Steps

1. From the compliance workspace root, run:

```bash
python scripts/provenance_log.py query --program [program] [--output-type TYPE] [--since YYYY-MM-DD] [-v]
```

Use `-v` when the lead program manager needs full fields. If no `--output-type` matches the ask, run without it and summarize entries relevant to the requested filter.

2. Optionally cross-check `logs/provenance.jsonl` (read-only) for entries the CLI filter missed, if the lead program manager named a custom deliverable type.

## Output

Present a concise list: timestamp, output path, output_type, purpose, reusability. Call out entries classified as reusable templates. If nothing matches, say so and suggest broadening the filter or date range.
