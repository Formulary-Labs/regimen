---
resource_type: spec
version: "1.1"
domain: compliance
triggers:
  - management_system_assembly
  - portfolio_assembly
  - certification_readiness
  - annual_review
inputs:
  - documentation_policy_yaml
  - governance_charter_yaml
  - compliance_artifacts_dir
  - reference_standard_docs
outputs:
  - unified_management_system_md
governed_by: config/constitution.md
standalone: true
entry_point: true
invoked_by:
  - engine/program-pipeline-orchestrator.md
invokes:
  - engine/quality-gate-spec.md
depends_on:
  - runs/[PROGRAM]/latest.json
  - data/[PROGRAM]/
---

# Management System Assembler Spec
**Version:** 1.1
**Purpose:** LLM-native assembly and review of a unified ISMS, AIMS, CSMS, or IMS document from program artifacts. Post-processing layer over the deterministic pipeline (`compliance-doc-generator-spec.md`) — reviews, summarizes, flags, and narrates pipeline outputs into an auditor-grade document. No external rendering dependencies — the agent writes the document directly.
**Governed by:** `config/constitution.md`

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here. Organization Neutrality: use `the Organization`, `the Program`, `the Management Team` unless `BRANDED_OUTPUT: yes`.]

## Persona
Principal Compliance Architect. Synthesizes artifacts and governance intent into Annex SL-structured management system documentation. Every clause traceable to a source artifact. Gaps named, nothing padded.

## Parameters
```
PROGRAM:              [slug]
STANDARD:             [iso27001 | iso42001 | iec62443 | integrated | auto-detect]
OUTPUT_NAME:          [document display name]
REVIEW_CADENCE:       [annual | biannual | quarterly — default: annual]
APPLICABILITY:        [scope statement]
BRANDED_OUTPUT:       [yes | no — default: no]
ORG_NAME:             [required only if BRANDED_OUTPUT: yes]
REVIEW_MODE:          [full_assembly | delta_review | section_update — default: full_assembly]
EXISTING_DOC_PATH:    [path to existing document — required for delta_review and section_update]
SECTION_TARGET:       [clause number, e.g. "8" or "6.2" — required only for section_update]
MODEL_TIER:           [opus | sonnet | compact — default: opus]
PIPELINE_OUTPUT_DIR:  [path to CDG output root — default: data/[PROGRAM]/Products/pipeline outputs/]
```

### REVIEW_MODE behavior
```
full_assembly  — execute all 5 passes; generate all Clauses 4–10 from scratch
delta_review   — Pass 2 loads EXISTING_DOC_PATH and extracts its version control table;
                 compare each clause's source data timestamp against run JSON last_updated;
                 Pass 3 skips clauses with no source data change since EXISTING_DOC_PATH version;
                 rewrites only changed clauses; preserves unchanged text verbatim
section_update — Pass 2 loads EXISTING_DOC_PATH; Pass 3 rewrites SECTION_TARGET clause only;
                 all other clauses copied verbatim from the existing document
```

### MODEL_TIER behavior
```
opus    — full [MSA] narration at each step; all intermediate summaries; full 6-gate quality gate
sonnet  — checkpoint narration only ([MSA] Pass N complete — N items); structural + constitutional gate only
compact — progress prefix lines only, no prose narration; skip per-spec quality gate invocation;
          rely on orchestrator Phase 6 gate for final validation
```

---

## Formulary Tool

