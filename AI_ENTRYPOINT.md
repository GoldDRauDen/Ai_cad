# AI ENTRYPOINT — TrainAiCad repo-direct production

Current production release is **V4.23**.

This file is the production routing authority. Normal CAD jobs use **repo-direct modular routing**. Do not load the complete portable skill by default.

## 1. Normal production flow

```text
SOURCE
  -> always-on CORE
  -> SOURCE CLASSIFICATION
  -> FEATURE CENSUS
  -> ROUTER
  -> selected mode / feature / reference modules
  -> CROSS-FEATURE VALIDATION
  -> canonical geometry
  -> DXF
  -> saved-DXF read-back / applicable source reprojection
```

Mandatory router files:
- `skills/lispcad/router/FEATURE_CENSUS.md`
- `skills/lispcad/router/ROUTER.yaml`
- `skills/lispcad/router/RULE_COVERAGE.yaml`

Always-on core is declared in `ROUTER.yaml`. Do not invent a different core set from memory.

## 2. Census before specialized rules

Inspect the actual source before selecting specialized modules. Build the preliminary census with only `YES`, `NO`, or `UNKNOWN`.

**UNKNOWN != NO.** Every `YES` and `UNKNOWN` family loads its route. After routed modules are loaded, re-check the source and close the final census.

Do not mark a feature absent merely because OCR did not find its keyword. Inspect geometry, leaders, witnesses, notes, revisions, sections/details and supplied customer DATA as applicable.

## 3. Source and mode routing

Classify exactly one source relationship using `references/SOURCE_DATA_CLASSIFICATION.md`:
- `PDF_ONLY`
- `PDF_DATA_RAW`
- `TRAIN_REFERENCE`
- `DIRECT_EXISTING_DXF_AUDIT`

For `PDF_DATA_RAW`, the router loads `references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md` and `references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md`. Customer DATA supplies physical geometry; PDF controls semantics, dimensions, revisions and manufacturing meaning under the approved rules.

For every bent or multi-face part, the router loads `skills/lispcad/modes/BEND_UNFOLD.md` and `references/FACE_GRAPH_UNFOLD_PROTOCOL.md`.

## 4. Release wiring index — backward-compatible regression contract

This compact index preserves the machine-readable release wiring required by existing regression tests. It is **not** an instruction to load every listed regression on every job.

- **V4.23:** `SOURCE_PHYSICAL_TO_CANONICAL`, `CANONICAL_TO_SOURCE_PHYSICAL`, `PER_BEND_WITNESS_LEDGER`, `THICKNESS_SINGLE_USE`, `THICKNESS_REPRESENTATION`; regression `regression/qa/521001-03_V4_23_APPROVED.md`; executable `regression/tools/check_521001_03_v423.py`.
- **V4.22:** `SOURCE_EXHAUSTED_BEFORE_VIEWS_ONLY` and `SOURCE_FEATURE_COMPLETENESS`; regression `regression/qa/520930-10_V4_22_APPROVED.md`; executable `regression/tools/check_520930_10_v422.py`.
- **V4.21:** `references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md`; regression `regression/qa/520930-03_V4_21_APPROVED.md`; retain `DATA_REQUIRED_MISSING` and mandatory source reprojection.
- **V4.20:** source/mechanical classification plus independent KEGAKI / SLIT_RELIEF / RIB / CURVED_SLOT routing.
- **V4.19 520929-25 hard-gate routing:** `references/FACE_GRAPH_UNFOLD_PROTOCOL.md`; regression `regression/qa/520929-25_V4_19_APPROVED.md`; executable `regression/tools/check_520929_25_v419.py`.
- **V4.18 520929-18 hard-gate routing:** detailed-source bundle, C/R semantic lock and BOXMET signed orientation; `references/BOXMET_SLIT_RELIEF.md`; regression `regression/qa/520929-18_V4_18_APPROVED.md`; executable `regression/tools/check_520929_18_v418.py`.
- **V4.17 520929-10 hard-gate routing:** source witness, mirror scope, datum, KEGAKI and actual-unit guards; regression `regression/qa/520929-10_V4_17_APPROVED.md`; executable `regression/tools/check_520929_10_v417.py`.
- **V4.16:** face-first dimension ownership, explicit R/C family quantity closure and BOXMET four-flange routing through `references/BOXMET_SLIT_RELIEF.md`; regression `regression/qa/520801-04_V4_16_APPROVED.md`.
- **V4.15:** acute bend <85° routing through `references/ACUTE_BEND_LT85_METHOD.md` and `references/ACUTE_BEND_LT85_FROM_SOURCE.md`.
- **V4.14:** existing-output direct audit and overlapping-cut QA retained in active core modules.
- **V4.13 and earlier approved rules:** retained in active core/mode/feature/reference modules as mapped by `skills/lispcad/router/RULE_COVERAGE.yaml`.

## 5. Production completeness

Before production PASS, close:

```text
SOURCE ACTIVE FAMILIES
  -> FINAL FEATURE CENSUS
  -> LOADED ROUTES
  -> CANONICAL GEOMETRY
  -> SERIALIZED OUTPUT
```

Then run the active validation and output contract. A correct bbox, entity count, syntactically valid DXF or successful read-back cannot compensate for a missing source manufacturing family.

If a source-supported feature has no route, stop with `ROUTING_COVERAGE_GAP`. Do not silently map it to generic CUT.

## 6. Portable and history policy

`skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md` is retained as the complete V4.23 compatibility/audit snapshot so no approved rule text is destroyed by this migration. It is **NOT part of the normal repo-direct load path**.

It may be read only to diagnose a `ROUTING_COVERAGE_GAP`, audit historical coverage, or perform an explicitly requested portability check. After a gap is found, do not silently continue production from the portable file; fix/approve the missing route first.

Normal production retrieval must exclude:
- `skills/lispcad/versions/**`
- `docs/history/**`

Historical snapshots never override active modular rules.

## 7. Regression and output

Load only regressions relevant to the routed rule/family or an explicit audit. Regression geometry is evidence/tests, not a source of missing dimensions for a new drawing.

Use the current core `VALIDATION.md` and `CAD_OUTPUT.md` contract plus applicable routed modules. Read back the actual saved DXF before calling production complete.

## 8. MCP boundary

**MCP is research-only and is NOT part of the production CAD pipeline.**

**Default CAD behavior remains repo-direct.**

Do not route through MCP for ordinary CAD production. Experimental code under `services/trainaicad-mcp/` has no production authority unless the user explicitly asks to work on MCP.
