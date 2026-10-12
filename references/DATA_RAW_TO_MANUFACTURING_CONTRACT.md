# DATA_RAW_TO_MANUFACTURING_CONTRACT — V4.25

**Status:** USER APPROVED 2026-10-02 from 521001-20 direct audit.
**Scope:** every `PDF_DATA_RAW` production job.

## 1. Core sequencing — DATA first, manufacturing second

`PDF_DATA_RAW` means:

`RAW_DATA_SNAPSHOT -> PHYSICAL_DATA_BASELINE -> PDF semantic lock -> SAME_PARAMETER_GATE -> MANUFACTURING_CHANGE_LEDGER -> MANUFACTURING_CANONICAL -> UNTOUCHED_DATA_INVARIANCE_CHECK -> source reprojection -> DXF save/read-back`.

The customer DXF DATA is the geometry source. The PDF is the semantic/manufacturing control source. Do not use PDF dimensions to recreate geometry that already exists in DATA.

## 2. RAW_DATA_SNAPSHOT and PHYSICAL_DATA_BASELINE

Before any tolerance, Nobi, thread-pilot, R/C or other manufacturing adjustment:

1. Harvest every relevant DATA primitive/view/face.
2. Freeze an immutable `RAW_DATA_SNAPSHOT` containing the source geometry/provenance.
3. Classify every harvested primitive by semantic role.
4. Build `PHYSICAL_DATA_BASELINE` from the source-supported physical manufacturing geometry after excluding drawing-only text/dimensions, hidden/projection-only helpers, thickness-representation-only edges and proved duplicates.

`100% DATA` means **100% source harvest/accounting before manufacturing**, not that title blocks or drawing-only entities must be serialized, and not that active manufacturing rules are disabled.

## 3. SAME_PARAMETER_GATE before canonicalization

**2026-10-12 override:** first check the explicit numeric customer-code policy from `CUSTOMER_CAD_RULES.yaml`. `DATA_NO_DIM_COMPARE` bypasses ONLY the PDF-vs-DATA numeric discrepancy test. Full M/Ø/hole count/location/identity, source membership, topology, provenance and read-back remain mandatory; discrepancies require local REVIEW. No matching customer-code record => general gate below. Do not confuse job-family 646 with customer-code 646.


The DATA<->PDF threshold is evaluated only between the **same physical parameter** after code/view/feature/datum/unit mapping.

For the normal customer threshold:
- `Delta < 0.1 mm` -> same-parameter gate passes.
- `Delta >= 0.1 mm` -> `DATA_PDF_DIM_DIFF`; exactly `0.1 mm` flags.

A passed gate **does not by itself authorize changing DATA to the PDF nominal**. If no active manufacturing rule controls that parameter, retain the DATA physical geometry unchanged even when the PDF nominal differs by less than the threshold.

A failed gate blocks automatic canonicalization of that conflicting parameter. Keep the DATA value/geometry, FLAG the local conflict, and continue unrelated proved families under the normal local-uncertainty rules.

Different physical parameters must never be compared through this gate. Example: a DATA `THREAD_PREHOLE_SOURCE` diameter is not the same parameter as PDF `M<n>` nominal thread diameter. An identifiable `THREAD_NOMINAL_REFERENCE` is the comparable parameter.

## 4. MANUFACTURING_CHANGE_LEDGER

Any intentional physical change from `PHYSICAL_DATA_BASELINE` to production geometry requires one ledger record:

`source_members, host_face, source_geometry_or_value, same_parameter_gate_status, controlling_rule, changed_scope, canonical_geometry_or_value, serialized_members`.

Allowed changes are only those caused by an active routed manufacturing rule with proved scope, including as applicable:
- mid-tolerance / limit-dimension conversion;
- M* thread-pilot conversion;
- explicit PDF R/C;
- material-table automatic Laser R;
- Nobi / bend placement between preserved faces;
- another explicitly routed production rule.

The ledger is local. A rule that changes one edge, corner, hole diameter or face placement does not authorize refitting, rounding or simplifying neighboring DATA geometry.

## 5. UNTOUCHED_DATA_INVARIANCE_CHECK

Every physical DATA member outside all approved `changed_scope` regions must remain physically identical after canonicalization and final serialization, modulo proved rigid/uniform source transforms and normal CAD floating-point serialization precision.

Production FAIL if an untouched endpoint, center, radius, sweep, straight/curved boundary, slot/hole location or other physical curve drifts because of:
- PDF redraw;
- rounding/snapping;
- analytic refit/simplification;
- bbox reconstruction;
- arbitrary tangent rebuilding;
- tolerance used as a redraw allowance.

The `0.1 mm` DATA<->PDF threshold is **not** an allowed geometry-drift tolerance.

## 6. Representation equivalence

Entity type identity is not required when physical geometry is unchanged. Exact LINE/ARC/CIRCLE geometry may be serialized as an equivalent LWPOLYLINE/bulge representation, and vice versa, if the represented physical curves are identical within CAD numerical precision and topology/feature semantics remain unchanged.

Therefore AutoCAD `OVERKILL` behavior or raw entity count is not a production acceptance criterion. Prefer retaining source primitives when that is simpler and less error-prone; re-encoding is acceptable only after exact physical-equivalence QA.

## 7. 521001-20 approved examples

- DATA nominal `855` matching PDF nominal `855`, followed by the applicable source tolerance, may become manufacturing `854.75`; the change is a tolerance canonicalization, not PDF redraw.
- DATA nominal `600` matching PDF nominal `600`, followed by the applicable source tolerance, may become manufacturing `599.75`.
- PDF M5 + DATA nominal-reference `Ø5` + raw pre-hole `Ø4.134` locks M5 identity from the nominal-reference comparison; final laser pilot is `Ø4.2` under the active thread-pilot rule. The raw pre-hole is provenance, not a nominal-thread delta input.
- DATA physical height `60.000709679` versus PDF nominal `60` is below the general threshold. If no manufacturing rule controls that height, retain `60.000709679`; do not snap it to `60.000` merely because the PDF prints 60.

## 8. PASS boundary

For `PDF_DATA_RAW`, production PASS requires all of:

`RAW_DATA_SNAPSHOT_COMPLETE`
`PHYSICAL_DATA_BASELINE_COMPLETE`
`SAME_PARAMETER_GATE_CLOSED`
`MANUFACTURING_CHANGE_LEDGER_COMPLETE`
`UNTOUCHED_DATA_INVARIANCE_PASS`
`SOURCE_PHYSICAL_TO_CANONICAL_PASS`
`CANONICAL_TO_SOURCE_PHYSICAL_PASS`
`SOURCE_REPROJECTION_PASS`
`SAVED_DXF_READBACK_PASS`.

A valid DXF, matching bbox, successful OVERKILL, or reference/sample resemblance cannot compensate for a missing source member, unlogged manufacturing change or untouched-DATA drift.
