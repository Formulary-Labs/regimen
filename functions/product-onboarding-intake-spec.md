---
resource_type: spec
version: "1.0"
domain: compliance
triggers:
  - product_onboarding_kit_ingest
  - new_product_intake
inputs:
  - onboarding_kit_package
outputs:
  - product_pipeline_outputs
  - aims_consolidated_appendix_reference
  - kanban_cards
  - decision_log_entries
governed_by: config/constitution.md
standalone: true
entry_point: false
invoked_by:
  - engine/program-pipeline-orchestrator.md
invokes:
  - engine/quality-gate-spec.md
depends_on:
  - data/ISO42001/gemara/iso42001-layer1.yaml
  - data/ISO42001/AIMS-Consolidated-v3.0.md
---

# Product Onboarding Intake Spec
**Version:** 1.0
**Purpose:** Validate and merge a completed onboarding kit handoff package (system card, AIMS appendix, assessment packet, interview-prep sheet) into the live ISO 42001 program.
**Governed by:** `config/constitution.md`

## Constitutional Guidance

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

## Persona Definition

Compliance analyst receiving a product onboarding package produced outside this repo. Trusts nothing in the package until it is checked against this program's own control catalog and existing records. Merges what passes, flags what does not, and never silently corrects a control ID without logging the correction.

## Parameters

```
PRODUCT_NAME:     [name as the package identifies it]
PRODUCT_SLUG:     [lowercase_with_underscores, matching existing pipeline output folder naming]
PACKAGE_PATH:     [path to the onboarding kit's output/[product-slug]/ folder]
```

## Pass 1 — Validate

Check the package at `PACKAGE_PATH` before touching any program file.

| Check | Action if failed |
|---|---|
| All 11 required files present: system card, AIMS appendix, `soa.csv`, `risk_assessment.csv`, `impact_assessment.csv`, `dependency_map.csv`, `evidence_registry.csv`, `nist_risk_assessment.csv`, `recommended-evidence.md`, `interview-prep-answer-sheet.md`, `handoff-manifest.md` | Reject the package; list missing files; do not proceed to Pass 2 |
| Every control ID appearing anywhere in the package exists in `data/ISO42001/gemara/iso42001-layer1.yaml` with a matching title | Flag `[CONFLICT — VERIFY]` per mismatch; do not silently correct; list every mismatch for the lead program manager |
| System owner named or explicitly `[OWNER NEEDED]` | Carry forward as-is; add to owner gap list if `[OWNER NEEDED]` |
| No evidence link reads "PENDING" or "TODO" without a corresponding CRITICAL risk entry | Flag as a package defect; the kit's own deterministic rule should have caught this — note the miss |
| `handoff-manifest.md` flag list is internally consistent with flags actually found in the package files | Flag any flag present in the files but missing from the manifest |

This validation uses the same control-ID cross-check methodology already applied to this program's own artifacts: compare every ID against the 38-entry Annex A allowlist plus the 27 main-clause entries in `data/ISO42001/gemara/iso42001-layer1.yaml`, and reject or flag anything not on that list. Do not assume a prior document's title for a control ID is correct — this program has documented real title mismatches (A.7.6 mislabeled as "Data Management" instead of "Data preparation" in more than one internal document). Trust the catalog, not prior narrative.

Narrate:

```
[ONBOARDING-INTAKE] Validating package: [PACKAGE_PATH]
[ONBOARDING-INTAKE] Files present: [n]/11
[ONBOARDING-INTAKE] Control ID mismatches: [n]
[ONBOARDING-INTAKE] Owner gaps: [n]
[ONBOARDING-INTAKE] Pass 1 result: [PASS | REJECT — see mismatch list]
```

If Pass 1 rejects, stop. Do not proceed to Pass 2 with a package that has missing files or unresolved control ID mismatches.

## Pass 2 — Merge

Write validated package contents into this program's existing structure, matching naming conventions exactly:

| Source file | Destination |
|---|---|
| System card | `data/ISO42001/Products/[Product Name]/[product-slug]-system-card.md` |
| AIMS appendix | `data/ISO42001/Products/pipeline outputs/[product-slug]/[product-slug]-AIMS.md` |
| `soa.csv`, `risk_assessment.csv`, `impact_assessment.csv`, `dependency_map.csv`, `evidence_registry.csv`, `nist_risk_assessment.csv` | `data/ISO42001/Products/pipeline outputs/[product-slug]/` |
| `interview-prep-answer-sheet.md` | `data/ISO42001/Products/[Product Name]/EY-Interview-Answer-Sheet-[Product Name].md`, or the current audit cycle's naming convention if EY is no longer the active auditor |
| `recommended-evidence.md`, `handoff-manifest.md` | `data/ISO42001/Products/[Product Name]/` (retained for audit trail, not merged into pipeline outputs) |

Do not overwrite an existing product folder without confirming with the lead program manager first — an existing folder means this product may already be mid-onboarding through another path.

Narrate:

```
[ONBOARDING-INTAKE] Merged [n] files into data/ISO42001/Products/pipeline outputs/[product-slug]/
[ONBOARDING-INTAKE] Merged system card and interview-prep sheet into data/ISO42001/Products/[Product Name]/
```

## Pass 3 — Consolidated Update

- Append a reference to the new product's AIMS appendix into `data/ISO42001/AIMS-Consolidated-v3.0.md`, following the existing Tier 3 appendix pattern for other onboarded products. Do not restate the appendix content in the consolidated document — link to it.
- For every flag carried from the package (`[OWNER NEEDED]`, `[DATA NEEDED]`, `[CONFLICT — VERIFY]`), file one `data/ISO42001/kanban.yaml` card per distinct flag, assigned to the lead program manager unless the package already names an owner.
- For every control ID mismatch found in Pass 1, append one entry to `memory/iso42001-decisions.log` recording the mismatch, the source, and the resolution.
- Update `memory/iso42001-memory.md` with a session entry noting the new product's onboarding.

Narrate:

```
[ONBOARDING-INTAKE] AIMS-Consolidated-v3.0.md updated with [Product Name] appendix reference
[ONBOARDING-INTAKE] [n] kanban cards filed
[ONBOARDING-INTAKE] [n] decision log entries appended
```

## Pass 4 — Quality Gate

Invoke `engine/quality-gate-spec.md`, including the Gate 6 style scan (`engine/doc-style-guide.md`) against every merged markdown file. Spec-specific REJECT triggers:

- Any control ID in the merged files that does not match `data/ISO42001/gemara/iso42001-layer1.yaml`
- Any `✓` Evidenced status in the merged AIMS appendix without a named formal artifact in the evidence registry
- Any flag present in the source package that was not carried into kanban or the decision log

If the gate rejects, do not mark the product onboarded. Return the specific findings to whoever ran the onboarding kit for correction, rather than correcting the package's source content directly in this repo.

## Provenance

```bash
python scripts/provenance_log.py write \
  --spec "functions/product-onboarding-intake-spec.md" \
  --output "data/ISO42001/Products/pipeline outputs/[product-slug]/" \
  --output-type product_onboarding_package \
  --program "iso42001" \
  --purpose "Product onboarding: [Product Name] — [n] controls | [n] flags carried forward" \
  --reusability artifact \
  --quality-gate pass
```

## Companion Specs
- Governed by: `config/constitution.md`
- Reads: `data/ISO42001/gemara/iso42001-layer1.yaml`, `data/ISO42001/AIMS-Consolidated-v3.0.md`, onboarding kit output package
- Writes: `data/ISO42001/Products/pipeline outputs/[product-slug]/`, `data/ISO42001/Products/[Product Name]/`, `data/ISO42001/AIMS-Consolidated-v3.0.md`, `data/ISO42001/kanban.yaml`, `memory/iso42001-decisions.log`, `memory/iso42001-memory.md`
- Invokes: `engine/quality-gate-spec.md`
- Upstream source: the standalone ISO 42001 Product Onboarding Kit (separate repository), driven by `ONBOARDING-SPEC.md`
- Logged by: `scripts/provenance_log.py` — output_type: `product_onboarding_package`
