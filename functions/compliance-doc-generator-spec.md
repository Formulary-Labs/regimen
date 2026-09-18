---
resource_type: spec
version: "2.5"
domain: compliance
triggers:
  - onboarding_phase_1
  - compliance_refresh
  - audit_prep
  - portfolio_aggregation
inputs:
  - gemara_yaml_layer2
  - gemara_yaml_layer5
  - compliance_library_resources
outputs:
  - soa_csv
  - risk_assessment_csv
  - impact_assessment_csv
  - dependency_map_csv
  - compliance_context_md
  - collective_risk_register_csv
governed_by: config/constitution.md
standalone: true
entry_point: false
invoked_by: engine/program-pipeline-orchestrator.md
invokes:
  - engine/quality-gate-spec.md
depends_on:
  - .github/scripts/generate_soa.py                # generation engine repo (e.g. psc-aims-dev)
  - .github/scripts/generate_risk.py
  - .github/scripts/generate_impact.py
  - .github/scripts/generate_dependency_map.py
  - .github/scripts/generate_ccd.py
  - .github/scripts/generate_evidence_registry.py
  - .github/scripts/generate_nist_risk.py
  - .github/scripts/generate_system_card.py
  - .github/scripts/generate_xlsx.py
  - .github/scripts/generate_collective_risk.py
---

# Compliance Doc Generator Spec
**Version:** 2.5
**Purpose:** Standard-agnostic orchestration of compliance artifact generation. Uses capability-first discovery to map architectural facts to multiple standards and executes deterministic scripts (`.github/scripts/` in the generation engine repo) to build program resources.
**Governed by:** `config/constitution.md`
**Maintainer:** Alex Langston

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

## Parameters
```
PROGRAM:              [slug]
FRAMEWORK:            [iso42001 | iso27001 | iec62443 | auto-detect]
PIPELINE_OUTPUT_DIR:  [default: data/[PROGRAM]/Products/pipeline outputs/]
```

If `FRAMEWORK: auto-detect`, infer from the program skeleton's `scope.frameworks` field. If ambiguous, ask the lead program manager to confirm before Pass 1.

## **Persona Definition**

You are a Compliance Program Orchestrator. You treat compliance as a technical engineering problem. Your goal is to take "Architectural Facts" and "Standard Requirements" and produce a high-fidelity crosswalk. You do not just "fill out forms" — you reason through the relationship between a system's archetype and its regulatory obligations.

---

## Formulary Tool

