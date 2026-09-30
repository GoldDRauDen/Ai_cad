# SOURCE_DATA_CLASSIFICATION — V4.21 approved source routing

**Status:** USER APPROVED V4.20 2026-09-29; V4.21 geometry-preservation hardening approved 2026-09-30.

**V4.21 hard gate:** for every PDF + customer DXF DATA job, existing DATA geometry must be harvested/preserved and assembled by proved transforms; do not redraw the same geometry from PDF dimensions. Load `references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md`. Job family `646` is DATA-required by default: if its customer DATA is absent, report `DATA_REQUIRED_MISSING` and ask for it instead of silently using PDF_ONLY.

## 1. Four source relationships

### PDF_ONLY
PDF/image is the source geometry. During explicit training/calibration workflows, absence of an unprovided DATA DXF is not a reason to ask whether one exists; continue from PDF. In ordinary production, if a page visibly carries a boxed/stamped `DATA` mark but its CAD DATA is absent, report `DATA_EXPECTED_MISSING` when the current task requires that DATA.

### PDF_DATA_RAW
Use when customer CAD/DXF is supplied together with the corresponding PDF/page. A boxed/stamped `DATA` mark on the PDF is evidence that CAD DATA exists for that page. PDF + DXF supplied together defaults to `PDF_DATA_RAW` unless the user explicitly declares the DXF to be a clean/sample/approved/training reference.

Authority split:
- **DATA supplies source geometry 100%**: source lines/arcs/curves, face/view outlines, hole/slot geometry and locations.
- **PDF supplies semantics/control**: code, material, thickness, printed dimensions/witnesses, Nobi, revision/handwriting, feature identity/count and BEND/KEGAKI/RIB/PIASU meaning.

Pipeline:
`PDF semantic lock -> DATA geometry extraction -> classify views/faces -> remove text/dimension/hidden/construction/thickness duplicates -> map feature ownership -> assemble/unfold -> canonicalize explicitly PDF-controlled parameters -> QA DATA<->PDF -> export/read-back`.

Do not redraw the whole part, face contour, radius/relief, hole/slot center, or other existing physical geometry from PDF dimensions/picture approximation when that geometry exists in customer DATA. Harvest it, clean it and preserve it. Use proved transforms to assemble/unfold. Nobi changes placement between preserved faces; it is not permission to recreate those faces.

Before PASS, inverse-transform/reproject every non-canonicalized unfolded face/feature to its extracted DATA source. Any measurable redraw drift beyond CAD serialization/numerical precision is FAIL. The DATA<->PDF numeric gate below is not a redraw tolerance.

### TRAIN_REFERENCE
User explicitly declares the DXF as sample, clean/extracted drawing, approved/ground-truth CAD or training comparison artifact. It is audit/calibration evidence, not raw DATA for direct extraction. For NEW construction, interpret source independently first.

### DIRECT_EXISTING_DXF_AUDIT
When evaluating an already-exported AI DXF against an approved reference, compare those two DXFs first in proved physical units/orientation, report MATCH/PARTIAL/DIFF per code, then use PDF/source to diagnose causes.

## 2. DATA <-> PDF numeric gate

Compare only the same physical parameter after correct code/view/feature/datum/unit mapping.

For every customer except KH433:
- `Delta < 0.1 mm` -> NO FLAG.
- `Delta >= 0.1 mm` -> FLAG `DATA_PDF_DIM_DIFF`.

Exactly 0.1 mm FLAGS.

For KH433, only when explicitly identified as that customer:
- `Delta < 1.0 mm` -> accepted DATA noise if topology and feature identity/count are unchanged.
- `Delta >= 1.0 mm` -> FLAG.

Numeric allowance never waives topology, feature family/count, bend order, revision/cancellation, unit, mirror, KEGAKI/PIASU/SLIT/RIB identity, self-intersection or duplicate-toolpath errors.

## 3. Canonicalization
When a parameter is explicitly controlled by PDF and DATA differs within the applicable threshold, retain DATA as geometry/topology provenance but canonicalize that production parameter to the exact PDF value without FLAG. At or above threshold, report both values and FLAG instead of silently forcing agreement. For geometry not explicitly dimension-controlled by PDF, retain cleaned DATA geometry rather than inventing rounded values.


## 4. V4.21 646 DATA-required routing
For production job family `646`, corresponding customer DATA is expected by default. If it is absent: status `DATA_REQUIRED_MISSING`; ask for DATA; do not silently downgrade to `PDF_ONLY`; do not generate production geometry until resolved. Once DATA is present, the same universal PDF_DATA_RAW geometry-preservation rules apply as for every other job.
