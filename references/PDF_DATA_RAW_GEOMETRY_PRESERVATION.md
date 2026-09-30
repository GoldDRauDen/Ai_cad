# PDF_DATA_RAW_GEOMETRY_PRESERVATION — V4.21 approved implementation contract

**Status:** USER APPROVED 2026-09-30.

## Scope
Applies to every job where the customer supplies a PDF/image together with corresponding customer CAD/DXF DATA.

- Customer DATA is the **geometry authority** and authoritative geometry source.
- PDF is the semantic/control source for code, material, thickness, view/face meaning, dimension witnesses/datums, drawing scale, revision/handwriting, Nobi, BEND, KEGAKI, RIB, PIASU, feature identity/count and manufacturing semantics.
- Job family `646` is DATA-required by default. If a 646 production job arrives without its corresponding customer DATA, report `DATA_REQUIRED_MISSING`, ask for the DATA, and do not silently fall back to PDF_ONLY.

## Geometry-preservation hard gate
When the same physical geometry exists in customer DATA, do not reconstruct/redraw it from PDF dimensions, bbox, screenshots or visual approximation.

Required flow:
1. Read PDF to lock code/page mapping, semantics, witnesses, scale and formed-face meaning.
2. Extract the actual DATA primitives/curves for the relevant views/faces.
3. Remove drawing-only entities: frame, title block, dimensions, text, hidden/construction lines, duplicated thickness edges and unrelated views.
4. Preserve retained source geometry in its local face/view coordinate system.
5. Assemble/unfold using only proved transforms: translation, rotation, source-proved reflection and source-proved uniform drawing-scale conversion.
6. Apply Nobi/bend rules to placement between faces, not by redrawing face geometry.
7. Canonicalize only when an active PDF/manufacturing rule explicitly controls that parameter; record each canonicalized element separately.

## Scale
Prove physical scale per corresponding PDF page/view. Never apply one common scale to all DATA files merely because they belong to one job. A proved 1:2 source view is converted to physical geometry by x2 before assembly; this is a source transform, not permission to redraw.

## QA / source reprojection
Before production PASS:
- inverse-transform/reproject every non-canonicalized unfolded face/feature back to its extracted DATA source geometry;
- residual may only reflect CAD serialization/numerical precision;
- any visible or measurable redraw drift is FAIL;
- DATA<->PDF dimension thresholds are not redraw tolerances;
- audit CUT, HOLE/SLOT, BEND, KEGAKI and RIB independently;
- bbox/flat-size closure alone is insufficient.

## Forbidden shortcuts
FAIL if existing DATA geometry is rebuilt from printed dimensions; endpoints/radii/centers are rounded without an explicit canonicalization rule; bbox resemblance substitutes for face ownership; scale is forced to make dimensions match; mirror/rotation is inferred without evidence; or small redraw drift is accepted under shop/customer delta thresholds.

## Relationship to V4.20
V4.20 already stated that DATA supplies source geometry 100%. V4.21 makes that statement executable through mandatory geometry harvesting/preservation, transform-only assembly, source reprojection, and the 646 missing-DATA gate.
