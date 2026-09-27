# TrainAiCad V4.9 Core — ONE labeled composite DXF by default

## V4.12 approved local-FLAG precedence

Keep a source-proved flat even when a separate round-hole Ø or center awaits confirmation: represent only the unresolved hole dimension/position with Magenta `CIRCLE` and adjacent `Ø?`/coordinate FLAG. Never make an unknown Ø a guessed capacity POINT. Use the existing V4.11 separate labeled source views only if no defensible flat/unfold order exists. No PREVIEW can be called production PASS; the entire mixed-confidence composite stays `REVIEW ONLY — NO CUT`. Routine shop bridge/spacing/bend-proximity acceptance questions are suppressed, without weakening actual geometric containment, source tracing or material-capacity checks.

## V4.11 approved non-production provisional clusters

The default remains exactly ONE top-to-bottom code-labeled DXF. When a drawing supports a plausible but not fully proved shape, retain exact confirmed geometry and include the assumed portion in **Magenta Layer-0** with an adjacent Magenta explanatory FLAG; label the code `PREVIEW`. Truly estimated numeric values are integer-rounded. If the flat shape or bend sequence cannot be inferred responsibly, include independently proved source/orthographic views as **separate labeled subgroups** under that code and mark `VIEWS_ONLY`; do not silently omit it. Any estimate or unresolved view makes the entire combined file `*_ALL_REVIEW_ONLY.dxf` with **NO CUT**. Explicit user QA confirmation closes only its specific resolved question, and later changes require full Section 5 and saved-DXF validation. This V4.11 approval supersedes previous **numeric-only preview** constraints for non-production output, not production shape/type/datum requirements. See portable §4.4.1 and [520625-15 approved regression](../../../regression/qa/520625-15_V4_11_APPROVED.md).

**Current V4.9 user-approved output:** ONE top-to-bottom composite DXF, with exact code labels outside each nonoverlapping part cluster; per-code files and manifest only by explicit request. Incomplete flats remain source-view groups under the correct code; any FLAG makes the entire combined file `REVIEW_ONLY - NO CUT`. This changes only packaging, not the V4.8-approved or earlier manufacturing rules. AutoLISP remains explicit-request only.

**V4.8 upstream gate:** Write canceled source-family provenance and effective zero-count into canonical job trace, omit all deleted hole entities, and verify that the deleted group is also absent in the translated composite. No CAD serialization or DXF schema change; only user-confirmed PDF reading, counts and regression cases were approved.

## 8.1 ONE independently verified canonical geometry model

Before generating any file, apply ALL current V4.6 Section 2–7 PDF-first rules: real outline topology, actual witness-line datum graph, independent quantity counts, material/thickness/handwritten evidence, approved material-table Laser R, scoped POINT/CIRCLE decisions, mid-tolerance, ID→OD rounding, Nobi, exact face/bend order, local-face→global-flat transforms, containment and bend-domain checks. A user-declared reference DXF may be used for calibration AFTER independent drawing interpretation, not as a hidden coordinate source.

Store part-local coordinates in millimeters, one record per declared drawing code, with provenance/trace records and one canonical sequence of CAD primitives. Use THIS SAME geometry for the default combined DXF, optional individual files and optional Lisp; never solve dimensions independently a second time.

Canonical job fields: `job_id`, ordered `parts`. Part fields: `code`, `material`, `thickness_mm`, `status` (`PASS` or explicitly non-production `PREVIEW`), independently executed `checks`, optional `flags`, and ordered `entities`.

