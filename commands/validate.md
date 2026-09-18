# Validate

Run the system's structural validators in one pass and summarize results. This is a repo-health check, not a compliance-content check — it validates that the spec/schema/renderer system itself is internally consistent, not that any program's compliance posture is correct.

## Input Required

None required. Optionally:

- Scope: [system | program-slug] (default: system — the 5 system-wide validators below; a program slug additionally runs that program's validators if any exist, e.g. `validate_aims_xlsx.py` for `iso42001`)

## Steps

Run the unified runner, which executes all 5 system validators (and the program validator if `--program` is given) and prints the summary table directly:

```bash
python scripts/validate_all.py
python scripts/validate_all.py --program iso42001   # adds validate_aims_xlsx.py --all
python scripts/validate_all.py --program 62443       # adds test_guide_urls.py
```

Equivalent to running each validator individually and capturing its exit code and output:

```bash
python scripts/integrity_check.py
python scripts/validate_frontmatter.py
python scripts/validate_schema_drift.py
python scripts/spec_coverage.py
python scripts/validate_script_safety.py
```

Program validators currently registered: `iso42001` → `scripts/validate_aims_xlsx.py`; `62443` → `scripts/test_guide_urls.py` for implementation-guide link health.

`scripts/eval_routing.py` is a related but separate check — a regression harness for the routing table's classification behavior (not structural link integrity, which `spec_coverage.py` already covers). It is not part of `/validate`'s default run since it's a routing-table-specific concern, not a general repo-health check; run it directly after editing `engine/session-init-spec.md`'s routing table.

## Output

```
VALIDATION RUN — [date]

integrity_check.py         [PASS | FAIL — n headings missing]
validate_frontmatter.py    [PASS | FAIL — n files]
validate_schema_drift.py   [PASS | FAIL — n errors, n warnings]
spec_coverage.py           [PASS | FAIL — n specs uncovered]
validate_script_safety.py  [PASS | FAIL — n scripts fail execution-safety]
[program validator if run] [PASS | FAIL — n findings]

OVERALL: [PASS | FAIL]
```

If any validator fails, show its actual error output beneath the summary table — do not just say "FAIL." `validate_schema_drift.py` warnings (declared-but-unread schema properties) are informational, not failures; only its ERRORS block affects overall PASS/FAIL. `validate_script_safety.py` findings map directly to `config/tool-requirements.md`'s Execution Safety section — a failing script has no `if __name__ == "__main__":` guard, a top-level write, or no confirm/required-arg gate before it can mutate files. Do not silently fix anything found — report it and let the lead program manager decide what to fix and when.
