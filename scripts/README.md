# Scripts — Tools Registry

**Path:** `scripts/`

This file is the authoritative registry of all reusable scripts in the pipeline. Agents must scan this file before writing new code — if a script already covers the needed function, invoke it rather than reimplementing it. Each entry includes purpose, inputs, outputs, and the exact CLI signature.

---

## Shared Utilities

### `utils.py`

Canonical helpers shared across scripts — currently just `resolve_repo_root()`, which had independently drifted into 5 different copies before this module existed. Import from here (`from utils import resolve_repo_root`) rather than redefining it. No CLI, no side effects on import.

---

## Renderers

Produce human-readable HTML or markdown from run/data JSON. Standard library only — no install required unless noted.

---

### `auditor_view_renderer.py`

Generates a read-only, per-program auditor compliance posture dashboard as static HTML. Shows control coverage, risk posture, evidence collection cadence, and continuous monitoring signals. Suitable for sharing with third-party auditors.

| | |
|---|---|
| **Input** | `runs/[PROGRAM]/latest.json` (auto-resolved from repo root) |
| **Output** | `ui/[program]-auditor-[date].html` |
| **Dependencies** | Standard library only |

```
python scripts/auditor_view_renderer.py --program fedramp-high
python scripts/auditor_view_renderer.py --program fedramp-high --lookback 180
python scripts/auditor_view_renderer.py --program fedramp-high --output ui/custom.html
python scripts/auditor_view_renderer.py --program fedramp-high --open
```

---

### `briefing_renderer.py`

Reads a program pipeline run JSON and produces a clean markdown daily briefing digest. Terminal preview available if `rich` is installed.

| | |
|---|---|
| **Input** | `runs/[PROGRAM]/latest.json` |
| **Output** | Markdown file or stdout |
| **Dependencies** | Standard library; `rich` optional for terminal preview |

```
python scripts/briefing_renderer.py --run runs/[PROGRAM]/latest.json
python scripts/briefing_renderer.py --run runs/[PROGRAM]/latest.json --output briefing.md
python scripts/briefing_renderer.py --run runs/[PROGRAM]/latest.json --stdout
```

---

### `dashboard.py`

Reads all `runs/*/latest.json` files and generates a single static HTML dashboard showing multi-program health, decision queues, and flags.

| | |
|---|---|
| **Input** | `runs/*/latest.json` (auto-glob) |
| **Output** | `ui/dashboard.html` |
| **Dependencies** | Standard library only |

```
python scripts/dashboard.py
python scripts/dashboard.py --runs path/to/runs/ --output dashboard.html
python scripts/dashboard.py --open
```

---

### `draft_formatter.py`

Reads a program pipeline run JSON and writes one markdown file per draft communication into an output directory. Files are organized for review, light editing, and sending.

| | |
|---|---|
| **Input** | `runs/[PROGRAM]/latest.json` |
| **Output** | `drafts/[PROGRAM]_[DATE]/` (one `.md` per draft) |
| **Dependencies** | Standard library only |

```
python scripts/draft_formatter.py --run runs/[PROGRAM]/latest.json
python scripts/draft_formatter.py --run runs/[PROGRAM]/latest.json --output drafts/custom/
python scripts/draft_formatter.py --run runs/[PROGRAM]/latest.json --list
```

---

### `fleet_dashboard.py`

Produces a fleet-wide HTML observability dashboard. Covers agent health (status, trust level, error rate, token usage), program performance (health trajectory, finding velocity, evidence coverage), cost tracking, and decision audit trail.

| | |
|---|---|
| **Input** | `data/fleet-metrics.json` (optional; renders empty state if absent) |
| **Output** | `ui/fleet-dashboard.html` |
| **Dependencies** | Standard library only |

```
python scripts/fleet_dashboard.py --output ui/fleet-dashboard.html
python scripts/fleet_dashboard.py --metrics data/fleet-metrics.json --open
python scripts/fleet_dashboard.py --summary
```

---

