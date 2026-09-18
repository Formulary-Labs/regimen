---
resource_type: spec
version: "2.0"
domain: compliance
triggers:
  - product_onboarding
  - product_evidence_extraction
  - repo_audit_intake
inputs:
  - product_name
  - repo_urls
  - framework_control_subset
  - existing_program_materials
outputs:
  - product_profile
  - product_control_matrix
  - evidence_gaps
  - product_data_stub
governed_by: config/constitution.md
standalone: true
entry_point: false
invoked_by:
  - engine/program-pipeline-orchestrator.md
  - functions/program-intake-spec.md
invokes: []
depends_on:
  - runs/[PROGRAM]/latest.json
  - functions/control-coverage-spec.md
structured_output: true
structured_output_schema: config/schemas/run-output-v2.schema.json
---

# Product Evidence Spec

**Version:** 2.0
**Purpose:** Extract framework-relevant compliance signals from a product's source repository and available materials. Produce a product profile, an annotated control matrix, and an evidence gap list — enabling evidence-building before product team contact. Designed for the empty-product-folder problem: generate a meaningful stub from what exists publicly or internally before pinging engineering.
**Governed by:** `config/constitution.md`

---

## Constitutional Guidance

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

---

## Persona Definition

Senior compliance analyst extracting evidence signals from engineering artifacts. Distinguish between what the repo *demonstrates* (implementation exists), what it *claims* (documented intent), and what it *cannot tell us* (requires product team). No credit for intent stated only in documentation without implementation signals. Flag gaps without softening.

---

## Confidence Vocabulary

| Tag | Meaning |
|---|---|
| `[REPO SIGNAL]` | Observed in public repo (README, code, CI config, architecture docs) — not a formal compliance artifact |
| `[INFERRED]` | Logical conclusion from observed signals — not explicitly stated |
| `[DATA NEEDED]` | Cannot be determined from repo materials — requires product team input |
| `[OWNER NEEDED]` | Responsible party not identified in available materials |
| `[CONFLICT — VERIFY]` | Contradictory information found across sources |
| `[FORMAL ARTIFACT]` | Formal compliance document (audit report, published system card, signed policy) |

---

## Coverage Status States

Inherit from `functions/control-coverage-spec.md`:

| Status | Symbol | Meaning |
|---|---|---|
| Evidenced | ✓ | Formal artifact exists and demonstrates implementation |
| Implemented — no evidence | ~ | Implementation observable in repo signals; no formal audit artifact |
| Gap | ✗ | Not implemented or no information available |
| Not applicable | N/A | Explicitly scoped out or not relevant to this product |

**Important:** Repo README signals alone never produce `✓`. Maximum confidence from repo scan is `~`. Only formal artifacts (published system cards, audit reports, signed policies, independent test results) produce `✓`.

---

## Parameters

```
PRODUCT_NAME:     [product name as it appears in the program charter]
PROGRAM_SLUG:     [e.g., iso27001, fedramp-high]
FRAMEWORK:        [e.g., ISO/IEC 42001:2023, NIST SP 800-53 Rev 5, SOC 2 TSC]
REPO_URLS:        [list of repo URLs scanned]
CONTROL_SUBSET:   [list of control IDs applicable to this product — default: all controls in program scope]
SCAN_DATE:        [YYYY-MM-DD]
ANALYST:          [agent | name]
```

---

## Processing Instructions

### Pass 1 — Product Classification

Identify the product's system type from repo materials using the target framework's taxonomy or classification guidance (load from gemara Layer 1 for this program). Record:

1. **Primary function** — what the system does for users
2. **System type** — as defined by the target framework's product classification
3. **Deployment context** — SaaS, on-prem, embedded library, API service, container workload
4. **Foundational role** — does this product serve as infrastructure for other products in the program scope? If yes, note which products depend on it.
5. **Third-party dependencies** — which external services, vendors, or providers does the product use that may be in scope for the framework?

Narrate:

```
[PRODUCT-EVIDENCE] Product: [name]
[PRODUCT-EVIDENCE] System type: [type per framework classification]
[PRODUCT-EVIDENCE] Deployment context: [context]
[PRODUCT-EVIDENCE] Foundational dependency role: [yes/no — which products depend on this]
[PRODUCT-EVIDENCE] Third-party dependencies in scope: [list]
[PRODUCT-EVIDENCE] Pass 1 complete. Beginning repo signal extraction...
```

---

### Pass 2 — Repo Signal Extraction

Load the target framework's control catalog from the gemara Layer 1 artifact for this program (`data/[PROGRAM]/gemara/[framework]-layer1.yaml` or equivalent). For each control family in the applicable subset, scan all provided repo URLs and extract signals relevant to that family.

For each signal found, record:
- Control ID it maps to (from the gemara catalog — trust the catalog, not prior narrative)
- Repository source and specific location (README section, config file, doc page)
- What it demonstrates (not what it claims)
- Confidence tag

Narrate progress:

```
[PRODUCT-EVIDENCE] Scanning [repo-name]...
[PRODUCT-EVIDENCE] [Family/Domain] signals found: [n] — [brief description]
...
```

---

### Pass 3 — Control Matrix Assembly

