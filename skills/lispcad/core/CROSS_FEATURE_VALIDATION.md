# V4.33 holistic cross-feature anomaly checks

In addition to feature-family interactions, run these whole-part contradictions before final PASS:

- source physical/view inventory vs source-group/member ledger completeness;
- barcode/constituent/assembly ownership vs assigned DATA/view bundles;
- BEND shared-edge semantic ownership vs face/blank extents;
- handwritten/printed flat arithmetic vs claimed inability to attempt a flat;
- local unresolved feature vs whole-part VIEWS_ONLY escalation;
- complete proved source-view inventory vs VIEWS_ONLY canonical members.

Any contradiction raises `ENGINEERING_ANOMALY_DETECTED` and returns the part to source interpretation. Do not choose a missing answer by confidence, symmetry or sample geometry.

# LISPCAD Core — Cross-feature validation

## Scope

Always run after feature routing and before production DXF export. This module adds no new dimensional formula; it prevents individually-correct feature modules from producing an incorrect combined part.

## Mandatory interactions

- **BEND ↔ FACE EDGE OWNERSHIP (V4.32):** every bend must pass `BEND_ATTACHMENT_EDGE_LOCKED` from `references/BEND_ATTACHMENT_EDGE_OWNERSHIP.md`. Prove the physical `FACE_A.edge_i <-> BEND <-> FACE_B.edge_j` connection; `NEAREST_VIEW_EDGE`, paper proximity and page-side assumptions are forbidden evidence.
- **FEATURE DATUM ↔ ATTACHED FACE ORIENTATION (V4.32):** holes/cutouts/notches/chamfers on a bent face retain physical edge identity such as `BEND_EDGE` or `FREE_EDGE` through rotation/reflection and local-face -> flat mapping. A reversed attachment that swaps those identities is FAIL even when total flat length is unchanged.
- **FORMED OD ↔ NOBI ↔ FLAT (V4.32):** when `references/FORMED_PROFILE_OD_MEASUREMENT.md` applies, establish `OD_actual` from the source-supported formed profile/outside envelope and explicit thickness/offset ownership before subtracting Nobi. Directly treating an inside/formed scalar as OD without proof is FAIL.
- **MEASUREMENT VIEW ↔ MANUFACTURING OUTPUT (V4.32):** a `MEASUREMENT_CONSTRUCTION_VIEW` may prove topology, attachment or outside length but is not CUT merely because it is present beside a flat or on Layer 0 in a reference.
- **SOURCE MANUFACTURING NOTE ↔ feature family (V4.29):** every production-affecting printed/handwritten instruction must retain a resolved family/output status under `references/SOURCE_MANUFACTURING_NOTE_CENSUS.md`. A source-active instruction may not disappear between preliminary census, routed modules, canonical geometry and serialized output.
- **HOLE/TAP ↔ BEND:** preserve host-face ownership and the proved local-face -> flat transform. Do not move printed geometry merely to satisfy a generic shop-distance advisory.
- **KEGAKI ↔ BEND/MULTI_FACE:** transform each mark with its owning face and verify fold-back locating function, count and segmentation.
- **SLIT/RELIEF ↔ BEND:** verify the slit/relief mechanism, source scope, quantity/value when specified, direction, connectivity, host edge/face and actual BEND interaction. For a V4.29 custom source-instructed slit, do not infer size or position from BEND geometry: relation to a bend center/domain must be source-proved. BOXMET rules apply only when BOXMET topology is proved.
- **CHAMFER/FILLET ↔ MATERIAL auto-R:** explicit source R/C semantics and quantities take precedence over automatic material corner treatment.
- **TAP ↔ HOLE:** thread-to-pilot conversion changes the manufactured diameter representation, not source family quantity or datum ownership.
- **PIASU ↔ HOLE/MATERIAL:** apply the active point/circle and material-capacity rules without changing source quantity or identity.
- **REVISION/CANCELLATION ↔ every family:** cancellation is scoped to the actual callout/leader/family. Never delete neighboring families by proximity.
- **RIB ↔ KEGAKI:**- **WELD SITE ↔ CUSTOMER 851 ↔ KEGAKI:** independently identify every A/B assembly view, proved parent/child weld contact and host face before KEGAKI routing. Numeric KH851 requires marking each proved weld site, even without a printed mark callout. Run references/WELD_SITE_KEGAKI_CLOSURE.md and enforce source weld-site IDs == canonical scoped KEGAKI/FLAG ownership; an omitted source weld site or required mark is FAIL regardless of otherwise valid DXF read-back.
 RIB-part CUT/HOLE and main-part locating KEGAKI are independent families; cancellation of one does not imply cancellation of the other.
- **WELD_REQUIRED_CUE ↔ RIB/support ↔ KEGAKI (V4.27):** `REVERSED_E_ABOVE_BARCODE` is scoped to its associated barcode/code cluster and proves a welding-process expectation, not KEGAKI geometry. If a welded child cannot self-locate, locating KEGAKI must be source-proved/derived from actual contact function or remain locally `UNKNOWN`/FLAG; it must not disappear from the final family closure. A specific KEGAKI instruction is independently sufficient. If neither barcode weld cue nor specific KEGAKI instruction exists, do not infer welding/KEGAKI from a RIB/support alone.
- **DATA provenance ↔ all features:** semantic cleanup/canonicalization must not silently redraw unchanged customer DATA geometry.
- **DATA provenance ↔ MATERIAL auto-R:** a sharp DATA corner does not suppress a required material-table R. For otherwise uncalled eligible outside corners <=90 degrees, preserve source-corner provenance, apply the active R as recorded `DATA_AUTO_R_CANONICALIZATION`, and retain explicit source R/C precedence.
- **DATA TAP representation ↔ THREAD_PILOT:** for every proved M*, distinguish `THREAD_NOMINAL_REFERENCE` from `THREAD_PREHOLE_SOURCE`; apply the nominal DATA<->PDF delta gate only to the nominal reference, then serialize exactly one controlled pilot CUT. Never output nominal-reference + pilot as two cuts.

## Closure

For every final family record, confirm:

1. source identity and quantity;
2. applicable source manufacturing-note provenance/resolution;
3. host face / datum ownership, including physical edge identity for bent-face datums;
4. routed rule modules;
5. canonical geometry representation;
6. interactions with other active families;
7. serialized DXF representation;
8. applicable source-reprojection and saved-DXF read-back.

For bent/multi-face parts, fold-back must also reproduce the proved **attachment edge identity**, not only the same silhouette, bbox or total length.

Any unexplained source-note loss, family loss, duplication, ownership conflict, bend-edge attachment conflict, measurement-view leakage into manufacturing geometry, or cross-feature contradiction is production FAIL/FLAG under the active validation rules.
