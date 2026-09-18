# Daily Brief

Produce a concise morning briefing across all active programs.

## Steps

1. Read all `memory/*.md` files
2. Scan all `runs/*/latest.json` files
3. Check `data/portfolio/latest.json` if present
4. Tail `logs/provenance.jsonl` — last 5 entries

## Output Format

```
DAILY BRIEF — [today's date]

PORTFOLIO HEALTH
  [program-slug]  🔴/🟡/🟢  [one-line reason if red or yellow]

DUE TODAY
  [item] — [program] — [owner]

DUE THIS WEEK
  [item] — [program] — [due date]

DECISIONS PENDING
  [item] — [program] — [age in days]

OPEN BLOCKERS
  [item] — [program] — [owner]

RECENT ACTIVITY (last 5 provenance entries)
  [date] [artifact type] [program]

SUGGESTED FIRST ACTION
  [single most urgent item across all programs]
```

Keep the entire brief under 40 lines. If a program is green with nothing due, omit it from all sections except the health summary. Do not editorialize — surface data, not commentary.

## Structured Output (optional)

The prose format above is canonical. If a JSON form is needed (agent handoff, canvas rendering, automation), the same data conforms to `config/schemas/briefing-output.schema.json` — emit that shape rather than inventing an ad hoc structure.