### `portfolio_renderer.py`

Reads the portfolio state JSON and renders a cross-program HTML dashboard showing health, decisions, blockers, escalations, and cross-program signals.

| | |
|---|---|
| **Input** | `data/portfolio/latest.json` |
| **Output** | `ui/portfolio.html` |
| **Dependencies** | Standard library only |

```
python scripts/portfolio_renderer.py
python scripts/portfolio_renderer.py --portfolio data/portfolio/latest.json
python scripts/portfolio_renderer.py --output ui/portfolio.html --open
```

---

## Validators

CI and integrity checks. All exit non-zero on failure. Run as part of the CI `validate` stage and before modifying protected files.

---

### `integrity_check.py`

Validates that protected system files (`constitution.md`, `program-pipeline-orchestrator.md`, `quality-gate-spec.md`) retain all required headings. Run before and after any LLM-assisted edits to those files. Prints a restoration notice if a heading is missing.

| | |
|---|---|
| **Input** | `config/constitution.md`, `engine/program-pipeline-orchestrator.md`, `engine/quality-gate-spec.md` |
| **Output** | stdout (pass/fail + restoration instructions) |
| **Exit** | `0` = pass, `1` = missing headings |

```
python scripts/integrity_check.py
python scripts/integrity_check.py --file constitution.md
python scripts/integrity_check.py --fix-prompt
```

---

### `spec_coverage.py`

Validates cross-reference integrity across the spec system: every spec in `engine/` and `functions/` has a routing table entry in `session-init-spec.md`, every routing target exists on disk, every orchestrator invocation target exists, and every agent is referenced by at least one routing entry.

| | |
|---|---|
| **Input** | `engine/session-init-spec.md`, `engine/program-pipeline-orchestrator.md`, `agents/`, `functions/` |
| **Output** | stdout (pass/fail) |
| **Exit** | `0` = pass, `1` = broken references |

```
python scripts/spec_coverage.py
python scripts/spec_coverage.py --repo /path/to/compliance
```

---

### `validate_frontmatter.py`

Validates YAML frontmatter in all spec files against the canonical schema. Checks all `.md` files in `engine/`, `functions/`, and `agents/`.

| | |
|---|---|
| **Input** | `config/spec-frontmatter-schema.yaml`, `engine/*.md`, `functions/*.md`, `agents/*.md` |
| **Output** | stdout (pass/fail with field-level errors) |
| **Exit** | `0` = pass, `1` = validation errors |

```
python scripts/validate_frontmatter.py
python scripts/validate_frontmatter.py --strict
```

---

### `validate_schema_drift.py`

Detects misalignment between what renderer scripts read from JSON and what the canonical schemas declare. ERRORs (renderer reads undeclared key) cause a non-zero exit; WARNINGs (schema declares a key no renderer reads) are informational only.

Checks covered:
- `scripts/dashboard.py` → `config/schemas/run-output.schema.json`
- `scripts/auditor_view_renderer.py` → `config/schemas/run-output.schema.json`
- `scripts/portfolio_renderer.py` → `config/schemas/portfolio-state.schema.json`

| | |
|---|---|
| **Input** | `config/schemas/*.schema.json`, renderer scripts |
| **Output** | stdout (ERROR / WARNING lines) |
| **Exit** | `0` = no errors, `1` = schema drift detected |

```
python scripts/validate_schema_drift.py
python scripts/validate_schema_drift.py --repo /path/to/compliance
python scripts/validate_schema_drift.py --renderers scripts/dashboard.py
```

---

### `validate_script_safety.py`

Static check that every script in `scripts/` follows the Execution Safety rules in `config/tool-requirements.md`: no file-mutating call at module top level, `if __name__ == "__main__":` guard present when `main()` is defined, and mutating scripts gated behind a `--confirm`/`--yes` flag or a required argument (either of which makes bare invocation and `--help` safe no-ops). Heuristic AST-based check, not a type-checker — see the module docstring for exactly what write patterns it looks for and the two manually-maintained exemption lists (`READ_ONLY_EXEMPT`, `DESIGNATED_OUTPUT_EXEMPT`) for scripts that are safe by a pattern the static check can't verify on its own.

