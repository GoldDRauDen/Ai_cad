# MECHANICAL_CLASSIFIER — V4.20 mandatory pre-geometry routing

**Status:** USER APPROVED 2026-09-29.

Before production geometry, create a mechanical classification record. It routes modules; it never substitutes for V4.19 FACE_GRAPH proof.

Required fields:
`source_mode, part_class, face_count, bend_axes, bend_angles_and_signs, feature_inventory, evidence_status, loaded_modules`.

Part classes include:
`FLAT_NO_BEND, SINGLE_BEND_L, DOUBLE_BEND_U, OFFSET_Z_JOG, MULTI_FACE_ORTHOGONAL, STEPPED_BENT, BOX_4_FLANGE, INSIDE_VIEW_ASSEMBLY, MIRROR_PART, OTHER_PROVED_TOPOLOGY`.

Feature inventory is independent:
- outer/inner CUT;
- round hole/tap;
- straight slot;
- curved/circular-arc slot;
- BEND;
- KEGAKI;
- PIASU/PIERCING POINT;
- SLIT/RELIEF;
- RIB;
- R/C/chamfer;
- other forming feature.

Do not classify from color alone. Use entity type, connectivity/topology, source callout/leader, host face and manufacturing function.

Routing:
- flat -> FLAT_NO_BEND;
- any bent/multi-face -> BEND_UNFOLD + FACE_GRAPH protocol;
- curved slot -> `features/CURVED_SLOT.md`;
- KEGAKI -> `features/KEGAKI.md`;
- SLIT/RELIEF -> `features/SLIT_RELIEF.md`;
- RIB -> `features/RIB.md`;
- PIASU/PIERCING -> existing HOLES_TAPS/forming rules.

No code receives production PASS until every detected/required manufacturing family has an explicit status.
