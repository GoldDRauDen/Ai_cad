# LISPCAD Core — Cross-feature validation

## Scope

Always run after feature routing and before production DXF export. This module adds no new dimensional formula; it prevents individually-correct feature modules from producing an incorrect combined part.

## Mandatory interactions

- **HOLE/TAP ↔ BEND:** preserve host-face ownership and the proved local-face -> flat transform. Do not move printed geometry merely to satisfy a generic shop-distance advisory.
- **KEGAKI ↔ BEND/MULTI_FACE:** transform each mark with its owning face and verify fold-back locating function, count and segmentation.
- **SLIT/RELIEF ↔ BEND:** verify the slit/relief mechanism, direction, connectivity and actual BEND interaction. BOXMET rules apply only when BOXMET topology is proved.
- **CHAMFER/FILLET ↔ MATERIAL auto-R:** explicit source R/C semantics and quantities take precedence over automatic material corner treatment.
- **TAP ↔ HOLE:** thread-to-pilot conversion changes the manufactured diameter representation, not source family quantity or datum ownership.
- **PIASU ↔ HOLE/MATERIAL:** apply the active point/circle and material-capacity rules without changing source quantity or identity.
- **REVISION/CANCELLATION ↔ every family:** cancellation is scoped to the actual callout/leader/family. Never delete neighboring families by proximity.
- **RIB ↔ KEGAKI:** RIB-part CUT/HOLE and main-part locating KEGAKI are independent families; cancellation of one does not imply cancellation of the other.
- **WELD_REQUIRED_CUE ↔ RIB/support ↔ KEGAKI (V4.27):** `REVERSED_E_ABOVE_BARCODE` is scoped to its associated barcode/code cluster and proves a welding-process expectation, not KEGAKI geometry. If a welded child cannot self-locate, locating KEGAKI must be source-proved/derived from actual contact function or remain locally `UNKNOWN`/FLAG; it must not disappear from the final family closure. A specific KEGAKI instruction is independently sufficient. If neither barcode weld cue nor specific KEGAKI instruction exists, do not infer welding/KEGAKI from a RIB/support alone.
- **DATA provenance ↔ all features:** semantic cleanup/canonicalization must not silently redraw unchanged customer DATA geometry.
- **DATA provenance ↔ MATERIAL auto-R:** a sharp DATA corner does not suppress a required material-table R. For otherwise uncalled eligible outside corners <=90 degrees, preserve source-corner provenance, apply the active R as recorded `DATA_AUTO_R_CANONICALIZATION`, and retain explicit source R/C precedence.
- **DATA TAP representation ↔ THREAD_PILOT:** for every proved M*, distinguish `THREAD_NOMINAL_REFERENCE` from `THREAD_PREHOLE_SOURCE`; apply the nominal DATA<->PDF delta gate only to the nominal reference, then serialize exactly one controlled pilot CUT. Never output nominal-reference + pilot as two cuts.

## Closure

For every final family record, confirm:

1. source identity and quantity;
2. host face / datum ownership;
3. routed rule modules;
4. canonical geometry representation;
5. interactions with other active families;
6. serialized DXF representation;
7. applicable source-reprojection and saved-DXF read-back.

Any unexplained family loss, duplication, ownership conflict, or cross-feature contradiction is production FAIL/FLAG under the active validation rules.