| | |
|---|---|
| **Input** | `scripts/*.py` |
| **Output** | stdout (PASS/FAIL per script, findings) |
| **Exit** | `0` = all scripts pass, `1` = one or more scripts fail |

```
python scripts/validate_script_safety.py
python scripts/validate_script_safety.py --verbose
python scripts/validate_script_safety.py --dir scripts
```

---

### `validate_all.py`

Unified runner for the 5 system-wide validators above (plus a program's dedicated validator if `--program` is given, e.g. `validate_aims_xlsx.py --all` for `iso42001`). Read-only — invokes each validator as a subprocess and prints the summary table defined in `commands/validate.md`. Prints full raw output for any failing validator unless `--quiet` is passed.

| | |
|---|---|
| **Input** | None (invokes the other validators, which read their own inputs) |
| **Output** | stdout (summary table; raw failing-validator output unless `--quiet`) |
| **Exit** | `0` = all run validators pass, `1` = one or more fail |

```
python scripts/validate_all.py
python scripts/validate_all.py --program iso42001
python scripts/validate_all.py --program 62443
python scripts/validate_all.py --quiet
```

---

### `eval_routing.py`

Regression harness for `engine/session-init-spec.md`'s routing table. Complementary to `spec_coverage.py`, not a replacement: `spec_coverage.py` checks structural link integrity (every routing target exists on disk, `scripts/*.py`/`agents/*.md` targets excluded by design); `eval_routing.py` checks classification behavior against a curated fixture set (sample input → expected Work Pattern row) using a deliberately crude keyword-overlap heuristic, and additionally validates the `scripts/*.py`/`agents/*.md` targets `spec_coverage.py` skips. A heuristic miss on a semantically close fixture is expected, not a failure — the real classification happens in the LLM reading the table, not in this script. Fails on structural problems (missing routing targets, fixtures referencing renamed/removed Work Pattern labels) or if accuracy drops below a 60% floor, which would indicate the table's wording itself has become ambiguous.

| | |
|---|---|
| **Input** | `engine/session-init-spec.md` routing table; fixtures hardcoded in the script |
| **Output** | stdout (accuracy summary, misses, structural findings) |
| **Exit** | `0` = passed, `1` = structural error or accuracy below floor |

```
python scripts/eval_routing.py
python scripts/eval_routing.py --verbose
```

---

## Analysis

Derive structured insights or calendar data from historical run output. Outputs are JSON or `.ics` files consumed by other scripts or agents.

---

### `calendar_exporter.py`

Transforms the `calendar_events` array from a pipeline run JSON into a portable RFC 5545 `.ics` file and/or a human-readable markdown event list. Companion to `functions/calendar-output-spec.md`.

| | |
|---|---|
| **Input** | `runs/[PROGRAM]/latest.json` |
| **Output** | `.ics` file (default) or markdown event list |
| **Dependencies** | Standard library only |

```
python scripts/calendar_exporter.py --run runs/[PROGRAM]/latest.json
python scripts/calendar_exporter.py --run runs/[PROGRAM]/latest.json --output events.ics
python scripts/calendar_exporter.py --run runs/[PROGRAM]/latest.json --markdown
python scripts/calendar_exporter.py --run runs/[PROGRAM]/latest.json --preview
```

---

### `predictive_health.py`

Analyzes historical run data across programs to produce: certification timeline prediction based on current velocity and open gap count, resource contention forecasting, audit readiness scoring with trajectory, and finding velocity trends.

| | |
|---|---|
| **Input** | `runs/` directory (historical `*-run.json` files) or `data/portfolio/latest.json` |
| **Output** | `data/predictions.json` |
| **Dependencies** | Standard library only |

```
python scripts/predictive_health.py --runs-dir runs/ --output data/predictions.json
python scripts/predictive_health.py --program fedramp-high --detail
python scripts/predictive_health.py --portfolio data/portfolio/latest.json
```

---

## ISO 42001 Program Tools

Program-specific tools for `iso42001`. Not general-purpose — invoke only when working in that program's scope.

---

### `validate_aims_xlsx.py`

Validates AIMS xlsx assessment packets against the Layer 1 Gemara control catalog (`data/ISO42001/gemara/iso42001-layer1.yaml`). Catches fabricated and misattributed control IDs before they reach an auditor-facing artifact.

| | |
|---|---|
| **Input** | xlsx file(s) named as positional args, or `--all` to scan all known AIMS xlsx targets |
| **Output** | stdout (pass/fail per file); optional markdown report via `--report` |
| **Dependencies** | `openpyxl` |

```
python scripts/validate_aims_xlsx.py --all
python scripts/validate_aims_xlsx.py "data/ISO42001/Products/pipeline outputs/aap_chatbot/aap_chatbot_aims_assessment.xlsx"
python scripts/validate_aims_xlsx.py --all --report data/ISO42001/Resources/xlsx-validation-report.md
```

---

### `generate_iso42001_control_coverage_report_csv.py`

Emits a single CSV rollup for `iso42001`: enterprise coverage, platform map, products, control rows, and risks. Reads `runs/iso42001/latest.json` and product `control-matrix.md` files under `data/ISO42001/`. Does not read Hyperproof directly — aligns with whatever `control_coverage.source` in `latest.json` currently states.

| | |
|---|---|
| **Input** | `runs/iso42001/latest.json`, `data/ISO42001/**/control-matrix.md` |
| **Output** | CSV (stdout or `-o` path) |
| **Dependencies** | Standard library only |

```
python scripts/generate_iso42001_control_coverage_report_csv.py -o coverage.csv
python scripts/generate_iso42001_control_coverage_report_csv.py --run-json runs/iso42001/latest.json --platform-map path/to/map.yaml
```

---

### `iso42001_ingest_standard_pdf.py`

Indexes the licensed ISO/IEC 42001:2023 PDF for the `iso42001` program — produces the derivative clause/Annex index used to pin normative wording against the Layer 1 catalog. See `memory/iso42001-decisions.log` 2026-05-12 for the ingest provenance record (SHA-256 pin).

| | |
|---|---|
| **Input** | Licensed PDF (`--pdf`, path not committed to the repo) |
| **Output** | `data/ISO42001/references/ISO-IEC-42001-2023-index.json` and an ingestion report |
| **Dependencies** | PDF-parsing library (see script imports) |

```
python scripts/iso42001_ingest_standard_pdf.py --pdf /path/to/ISO_IEC_42001_2023.pdf
```

---

### `build_enterprise_assessment.py`

Builds the enterprise-tier AIMS Assessment Packet XLSX: all 70 ISO 42001 controls at the corporate tier, product applicability matrix (38 Annex A × 8 products), enterprise impact assessment, evidence coverage summary, and version history. No CLI arguments — hardcoded output path.

| | |
|---|---|
| **Input** | `data/ISO42001/gemara/iso42001-layer1.yaml` and program artifacts (see script) |
| **Output** | `data/ISO42001/Planning/AIMS-Enterprise-Assessment.xlsx` (overwrites) |
| **Dependencies** | `openpyxl` |

```
python scripts/build_enterprise_assessment.py --confirm
```

Requires `--confirm` to run; bare invocation or `--help` prints what it would do and exits without touching any files.

---

### `rebuild_xlsx.py`

Rebuilds all per-product AIMS assessment XLSX files from corrected CSV data in `data/ISO42001/Products/pipeline outputs/[product]/`. Applies Red Hat brand formatting, conditional risk-level coloring, auto-filters, and freeze panes; drops the Evaluation Procedures sheet. No CLI arguments — iterates all known products and overwrites their xlsx files.

| | |
|---|---|
| **Input** | `data/ISO42001/Products/pipeline outputs/[product]/*.csv` |
| **Output** | `data/ISO42001/Products/pipeline outputs/[product]/[product]_aims_assessment.xlsx` (overwrites, one per product) |
| **Dependencies** | `openpyxl` |

```
python scripts/rebuild_xlsx.py --confirm
```

Requires `--confirm` to run; bare invocation or `--help` prints what it would do and exits without touching any files. Deterministic given unchanged CSV inputs.

---

### `remediate_pipeline_outputs.py`, `remediate_soa.py`, `aims_v25_auditor_cleanup.py`, `aims_v25_pass_b.py`

One-shot, hardcoded-path remediation scripts written for specific historical correction passes (see `memory/iso42001-decisions.log` Sessions 19, 30 for `remediate_pipeline_outputs.py`'s context; SOA remediation and the AIMS v2.5 auditor cleanup pass for the others). Each targets a specific file or directory by hardcoded path and is **not safe to re-run generically** — several read from `~/Downloads/` reference files that will not exist on another machine, and all mutate files in place. Each requires a `--confirm` flag to execute; bare invocation or `--help` prints what it would do and exits without touching any files.

| Script | Targets | Depends on |
|---|---|---|
| `remediate_pipeline_outputs.py` | `data/ISO42001/Products/pipeline outputs/*` CSVs + xlsx rebuild | NIST AI RMF playbook CSV (external path, see script) |
| `remediate_soa.py` | Per-product `soa.csv` files (9 AI products) | Audited RHOAI SOA xlsx (external path, see script) |
| `aims_v25_auditor_cleanup.py` | `data/ISO42001/AIMS-Consolidated-v2.5.md` | None — self-contained regex passes |
| `aims_v25_pass_b.py` | `data/ISO42001/AIMS-Consolidated-v2.5.md` | None — self-contained string replacements |

Treat these as historical record of how a past correction was made, not as reusable tools. If a similar correction is needed again, write a new script rather than re-running one of these against current content — the hardcoded replacement strings are specific to the document state at the time they were written.

---

## IEC 62443 Guide Maintenance

Tools for the `62443` program's implementation guide documents in `data/62443/Guides/`.

---

### `test_guide_urls.py`

Extracts and HEAD-tests every URL in the three IEC 62443-4-2 implementation guides. Outputs a markdown report grouped by file with status codes and a broken-link summary. Makes live network requests — expect some `403`/timeout noise from sites that block automated HEAD requests even when the link is fine in a browser.

| | |
|---|---|
| **Input** | `data/62443/Guides/*.md` (hardcoded list — MicroShift, OpenShift, RHEL guides) |
| **Output** | Markdown report to stdout |
| **Dependencies** | Standard library only (`urllib`) |

```
python scripts/test_guide_urls.py > data/62443/Guides/url-audit-report.md
```

---

### `fix_guide_urls.py`

Applies a fixed set of known URL corrections to the same three guides (stigviewer.com version bumps, MicroShift/OCP doc version corrections, and a few miscellaneous fixes). No CLI arguments — runs all fix categories immediately and writes changes in place.

| | |
|---|---|
| **Input** | `data/62443/Guides/*.md` (same hardcoded list as `test_guide_urls.py`) |
| **Output** | In-place edits to the guide files; prints a per-file change summary |
| **Dependencies** | Standard library only |

```
python scripts/fix_guide_urls.py --confirm
```

Requires `--confirm` to run; bare invocation or `--help` prints what it would do and exits without touching any files. Run `test_guide_urls.py` first to see what's actually broken before applying fixes.

---

### `strip_microshift_internals.py`

Removes internal process language (determination lines, header metadata, gap-section framing) from the MicroShift 4.21 IEC 62443 implementation guide so it reads as a clean external-facing document. Hardcoded to one file.

| | |
|---|---|
| **Input** | `data/62443/Guides/MicroShift 4.21 Implementation Guide for ISA_IEC 62443-4-2 SL-2.md` |
| **Output** | In-place edit; prints a per-pass change count |
| **Dependencies** | Standard library only |

```
python scripts/strip_microshift_internals.py --confirm
```

Requires `--confirm` to run; bare invocation or `--help` prints what it would do and exits without touching any files.

---

## Reporting & Import Utilities

---

### `generate_hyperproof_import.py`

Generates a Hyperproof-importable CSV for ISO 42001 product-level evidence requests, derived from a reference evidence-request xlsx (amber-highlighted rows = product-level controls; `A.4.6` excluded per program decision). Reads from and writes to `~/Downloads/` by convention — this is a personal-workflow tool, not a repo-relative one.

| | |
|---|---|
| **Input** | `~/Downloads/Reference Red Hat ISO 42001 Evidence Request List.xlsx` (hardcoded path, not in repo) |
| **Output** | `~/Downloads/hyperproof-42001-product-requests-import.csv` |
| **Dependencies** | `openpyxl` |

```
python scripts/generate_hyperproof_import.py --confirm
```

Requires `--confirm` to run; bare invocation or `--help` prints what it would do and exits without touching any files.

---

### `build_pages.py`

Assembles the GitLab Pages `public/` directory for the compliance portfolio from the `runs/`, `ui/`, and `scripts/` directories — the publish step for any hosted dashboards.

| | |
|---|---|
| **Input** | `runs/`, `ui/`, `scripts/` (paths overridable) |
| **Output** | `public/` (GitLab Pages artifact directory) |
| **Dependencies** | Standard library only |

```
python scripts/build_pages.py
python scripts/build_pages.py --output public/ --skip-regen
```

---

### `kanban_renderer.py`

Generates a static HTML kanban board from `data/[program]/kanban.yaml`. Companion renderer to `functions/kanban-spec.md`.

| | |
|---|---|
| **Input** | `data/[program]/kanban.yaml` |
| **Output** | `ui/[program]-kanban-[date].html` |
| **Dependencies** | Standard library only |

```
python scripts/kanban_renderer.py --program fedramp-high
python scripts/kanban_renderer.py --all
python scripts/kanban_renderer.py --program fedramp-high --open
```

---

### `program_dashboard_renderer.py`

Generates a 62443-style, light-theme, single-program HTML dashboard from a program's run JSON. Distinct from `dashboard.py` (multi-program) and `portfolio_renderer.py` (portfolio-level) — this is the per-program detail view.

| | |
|---|---|
| **Input** | `runs/[program]/latest.json` |
| **Output** | `runs/[program]/dashboard.html` (default) |
| **Dependencies** | Standard library only |

```
python scripts/program_dashboard_renderer.py --program fedramp-high
python scripts/program_dashboard_renderer.py --program fedramp-high --output ui/custom.html
```

---

## Logging

Append-only audit infrastructure. Agents must write to the provenance log via this script — never write to `logs/provenance.jsonl` directly.

---

### `provenance_log.py`

Append-only JSONL log of all deliverables produced by the pipeline. Tracks what was created, when, why, for which program, and whether the artifact is reusable. Supports querying by program, spec, reusability class, date, or output type.

| | |
|---|---|
| **Input** | CLI arguments |
| **Output** | `logs/provenance.jsonl` (append) or stdout (query/summary/tail) |
| **Dependencies** | Standard library only |
| **Constraint** | Never write to `logs/provenance.jsonl` directly — always use this script |

```
# Append an entry
python scripts/provenance_log.py write \
    --spec "program-intake-spec.md" \
    --output "runs/fedramp/2025-03-01-run.json" \
    --program "fedramp_high" \
    --purpose "Initial onboarding" \
    --reusability template

# Query
python scripts/provenance_log.py query --program fedramp_high
python scripts/provenance_log.py query --reusability template
python scripts/provenance_log.py query --since 2025-01-01
python scripts/provenance_log.py query --output-type report

# Summary and tail
python scripts/provenance_log.py summary
python scripts/provenance_log.py tail --n 10
```
