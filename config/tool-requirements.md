---
resource_type: requirements
version: "1.2"
scope: all scripts and tools
governed_by: config/constitution.md
audience: LLMs generating tools
---

# Tool Development Requirements
**Version:** 1.2 — added Execution Safety section (2026-07-29), triggered by 10 scripts found executing file-mutating side effects on bare invocation or `--help`.
**Purpose:** Behavioral contract for all scripts and tools in this repo. Read before building any tool over ~200 lines.
**Scope:** Python, Bash/Shell, Node.js — any language.

---

## When to Build a Tool

Build and commit a script when any of these are true:
- Logic exceeds ~200 lines
- The operation runs more than once
- It reads or writes files, JSON, or external state
- It requires argument parsing, error handling, or logging
- Output must be consistent and reproducible across sessions

Under ~200 lines used once: inline code is sufficient. Do not create files for throwaway logic.

---

## Before Writing Any Code

Present a plan and wait for confirmation before implementing any tool over ~200 lines:

```
TOOL PLAN
Name:            [filename and repo path]
Purpose:         [one sentence]
Language:        [language]
Style:           [declared standard — language best practices unless deviation noted]
Inputs:          [args, files, stdin]
Outputs:         [files, stdout, exit codes]
Dependencies:    [external packages — justify each]
Security:        [credentials, user data, or sensitive inputs handled?]
Estimated lines: [approximate]
Integration:     [which specs or scripts invoke this]
```

---

## Standards Declaration

Every tool declares its style standard in the file header. Apply the recognized best-practice standard for the language (PEP 8 for Python, Google Shell Style Guide for Bash, etc.). List any intentional deviations with justification. An unjustified deviation is a defect.

```
# [Tool Name]
# Purpose: [one sentence]
# Style: [standard name]
# Deviations: [list with justification | None]
```

Apply the standard as a competent practitioner would — type hints, docstrings, proper error handling, idiomatic patterns. Do not quote the standard back; embody it.

---

## Security — Non-Negotiable

**No credentials in code.** API keys, tokens, passwords, and connection strings are always read from environment variables. Never hardcoded. Never in committed `.env` files.

```python
# Correct
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set")
```

Document required environment variables in the tool header.

**No sensitive data in logs.** Log paths, operation names, counts, and status. Never credentials, tokens, or raw request/response bodies that may contain sensitive content. Use log levels correctly — DEBUG for development detail, INFO for normal operation, WARNING for recoverable issues, ERROR for failures.

---

## Execution Safety Guardrails

Triggered by a 2026-07-29 incident: 10 scripts executed file-mutating side effects on bare invocation or `--help` because side-effecting code ran at module top level, or a `main()` with no argparse gate ran unconditionally. Applies to every script regardless of size, purpose, or expected lifespan — **"it's a one-shot / historical / internal-only script" is not an exemption.**

**No side-effecting code at module top level.** Reading config is fine at import time. Opening files for write, deleting, calling network/subprocess, or mutating shared state is not. All of it lives inside a function.

```python
# Wrong — runs on import, runs on `--help`, runs on bare invocation
with open(TARGET, "w") as f:
    f.write(content)

# Correct
def main():
    with open(TARGET, "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
```

**`if __name__ == "__main__":` guard is mandatory** for any script with an entry point — no exceptions, even for a script nobody expects to import.

**Any operation that writes, deletes, overwrites, or otherwise mutates a file, external system, or persistent state requires an explicit opt-in flag** (`--confirm` or `--yes`) before it executes. Bare invocation and `--help` must always be a safe no-op: print what the tool would do (target paths, scope, count of changes) and exit 0 without touching anything.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("--confirm", action="store_true",
                         help="Required to execute. Without it, prints intended effects and exits without changes.")
    args = parser.parse_args()
    if not args.confirm:
        print("Dry run — no files were modified. Pass --confirm to execute.")
        raise SystemExit(0)
    main()