Canonical entity representations:
- `LWPOLYLINE`: `vertices:[[x,y,bulge],...]`, `closed:true` for one CCW proved outer outline and each CW interior cutout or slot. No duplicate final vertex; no fake bounding rectangle. Bake all qualified C/R into true tangent points/bulges, no faceting.
- `CIRCLE`: `center:[x,y]`, positive `radius` for a verified cut hole or thread-pilot hole *after* V4.6 decisions.
- `POINT`: `point:[x,y]`, actual point entity, never a tiny circle. Ordinary POINT is ByLayer; only explicitly scoped PDF PIERCING+THROUGH HOLE yields a Green POINT.
- `LINE` (start/end) and `ARC` (center/radius/start_angle/end_angle, degrees) for proven manufacturing line/relief; double bend lines DASHED and clipped to real material. The approved `055958` one Green slit comprises two LINEs + one ARC R0.5 connected end-to-end; 3 entities = 1 operation, never a universal R0.5 slit formula.
- `TEXT` is allowed ONLY as adjacent Magenta warning on an expressly requested numeric-only non-production preview; never add code labels to production modelspace.

Slot source semantics must be classified first: `L_TOTAL` means actual end-to-end; `W` means end circle diameter; center distance `C` becomes `L_TOTAL=C+W`. Use one closed LWPOLYLINE with two straight tangents and two semicircular bulges of magnitude 1. Do not encode a source center distance as overall length.

## 8.2 DXF header, Layer 0 and V4.6 entity legend

Write real DXF with millimeter `$INSUNITS=4`, `$MEASUREMENT=1`, decimal `$LUNITS=2`, display-only precision `$LUPREC=2`. Preserve numeric calculation precision; do NOT truncate CAD coordinates to two decimals. Define the `DASHED` linetype. ALL actual geometry stays on Layer `0`. Only non-cut, automatically generated code/status/FLAG `TEXT` uses dedicated non-plot `AI_META`, with gray code labels or Magenta review notes.

| V4.6 feature | DXF entity | Color 62 | Linetype |
| :-- | :-- | :-- | :-- |
| Outer/inner contour and slot | Closed LWPOLYLINE with real bulges | ByLayer (omit/256) | ByLayer |
| Verified cut circle/M pilot | CIRCLE | ByLayer | ByLayer |
| Ordinary PIERCING or capability POINT | actual POINT | ByLayer | ByLayer |
| Explicit PDF PIERCING + THROUGH HOLE | actual POINT | Green 3 | ByLayer |
| Kegaki/formed mark | LINE or proved LWPOLYLINE | Red 1 | ByLayer |
| Double bend lines on material only | LINE ×2 | ByLayer | DASHED |
| Proven explicitly Green slit/relief | LINE or ARC per source | Green 3 | ByLayer |
| Numeric-only non-production estimate and adjacent note | appropriate entity and TEXT | Magenta 6 | ByLayer |

Do NOT reintroduce superseded V4.3 blanket DXF-only R0.5 omission, green-by-default Piasu or universal minimum-hole rules. Apply V4.6 approved material workbook and case-specific precedence in every export. A source-only feature/quantity unknown blocks production instead of inventing it.

## 8.3 V4.9 mandatory single composite

Default **one DXF only**: `<JOB>_ALL.dxf` if every code has independent manufacturing PASS; otherwise `<JOB>_ALL_REVIEW_ONLY.dxf` including all codes and visible **NO CUT** annotation. Individual DXFs/manifest are NOT default and require explicit request. Preserve Stage 1 per-code status/report without delivering unnecessary individual CAD files.

Use the declared page-1 code order strictly top-to-bottom, with >=10 mm **layout-only** clearance between part/view-group geometry bboxes, no overlaps and no geometric rescaling. Every code appears exactly once beside its own cluster as generated `TEXT` on non-plot `AI_META`, not as a Layer-0 cut path. Internally record code, status, bbox, XY translation, flags and per-code machining entity counts even when the user did not request an external manifest.

For known-topology numeric-only uncertainty: preserve all proved sizes and positions, isolate an integer-rounded Magenta estimate plus adjacent Magenta FLAG note. For unknown unfold dimensions/order: output only independently proved orthographic/source views, grouped and labeled by source view under the correct code (`VIEWS_ONLY`), never a fabricated flat. If a temporary Ø is user-authorized, label it `Ø?` and treat it as review-only, not a verified hole. If there is not enough evidence even to draw a source view or assign the correct code, STOP and ask.

