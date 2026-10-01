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
- **DATA provenance ↔ all features:** semantic cleanup/canonicalization must not silently redraw unchanged customer DATA geometry.

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
