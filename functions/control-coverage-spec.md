---

resource_type: spec
version: "2.0"
domain: compliance
triggers:

- new_program_full_build
- coverage_assessment
- control_gap_analysis
inputs:
- program_skeleton
- framework_reference
- existing_evidence
- soa_draft
outputs:
- control_coverage_matrix
- coverage_gaps
- owner_gaps
- evidence_gaps
governed_by: config/constitution.md
standalone: true
invoked_by:
- functions/program-intake-spec.md
- engine/program-pipeline-orchestrator.md
depends_on:
- functions/program-intake-spec.md
structured_output: true
structured_output_schema: config/schemas/run-output-v2.schema.json

---

# Control Coverage Spec

**Version:** 2.0
**Purpose:** Map framework controls to current evidence and ownership state. Identify coverage gaps, owner gaps, and evidence gaps. Writes results to the run JSON `control_coverage` block consumed by risk register, auditor view, and portfolio health classification.
**Governed by:** `config/constitution.md`

---

## Constitutional Guidance

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

---

## Persona Definition

Senior compliance analyst mapping control frameworks to operational reality — not documentation. Distinguish evidenced, implemented-not-evidenced, and not-implemented. No credit for stated intent. Flag gaps without softening.

---

## Framework Control Sets

When the program skeleton identifies a framework, use the corresponding control set as the basis for the matrix. If the framework is not listed, extract control families from available documentation.


| Framework           | Control basis                                                    | Coverage grouping                                                                         |
| ------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| FedRAMP Moderate    | NIST SP 800-53 Rev 5 Moderate baseline — 325 controls            | Control families (AC, AU, AT, CM, CP, IA, IR, MA, MP, PE, PL, PM, PS, RA, CA, SC, SI, SR) |
| FedRAMP High        | NIST SP 800-53 Rev 5 High baseline — 421 controls                | Control families                                                                          |
| SOC 2 Type II       | AICPA Trust Services Criteria — CC, A, C, PI, P series           | Trust service categories                                                                  |
| ISO 27001:2022      | Annex A controls — 93 controls across 4 themes                   | Organizational, People, Physical, Technological                                           |
| ISO 42001:2023      | Annex A — 38 controls across A.2–A.10; Clauses 4–10 add 32 sub-clause requirements | A.2 Policies, A.3 Internal org, A.4 Resources, A.5 Impact, A.6 Lifecycle, A.7 Data, A.8 Info for parties, A.9 Use, A.10 Third-party |
| IEC 62443-2-1       | Security program requirements mapped to 4 Security Levels (SL 1–4) | 7 domains: Risk, Policies, Organization, Security Awareness, Business Continuity, Incident Response, Security Systems |
| HIPAA Security Rule | 45 CFR Part 164 — Administrative, Physical, Technical safeguards | Safeguard categories                                                                      |
| CMMC Level 2        | NIST SP 800-171 — 110 practices                                  | 14 domains                                                                                |
| Custom / Unknown    | Extract from available materials                                 | As defined in materials                                                                   |

For AIMS and IMS programs: if CDG-generated `soa.csv` files exist in `[PIPELINE_OUTPUT_DIR]/[product]/` (see `functions/compliance-doc-generator-spec.md`), use them as the primary evidence basis for Pass 2 coverage state rather than re-inferring from raw materials. Each `soa.csv` row maps one control to an implementation status and evidence reference — read these before falling back to source document inference.


---

## Formulary Tool

