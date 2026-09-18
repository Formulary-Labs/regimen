---
description: Lightweight mid-session compliance verification checklist. Flags common quality gate violations before submission to engine/quality-gate-spec.md for full validation.
---

# Compliance Quality Self-Check

Use this skill during a session to quickly verify a draft compliance artifact (spec, output, plan) against quality gate principles **before** submitting it to the full quality gate. This is a fast checklist, not a substitute for `engine/quality-gate-spec.md`.

**Run time:** 2–5 minutes. **Output:** pass/fail + specific flagged issues.

## Checklist

### Flag Vocabulary Applied
- [ ] `[DATA NEEDED: source]` appears on all assertions without a primary source
- [ ] `[OWNER NEEDED]` on all unassigned tasks or decisions
- [ ] `[INFERRED]` on all inferred content not explicitly stated in the source
- [ ] `[CONFLICT — VERIFY]` on all contradictions found (and resolved in text)
- [ ] `[CITATION NOT FOUND]` if claiming a fact from a document but can't locate the exact section

### Provenance
- [ ] Artifact has a unique, descriptive name (e.g. `iso42001-control-gap-2026-07-29.json`)
- [ ] Artifact includes a `run_date` or `produced_date` field in ISO 8601 format
- [ ] If this is a new POA&M item, corrective action, or risk entry, the source is named (audit finding ID, control ID, threat ID, etc.)

### Schema Compliance
- [ ] If the artifact is JSON, it validates against its declared schema (e.g. `run-output-v2.schema.json`)
- [ ] All required fields are present and not null
- [ ] No `[DATA NEEDED]` flags remain in fields marked as required

### No Loose Ends
- [ ] All `[OWNER NEEDED]` entries have been escalated or are explicitly noted as escalation items
- [ ] All `[DATA NEEDED: X]` flags identify the specific data source or owner
- [ ] No `[CONFLICT — VERIFY]` remains unresolved (either resolved inline or escalated)

### Ready for Gate
- [ ] Artifact is ready to submit to `engine/quality-gate-spec.md` for full validation
- [ ] If any checks failed, list flagged issues below and do NOT submit to gate yet

## Flagged Issues

(List any issues found. If none, mark PASS and proceed to full quality gate.)

---

**Full Validation:** After this checklist passes, route to `engine/quality-gate-spec.md` for compliance output gate review.
