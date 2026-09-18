# Functions

Discrete callable work specs. Each encodes one domain. Invoked by the engine when work matches their domain.

**Path:** `functions/`

## Contents

| File | Domain | Standalone | Formulary CLI | Purpose |
|------|--------|------------|---------------|---------|
| **auditor-view-spec.md** | Compliance | ✓ | [`exhibit`](https://github.com/Formulary-Labs/exhibit) | Read-only auditor compliance posture dashboard |
| **calendar-output-spec.md** | Compliance | ✓ | [`dose`](https://github.com/Formulary-Labs/dose) | LLM fallback calendar generation |
| **compliance-doc-generator-spec.md** | Compliance | ✓ | [`formula`](https://github.com/Formulary-Labs/formula) | Orchestrated CSV/MD compliance output generation |
| **compliance-entropy-spec.md** | Compliance | ✓ | [`decay`](https://github.com/Formulary-Labs/decay) | Longitudinal compliance analysis |
| **compliance-redteam-spec.md** | Compliance | ✓ | [`challenge`](https://github.com/Formulary-Labs/challenge) | Adversarial artifact review |
| **control-assessment-spec.md** | Compliance | ✓ | [`assay`](https://github.com/Formulary-Labs/assay) | Auditor template filling from framework + product docs |
| **control-coverage-spec.md** | Compliance | ✓ | [`titer`](https://github.com/Formulary-Labs/titer) | Control mapping and gap analysis |
| **external-intel-spec.md** | Intelligence | ✓ | [`scan`](https://github.com/Formulary-Labs/scan) | External source monitoring and risk deltas |
| **management-system-assembler-spec.md** | Compliance | ✓ | [`compound`](https://github.com/Formulary-Labs/compound) | ISMS/AIMS document assembly from artifacts |
| **program-comms-spec.md** | Communications | ✓ | — | Status reports, recaps, requests |
| **program-intake-spec.md** | Program Management | — | — | Program onboarding and full build |
| **program-monitoring-spec.md** | Program Management | — | — | Ongoing oversight and escalations |
| **risk-register-spec.md** | Compliance | ✓ | [`specimen`](https://github.com/Formulary-Labs/specimen) | Risk register and POA&M starter |
| **vendor-management-spec.md** | Vendor Management | — | — | Vendor scoring and remediation |
| **post-audit-spec.md** | Program Management | ✓ | — | Post-audit lessons learned, corrective actions, and feed-forward for next cycle |
| **product-evidence-spec.md** | Compliance | ✓ | — | Product documentation as evidence: mapping product artifacts to control narratives |
| **kanban-spec.md** | Program Management | ✓ | — | Per-program kanban boards, Jira export |
| **program-dashboard-spec.md** | Program Management | ✓ | [`vital`](https://github.com/Formulary-Labs/vital) | Per-program + portfolio HTML dashboard generation, light-theme renderer |
| **product-onboarding-intake-spec.md** | Compliance | ✓ | — | Validates and merges a completed onboarding kit handoff package into the live ISO 42001 program |

> **Note:** `quality-gate-spec.md` lives in `engine/`, not here. It is an engine spec applied before every delivery.
>
> **Formulary CLI column:** When a Formulary CLI is listed, prefer it for the deterministic execution steps. The spec still governs routing, judgment, flagging, and quality gate. See [`FORMULARY.md`](../FORMULARY.md) for the full integration map.
