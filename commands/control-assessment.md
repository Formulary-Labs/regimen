# Control Assessment

Fill an auditor template, STIG checklist, CIS benchmark, IEC 62443-4-2 assessment, or functional test plan by mapping framework requirements to product documentation. Operates in validated batches with resumability for large control sets.

## Input required

If not provided after the command, ask before proceeding:

- **program** — program slug
- **framework type** — `iec62443-4-2` `disa-stig` `cis-benchmark` `functional-test-plan` `custom`
- **template path** — auditor template file
- **framework document path** — cert or framework document
- **product source** — directory, MCP server, URL, or file
- **product name** and **product version**
- **Resume** (if continuing): `RUN_ID` and `RESUME: yes` when restarting an interrupted run

## Steps

1. Load `runs/[program]/latest.json` if needed for program context.
2. Execute `functions/control-assessment-spec.md` with this invocation block (fill all fields):

```
PROGRAM:          [program slug]
FRAMEWORK:        [iec62443-4-2 | disa-stig | cis-benchmark | functional-test-plan | custom]
TEMPLATE_PATH:    [path]
FRAMEWORK_PATH:   [path]
PRODUCT_SOURCE:   [path | MCP | URL | file]
PRODUCT_NAME:     [name]
PRODUCT_VERSION:  [version]
RESUME:           [yes | no]
RUN_ID:           [if resuming]
BEGIN CONTROL ASSESSMENT
```

Follow the spec's phases, confirmation points (inventory count, custom field mapping, consistency resolution), and batch validation. Do not present final outputs until they pass `engine/quality-gate-spec.md`.

## Output

Per the control-assessment spec: filled template, markdown artifact, gap report, and state file under `data/[program]/assessments/` as defined there. Log provenance with `scripts/provenance_log.py` when the spec instructs.
