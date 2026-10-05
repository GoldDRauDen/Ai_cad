# SOURCE_MANUFACTURING_NOTE_CENSUS — V4.29 source-instruction closure gate

**Approved:** 2026-10-05 from calibration/audit job `521005-13`.

## Purpose

Prevent a manufacturing feature from disappearing because its evidence is carried primarily by a printed/handwritten instruction rather than by visually prominent geometry.

This is an always-on source-reading gate. It adds no Nobi, material, tolerance, hole, slit-length, or bend-position formula.

## 1. SOURCE_MANUFACTURING_NOTE_CENSUS

Before final preliminary Feature Census, inspect every production-affecting Japanese/English printed note, handwritten note, revision note, leader, witness, and locally scoped instruction.

For every potentially production-affecting note retain an evidence-equivalent record:

`note_text | evidence_type | code_scope | target/leader/witness | candidate_family | quantity | explicit_value | location/direction evidence | resolution`

Allowed `resolution` states include:
- `ROUTED`
- `CANCELLED`
- `IRRELEVANT_TO_MANUFACTURING`
- `UNRESOLVED`

A note may not disappear merely because its feature is small, edge-open, visually similar to CUT geometry, or absent from OCR output.

## 2. SOURCE_NOTE_TO_FAMILY gate

A source instruction that proves or plausibly indicates a known manufacturing family must affect Feature Census before that family may be marked `NO`.

- Identity and scope proved -> route the family as `YES`.
- A manufacturing instruction exists but identity, scope, quantity, host, value, location, or direction remains materially unresolved -> route the relevant family as `UNKNOWN` until source exhaustion.
- `NO` is allowed only after applicable manufacturing notes have been resolved as cancelled, irrelevant to that family, or positively shown to belong elsewhere.

`UNKNOWN != NO`; unresolved notes must not be suppressed to avoid loading a route.

## 3. CUSTOM_SOURCE_SLIT

`スリット`, `SLIT`, or an equivalent explicit slit instruction can define a **custom source-instructed slit**.

Rules:

1. **Instruction required for this custom branch.** Do not create a custom anti-deformation slit merely because a bend exists, because a location looks mechanically useful, or because an approved sample has one.
2. The slit value is drawing-specific. `スリット 8` means the controlling explicit slit value for that scoped feature is `8` in that drawing; `8` is not a universal slit size.
3. Quantity, edge/host, position, direction, and relation to BEND come from source instruction/witness/geometry. Slits are often used near bend regions to reduce deformation, but that mechanical purpose does **not** prove a centerline location.
4. Never hardcode `BEND_CENTER -> SLIT`, and never copy coordinates from a reference DXF into a new drawing.
5. When an explicit source slit dimension controls the custom feature, preserve that value. Do not replace it with a generic relief formula such as `t+0.2` or `t*sin(theta)`.
6. If `スリット/SLIT` identity is proved but the exact construction remains incomplete, keep the feature routed and FLAG only the unresolved fields; do not delete the family.
7. Existing separately-triggered mechanisms such as crossing-bend relief, opposite-fold `R=t`, BOXMET slit/relief, or other approved relief families remain independent. This custom-instruction gate does not disable or redefine their trigger rules.

## 4. SOURCE_NOTE_FEATURE_COMPLETENESS

Before production PASS, close:

`SOURCE MANUFACTURING NOTES -> FEATURE CENSUS -> LOADED ROUTES -> CANONICAL FAMILY -> SERIALIZED DXF -> READ-BACK`

Any source-active manufacturing instruction that has no resolved family/output status is a production FAIL/FLAG.

For source-instructed custom slit, validate at minimum:
- source instruction scope;
- slit family identity;
- quantity when specified/proved;
- explicit size/value when specified;
- host edge/face and direction;
- source-proved relationship to BEND, if any;
- canonical representation;
- serialized physical geometry;
- saved-DXF read-back.

## 5. 521005-13 regression intent

For `058155` and `058156`, the source carries `スリット 8`; the approved sample confirms two edge-open slit features for each code. The job-specific value `8` and approved local coordinates belong only to that regression.

The generalized lesson is only:

**Do not lose an explicitly instructed manufacturing slit during source-note census/routing. Do not invent its size or position when the source does not specify them.**