A single unresolved `PREVIEW`/`VIEWS_ONLY`/FLAG invalidates *production use of the entire composite*, even if other part clusters are individually correct. An explicitly requested legacy dual export may be supplied for compatible jobs but never silently substituted for the V4.9 default.

## 8.4 Executed verification, read-back and limitations

Execute all V4.8/Section 5 checks for every production PASS part before serialization. A source view with no proveable flat retains explicit `VIEWS_ONLY` flags and does NOT inherit invented PASS results. Numeric-only PREVIEW needs source-supported topology and Magenta explanatory warnings.

Reopen/audit the ONE saved DXF for units mm, all manufacturing primitives Layer 0 and their approved properties, actual CCW/CW bulges and counts, source-cluster geometry equality by inverse XY translation, correct distinct descending-Y source-code labels on non-plot `AI_META`, >=10 mm layout gaps and explicit NO CUT filename/global note whenever a FLAG exists. Metadata labels are never holes, slots, bend lines, or cut primitives. Check canceled families for zero surviving machining entities. Labels must be excluded from CAM toolpaths.

The exporter performs structural serialization, schema, packaging and read-back checks; it never proves PDF datum/face order, missing Nobi, material selection or full manufacturing containment. Do not claim otherwise.

## 8.5 Optional request-only AutoLISP

Only if explicitly requested, generate existing approved `c:DRAW` AutoLISP and dynamic DCL (multi-select `*parts*`, temporary DCL under `TEMPPREFIX`, placement `getpoint`) from THE SAME verified canonical entities, not a second PDF coordinate solution. Initialize `INSUNITS=4`, `LUNITS=2`, `LUPREC=2`. No interactive geometry picking with FILLET/CHAMFER/SLOT/OFFSET. Optional legacy `*parts*` fields remain drawing code, material, thickness, OUTLINE, OUTER_FILLETS, CHAMFERS, BEND_LINES, CORNER_RELIEFS, INTERNAL_FILLETS, HOLES, KEGAKI_LINES and PIASUS. Legacy `(SLOTX L_TOTAL W)` / `(SLOTY L_TOTAL W)` use OVERALL slot length. Retain V4.6 Layer 0 and all color/POINT rules. Lisp is never automatic fallback when DXF generation is unavailable.

## 9. DXF-first compact dual-stage response

**Stage 1:** concise per-code barcode/material/thickness/proved flat extent table, real geometry-affecting corrections (handwritten Nobi, mid-tolerance, rounded ID→OD, table selection/material R), one aggregate PASS only for actually executed checks, and EVERY FAIL/FLAG/WARN/outstanding customer confirmation. Do not bury unproven dimensions or claim that bounding extents prove topology.

**Stage 2 (default):** link exactly ONE verified top-to-bottom composite DXF, `_ALL.dxf` when all parts PASS or `_ALL_REVIEW_ONLY.dxf` when any part remains FLAG/VIEWS_ONLY/PREVIEW. Only explicit request produces individual DXFs and manifest. Generate Lisp only when explicitly requested. An audit-only request skips CAD emission. When critical topology/type/datum/bend/material is unresolved, stop before speculative production files; when the environment cannot create or verify DXF links, report that limitation instead of inventing attachments or silently outputting Lisp.

### V4.14 physical-geometry equivalence when auditing user DXF

An audit of already generated AI CAD against a declared customer-reference CAD compares actual manufactured curves after verified unit/part-local-frame normalization; equivalent LINE+ARC versus closed LWPOLYLINE with true bulges need NOT have identical entity types or raw entity totals. However, prove exactly matching contour topology, source family membership/counts and positions, radius/chamfer geometry, the complete unfolded part and each true bend pair clipped to material. Regression-match parts remain invariant before/after repacking and any corrections elsewhere. For NEW production DXF, the existing canonical Layer-0 LWPOLYLINE/bulge export contract and mandatory independent PDF/Section-5 checks remain unchanged.
