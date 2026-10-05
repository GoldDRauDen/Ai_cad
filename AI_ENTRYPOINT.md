# AI ENTRYPOINT — TrainAiCad repo-direct production

Current production release is **V4.27**.

This file is the production routing authority. Normal CAD jobs use **repo-direct modular routing**. Do not load the complete portable skill by default.

## 1. Normal production flow

```text
SOURCE
  -> always-on CORE
  -> SOURCE CLASSIFICATION
  -> DXF PHYSICAL-CURVE DECODE when DXF source/reference exists
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

Always-on core/source-parsing references are declared in `ROUTER.yaml`. Do not invent a different core set from memory.

## 2. Census before specialized rules

Inspect the actual source before selecting specialized modules. Build the preliminary census with only `YES`, `NO`, or `UNKNOWN`.

**UNKNOWN != NO.** Every `YES` and `UNKNOWN` family loads its route. After routed modules are loaded, re-check the source and close the final census.

Do not mark a feature absent merely because OCR did not find its keyword. Inspect geometry, leaders, witnesses, notes, revisions, sections/details, barcode/process cues and supplied customer DATA as applicable.

V4.27 weld-cue gate: a proved reversed-e mark immediately above a barcode is `REVERSED_E_ABOVE_BARCODE -> WELD_REQUIRED_CUE` for that barcode's code/detail cluster only. The cue proves a welding-process expectation, not KEGAKI geometry. If a scoped welded RIB/gusset/support cannot self-locate, KEGAKI must be source-proved or retained as `UNKNOWN`/FLAG until locating/contact evidence is exhausted. A specific KEGAKI instruction independently requires KEGAKI. If neither cue nor specific KEGAKI instruction exists, do not infer welding/KEGAKI solely from a secondary RIB/support. Use `skills/lispcad/features/KEGAKI.md`.

V4.26 hard gate: whenever DXF geometry participates as customer DATA, reference, or direct-audit evidence, decode its physical curves before Feature Census. For `POLYLINE`/`LWPOLYLINE`, nonzero bulge means ARC, not the endpoint chord; closed final->first segments are included. Use `references/DXF_PHYSICAL_CURVE_DECODING.md`.

## 3. Source and mode routing

Classify exactly one source relationship using `references/SOURCE_DATA_CLASSIFICATION.md`:
- `PDF_ONLY`
- `PDF_DATA_RAW`
- `TRAIN_REFERENCE`
- `DIRECT_EXISTING_DXF_AUDIT`

For `PDF_DATA_RAW`, the router loads `references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md`, `references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md` and `references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md`. Customer DATA supplies physical geometry; PDF controls semantics, dimensions, revisions and manufacturing meaning under the approved rules. V4.25 requires the complete DATA geometry to be frozen/accounted before manufacturing canonicalization, every intentional change to be rule-scoped in `MANUFACTURING_CHANGE_LEDGER`, and all untouched DATA geometry to pass physical invariance/reprojection. V4.26 additionally requires that the frozen physical baseline preserve decoded LINE/ARC/CIRCLE geometry; endpoint-only preservation of a bulged polyline is incomplete DATA harvest.

For every bent or multi-face part, the router loads `skills/lispcad/modes/BEND_UNFOLD.md` and `references/FACE_GRAPH_UNFOLD_PROTOCOL.md`.

## 4. Release wiring index — backward-compatible regression contract

- **V4.27:** `REVERSED_E_ABOVE_BARCODE`, `WELD_REQUIRED_CUE`, barcode/code scope, welded non-self-locating RIB/support -> KEGAKI `YES|UNKNOWN` gate, and no-RIB-only weld inference; active modules `skills/lispcad/router/FEATURE_CENSUS.md`, `skills/lispcad/features/KEGAKI.md`, `skills/lispcad/core/CROSS_FEATURE_VALIDATION.md`; regression `regression/qa/521005-01_V4_27_APPROVED.md`; executable `regression/tools/check_521005_01_v427.py`. Existing slot, datum, Nobi, thread, material and DATA<->PDF numeric rules are unchanged.
- **V4.26:** `DXF_PHYSICAL_CURVE_DECODE_BEFORE_CENSUS`, `PHYSICAL_CURVE_CENSUS`, `POLYLINE_BULGE_IS_ARC`, `BULGE_ARC_NOT_CHORD`, closed final->first segment coverage and physical-curve reprojection; reference `references/DXF_PHYSICAL_CURVE_DECODING.md`; regression `regression/qa/521001-19_V4_26_APPROVED.md`; executable `regression/tools/check_521001_19_v426.py`. No numeric Nobi/thread/material/tolerance table or DATA<->PDF threshold is changed.
- **V4.25:** `RAW_DATA_SNAPSHOT`, `PHYSICAL_DATA_BASELINE`, `SAME_PARAMETER_GATE`, `MANUFACTURING_CHANGE_LEDGER`, `UNTOUCHED_DATA_INVARIANCE_CHECK`, representation-equivalent physical geometry; reference `references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md`; regression `regression/qa/521001-20_V4_25_APPROVED.md`; executable `regression/tools/check_521001_20_v425.py`. No numeric Nobi/thread/material/tolerance table or DATA<->PDF threshold is changed.
- **V4.24:** `DATA_MANUFACTURING_CANONICALIZATION`, `DATA_AUTO_R_CANONICALIZATION`, `DATA_TAP_NOMINAL_VALIDATION`; regression `regression/qa/521001-13_V4_24_APPROVED.md`; executable `regression/tools/check_521001_13_v424.py`. No numeric Nobi/thread/material table is changed.
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

Then run the active validation and output contract. A correct bbox, entity count, syntactically valid DXF or successful read-back cannot compensate for a missing source manufacturing family or a bulged source ARC flattened to its chord.

If a source-supported feature has no route, stop with `ROUTING_COVERAGE_GAP`. Do not silently map it to generic CUT.

## 6. Portable and history policy

`skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md` is retained as a complete compatibility/audit snapshot (currently V4.24) so approved historical rule text is not destroyed by repo-direct modular releases. It is **NOT part of the normal repo-direct load path** and is not required to be version-equal to the current repo-direct production release.

It may be read only to diagnose a `ROUTING_COVERAGE_GAP`, audit historical coverage, or perform an explicitly requested portability check. After a gap is found, do not silently continue production from the portable file; fix/approve the missing route first.

Normal production retrieval must exclude:
- `skills/lispcad/versions/**`
- `docs/history/**`

Historical snapshots never override active modular rules.

## 7. Regression and output

Load only regressions relevant to the routed rule/family or an explicit audit. Regression geometry is evidence/tests, not a source of missing dimensions for a new drawing.

Use the current core `VALIDATION.md` and `CAD_OUTPUT.md` contract plus applicable routed modules. Read back the actual saved DXF before calling production complete. For DXF-bearing sources, source/reprojection QA must compare decoded physical curves, not just polyline vertices, bbox, or raw entity count.

## 8. MCP boundary

**MCP is research-only and is NOT part of the production CAD pipeline.**

**Default CAD behavior remains repo-direct.**

Do not route through MCP for ordinary CAD production. Experimental code under `services/trainaicad-mcp/` has no production authority unless the user explicitly asks to work on MCP.
