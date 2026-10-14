# MECHANICAL_CLASSIFIER — V4.33 identity/challenge hardening over V4.23/V4.20

## V4.33 required identity/challenge fields

Extend the mechanical record with:
`part_identity_graph_status, source_utilization_status, first_solve_status, holistic_challenge_status, unresolved_blocker_class, final_engineering_sanity_status`.

When multiple barcodes/codes, constituent marks, weld relationships or candidate child parts share a drawing/detail/DATA cluster, load `references/PART_IDENTITY_GRAPH.md` and close ownership before manufacturing geometry is assigned.

A high-evidence part that the current solver cannot close is `AI_INTERPRETATION_GAP` until source exhaustion proves a true ambiguity; do not silently convert solver difficulty into customer missing-data status.

## V4.23 required source-census fields

Extend the preliminary mechanical record with:
`source_entity_census, source_physical_inventory, drawing_only_inventory, canonicalized_inventory, bidirectional_diff_status, per_bend_witness_ledger_status`.

Every relevant DATA primitive must receive a semantic role before it is eligible for manufacturing canonical geometry. `THICKNESS_REPRESENTATION`, hidden/projection-only, dimension-helper/construction and duplicate/coincident entities do not become CUT by default. Every active physical family must still receive its normal manufacturing-family classification and host/status.


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
