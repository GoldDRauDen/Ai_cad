# DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA — V4.24

**Status:** USER APPROVED 2026-10-01 from 521001-03 direct audit.
**Scope:** every `PDF_DATA_RAW` job. This reference adds no Nobi/material formula.


## V4.24 manufacturing-canonicalization ledger

For `PDF_DATA_RAW`, extend source-role classification with these roles when proved:
- `THREAD_NOMINAL_REFERENCE`: a nominal-diameter circle/ring that identifies the M* thread size; semantic evidence, not a production cut.
- `THREAD_PREHOLE_SOURCE`: the inner/raw pre-hole geometry associated with the same tap feature.
- `MANUFACTURING_CANONICALIZED`: canonical geometry intentionally produced by an active rule from proved source provenance, such as an automatic material Laser R or a standard thread pilot.

For every canonicalized member retain `source_members, host_face, controlling_rule, source_value_or_geometry, canonical_value_or_geometry, serialized_members`.

### DATA_TAP_NOMINAL_VALIDATION
Applies to **every proved `M<n>`**. When the corresponding DATA contains an identifiable nominal-reference diameter, compare `abs(D_DATA_NOMINAL - n)` using the general customer threshold: `Delta < 0.1 mm` passes; `Delta >= 0.1 mm` => `DATA_PDF_DIM_DIFF`. Exactly 0.1 mm flags. Do not use the raw pre-hole/pilot diameter for this nominal-identity comparison.

After identity is locked, the nominal-reference geometry remains non-cut. The raw pre-hole stays as provenance, while the final production hole is the approved M* pilot from `THREAD_PILOT_TABLE.md` unless the PDF explicitly specifies another effective hole diameter. Example only: M6 + nominal DATA Ø6 + inner DATA Ø5.1 -> one production Ø5.0 pilot.

### DATA_AUTO_R_CANONICALIZATION
A sharp DATA vertex does not suppress an active material-table auto-R. If `MATERIAL_RULES.md` requires R at an otherwise uncalled eligible outside corner `<=90°`, canonicalize that local corner to the required tangent R and record the controlling material/thickness row. Explicit source R/C takes precedence. Surrounding unchanged DATA geometry remains subject to exact source reprojection.

These recorded manufacturing canonicalizations satisfy `CANONICAL_TO_SOURCE_PHYSICAL` through explicit rule provenance; unrecorded extra arcs/holes remain FAIL.

## 1. Complete DATA entity census
Before canonical geometry, harvest every relevant DATA primitive/view/face and assign a semantic role: `PHYSICAL_CUT_OR_FACE_EDGE`, `PHYSICAL_HOLE_SLOT_OR_FEATURE`, `BEND_SUPPORT`, `THICKNESS_REPRESENTATION`, `HIDDEN_OR_PROJECTION_ONLY`, `DIMENSION_HELPER_OR_CONSTRUCTION`, `DUPLICATE_COINCIDENT`, or another explicitly documented role. Presence in customer DXF proves provenance, not manufacturing meaning.

## 2. Drawing-only thickness representation
Paired/projection edges whose purpose is only to show sheet thickness may support face/thickness/witness interpretation but MUST NOT enter manufacturing CUT unless independent source evidence proves that exact edge is a real blank boundary.

## 3. Bidirectional source/canonical QA
### SOURCE_PHYSICAL_TO_CANONICAL
Every active physical source family/curve must have host face/transform, retained/canonicalized/canceled status, quantity/value where applicable, and canonical/serialized presence. Any unaccounted active physical geometry is FAIL.

### CANONICAL_TO_SOURCE_PHYSICAL
Every manufacturing canonical/output primitive must map to physical source evidence or an explicit recorded canonicalization. Any extra manufacturing primitive without provenance is FAIL.

Inverse reprojection of only the AI-selected subset does not satisfy these gates.

## 4. Feature-family closure
Retain `family, value/size, quantity, host_face, source members, canonical members, serialized members, cancellation/canonicalization status`. Missing a family member remains FAIL even if the rest of the contour reprojects.

## 5. PER_BEND_WITNESS_LEDGER
Each bend requires `bend_id, face_A, face_B, witnesses, ID_OD_semantics, thickness_terms_and_owners, Nobi, face_order, fold_sign, material_domain, pair_coordinates, fold_back_status`.

### THICKNESS_SINGLE_USE
Every thickness contribution has exactly one owned use. A residual exactly equal to `±t` is a diagnostic pattern for witness/thickness ownership review, not a universal correction formula.

## 6. Reference duplicate normalization
In reference/direct-audit mode, exact coincident/reversed duplicate curves are normalized before physical quantity comparison and reported as `REFERENCE_ANOMALY`. Do not teach duplicate entity count as manufacturing quantity and do not mutate the sample.

## 7. PASS boundary
Production eligibility requires `SOURCE CENSUS -> ROLE CLASSIFICATION -> FAMILY INVENTORY -> FACE_GRAPH -> PER_BEND_WITNESS_LEDGER -> UNFOLD -> SOURCE_PHYSICAL_TO_CANONICAL -> CANONICAL_TO_SOURCE_PHYSICAL -> FAMILY/BEND DOMAIN QA -> FOLD_BACK/REPROJECTION -> DXF SAVE -> READ-BACK`. Downstream read-back cannot override an upstream census/semantic failure.
