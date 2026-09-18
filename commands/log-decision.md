# Log Decision

Capture a decision made outside a pipeline run and write it to the program's memory file and optionally update the relevant run JSON item.

## Input Required

If not provided after the command, ask before proceeding:

- Program: [program slug]
- Decision summary: [what was decided]

Optionally:
- GRC ID of related item: [ID]
- Rationale: [why]
- Revisit condition: [when or under what circumstances to revisit]
- Decision maker: [name — defaults to lead program manager]

## Steps

1. Read `memory/[program]-memory.md` — confirm file exists
2. Format the decision log entry to match the table's actual 4 columns (`| Date | Decision | Rationale | Revisit condition |` — see the template in `memory/session-memory-template.md`, consistent across all programs). There is no separate "decision maker" column; if a decision maker other than the lead program manager is relevant, fold it into the Decision or Rationale cell (e.g. "Confirmed by [name]: ...").

```
| [today's date] | [decision summary — prefix with decision maker if not the lead program manager] | [rationale or —] | [revisit condition or —] |
```

3. Append to the Decision Log table in `memory/[program]-memory.md`
4. If a GRC ID was provided, note the decision against that item in `runs/[program]/latest.json` under the relevant section — do not change item status unless explicitly instructed
5. Log provenance:

```bash
python scripts/provenance_log.py write \
  --spec "commands/log-decision.md" \
  --output "memory/[program]-memory.md" \
  --output-type decision_log \
  --program "[program]" \
  --purpose "Decision logged: [summary truncated to 60 chars]" \
  --reusability instance \
  --quality-gate not_applicable
```

## Output

Confirm what was written:
```
DECISION LOGGED — [program]
  Date: [date]
  Decision: [summary]
  Written to: memory/[program]-memory.md → Decision Log
  [GRC item updated: ID-XX] if applicable
```

This is a one-way write to the memory file. Confirm before executing if the decision summary is ambiguous.
