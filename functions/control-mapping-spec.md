---

resource_type: spec
version: "1.0"
domain: compliance
triggers:
- cross_framework_mapping
- control_overlap_analysis
- multi_framework_program
inputs:
- mapping_document_path
- source_catalog_path
- target_catalog_path
outputs:
- mapping_result_json
- mapping_result_md
- mapping_result_csv
governed_by: config/constitution.md
standalone: true
invoked_by:
- agents/coordinator.md
- agents/program-agent.md
depends_on: []
structured_output: true

---

# Control Mapping Spec

**Version:** 1.0
**Purpose:** Resolve cross-framework control mappings from a gemara `MappingDocument`. Identify which source controls map to which target controls, which are unmapped, and flag IDs not found in the source catalog.
**Governed by:** `config/constitution.md`

---

## Constitutional Guidance

[Constitution in effect — `config/constitution.md` governs all behavior. Load it at session start; do not re-read guidance here.]

---

## When to invoke

Invoke this spec when the user or program context indicates any of the following:

- "Map ISO 27001 controls to NIST 800-53" or similar cross-framework request
- A program operates under two or more frameworks and needs to understand control overlap
- Building a combined SOA or evidence plan across multiple frameworks
- Investigating which source controls have no target match (unmapped gap analysis)
- Preparing a cross-framework audit package where control equivalence must be documented

Do not invoke for single-framework coverage analysis — use `functions/control-coverage-spec.md` and `titer` for that.

---

## Formulary Tool

**CLI:** [`bind`](https://github.com/Formulary-Labs/bind) — `github.com/Formulary-Labs/bind`

`bind` handles the deterministic mapping resolution layer:

- Reads a gemara `MappingDocument` (Layer 1 artifact)
- Resolves each source control to its target framework controls
- Classifies entries as `mapped` or `unmapped` (based on relationship type)
- Flags source IDs absent from the source catalog with `[CONFLICT — VERIFY]`
- Outputs JSON (pipeline), Markdown (human review), or CSV (spreadsheet/SOA)

```bash
# Resolve a mapping document — IDs only
bind --document mappings/iso27001-to-nist800-53.yaml --format json

# With title resolution and source-ID validation
bind --document mappings/iso27001-to-nist800-53.yaml \
     --source-catalog catalogs/iso27001.yaml \
     --target-catalog catalogs/nist800-53.yaml \
     --format md

# Unmapped gaps only — feed into specimen as coverage_gap risks
bind --document mappings/iso42001-to-iso27001.yaml \
     --filter unmapped --format csv > unmapped-gaps.csv
```

> See [`FORMULARY.md`](../FORMULARY.md) for the full integration map.

---

## Processing Instructions

### Pass 1 — Input Validation

Confirm the following before invoking `bind`:

1. A `MappingDocument` YAML exists at the specified path
2. The document is a valid gemara artifact — run `probe <mapping.yaml>` to confirm
3. Source and target catalog paths are known (required for title resolution and conflict detection)

If no `MappingDocument` exists, this spec cannot proceed. Surface the gap to the program manager and note that a gemara `MappingDocument` must be authored or sourced — see [CATALOGS.md](https://github.com/Formulary-Labs/.github/blob/main/CATALOGS.md) for known upstream mapping sources.

Narrate:
```
[MAPPING] Validating MappingDocument at [path]...
[MAPPING] Source framework: [id] | Target framework: [id]
[MAPPING] Invoking bind for resolution...
```

---

### Pass 2 — Resolution

Invoke `bind`:

```bash
bind --document [MAPPING_DOCUMENT_PATH] \
     --source-catalog [SOURCE_CATALOG_PATH] \
     --target-catalog [TARGET_CATALOG_PATH] \
     --program [PROGRAM] \
     --format json > data/[PROGRAM]/mapping-[source]-to-[target].json
```

Omit `--source-catalog` and `--target-catalog` if catalog paths are not available. Title resolution and conflict detection will be skipped — note this in the output.

---

### Pass 3 — Surface Results

Parse the JSON output. Narrate a summary:

```
[MAPPING] Resolution complete.
[MAPPING] [n] total mappings | [n] mapped ([x]%) | [n] unmapped ([x]%)
[MAPPING] [n] data quality flags (source IDs not found in catalog)
```

If `flags` is non-empty, surface each `[CONFLICT — VERIFY]` entry. These are source control IDs in the `MappingDocument` that do not exist in the source catalog — they require human verification before the mapping is used in an audit package.

---

### Pass 4 — Downstream Routing

Route the output to downstream steps based on context:

| Use case | Next step |
|----------|-----------|
| Combined SOA across frameworks | Feed mapped controls into `formula` or `compound` as the multi-framework control set |
| Unmapped gap analysis | Export unmapped CSV → `specimen add` to create risk entries |
| Audit package | Export markdown table → attach to audit package alongside the source `MappingDocument` |
| Program health snapshot | Include mapping coverage % in `vital` dashboard input |

---

## Output Schema

`bind` emits a `MappingResult` JSON conforming to the following shape:

```json
{
  "source": "iso27001",
  "target": "nist-sp-800-53-rev-5",
  "total": 114,
  "mapped": 108,
  "unmapped": 6,
  "entries": [
    {
      "source_id": "A.5.1",
      "source_title": "Policies for information security",
      "relationship": "subset-of",
      "targets": [
        {
          "target_id": "PM-1",
          "target_title": "Information Security Program Plan",
          "strength": 8,
          "rationale": "..."
        }
      ]
    }
  ],
  "flags": []
}
```

Relationship values: `subset-of`, `superset-of`, `equivalent`, `related`, `no-match`.

`no-match` entries are always classified as `unmapped`.

---

## Provenance

`bind` writes a provenance entry automatically after each run. No additional provenance write is required from this spec. Verify the entry appears in `logs/provenance.jsonl` with `output_type: other` and `spec: functions/control-coverage-spec.md`.

---

## Companion Specs

| Spec | Relationship |
|------|-------------|
| `functions/control-coverage-spec.md` | Single-framework coverage — use `titer` for this, `bind` for cross-framework |
| `functions/auditor-view-spec.md` | Mapping results can be attached to auditor view as a supplemental section |
| `functions/risk-register-spec.md` | Unmapped controls feed into the risk register as `coverage_gap` source risks |
| `functions/management-system-assembler-spec.md` | Mapped control equivalences inform multi-framework ISMS/AIMS clauses |