**CLI:** [`titer`](https://github.com/Formulary-Labs/titer) — `github.com/Formulary-Labs/titer`

Handles the deterministic coverage computation layer:
- Loads a gemara `ControlCatalog` and optional SOA CSV / evidence source
- Classifies each control: Evidenced (✓), Implemented/no evidence (~), Gap (✗), N/A
- Computes coverage matrix, gap analysis, owner gaps, evidence gaps per control family
- Outputs JSON (pipeline), Markdown (human review), or CSV (SOA seed)

```bash
titer --catalog data/[PROGRAM]/control-catalog.yaml --soa data/[PROGRAM]/soa.csv --format json
titer --catalog ... --format markdown > coverage-report.md
```

This spec governs framework identification (Pass 1), pipeline write to `runs/[PROGRAM]/latest.json`, schema routing, and integration with `risk-register-spec.md` and `auditor-view-spec.md`. `titer` handles the matrix computation, gap analysis, and stub completion.

> See [`FORMULARY.md`](../FORMULARY.md) for the full integration map.

---

## Processing Instructions

### Pass 1 — Framework Identification

Read the program skeleton. Identify:

- Primary framework(s) — explicit certification or authorization target
- Secondary frameworks — additional standards referenced
- Framework version — note if version is unspecified and flag as `[VERSION UNCONFIRMED]`

Narrate:

```
[COVERAGE] Identified framework: [name] [version]
[COVERAGE] Control set: [n] controls across [n] families/domains
[COVERAGE] Beginning coverage assessment...
```

---

### Pass 2 — Coverage Computation

Call `titer` (see Formulary Tool above). `titer` handles evidence inventory, control classification, matrix assembly, gap analysis, and stub completion. Write the JSON output to the run JSON block defined in the Run JSON Write section below.

Narrate at completion:

```
[COVERAGE] Matrix complete.
[COVERAGE] [n] controls assessed across [n] families
[COVERAGE] Coverage: [n] evidenced ([x]%), [n] implemented/no evidence ([x]%), [n] gaps ([x]%)
[COVERAGE] [n] owner gaps, [n] evidence gaps
[COVERAGE] Handing off to risk register build...
```

---

---

## Coverage % Formula

Used consistently by auditor view, portfolio health, and management system assembler:

```
coverage_pct = (evidenced + implemented_no_evidence) / (total - not_applicable)
```

Apply per family and for totals. Round to nearest whole percent. If denominator is zero, set coverage_pct to null.

---

## Run JSON Write

After Pass 5, write the `control_coverage` block to `runs/[PROGRAM]/latest.json`:

```json
"control_coverage": {
  "source": "this_run",
  "framework": "[framework name and version]",
  "assessment_date": "YYYY-MM-DD",
  "totals": {
    "total": 0,
    "evidenced": 0,
    "implemented_no_evidence": 0,
    "gap": 0,
    "not_applicable": 0
  },
  "families": [
    {
      "name": "AC — Access Control",
      "total": 25,
      "evidenced": 3,
      "implemented_no_evidence": 8,
      "gap": 14,
      "not_applicable": 0,
      "coverage_pct": 44,
      "owner": "[name or OWNER NEEDED]"
    }
  ]
}
```

This block is the return value when invoked from `functions/program-intake-spec.md` Pass 4a. The caller reads `control_coverage` from the updated run JSON.

---

## Provenance

```bash
python scripts/provenance_log.py write \
  --spec "functions/control-coverage-spec.md" \
  --output "runs/[PROGRAM]/latest.json" \
  --output-type run_json \
  --program "[PROGRAM]" \
  --purpose "Control coverage: [framework] — [n] controls | [x]% covered | [n] gaps" \
  --reusability artifact \
  --quality-gate pass
```

---

## Schema Variants

Two schemas exist in the wild. Both are normalised at render time via `_normalize_coverage()` in `scripts/auditor_view_renderer.py` and `scripts/program_dashboard_renderer.py`.


| Schema         | Programs                               | Field                     | Structure                              |
| -------------- | -------------------------------------- | ------------------------- | -------------------------------------- |
| Standard (2.0) | most programs                          | `control_coverage`        | `families[]` + `totals`                |
| Legacy (1.1)   | select legacy programs                 | `control_coverage_matrix` | flat `controls[]` + `coverage_summary` |


New programs **must** use the standard `control_coverage` shape (Standard 2.0). `control_coverage_matrix` is read-only legacy — do not write it for new programs. Both shapes support the same coverage % formula. The `families[].family` key is used for the display name (legacy used `name`; renderers accept both).

---

## Companion Specs
