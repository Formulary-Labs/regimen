# Post Audit

Process audit closure into structured lessons learned, corrective action plans, and feed-forward artifacts for the next program cycle, per `functions/post-audit-spec.md`.

## Input Required

If not provided after the command, ask before proceeding:

- Program: [program slug]
- Audit type: [external | surveillance | internal]
- Audit cycle: [YYYY or YYYY-MM-DD range]
- Mode: [standard | full_retrospective] (default: standard — full_retrospective additionally produces program improvement items, the feed-forward artifact, and a draft closure communication)

## Steps

1. Load `runs/[program]/latest.json` and, if available, the audit report / findings list the lead program manager is providing
2. Execute `functions/post-audit-spec.md` with:

```
AUDIT_TYPE:        [external | surveillance | internal]
AUDIT_CYCLE:       [YYYY or YYYY-MM-DD range]
OUTPUT_FORMAT:     [markdown | json | both]
POST_AUDIT_MODE:   [standard | full_retrospective]

BEGIN POST-AUDIT REVIEW
```

3. Follow the spec's passes in order. Do not skip the quality gate. Log provenance per the spec's per-artifact `output_type` values before presenting results.

## Output

Per the spec: `lessons_learned_report` and `corrective_action_plan` always; `program_improvement_items`, `feed_forward_artifact`, and a draft closure communication additionally on `full_retrospective`. All written under `data/[program]/post-audit/[AUDIT_CYCLE]-*`.

The feed-forward artifact (full_retrospective only) is consumed by the next `program-intake-spec.md` run for this program (`existing_transition` type) — note this to the lead program manager so it isn't lost before the next cycle starts.
