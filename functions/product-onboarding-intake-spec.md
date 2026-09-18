---
resource_type: spec
version: "2.0"
domain: compliance
triggers:
  - product_onboarding_kit_ingest
  - new_product_intake
inputs:
  - onboarding_kit_package
outputs:
  - product_pipeline_outputs
  - consolidated_document_update
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
  - data/[PROGRAM]/gemara/[framework]-layer1.yaml
  - runs/[PROGRAM]/latest.json
---

# Product Onboarding Intake Spec

**Version:** 2.0
**Purpose:** Validate and merge a completed product onboarding kit handoff package into a live compliance program. The package is produced externally (by a product team or a separate onboarding workflow) and handed off here for validation against this program's control catalog and integration into the program's data structure.
**Governed by:** `config/constitution.md`

---

## Constitutional Guidance

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

---

## Persona Definition

Compliance analyst receiving a product onboarding package produced outside this repo. Trusts nothing in the package until it is checked against this program's own gemara Layer 1 control catalog and existing records. Merges what passes, flags what does not, and never silently corrects a control ID without logging the correction.

---

## Parameters

```
PRODUCT_NAME:     [name as the package identifies it]
PRODUCT_SLUG:     [lowercase-with-hyphens, matching existing pipeline output folder naming]
PROGRAM_SLUG:     [e.g., iso27001, fedramp-high]
PACKAGE_PATH:     [path to the onboarding kit's output folder]
```

---

## Pass 1 — Validate

Check the package at `PACKAGE_PATH` before touching any program file. The specific required files depend on the program's onboarding kit definition — load from `data/[PROGRAM_SLUG]/onboarding-kit-manifest.md` or equivalent if it exists; otherwise validate against the fields the program's run JSON schema requires for a product entry.

| Check | Action if failed |
|---|---|
| All required files present per the program's kit definition | Reject the package; list missing files; do not proceed to Pass 2 |
| Every control ID in the package exists in `data/[PROGRAM_SLUG]/gemara/[framework]-layer1.yaml` with a matching title | Flag `[CONFLICT — VERIFY]` per mismatch; do not silently correct; list every mismatch for the lead program manager |
| System owner named or explicitly `[OWNER NEEDED]` | Carry forward as-is; add to owner gap list if `[OWNER NEEDED]` |
| No evidence listed as "PENDING" or "TODO" without a corresponding risk entry | Flag as a package defect |
| Package manifest flag list is internally consistent with flags actually found in the package files | Flag any discrepancy |

When validating control IDs, trust the gemara Layer 1 catalog — not the package's own narrative. The catalog is the authoritative source; mismatched titles in the package are findings, not corrections to the catalog.

Narrate:

```
[ONBOARDING-INTAKE] Validating package: [PACKAGE_PATH]
[ONBOARDING-INTAKE] Files present: [n]/[required]
[ONBOARDING-INTAKE] Control ID mismatches: [n]
[ONBOARDING-INTAKE] Owner gaps: [n]
[ONBOARDING-INTAKE] Pass 1 result: [PASS | REJECT — see mismatch list]
```

If Pass 1 rejects, stop. Do not proceed to Pass 2 with missing files or unresolved control ID mismatches.

---

## Pass 2 — Merge

Write validated package contents into the program's existing data structure at `data/[PROGRAM_SLUG]/products/[product-slug]/`. Follow the naming conventions already established for other products in this program.

Do not overwrite an existing product folder without confirming with the lead program manager first — an existing folder means this product may already be mid-onboarding through another path.

Narrate:

```
[ONBOARDING-INTAKE] Merged [n] files into data/[PROGRAM_SLUG]/products/[product-slug]/
```

---

## Pass 3 — Program State Update

- If a consolidated program document exists (e.g., a program appendix compendium or consolidated assessment reference), append a reference to the new product following the existing pattern — do not restate the product's content, link to it.
- For every flag carried from the package (`[OWNER NEEDED]`, `[DATA NEEDED]`, `[CONFLICT — VERIFY]`), file one kanban card in `data/[PROGRAM_SLUG]/kanban.yaml` per distinct flag, assigned to the lead program manager unless the package already names an owner.
- For every control ID mismatch found in Pass 1, append one entry to `memory/[PROGRAM_SLUG]-decisions.log` recording the mismatch, source, and resolution.
- Update `memory/[PROGRAM_SLUG]-memory.md` with a session entry noting the new product's onboarding.
- Append the product entry to `runs/[PROGRAM_SLUG]/latest.json → products[]` using the format defined in `functions/product-evidence-spec.md`.

Narrate:

```
[ONBOARDING-INTAKE] Program state updated
[ONBOARDING-INTAKE] [n] kanban cards filed
[ONBOARDING-INTAKE] [n] decision log entries appended
```

---

## Pass 4 — Quality Gate

Invoke `engine/quality-gate-spec.md`. Spec-specific REJECT triggers:

- Any control ID in the merged files that does not match the gemara Layer 1 catalog
- Any `✓` Evidenced status without a named formal artifact
- Any flag from the source package not carried into kanban or the decision log

If the gate rejects, do not mark the product onboarded. Return findings to whoever produced the onboarding kit for correction — do not correct the package's source content directly in this repo.

---

## Provenance

```bash
python scripts/provenance_log.py write \
  --spec "functions/product-onboarding-intake-spec.md" \
  --output "data/[PROGRAM_SLUG]/products/[product-slug]/" \
  --output-type product_onboarding_package \
  --program "[PROGRAM_SLUG]" \
  --purpose "Product onboarding: [Product Name] — [n] controls | [n] flags carried forward" \
  --reusability artifact \
  --quality-gate pass
```

---

## Companion Specs

- Governed by: `config/constitution.md`
- Reads: `data/[PROGRAM_SLUG]/gemara/[framework]-layer1.yaml`, onboarding kit output package
- Writes: `data/[PROGRAM_SLUG]/products/[product-slug]/`, `data/[PROGRAM_SLUG]/kanban.yaml`, `memory/[PROGRAM_SLUG]-decisions.log`, `memory/[PROGRAM_SLUG]-memory.md`, `runs/[PROGRAM_SLUG]/latest.json`
- Invokes: `engine/quality-gate-spec.md`
- Logged by: `scripts/provenance_log.py` — output_type: `product_onboarding_package`