```

Read-only tools (reports, audits, network checks with no writes) are exempt from the `--confirm` gate but still need the `__main__` guard and safe `--help`.

**Validation:** every script in `scripts/` is checked by `scripts/validate_script_safety.py` (part of `/validate`). A script with unguarded top-level writes, or a mutating `main()` reachable without a confirm flag, fails validation and cannot be merged.

---

## Error Handling

- All file operations and external calls handle failure explicitly
- Errors produce a meaningful message to stderr and exit non-zero
- Never silently swallow exceptions

---

## Structure

- **Header:** Every tool begins with name, purpose, usage examples, dependencies, repo path
- **Functions:** One responsibility per function. If it exceeds ~40 lines, split it
- **Naming:** Descriptive, not abbreviated. `load_run` not `lr`. Constants in `UPPER_SNAKE_CASE`
- **Dependencies:** Standard library preferred. Every third-party dependency justified in the plan and pinned in `requirements.txt` or `package.json`
- **CLI:** `--help` supported, long-form flags, required arguments validated with clear failure messages, exit 0 on success / non-zero on failure

---

## Repo Integration

When committing a new tool:

1. Place in `scripts/` unless a subdirectory is justified
2. Update README — Script Reference section with usage examples
3. Update `provenance_log.py OUTPUT_TYPES` if the tool produces a new deliverable type
4. Update calling specs — add to companion specs section of any spec that invokes this tool

---

## Self-Check Before Delivery

```
TOOL SELF-CHECK
□ Plan presented and confirmed before implementation
□ Standards declaration in header — deviations listed or "None"
□ No hardcoded credentials — environment variables used
□ No sensitive data in logs
□ Error handling on all file and external operations
□ Module/file docstring and public function docstrings present
□ CLI uses flags with --help — exit codes meaningful
□ No side-effecting code at module top level — all writes inside functions
□ if __name__ == "__main__": guard present
□ Mutating operations gated behind --confirm/--yes — bare invocation and --help are safe no-ops
□ README update identified
□ Calling specs updated if applicable
□ Dependencies pinned if new packages added
```

---

## Suggested Repo Path
`/config/tool-requirements.md`

---

## Go / Formulary Tools

Formulary tools (in [`github.com/Formulary-Labs`](https://github.com/Formulary-Labs)) are written in Go and follow the same behavioral contract as Python scripts, adapted for Go idioms.

### When to build a Formulary tool (Go)

Build a new Formulary CLI tool (not a Python script) when:
- The function's deterministic execution layer needs standalone binary distribution
- The tool needs to run in CI without a Python environment
- The tool reads or writes gemara-compatible artifacts (CUE/YAML schema)
- Long-term the tool will be used across organizations, not just this portfolio

### Go conventions for Formulary tools

```
# Tool header comment in each Go package
// Package [name] implements [one sentence].
// Style: Effective Go
// Exit codes: from github.com/Formulary-Labs/substrate/exit
```

- Import `github.com/Formulary-Labs/substrate` for exit codes, format types, provenance, and gemara wrappers
- Provenance: call `substrate/provenance.Append(...)` on every file write — same contract as `provenance_log.py`
- Output: support `--format json` (default) and `--format markdown`; never mix them
- Exit codes: `0` = success, `1` = validation error, `2` = usage error, `3` = data error — use `substrate/exit` constants
- Dry-run: `--dry-run` flag required for any tool that writes files; bare invocation must be a safe no-op
- Tests: unit tests in `<pkg>/<pkg>_test.go`; test fixtures in `testdata/`
- Build: standard `go build ./cmd/<tool>/...`; `goreleaser` config in `.goreleaser.yaml`
- CI: `.github/workflows/ci.yaml` — test, build, goreleaser dry-run on push/PR

### Self-check for Go tools

```
□ substrate imported for exit, format, flags, provenance
□ --format json|markdown supported
□ --dry-run flag present; bare invocation is a safe no-op
□ exit codes use substrate/exit constants
□ provenance.Append called on every file write
□ unit tests in <pkg>_test.go with testdata/ fixtures
□ README updated
□ goreleaser config present
□ CI workflow present
```

See [`FORMULARY.md`](FORMULARY.md) for the spec → tool mapping and gemara schema notes.