**CLI:** [`compound`](https://github.com/Formulary-Labs/compound) — `github.com/Formulary-Labs/compound`

Handles the deterministic Annex SL document scaffold layer:
- Generates a fully-structured ISMS/AIMS/CSMS document with all mandatory Annex SL clauses
- Populates deterministic fields (scope, dates, framework, control references) from program state
- Marks narrative-required sections with `[DATA NEEDED: narrative]` for LLM completion
- Supports ISO 27001, ISO 42001, and IEC 62443 management system types

```bash
compound --run runs/[PROGRAM]/latest.json --type iso42001 --out data/[PROGRAM]/AIMS-v1-scaffold.md
compound --run ... --dry-run   # preview structure only
```

This spec governs the full assembly workflow: multi-pass narrative generation (Passes 2–5), source synthesis from CDG outputs, quality gate, and reviewer protocol. `compound` handles the deterministic scaffold (Clauses 4–10 structure); this spec handles all narrative and review passes.

> See [`FORMULARY.md`](../FORMULARY.md) for the full integration map.

---

## Pass 1 — Archetype and Standard Detection

| Archetype | Signal | Annex coverage |
|---|---|---|
| ISMS | ISO 27001 present, no AI/OT standard | Annex A — 93 controls, 4 themes |
| AIMS | ISO 42001, NIST AI RMF, or EU AI Act present | Annex A — 38 controls, A.2–A.10 |
| CSMS | IEC 62443-2-1 present | 7 program domains, SL-T based |
| IMS | Multiple standards present | Merge structures; flag single-standard clauses as partial coverage |

If `STANDARD: auto-detect` and detection is ambiguous, ask lead program manager to confirm before continuing.

Clause map: Annex SL clauses 4–10 for all archetypes. AIMS additionally maps ISO 42001:2023 Annex A (38 controls, A.2–A.10). ISMS additionally maps ISO 27001:2022 Annex A (93 controls, 4 themes). CSMS additionally maps IEC 62443-2-1 (7 domains, 4 SL tiers). IMS: merge structures, note which standard each sub-section satisfies, flag single-standard clauses as partial coverage. `functions/control-coverage-spec.md`'s `control_coverage` block is the authoritative source for all Annex mappings — do not re-derive from SOA when it is present.

Metadata block (written to document header):

| Field | Value |
|---|---|
| Document Name | `[OUTPUT_NAME]` |
| Version | [n — 1.0 on full_assembly, incremented on delta_review/section_update] |
| Date | today |
| Next Review | today + `[REVIEW_CADENCE]` |
| Applicability | `[APPLICABILITY]` |
| Reference | detected standards |
| Status | Draft |

Narrate: `[MSA] Archetype: [type] | Standards: [list] | Clauses: 4–10 | Proceeding to ingestion...`

---

## Pass 2 — Artifact Ingestion

Load each source. For missing sources, state affected clauses before proceeding. If `REVIEW_MODE: delta_review` or `section_update`, first load `EXISTING_DOC_PATH` and extract its version control table before loading other sources — this establishes the baseline for the diff.

| Source | Path | Extracts |
|---|---|---|
| Program run state | `runs/[PROGRAM]/latest.json` | phase, health, risk summary, coverage |
| Risk register | `latest.json → risk_register` | open items by severity, POA&M, closure rate |
| Control coverage | `latest.json → control_coverage` | coverage %, gaps by family |
| Evidence calendar | `latest.json → evidence_calendar` | window status |
| Program memory | `memory/[PROGRAM]-memory.md` | decisions, governance notes, deferred items |
| SOA (fallback) | `data/[PROGRAM]/soa.*` | controls in scope, applicability rationale — use only if CDG pipeline outputs below are absent |
| Governance charter | `governance_charter_yaml` | roles, board, accountability |
| Documentation policy | `documentation_policy_yaml` | formatting rules, cadence |
| Impact assessment (fallback) | `data/[PROGRAM]/impact_assessment.*` | criticality, data classification — use only if CDG pipeline outputs below are absent |
| Provenance log | `logs/provenance.jsonl` (filtered) | monitoring cadence |
| CDG SoA (per product) | `[PIPELINE_OUTPUT_DIR]/[product]/soa.csv` | per-product control status, applicability, evidence refs |
| CDG risk assessment | `[PIPELINE_OUTPUT_DIR]/[product]/risk_assessment.csv` | per-product risk posture, scores, treatment |
| CDG impact assessment | `[PIPELINE_OUTPUT_DIR]/[product]/impact_assessment.csv` | per-product criticality, goals, archetype |
| CDG compliance context | `[PIPELINE_OUTPUT_DIR]/[product]/[product]-CCD.md` | per-product LLM-optimized compliance narrative |
| CDG evidence registry | `[PIPELINE_OUTPUT_DIR]/[product]/evidence_registry.csv` | per-product evidence artifacts and status |
| CDG NIST risk (AIMS) | `[PIPELINE_OUTPUT_DIR]/[product]/nist_risk_assessment.csv` | NIST AI RMF risk profile |
| Collective risk register | `[PIPELINE_OUTPUT_DIR]/collective_risk_register.csv` | cross-product risk aggregation |

`[PIPELINE_OUTPUT_DIR]` defaults to `data/[PROGRAM]/Products/pipeline outputs/` (see `functions/compliance-doc-generator-spec.md` Output Path Convention). CDG pipeline outputs take precedence over raw source materials for all fields they cover — do not re-derive control status, risk scores, or impact classification from YAML when CDG outputs are present.

Missing source format: `[MSA] Source not found: [name] at [path] — Affected clauses: [list] → [DATA NEEDED]`

**Compute for Clause 8.2:**
- Total systems in scope — SOA or impact assessment
- Risk profile — Critical / High / Medium / Low open item counts
- Criticality tally — systems by tier
- Control coverage % — overall and by family
- Evidence completion rate — current period
- Monitoring cadence — average days between runs from provenance log

**Delta computation (REVIEW_MODE: delta_review only):** For each clause, compare the source data's last-modified timestamp (run JSON `last_updated`, or file mtime for CDG outputs) against the version recorded in `EXISTING_DOC_PATH`'s version control table. Mark each clause `changed` or `unchanged`. Pass 3 regenerates only `changed` clauses.

---

## Pass 3 — Document Assembly

Write each clause section in full before advancing. Complete or write `[DATA NEEDED: source description]` — no silent gaps.

Apply `REVIEW_MODE`: `full_assembly` writes every clause below. `delta_review` writes only clauses marked `changed` in Pass 2 and copies all other clause text verbatim from `EXISTING_DOC_PATH`. `section_update` writes only `SECTION_TARGET` and copies everything else verbatim.

Apply `MODEL_TIER` narration rules (see Parameters) throughout this pass.

### Document Header
```markdown
# [OUTPUT_NAME]

| Field | Value |
|---|---|
| Document Name | [OUTPUT_NAME] |
| Version | [n] |
| Date | [today] |
| Next Review | [computed] |
| Applicability | [APPLICABILITY] |
| Reference | [standards] |
| Status | Draft |
```

### Clause 4 — Context
- **4.1** Internal/external factors from charter and memory; AI context if AIMS
- **4.2** Stakeholders and requirements from charter roles and compliance obligations
- **4.3** `[APPLICABILITY]` verbatim + SOA boundary conditions and exclusions
- **4.4** System structure referencing control coverage matrix and SOA as control inventory

### Clause 5 — Leadership
- **5.1** Governance board/sponsor role from charter; review cadence, resource allocation, policy ownership
- **5.2** Policy from charter and documentation policy — must include: scope, objectives, commitment to improvement, commitment to requirements
- **5.3** Roles table from charter YAML:

| Role | Responsibilities | Authority |
|---|---|---|
| [from charter] | [responsibilities] | [authority level] |

### Clause 6 — Planning
- **6.1** Risk assessment approach and treatment options from risk register; reference as live record, do not duplicate individual items
- **6.2** Objectives table:

| Objective | Measure | Target | Current | Source |
|---|---|---|---|---|
| Control coverage | % evidenced | [target] | [from run JSON] | control_coverage |
| POA&M closure | % closed/period | [target] | [from risk register] | risk_register |

Add program-specific objectives from memory if present.

### Clause 7 — Support
- **7.1** Resources — tooling, personnel, review processes from charter
- **7.2** Competence — role competence requirements from charter
- **7.3** Awareness — `[DATA NEEDED: awareness program documentation]` if no source covers this
- **7.4** Communication — internal/external processes; draw from `drafts/` if available
- **7.5** Document inventory:

| Document | Location | Owner | Review Cadence |
|---|---|---|---|
| Statement of Applicability | `data/[PROGRAM]/soa` | [from charter] | Annual |
| Risk Register | `runs/[PROGRAM]/latest.json` | [from charter] | Continuous |
| Control Coverage Matrix | `runs/[PROGRAM]/latest.json` | [from charter] | Per pipeline run |
| Evidence Calendar | `runs/[PROGRAM]/latest.json` | [from charter] | Per pipeline run |
| [additional artifacts from Pass 2] | | | |

### Clause 8 — Operation
- **8.1** Pipeline cadence from provenance log as operational heartbeat
- **8.2** Portfolio summary from Pass 2 computations:

| Metric | Value |
|---|---|
| Total Systems in Scope | [n] |
| Risk — Critical | [n] open |
| Risk — High | [n] open |
| Risk — Medium | [n] open |
| Risk — Low | [n] open |
| Control Coverage | [pct]% |
| Evidence Completion | [pct]% |
| Monitoring Cadence | every [n] days avg |

Multi-product: one row per system with criticality tier and coverage status.

- **8.3** Standard-specific operational controls — read SOA/control coverage for the detected `STANDARD`. For each Annex/domain family:
  - AIMS (ISO 42001): AI lifecycle controls (A.5–A.6), data governance (A.7), transparency (A.8), use controls (A.9), TPRM (A.10) — source: CDG SoA CSVs, fallback to CCS `control_coverage`
  - ISMS (ISO 27001): Organizational (A.5), People (A.6), Physical (A.7), Technological (A.8) — source: CCS `control_coverage` families
  - CSMS (IEC 62443): Zone/Conduit model, SL-T per zone, 7 program domains (Risk, Policies, Organization, Security Awareness, Business Continuity, Incident Response, Security Systems)
  - IMS: render one sub-section per standard present; cross-reference shared controls to avoid duplication
  - `[DATA NEEDED]` for any Annex/domain family with no SOA or coverage data

### Clause 9 — Performance Evaluation
- **9.1** Monitoring — what (controls, risks, evidence), how (pipeline runs, manual reviews), cadence from provenance log
- **9.2** Internal audit program; reference `data/[PROGRAM]/` audit records; else `[DATA NEEDED: internal audit records]`
- **9.3** Management review — inputs (audit results, risk status, objective performance), outputs (improvement and resource decisions), frequency `[REVIEW_CADENCE]`; draw from charter and memory

### Clause 10 — Improvement
- **10.1** POA&M as corrective action: identification → risk register → closure tracking
- **10.2** Pipeline cadence as continuous monitoring; annual review as formal improvement cycle; improvement decisions from memory

### Version Control
```markdown
| Version | Date | Author | Changes | Generated By |
|---|---|---|---|---|
| [n] | [today] | [ORG_NAME if branded, else "the Organization"] | [Initial assembly | Delta review — clauses updated: list | Section update — clause: n] | management-system-assembler-spec.md v1.1 — [timestamp] |
```

---

## Pass 4 — Quality Gate

Invoke `engine/quality-gate-spec.md` per `MODEL_TIER` rules (opus: full gate; sonnet: structural + constitutional only; compact: skip, rely on orchestrator Phase 6). Additionally verify:

- [ ] Every clause 4–10 has ≥1 populated sub-section or explicit `[DATA NEEDED]`
- [ ] Clause 7.5 lists every artifact ingested in Pass 2
- [ ] Clause 8.2 populated from computed data, not placeholders
- [ ] Version control table includes generation timestamp and spec reference
- [ ] No org name, color, or branding unless `BRANDED_OUTPUT: yes`
- [ ] All `[DATA NEEDED]` flags collected and surfaced in post-assembly summary

```
[MSA] Assembly complete — [OUTPUT_NAME]
  Clauses fully populated: [n]/[n]
  [DATA NEEDED] flags: [n] — [affected clauses]
  Document inventory entries: [n]
  Systems in scope: [n]
  Output: data/[PROGRAM]/[OUTPUT_NAME]-v[n].md
  Quality gate: [pass | fail — reason]
  Provenance logged: yes
```

---

## Pass 5 — Provenance
```bash
python scripts/provenance_log.py write \
  --spec "functions/management-system-assembler-spec.md" \
  --output "data/[PROGRAM]/[OUTPUT_NAME]-v[n].md" \
  --output-type management_system \
  --program "[PROGRAM]" \
  --purpose "Management system assembled: [archetype] — [standards]" \
  --reusability artifact \
  --quality-gate [pass | fail]
```

---

## Trigger
```
PROGRAM: [slug]
STANDARD: [iso27001 | iso42001 | iec62443 | integrated | auto-detect]
OUTPUT_NAME: [display name]
APPLICABILITY: [scope statement]
REVIEW_CADENCE: [annual | biannual | quarterly]
REVIEW_MODE: [full_assembly | delta_review | section_update — optional, default: full_assembly]
MODEL_TIER: [opus | sonnet | compact — optional, default: opus]

BEGIN MANAGEMENT SYSTEM ASSEMBLY
```

## Suggested Repo Path
`functions/management-system-assembler-spec.md`

## Companion Specs
- Governed by: `config/constitution.md`
- Invoked by: `engine/program-pipeline-orchestrator.md`
- Invokes: `engine/quality-gate-spec.md`
- Reads: `runs/[PROGRAM]/latest.json`, `data/[PROGRAM]/`, `[PIPELINE_OUTPUT_DIR]` (CDG outputs), `memory/[PROGRAM]-memory.md`, `logs/provenance.jsonl`
- Upstream: `functions/compliance-doc-generator-spec.md` (artifact generation), `functions/control-coverage-spec.md` (control_coverage authoritative source)
- Writes: `data/[PROGRAM]/[OUTPUT_NAME]-v[n].md`
- Logged by: `scripts/provenance_log.py` — output_type: `management_system`
