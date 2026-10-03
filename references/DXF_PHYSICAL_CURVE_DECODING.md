# DXF_PHYSICAL_CURVE_DECODING — V4.26

**Status:** USER APPROVED 2026-10-03 from job 521001-19 / codes 057688-113 and 057689-114.  
**Scope:** every production/audit workflow that reads DXF geometry as source evidence, including `PDF_DATA_RAW`, `TRAIN_REFERENCE`, and `DIRECT_EXISTING_DXF_AUDIT`. This reference adds no Nobi, material, thread, tolerance, or R/C value.

## 1. FACT / failure mechanism

A DXF `POLYLINE` or `LWPOLYLINE` vertex list is not, by itself, the physical curve topology. A segment whose start vertex has nonzero **bulge** is an ARC, not the straight chord between its endpoint vertices.

Approved 521001-19 diagnosis: customer DATA for 057688/113 and 057689/114 contains quarter-circle bulged segments corresponding to the PDF `2-R3` and `2-R1`. Reading endpoint coordinates while ignoring bulge incorrectly converts those source radii into apparent 45-degree chamfers.

## 2. Mandatory decode before geometry/feature classification

When any source DXF is present, decode the complete physical curve representation **before** contour topology, R/C identity, Feature Census, physical-family inventory, bbox comparison, canonicalization, or reference comparison.

For every relevant entity:

- `LINE` -> physical straight segment.
- `ARC` -> physical circular arc using center/radius/start/end/sweep.
- `CIRCLE` -> physical full circle.
- `LWPOLYLINE` -> evaluate every segment from each vertex to the next using that **start vertex's bulge**.
- old-style `POLYLINE` / `VERTEX` -> evaluate every 2D polyline segment using the `VERTEX` bulge (DXF group 42) belonging to the segment start vertex.
- closed `POLYLINE` / `LWPOLYLINE` -> also evaluate the final-vertex -> first-vertex closing segment, including the final vertex's bulge.
- nested/block geometry -> apply the proved INSERT/block transform before physical comparison; do not classify transformed arc endpoints as a chord.
- unsupported/non-planar curve forms -> retain `UNKNOWN`/FLAG and do not simplify them into LINE merely to continue production.

## 3. Bulge semantics

For endpoints `P0`, `P1` and start-vertex bulge `b`:

- `b = 0` -> LINE from `P0` to `P1`.
- `b != 0` -> circular ARC.
- signed included angle: `theta = 4 * atan(b)`.
- chord length: `c = |P1 - P0|`.
- radius magnitude: `R = c * (1 + b^2) / (4 * |b|)`.
- bulge sign controls sweep orientation; preserve it rather than replacing the arc with its chord.

For a 90-degree quarter circle, `|b| = tan(90°/4) = 0.41421356237...`. Therefore endpoint deltas that visually resemble `3 x 3` or `1 x 1` are not evidence of `C3` or `C1` when the controlling segment carries this bulge; the decoded physical curves are R3 or R1 respectively when the radius calculation closes.

Use a CAD/DXF library's exact virtual/arc geometry when available. The formulas above are an independent audit definition, not permission to refit source curves.

## 4. PHYSICAL_CURVE_CENSUS

Before semantic feature classification, retain an evidence-equivalent census for every relevant source curve:

`source_entity, source_vertex_or_segment, curve_type, endpoints, bulge_if_any, center_if_arc, radius_if_arc, signed_sweep_if_arc, closed_segment_status, transform, physical_role`.

`curve_type` must reflect decoded physical geometry (`LINE`, `ARC`, `CIRCLE`, other proved curve), not entity-container appearance.

A `POLYLINE` container may therefore contribute a mixture of LINE and ARC physical segments.

## 5. R/C semantic interaction

DXF physical decoding answers **what physical curve exists in DATA/reference**. PDF/source callouts still control manufacturing semantics according to the active source-mode authority rules.

- Never classify `C` merely because two adjacent polyline vertices have equal X/Y offsets.
- Never classify `R` merely because a callout says R while DATA was not physically decoded.
- First decode DATA physical curves; then compare the decoded result with PDF/source R/C semantics and quantity/scope.
- A true DATA arc may be represented later as ARC or exact bulged LWPOLYLINE; representation change is acceptable only when the physical curve is invariant or an explicit manufacturing rule records the changed scope.

## 6. Hard QA gates

### DXF_SOURCE_BULGE_DECODE_COMPLETE
For every relevant source `POLYLINE`/`LWPOLYLINE`, account for every segment and bulge, including the closed final->first segment.

### BULGE_ARC_NOT_CHORD
If any relevant segment has `|bulge| > CAD numerical zero`, its physical source type is ARC. Production FAIL if the source physical census or unchanged canonical geometry treats that segment as a straight chord.

### PHYSICAL_CURVE_REPROJECTION
Source reprojection/reference comparison must compare physical LINE/ARC/CIRCLE geometry: endpoints plus center/radius/sweep for arcs. Vertex equality, bbox equality, chord equality, raw entity count, or a visually similar polyline is insufficient.

### R_C_SOURCE_CLOSURE
When PDF/source declares R/C, compare the callout family/value/count against the decoded physical DATA/reference curve family. Do not report `SOURCE_CONFLICT` until both sides have been decoded/classified correctly.

No production PASS is permitted when a relevant bulged source segment is unaccounted, flattened to a chord, or omitted from physical-curve QA.

## 7. Relationship to V4.25

V4.25 requires `RAW_DATA_SNAPSHOT`, physical baseline, representation-equivalent geometry and untouched-DATA invariance. V4.26 clarifies that the raw/physical baseline itself must contain **decoded physical curves**. Preserving only polyline endpoint vertices while dropping bulge is not 100% DATA harvest and is not representation equivalence.

This change does not modify numeric manufacturing tables or the DATA<->PDF threshold.