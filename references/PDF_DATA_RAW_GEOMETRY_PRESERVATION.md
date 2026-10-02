# PDF_DATA_RAW_GEOMETRY_PRESERVATION — V4.25 DATA-first hardening over V4.24

## V4.25 RAW DATA freeze before manufacturing canonicalization

For every `PDF_DATA_RAW` job, load `DATA_RAW_TO_MANUFACTURING_CONTRACT.md` and enforce this order before any production geometry is called complete:

`RAW_DATA_SNAPSHOT -> PHYSICAL_DATA_BASELINE -> SAME_PARAMETER_GATE -> MANUFACTURING_CHANGE_LEDGER -> MANUFACTURING_CANONICAL -> UNTOUCHED_DATA_INVARIANCE_CHECK`.

- **Freeze/account first:** harvest and classify the complete relevant customer DATA before tolerance, M* pilot, R/C, Nobi or another manufacturing adjustment is applied. `100% DATA` means complete source geometry/provenance accounting before manufacturing; drawing-only text/dimensions/hidden helpers/thickness-representation-only edges may still be excluded by proved semantic role.
- **No-rule low delta stays DATA:** a DATA<->PDF same-parameter difference below the applicable threshold is not permission to snap the DATA geometry to the PDF nominal. If no active manufacturing rule controls that parameter, retain the physical DATA value/curve unchanged.
- **Rule-scoped change only:** every intentional change after the freeze must have a proved controlling rule and local `MANUFACTURING_CHANGE_LEDGER` entry. Valid examples include source tolerance/mid-tolerance, M* pilot conversion, explicit R/C, material-table automatic Laser R and Nobi/bend placement.
- **Conflict does not self-correct:** a same-parameter difference at/above the threshold is `DATA_PDF_DIM_DIFF`; retain/flag the conflicting DATA parameter instead of silently forcing it to PDF. Continue unrelated proved geometry under normal local-uncertainty policy.
- **Untouched means physically invariant:** outside approved changed scopes, source endpoints, centers, radii, sweeps and curve geometry must survive within CAD numerical/serialization precision. The threshold is not a redraw tolerance.
- **Representation-neutral:** LINE/ARC/CIRCLE may be re-encoded as an exactly equivalent LWPOLYLINE/bulge representation, or vice versa, when physical curves/topology do not change. Prefer direct source primitives when they are simpler/safer. Raw entity count and AutoCAD `OVERKILL` are not acceptance criteria.

521001-20 approved examples: tolerance may legitimately produce `855 -> 854.75` and `600 -> 599.75`; proved M5 may produce raw pre-hole `Ø4.134 -> Ø4.2` through the thread-pilot rule; an otherwise uncontrolled DATA height `60.000709679` versus PDF `60` must remain `60.000709679` because the sub-threshold comparison alone does not authorize snapping.

## V4.24 manufacturing canonicalization after 100% DATA harvest

Customer DATA remains the source geometry/provenance authority, but `100% DATA` is a source-harvest rule, not a blanket instruction to serialize every raw DATA parameter unchanged. After source roles, host faces and feature identity are locked, apply every active manufacturing rule that explicitly controls production geometry.

- **Automatic Laser R:** an otherwise uncalled eligible outside corner `<=90°` must receive the active material/thickness Laser R from `MATERIAL_RULES.md` even when the harvested DATA corner is sharp. Record the local sharp-vertex -> tangent-R replacement as `DATA_AUTO_R_CANONICALIZATION`. Explicit source R/C still wins at its own corner.
- **Tapped M* holes:** preserve DATA center, quantity, host face and source role. Nominal-reference geometry and raw pre-hole geometry are evidence, not automatically final CUT geometry. Final pilot representation follows `HOLES_TAPS.md` + `THREAD_PILOT_TABLE.md` unless the PDF explicitly controls another effective hole diameter.
- A canonicalized R/pilot is allowed in `CANONICAL_TO_SOURCE_PHYSICAL` only with an explicit rule/provenance record. Every unchanged neighboring DATA segment/feature still must inverse-reproject to source within CAD numerical/serialization precision.
- FAIL if an implementation cites `DATA 100%` as the reason to omit required automatic R, preserve a raw tap pre-hole instead of the controlled pilot, or serialize a tap nominal-reference circle as an extra production cut.

## V4.23 physical DATA census and bidirectional closure

Before canonical geometry, classify every relevant harvested DATA primitive as one of:
- `PHYSICAL_CUT_OR_FACE_EDGE`
- `PHYSICAL_HOLE_SLOT_OR_FEATURE`
- `BEND_SUPPORT`
- `THICKNESS_REPRESENTATION`
- `HIDDEN_OR_PROJECTION_ONLY`
- `DIMENSION_HELPER_OR_CONSTRUCTION`
- `DUPLICATE_COINCIDENT`
- another explicitly proved physical/nonphysical role.

A DATA primitive is not automatically manufacturing geometry merely because it is present in customer CAD. Paired edges shown only to represent sheet thickness in Side/Section views remain `THICKNESS_REPRESENTATION` unless source semantics independently prove that edge is an actual cut boundary.

After unfold/canonicalization, run both `SOURCE_PHYSICAL_TO_CANONICAL` and `CANONICAL_TO_SOURCE_PHYSICAL`. Passing inverse reprojection for only the subset selected by the AI is insufficient. Missing physical source geometry and extra manufacturing geometry are both production FAIL. Load `DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md`.


**Status:** USER APPROVED 2026-09-30; V4.25 hardening approved 2026-10-02.

## Scope
Applies to every job where the customer supplies a PDF/image together with corresponding customer CAD/DXF DATA.

- Customer DATA is the **geometry authority** and authoritative geometry source.
- PDF is the semantic/control source for code, material, thickness, view/face meaning, dimension witnesses/datums, drawing scale, revision/handwriting, Nobi, BEND, KEGAKI, RIB, PIASU, feature identity/count and manufacturing semantics.
- Job family `646` is DATA-required by default. If a 646 production job arrives without its corresponding customer DATA, report `DATA_REQUIRED_MISSING`, ask for the DATA, and do not silently fall back to PDF_ONLY.

## Geometry-preservation hard gate
When the same physical geometry exists in customer DATA, do not reconstruct/redraw it from PDF dimensions, bbox, screenshots or visual approximation.

Required flow:
1. Read PDF to lock code/page mapping, semantics, witnesses, scale and formed-face meaning.
2. Extract the actual DATA primitives/curves for the relevant views/faces and freeze/account them before manufacturing adjustment.
3. Remove drawing-only entities: frame, title block, dimensions, text, hidden/construction lines, duplicated thickness edges and unrelated views only after role classification.
4. Preserve retained source geometry in its local face/view coordinate system.
5. Assemble/unfold using only proved transforms: translation, rotation, source-proved reflection and source-proved uniform drawing-scale conversion.
6. Apply Nobi/bend rules to placement between faces, not by redrawing face geometry.
7. Canonicalize only when an active PDF/manufacturing rule explicitly controls that parameter; record each canonicalized element separately and preserve all geometry outside its changed scope.

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
V4.20 already stated that DATA supplies source geometry 100%. V4.21 made that statement executable through mandatory geometry harvesting/preservation, transform-only assembly, source reprojection, and the 646 missing-DATA gate. V4.25 further makes the pre-manufacturing DATA snapshot and local change scope explicit so valid production canonicalization cannot leak into unrelated DATA geometry.