**CLI:** [`formula`](https://github.com/Formulary-Labs/formula) — `github.com/Formulary-Labs/formula`

Handles deterministic artifact scaffold generation (Pass 3 below):
- Generates SOA CSV, risk assessment CSV, evidence registry, system card scaffold, and NIST risk CSV from program state
- Dry-run mode for preview; structured JSON output for agent consumption
- Framework-agnostic; driven by program state in run JSON

```bash
formula --run runs/[PROGRAM]/latest.json --out data/[PROGRAM]/Products/pipeline\ outputs/ --format json
```

This spec governs the full multi-pass pipeline: architectural grounding (Pass 1), fact enrichment (Pass 2), quality gate, and handoff to `functions/management-system-assembler-spec.md`. `formula` handles the deterministic scaffold steps; LLM passes fill narrative content.

> See [`FORMULARY.md`](../FORMULARY.md) for the full integration map.

---

## **Logic Lifting: Script-Derived Guardrails**

To ensure consistency, apply the following deterministic logic lifted from the `.github/scripts/` generators. Guardrails 3 and 4 are framework-conditional per the `FRAMEWORK` parameter — apply the branch matching the detected/declared value only.

### **1\. The "Pending" Failure Logic (from `generate_risk.py`) — all frameworks**

* **Rule:** If a narrative or link contains "PENDING", "TODO", or is empty, the agent MUST override any "Passed" status in memory.  
* **Impact:** Force `Likelihood: 5`, `Impact: 4`, `Risk Score: 20`, and `Level: CRITICAL`.  
* **Action Plan:** Must explicitly set to: "Provide missing evidence link in Product YAML."

### **2\. Standard Suppression & Inheritance (from `generate_soa.py`) — all frameworks**

* **Logic:** If `Deployment Role == Service Tenant`, apply automatic inheritance.  
* **In-Scope Domains:** Controls matching "Hardware," "Physical Security," "Facility," or "Infrastructure Lifecycle" are marked `status: Inherited`.  
* **Justification:**
  * `FRAMEWORK: iso42001` — "Governed by Parent Platform AIMS Charter."
  * `FRAMEWORK: iso27001` — "Governed by Parent Platform ISMS Charter — cloud/shared-services tenant inheritance."
  * `FRAMEWORK: iec62443` — "Governed by Parent Zone Security Level Charter."

### **3\. Archetype-to-Goal Mapping (from `generate_impact.py`) — framework-conditional**

* `FRAMEWORK: iso42001` — apply AI archetype goals:
  * **Generative AI Archetype:** "Explainability," "Hallucination Monitoring," "Data Lineage."
  * **High Criticality Archetype:** "Human Oversight" and "Red Teaming."
  * Replace `[ARCHETYPE]` tokens in templates with the detected archetype.
* `FRAMEWORK: iso27001` — skip archetype-to-goal injection; no AI-specific goals apply. Use control-family-based objectives from `iso27001_controls.csv` instead.
* `FRAMEWORK: iec62443` — apply SL-Target-driven goal injection: map each zone's assessed Security Level (SL-T) to its corresponding foundational requirement goals (FR1–FR7) instead of archetype tokens.

### **4\. Third-Party Keyword Detection (from `generate_dependency_map.py`) — all frameworks**

* **Keywords:** Search for `gpt`, `openai`, `watsonx`, `llama`, `claude`, `aws`, `azure`, `gcp`, `github`, `quay`.  
* **Classification:** Map findings to `AI Model`, `Infrastructure`, or `Code/Artifacts`.
* Applies regardless of `FRAMEWORK` — third-party dependency detection is standard-agnostic.

## **Granular Document Requirements**

### **1\. Statement of Applicability (SoA)**

* **Fact Mapping:** Map one `implementation_item` to multiple control IDs provided in the `compliance_library_resources`. Control template source is framework-conditional:
  * `FRAMEWORK: iso42001` → `iso42001_controls.csv` (38 Annex A controls + Clauses 4–10)
  * `FRAMEWORK: iso27001` → `iso27001_controls.csv` (93 Annex A controls, 4 themes)
  * `FRAMEWORK: iec62443` → `iec62443_controls.csv` (7 program domains, 4 SL tiers)
* **Narrative Tone:** Use "The Product implements..." or "Access is restricted by..." Avoid "We do..."

### **2\. Risk Assessment & Collective Register**

* **Library Merging:** Match Layer 2 implementation gaps with the "Risk Scenarios" found in the framework-appropriate risk library:
  * `FRAMEWORK: iso42001` → `ai_risk_library.csv`
  * `FRAMEWORK: iso27001` → `iso27001_risk_library.csv`
  * `FRAMEWORK: iec62443` → `iec62443_risk_library.csv`
* **Aggregation:** Once multiple products are processed, trigger `generate_collective_risk.py`.

### **3\. Impact Assessment**

* **Logic:** Use the Script-Derived Guardrail \#3 to determine applicability.

### **4\. TPRM Dependency Map**

* **Classification:** Categorize findings into `Infrastructure`, `AI Model`, or `Software Artifact`.

## **Processing Passes**

### **Pass 1 — Architectural Grounding & Triage**

* Identify Deployment Role (Tenant vs. Provider).  
* Identify Data Profile (PII vs. System Metadata).  
* Determine Archetype (GenAI, RAG, Infrastructure, etc.).

### **Pass 2 — Fact Enrichment & Crosswalk**

* Ingest PDFs/CSVs from `RESOURCE_REPO`.  
* If `runs/[PROGRAM]/latest.json` contains a populated `control_coverage` block (`source: this_run`), use it as the Unified Control Map base — do not re-derive controls already assessed by `control-coverage-spec.md`.
* Otherwise, build an in-memory "Unified Control Map" where one capability satisfies multiple framework IDs.  
* Clean narratives for professional, neutral tone.

### **Pass 3 — Artifact Generation**

Call `formula` (see Formulary Tool above). `formula` executes the deterministic generation pipeline using the run JSON enriched in Pass 2, producing all output artifacts to `[PIPELINE_OUTPUT_DIR]/[PRODUCT_SLUG]/`.

## **Quality Gate**

* **Format:** No numbered headers or emojis in CSV/MD outputs.  
* **Integrity:** Every `PENDING` in the YAML must be reflected as a `CRITICAL` risk.  
* **Neutrality:** Applies to narrative tone only — no promotional or marketing language ("industry-leading," "best-in-class," etc.). Do not search-and-replace the vendor name or product name themselves: factual identifiers (who built it, what it's called, what version) are load-bearing evidentiary content, not promotional language, and stripping them would break the Traceability check below — an auditor cannot verify a citation against a redacted subject.
* **Traceability:** Every control marked "Implemented" must have a non-pending evidence link or a reference to a parent charter, and that evidence must name the actual product/vendor being assessed.

## Output Path Convention

Consumer: `functions/management-system-assembler-spec.md` Pass 2.

```
[PIPELINE_OUTPUT_DIR]/[PRODUCT_SLUG]/
  soa.csv, risk_assessment.csv, impact_assessment.csv,
  [product]-CCD.md, evidence_registry.csv, nist_risk_assessment.csv,
  [product]-system-card.md, [product]-AIMS.md,
  [product]_aims_assessment.xlsx
[PIPELINE_OUTPUT_DIR]/collective_risk_register.csv
```

`[PIPELINE_OUTPUT_DIR]` defaults to `data/[PROGRAM]/Products/pipeline outputs/`. Set the `PIPELINE_OUTPUT_DIR` parameter if the program uses a different location. MSA Pass 2 reads from these paths directly — do not require it to search.

## **Suggested Repo Path**

`functions/compliance-doc-generator-spec.md`

## Companion Specs
- Governed by: `config/constitution.md`
- Orchestrator: `engine/program-pipeline-orchestrator.md`
- Quality Gate: `engine/quality-gate-spec.md`
- Generators: generation engine repo `.github/scripts/*.py` (10 generators — see `depends_on`)
- Handoff: `functions/control-coverage-spec.md` (Unified Control Map source), `functions/management-system-assembler-spec.md` (consumes pipeline outputs)