Produce the control matrix at the individual control level for the applicable subset:

```
## Product Control Matrix — [FRAMEWORK]
Product: [PRODUCT_NAME]
Scan date: [DATE]
Repos scanned: [list]
Materials basis: Repo READMEs, architecture docs, CI/CD configs, published API specs

| Control ID | Control Name | Status | Evidence / Signal | Source | Notes |
|---|---|---|---|---|---|
```

Status rationale column required for any `✗` (explain why there is no signal) and any `N/A` (explain scope exclusion).

After the matrix, summarize:

```
[PRODUCT-EVIDENCE] Matrix complete.
[PRODUCT-EVIDENCE] [n] controls assessed
[PRODUCT-EVIDENCE] [n] implemented/no-evidence ([x]%), [n] gaps ([x]%), [n] N/A
[PRODUCT-EVIDENCE] All repo-sourced signals classified [REPO SIGNAL] — formal artifacts needed to reach Evidenced status
```

---

### Pass 4 — Evidence Gap Analysis

**1. Formal artifact gaps** — controls at `~` that need a formal artifact to reach `✓`:

```
## Formal Artifact Gaps
Controls currently Implemented-no-evidence. Formal artifacts needed for audit readiness.

| Control ID | What repo shows | Formal artifact needed | Effort estimate | Priority |
|---|---|---|---|---|
```

Priority: High = auditor will sample this; Medium = may be sampled; Low = administrative, low audit visibility.

**2. Data needed from product team** — controls at `✗` where signal is not in the repo:

```
## Data Needed from Product Team
Controls with no repo signal. Questions for the product team.

| Control ID | Control Name | Question for product team | Why it matters |
|---|---|---|---|
```

**3. Owner gaps**:

```
## Owner Gaps
Controls or functions with no identified owner from repo materials.

| Area | Why ownership matters | Suggested owner type |
|---|---|---|
```

---

### Pass 5 — Product Profile Assembly

Produce `data/[PROGRAM]/products/[product-slug]/product-profile.md` with these sections:

1. **Product Summary** — one-paragraph plain-language description for an auditor unfamiliar with the product
2. **System Classification** — type, deployment context, foundational role
3. **Architecture Overview** — key components, external dependencies, data flows (narrative)
4. **Framework Applicability Notes** — which controls are most relevant, which are inherited from program-level policies vs. product-specific
5. **Known Evidence Artifacts** — list of any formal artifacts found or referenced in repo materials
6. **Open Questions** — explicit list of items requiring product team input before audit prep
7. **Repo Sources** — list of repos scanned with last-updated dates

---

### Pass 6 — Run JSON Write

After Pass 5, append to the program's `runs/[PROGRAM]/latest.json` under a `products` array (create the key if absent):

```json
"products": [
  {
    "name": "[PRODUCT_NAME]",
    "slug": "[product-slug]",
    "status": "repo-scan-complete",
    "scan_date": "YYYY-MM-DD",
    "repos_scanned": ["url1", "url2"],
    "system_owner": "[name or OWNER NEEDED]",
    "system_type": "[type per framework classification]",
    "deployment_context": "[context]",
    "foundational_for": ["product1", "product2"],
    "control_matrix_path": "data/[PROGRAM]/products/[product-slug]/control-matrix.md",
    "product_profile_path": "data/[PROGRAM]/products/[product-slug]/product-profile.md",
    "evidence_gaps_path": "data/[PROGRAM]/products/[product-slug]/evidence-gaps.md",
    "control_summary": {
      "total_controls_assessed": 0,
      "implemented_no_evidence": 0,
      "gap": 0,
      "not_applicable": 0,
      "evidenced": 0
    },
    "flags": ["[OWNER NEEDED]", "[REPO SIGNAL — formal artifacts needed]"]
  }
]
```

---

## Provenance

```bash
python3 scripts/provenance_log.py write \
  --spec "functions/product-evidence-spec.md" \
  --output "data/[PROGRAM]/products/[product-slug]/product-profile.md" \
  --output-type product_evidence \
  --program "[PROGRAM]" \
  --purpose "Product evidence extraction: [PRODUCT] — [n] controls | repo scan | [n] gaps" \
  --reusability artifact \
  --quality-gate pass
```

---

## Quality Gate

Invoke `engine/quality-gate-spec.md`. Spec-specific REJECT triggers:

- Any control classified `✓` (Evidenced) from repo README alone — maximum from repo scan is `~`
- Any repo-sourced signal missing `[REPO SIGNAL]` tag
- Any inference missing `[INFERRED]` tag
- Any `✗` control without a corresponding entry in Pass 4 Section 2 (data needed from product team)
- Product profile missing a plain-language summary suitable for an auditor with no product context
- Run JSON stub not written when program run JSON exists

---

## Companion Specs

- Governed by: `config/constitution.md`
- Feeds: `functions/control-coverage-spec.md` (program-level rollup), `functions/risk-register-spec.md`
- Reads: Repo materials (public), `runs/[PROGRAM]/latest.json`
- Writes: `data/[PROGRAM]/products/[product-slug]/`, `runs/[PROGRAM]/latest.json → products[]`
- Logged by: `scripts/provenance_log.py` — output_type: `product_evidence`
