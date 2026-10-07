# CANONICAL_MEMBER_COMPLETENESS — V4.33 ledger-plausibility hardening over V4.31

**Status:** USER APPROVED 2026-10-06.

This is an executable production hard gate. It closes the gap where a job can correctly name a source family/group in text yet serialize only a hand-picked subset of the proved geometry.

## 0. V4.33 upstream ledger-plausibility gate

The V4.31 equalities remain necessary but are not sufficient when the source ledger itself is incomplete.

Before member equality, run the routed holistic challenge and verify:
- every relevant source physical/view inventory entry maps to a source member or an explicit drawing-only/helper/duplicate/canceled classification;
- every final feature-family YES/UNKNOWN has a scoped group/member or explicit unresolved group;
- substantial physical DATA with zero proved source members is challenged rather than accepted by self-equality;
- VIEWS_ONLY contains every independently proved source-view member required for the unresolved part;
- multi-code/constituent jobs pass PART_IDENTITY_GRAPH with no unexplained whole-bundle collision;
- a shared bend-edge dimension is not reused as an unrelated blank/face extent without same-physical-parameter proof.

If census/inventory/group/member records disagree, fail upstream with `SOURCE_LEDGER_PLAUSIBILITY_FAIL`. Do not proceed merely because `PROVED_SOURCE_MEMBER_IDS == PROVED_SOURCE_BACKED_CANONICAL_MEMBER_IDS`.

## 1. Required production chain

Normal repo-direct CAD production is:

`SOURCE -> SOURCE_FEATURE_GROUP ledger -> SOURCE MEMBER ledger -> DIMENSION/WITNESS graph -> CANONICAL MEMBER model -> CANONICAL ENTITIES -> V4.31 canonical serializer -> SAVED DXF -> READ-BACK`.

`tools/export_canonical_dxf.py` is the normal production serialization entrypoint. `tools/export_dxf.py` remains the lower-level packaging serializer and is not, by itself, evidence that source-member completeness was proved.

**NO_DIRECT_DXF_FROM_INTERPRETATION:** a job builder must not create production/review DXF directly from source interpretation by writing an ad-hoc subset to `ezdxf.modelspace()` and then calling `saveas()`. Build the canonical JSON contract first and pass it through the V4.31 gate.

## 2. Source groups and members

Every source-scoped leader/callout group that affects manufacturing must be persisted as a `source_group` with:

- stable `group_id`;
- `family`;
- `status = PROVED | FLAGGED | CANCELED`;
- `source_quantity` when quantity is proved, otherwise null;
- member records when members are enumerable;
- source/evidence note sufficient to trace the group back to the drawing.

Same family/size does not merge groups. Shared X witnesses do not imply shared Y witnesses.

Each enumerable member has a stable `member_id` and local status. A FLAGGED member/group stays in the ledger; uncertainty is local and does not authorize deletion of independently PROVED members.

## 3. Canonical member model

Every active enumerable source member must have exactly one source-backed canonical member record.

- source `PROVED` -> canonical `PROVED`;
- source `FLAGGED` -> canonical `PREVIEW` or `FLAGGED_NO_GEOMETRY`;
- source `CANCELED` -> no source-backed canonical member.

A canonical member may reference one or more entity IDs. One physical manufacturing feature can require multiple primitives (for example a slit composed of LINE+ARC+LINE or a bend represented by two DASHED lines). Conversely, several semantic members such as corner-R ownership may reference one shared contour entity when the physical DXF representation is a single polyline. Raw DXF entity count is not manufacturing quantity.

Rule-derived manufacturing members not explicitly called out by source may use `origin = DERIVED_RULE` only when they record `controlling_rule` and the source member(s)/source feature that triggered the derivation.

## 4. Mandatory equalities

Before serialization:

`PROVED_SOURCE_MEMBER_IDS == PROVED_SOURCE_BACKED_CANONICAL_MEMBER_IDS`

and all enumerable FLAGGED source members must remain represented as `PREVIEW` or `FLAGGED_NO_GEOMETRY`.

Before delivery:

`CANONICAL_ENTITY_IDS == SAVED_DXF_LAYER0_ENTITY_IDS`

The V4.31 wrapper stamps stable canonical `entity_id` values into Layer-0 DXF entities as `TRAINAICAD` XDATA, saves again, reopens the exact file, audits it, and proves the ID set/order survived. AI_META annotations are excluded from manufacturing-entity equality.

If either equality fails: `SOURCE_FEATURE_COMPLETENESS_FAIL` / `CANONICAL_SERIALIZATION_COMPLETENESS_FAIL`. Do not report generic READBACK PASS.

## 5. No orphan geometry

Every Layer-0 canonical manufacturing entity must have a unique `entity_id` and be referenced by at least one canonical member. Preview annotation TEXT may be exempt from manufacturing-member ownership but still receives an entity ID for read-back fidelity.

A canonical member referencing a missing entity is FAIL. A saved Layer-0 entity with no canonical entity ID is FAIL in the V4.31 normal production path.

## 6. 521005-05 failure lesson

The failed V4.30 runtime job demonstrated a workflow/implementation failure, not a serializer reduction failure: source groups for 057862/057864 and the M8 family on 057873 were not instantiated into a member-level canonical model before the raw `ezdxf` save. Selected read-back checks therefore passed a structurally valid but incomplete DXF.

V4.31 regression must prove at minimum:

- `057862`: independent `2-Ø9`, `6-M6`, `6-Ø9`, `2-Ø9` groups survive source -> canonical -> saved DXF member closure;
- `057864`: the proved 7 hole centers survive even while the separate `8-R5` issue remains customer-pending/FLAGGED;
- `057873`: four M8 members survive together with bend-edge lengths 248/50 and the already-approved 90-degree no-slit decision for positive bend-end offset;
- negative fixtures that reproduce the old subset behavior are rejected before/at canonical serialization.

The numeric fixture coordinates used by regression are synthetic test coordinates only. They are not construction data for future drawings.

## 7. Root-cause vocabulary

If source group/member records are missing despite readable source: `AI_WORKFLOW_ERROR`.
If a builder bypasses or violates the canonical contract: `AI_IMPLEMENTATION_BUG`.
If the gate/checker does not cover a demonstrated failure: `REGRESSION_COVERAGE_GAP`.
Do not label `AI_MISREAD` unless there is direct evidence that the source was semantically interpreted incorrectly; absence from a persisted ledger alone does not prove misreading.
