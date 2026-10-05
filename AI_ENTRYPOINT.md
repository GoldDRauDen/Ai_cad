# AI ENTRYPOINT — TrainAiCad repo-direct production

Current production release is **V4.30**.

This file is the production routing authority. Normal CAD jobs use **repo-direct modular routing**. Do not load the complete portable skill by default.

## 1. Normal production flow

```text
SOURCE
  -> RUNTIME AUTHORITY GUARD
  -> always-on CORE
  -> SOURCE CLASSIFICATION
  -> DXF PHYSICAL-CURVE DECODE when DXF source/reference exists
  -> SOURCE MANUFACTURING NOTE CENSUS
  -> SOURCE FEATURE-GROUP / REFERENCE-PARAMETER CLOSURE
  -> FEATURE CENSUS
  -> ROUTER
  -> selected mode / feature / reference modules
  -> BEND-EDGE / 90-DEG BEND-END RELIEF GATE when applicable
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

## 2. V4.30 runtime-authority hardening

Load `references/RUNTIME_AUTHORITY_GUARD.md` before inherited core text. Repo-direct authority is:

`USER TASK -> AI_ENTRYPOINT -> ROUTER -> ROUTED MODULES/REFERENCES`.

Inherited compatibility prose inside an active module that says the portable skill must be read in full is `LEGACY_COMPATIBILITY_TEXT`; it does not override repo-direct routing. Likewise, the current routed `CAD_OUTPUT.md` controls packaging over older wording that described automatic individual + combined output.

Portable CURRENT remains compatibility/audit only. A route gap is `ROUTING_COVERAGE_GAP`; do not silently continue from portable/history.

## 3. Census before specialized rules

Inspect the actual source before selecting specialized modules. Build the preliminary census with only `YES`, `NO`, or `UNKNOWN`.

**UNKNOWN != NO.** Every `YES` and `UNKNOWN` family loads its route. After routed modules are loaded, re-check the source and close the final census.

Do not mark a feature absent merely because OCR did not find its keyword. Inspect geometry, leaders, witnesses, notes, revisions, sections/details, barcode/process cues and supplied customer DATA as applicable.

### V4.30 source feature-group gate

Load `references/SOURCE_FEATURE_GROUP_CLOSURE.md` before final preliminary Feature Census.

- Separate broad **FEATURE_FAMILY** from source-scoped **SOURCE_FEATURE_GROUP**.
- Same family and same size do not prove one group. Close each leader/callout group independently through quantity + X witnesses + Y witnesses + datum + host face.
- A shared X chain does not authorize borrowing another group's Y chain.
- Aggregate family quantity is downstream of `GROUP_COUNT_CLOSURE`; a correct total with wrong per-group allocation is FAIL.
- Detail-view paper placement is arbitrary; dimensions inside the detail map through the detail identifier/leader to the physical target.
- Customer/sample/reference geometry does not silently close a genuinely `CUSTOMER_CONFIRMATION_PENDING` source field.
- Before declaring source/reference numeric conflict, pass `SAME_PHYSICAL_PARAMETER_BEFORE_REFERENCE_CONFLICT`: same group, host, physical witnesses, dimension semantics, inside/outside state, frame and units.
- For a bent corner/bend-end junction whose relief status depends on a still-unresolved signed bend-end offset, retain `SLIT_RELIEF = UNKNOWN` until the routed bend-end gate closes it.

### V4.29 source-manufacturing-note gate

Load `references/SOURCE_MANUFACTURING_NOTE_CENSUS.md` as always-on source parsing before final preliminary Feature Census. Every production-affecting printed/handwritten/revision instruction must retain a scoped note->family resolution. A source instruction that proves a family routes it `YES`; a plausible manufacturing instruction with unresolved scope/quantity/host/value/location/direction keeps the relevant family at least `UNKNOWN`, never premature `NO`.

`スリット`/`SLIT` may define a custom source-instructed slit: create that custom branch only when explicitly instructed, preserve any drawing-specific explicit value, and derive quantity/location/direction only from source evidence. Do not hardcode slit size or bend-center placement from a reference. Existing separately-triggered relief mechanisms remain independent.

### V4.28 face-creation gate

For `BEND`, `MULTI_FACE`, or `UNKNOWN` mode candidates, load `references/FACE_CREATION_BEND_EVIDENCE.md` before final FACE_GRAPH closure. A contour direction change, slope, step, recess, protrusion, R/C or silhouette break does not by itself prove a bend/new face. Run `SAME_FACE_FIRST`, require positive bend evidence for each created FACE boundary, and lock the actual local bend material domain before unfold.

### V4.27 weld-cue gate

A proved reversed-e mark immediately above a barcode is `REVERSED_E_ABOVE_BARCODE -> WELD_REQUIRED_CUE` for that barcode/code cluster only. It proves a welding-process expectation, not KEGAKI geometry. Use the routed KEGAKI/RIB logic and do not copy scope to adjacent codes.

### V4.26 physical-curve gate

Whenever DXF geometry participates as customer DATA, reference, or direct-audit evidence, decode physical curves before Feature Census. For `POLYLINE`/`LWPOLYLINE`, nonzero bulge means ARC, not the endpoint chord; closed final->first segments are included. Use `references/DXF_PHYSICAL_CURVE_DECODING.md`.

## 4. Bent / multi-face parts — V4.30 bend-edge and relief gate

Every bent or multi-face part loads `skills/lispcad/modes/BEND_UNFOLD.md`, `references/FACE_GRAPH_UNFOLD_PROTOCOL.md`, `references/FACE_CREATION_BEND_EVIDENCE.md`, and `references/BEND_EDGE_RELIEF_90.md`.

Before production unfold/output:

1. close FACE_GRAPH topology, witnesses, host faces, order, bend sign and material domain;
2. lock each **chiều dài cạnh uốn / bend-edge length** from the actual shared material edge, never from bbox;
3. for a scoped 90-degree bend-end relief candidate, prove signed bend-end offset `S`;
4. apply `BEND_END_OFFSET_90` only within its approved scope:
   - `S > 0` -> NO SLIT from this mechanism;
   - `S = 0` -> slit `T + 0.2` from the actual edge;
   - `S < 0` -> slit `T + 0.2` from the actual recessed edge; the endpoint distance from the zero/outside reference is `|S| + T + 0.2`;
   - there is no active `T/2` threshold/FLAG branch;
5. explicit source custom slit, BOXMET, opposite-fold `R=t`, and non-90-degree relief mechanisms remain separately routed and take precedence when their own triggers are proved;
6. do not create duplicate reliefs for one physical junction.

## 5. Source and mode routing

Classify exactly one source relationship using `references/SOURCE_DATA_CLASSIFICATION.md`:
- `PDF_ONLY`
- `PDF_DATA_RAW`
- `TRAIN_REFERENCE`
- `DIRECT_EXISTING_DXF_AUDIT`

For `PDF_DATA_RAW`, the router loads `references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md`, `references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md` and `references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md`. Customer DATA supplies physical geometry; PDF controls semantics, dimensions, revisions and manufacturing meaning under the approved rules.

V4.25 requires `RAW_DATA_SNAPSHOT`, `PHYSICAL_DATA_BASELINE`, `SAME_PARAMETER_GATE`, `MANUFACTURING_CHANGE_LEDGER` and `UNTOUCHED_DATA_INVARIANCE_CHECK`. V4.26 additionally requires decoded physical LINE/ARC/CIRCLE preservation for bulged polylines.

For reference/sample audits, compare physical geometry, but do not reverse-fit a new source interpretation from sample coordinates. V4.30 additionally requires same-physical-parameter identity before a numeric source/reference conflict is declared.

## 6. Release wiring index — backward-compatible regression contract

- **V4.30:** `RUNTIME_AUTHORITY_GUARD`, `SOURCE_FEATURE_GROUP`, `GROUP_COUNT_CLOSURE`, `SAME_PHYSICAL_PARAMETER_BEFORE_REFERENCE_CONFLICT`, `BEND_EDGE_LENGTH_LOCK`, `BEND_END_OFFSET_90`; active references `references/RUNTIME_AUTHORITY_GUARD.md`, `references/SOURCE_FEATURE_GROUP_CLOSURE.md`, `references/BEND_EDGE_RELIEF_90.md`; regression `regression/qa/521005-05_V4_30_APPROVED.md`; executable `regression/tools/check_521005_05_v430.py`. The 90-degree rule is `S>0 -> NO SLIT`, `S=0 -> T+0.2`, `S<0 -> T+0.2 from actual recessed edge / |S|+T+0.2 from zero reference`.
- **V4.29:** `SOURCE_MANUFACTURING_NOTE_CENSUS`, `SOURCE_NOTE_TO_FAMILY`, `SOURCE_NOTE_FEATURE_COMPLETENESS`, and custom source-instructed `スリット/SLIT`; active reference `references/SOURCE_MANUFACTURING_NOTE_CENSUS.md`; regression `regression/qa/521005-13_V4_29_APPROVED.md`; executable `regression/tools/check_521005_13_v429.py`; physical read-back fixture `regression/assets/521005-13/SLIT_FIXTURE.dxf`. Custom slit size/position is source-specific.
- **V4.28:** `FACE_CREATION_REQUIRES_BEND_EVIDENCE`, `SAME_FACE_FIRST`, `LOCAL_BEND_DOMAIN_BEFORE_UNFOLD`, `THEORETICAL_SHARP_CLOSURE_FOR_R_CONTOURS`; active reference `references/FACE_CREATION_BEND_EVIDENCE.md`; regression `regression/qa/521005-02_V4_28_APPROVED.md`; executable `regression/tools/check_521005_02_v428.py`.
- **V4.27:** `REVERSED_E_ABOVE_BARCODE`, `WELD_REQUIRED_CUE`; regression `regression/qa/521005-01_V4_27_APPROVED.md`; executable `regression/tools/check_521005_01_v427.py`.
- **V4.26:** `DXF_PHYSICAL_CURVE_DECODE_BEFORE_CENSUS`, `PHYSICAL_CURVE_CENSUS`, `POLYLINE_BULGE_IS_ARC`, `BULGE_ARC_NOT_CHORD`; reference `references/DXF_PHYSICAL_CURVE_DECODING.md`; regression `regression/qa/521001-19_V4_26_APPROVED.md`; executable `regression/tools/check_521001_19_v426.py`.
- **V4.25:** `RAW_DATA_SNAPSHOT`, `PHYSICAL_DATA_BASELINE`, `SAME_PARAMETER_GATE`, `MANUFACTURING_CHANGE_LEDGER`, `UNTOUCHED_DATA_INVARIANCE_CHECK`; reference `references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md`; regression `regression/qa/521001-20_V4_25_APPROVED.md`; executable `regression/tools/check_521001_20_v425.py`.
- **V4.24:** `DATA_MANUFACTURING_CANONICALIZATION`, `DATA_AUTO_R_CANONICALIZATION`, `DATA_TAP_NOMINAL_VALIDATION`; regression `regression/qa/521001-13_V4_24_APPROVED.md`; executable `regression/tools/check_521001_13_v424.py`.
- **V4.23:** `SOURCE_PHYSICAL_TO_CANONICAL`, `CANONICAL_TO_SOURCE_PHYSICAL`, `PER_BEND_WITNESS_LEDGER`, `THICKNESS_SINGLE_USE`, `THICKNESS_REPRESENTATION`; regression `regression/qa/521001-03_V4_23_APPROVED.md`; executable `regression/tools/check_521001_03_v423.py`.
- **V4.22:** `SOURCE_EXHAUSTED_BEFORE_VIEWS_ONLY` and `SOURCE_FEATURE_COMPLETENESS`; regression `regression/qa/520930-10_V4_22_APPROVED.md`; executable `regression/tools/check_520930_10_v422.py`.
- **V4.21:** `references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md`; regression `regression/qa/520930-03_V4_21_APPROVED.md`; retain `DATA_REQUIRED_MISSING` and mandatory source reprojection.
- **V4.20:** source/mechanical classification plus independent KEGAKI / SLIT_RELIEF / RIB / CURVED_SLOT routing; regression `regression/qa/520928-20_V4_20_APPROVED.md`, `regression/qa/HD4_V4_20_APPROVED.md`, `regression/qa/SILT_GT90_V4_20_APPROVED.md`; executable `regression/tools/check_v420_source_mech.py`.
- **V4.19:** V4.19 520929-25 hard-gate routing; `references/FACE_GRAPH_UNFOLD_PROTOCOL.md`; regression `regression/qa/520929-25_V4_19_APPROVED.md`; executable `regression/tools/check_520929_25_v419.py`.
- **V4.18:** V4.18 520929-18 hard-gate routing; detailed-source bundle, C/R semantic lock and BOXMET signed orientation; `references/BOXMET_SLIT_RELIEF.md`; regression `regression/qa/520929-18_V4_18_APPROVED.md`; executable `regression/tools/check_520929_18_v418.py`.
- **V4.17:** V4.17 520929-10 hard-gate routing; source witness, mirror scope, datum, KEGAKI and actual-unit guards; regression `regression/qa/520929-10_V4_17_APPROVED.md`; executable `regression/tools/check_520929_10_v417.py`.
- **V4.16:** face-first dimension ownership, explicit R/C family quantity closure and BOXMET four-flange routing through `references/BOXMET_SLIT_RELIEF.md`; regression `regression/qa/520801-04_V4_16_APPROVED.md`.
- **V4.15:** acute bend <85° routing through `references/ACUTE_BEND_LT85_METHOD.md` and `references/ACUTE_BEND_LT85_FROM_SOURCE.md`; regression `regression/qa/ACUTE_BEND_LT85_APPROVED.md`; executable `regression/tools/check_acute_bend_lt85.py`.
- **V4.14:** existing-output direct audit and overlapping-cut QA retained in active core modules; regression `regression/qa/520217-26_V4_14_APPROVED.md`.
- **V4.13:** source-unit conflict, strict derived comparison, inside-view and local-face mapping hardening; regression `regression/qa/520315-18_V4_13_APPROVED.md`.
- **V4.12:** material/preview/shop-distance hardening; regression `regression/qa/520217-27_V4_12_APPROVED.md`.
- **V4.11:** DRAW -> FLAG -> CONFIRM review-only preview; regression `regression/qa/520625-15_V4_11_APPROVED.md`.
- **V4.10:** source-origin/axis mapping; regression `regression/datum/520728-06_043793_TOP_LEFT_APPROVED.md`.
- **V4.9:** one composite DXF output contract; regression `regression/export/DXF_SINGLE_COMPOSITE.md`.
- **V4.8:** cancellation + datum/feature family regression `regression/datum/520709-07_APPROVED.md`.
- **V4.3–V4.7:** approved baseline rules remain in active modular core/mode/feature/reference files as mapped by `skills/lispcad/router/RULE_COVERAGE.yaml`.

The compact index preserves machine-readable/testable release wiring. It is not an instruction to load every listed regression on every job.

## 7. Production completeness

Before production PASS, close:

```text
SOURCE MANUFACTURING NOTES
  -> SOURCE FEATURE GROUPS
  -> SOURCE ACTIVE FAMILIES
  -> FINAL FEATURE CENSUS
  -> LOADED ROUTES
  -> CANONICAL GEOMETRY
  -> SERIALIZED OUTPUT
```

For bent parts also close FACE_GRAPH, per-bend witness ledger, bend-edge material domain and any applicable 90-degree bend-end relief decision before serialization.

A correct bbox, entity count, syntactically valid DXF or successful read-back cannot compensate for a missing source note, missing source group/family, false parameter comparison, wrong bend domain, or missing/extra relief.

If a source-supported family has no route, stop with `ROUTING_COVERAGE_GAP`. Do not silently map it to generic CUT.

## 8. Portable and history policy

`skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md` is retained as a complete compatibility/audit snapshot (currently V4.24). It is **NOT part of the normal repo-direct load path** and is not required to be version-equal to the current repo-direct release.

It may be read only to diagnose `ROUTING_COVERAGE_GAP`, audit historical coverage, or perform an explicitly requested portability check. After a gap is found, do not silently continue production from portable text.

Normal production retrieval excludes:
- `skills/lispcad/versions/**`
- `docs/history/**`

Historical snapshots never override active modular rules.

## 9. Regression and output

Load only regressions relevant to the routed rule/family or an explicit audit. Regression geometry is evidence/tests, not a source of missing dimensions for a new drawing.

Use current `VALIDATION.md` and `CAD_OUTPUT.md`. Read back the actual saved DXF before calling production complete. For DXF-bearing sources, source/reprojection QA compares decoded physical curves, not only vertices, bbox or raw entity count.

## 10. MCP boundary

**MCP is research-only and is NOT part of the production CAD pipeline.** Default CAD behavior remains repo-direct. Do not route through MCP for ordinary CAD production. Experimental code under `services/trainaicad-mcp/` has no production authority unless the user explicitly asks to work on MCP.
