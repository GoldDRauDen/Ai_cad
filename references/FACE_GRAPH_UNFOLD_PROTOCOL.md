# FACE_GRAPH_UNFOLD_PROTOCOL — V4.19 mandatory multi-face reasoning contract

**Approved:** 2026-09-29, calibration job 520929-25.  
**Scope:** every bent or multi-face sheet-metal part. This protocol adds no material, Nobi, thread, laser-R or acute-bend formula. It hardens how existing source evidence is converted into a unique formed model and then into a flat.

## 1. Core principle

Do **not** start a bent job from the desired flat contour, overall bbox, or a familiar shape label such as U/Z/box. First construct a source-supported formed-part model. Pattern recognition may propose a candidate topology, but only witness-owned dimensions, projection relationships, bend callouts, sections/details and explicit feature evidence may prove it.

The mandatory representation is a **constraint-closed signed FACE_GRAPH**:

- **FACE** = one material face with its own source/local frame and contour.
- **DIMENSION** = exact printed/derived value plus both witness endpoints, semantic family and owner.
- **FEATURE** = hole/slot/notch/R/C/KEGAKI/RIB/etc. with a mandatory host face and local datum.
- **BEND** = adjacency between exactly two faces, with shared material edge, signed fold orientation, angle/radius/thickness/Nobi evidence and actual material domain.
- **TRANSFORM** = deterministic local-face → flat mapping derived only after the face graph is locked.

A production flat is forbidden while an active graph element lacks its required ownership/constraint fields.

## 2. Mandatory intermediate records

For every multi-face part retain an internal/evidence-equivalent record sufficient to reproduce these fields:

```text
FACE:
  face_id
  source_view / source ROI
  local_origin
  local_axis_u / local_axis_v
  contour_edges
  source-proved face dimensions
  normal/orientation state

DIMENSION:
  dim_id
  value
  printed | derived | handwritten/revision
  witness_A
  witness_B
  semantic = FACE_CONTOUR | FEATURE_SIZE | FEATURE_POSITION |
             BEND_FACE_TRANSITION | OTHER_PROVED
  owner_face or owner_bend

FEATURE:
  feature_id
  family / size / quantity
  host_face
  local_datum
  local_geometry
  local_to_flat_transform

BEND:
  bend_id
  face_A
  face_B
  shared_edge
  signed_angle / fold_sign
  Rin / t / Nobi evidence as applicable
  material_domain
  resulting double-line domain
```

A printed number may not remain an unowned scalar. A feature may not be represented first as an arbitrary final-DXF `(x,y)`; its host face/local datum must be proved first.

## 3. Hard gates G1–G9

### G1 — TOPOLOGY_LOCKED
All material faces required by the source are identified and their actual adjacency is established. Similar silhouette or a closing overall sum is not topology evidence.

### G2 — DIMENSION_WITNESS_LOCKED
Every dimension used for contour, feature or bend construction has both witness endpoints and exactly one semantic owner. Hole/slot pitch cannot become a contour or bend distance.

### G3 — FEATURE_OWNERSHIP_LOCKED
Every manufacturing feature belongs to a proved face/local frame before unfold. Features transform with their face; they are not copied as global flat coordinates unless the source datum truly coincides with the flat datum.

### G4 — FACE_ORDER_LOCKED
For each unfold path, preserve the ordered face chain. `sum(OD)-sum(Nobi)` may be identical for different face orders; identical total length does not validate bend positions.

### G5 — BEND_SIGN_LOCKED
Every bend has a source-supported sign/orientation. Track face normals or an equivalent signed state so U, Z/S, return, joggle, local channel and mixed-axis structures cannot collapse into the same unsigned 90° description.

### G6 — BEND_DOMAIN_LOCKED
A bend exists only where material actually crosses the shared edge. Split/trim double lines around reliefs, cutouts, steps and local flanges. Never extend BEND through voids merely to span the bbox.

### G7 — CONSTRAINTS_CLOSED
The chosen graph must be uniquely determined by source evidence. Required checks:
- no unresolved owner fields;
- no unanchored face translation/orientation DOF;
- no alternative face order/sign assignment that satisfies the same used constraints;
- all declared feature quantities and face dimensions close;
- every derived flat equation traces back to exact printed inputs and approved formulas.

If two materially different graphs remain possible after source exhaustion, production is blocked and the unresolved choice must be FLAGGED/asked. Confidence is not evidence.

### G8 — FOLD_BACK_MATCH
After unfold, replay/fold the flat back through the signed graph (a deterministic 2.5D face graph is sufficient; a full B-rep is not required) and reproject/compare against the source-proved formed constraints.

At minimum verify:
- face dimensions and adjacency;
- relative face orientation/bend sign;
- formed outside dimensions that were used;
- feature host face, quantity and local offsets;
- view silhouette/topology where source-proved;
- local channel/tab/flange placement;
- bend-domain ownership.

A flat bbox match alone cannot pass G8. The strict `<0.01 mm` residual rule remains limited to correctly derived numeric comparisons and never repairs wrong topology, witness or printed dimensions.

### G9 — DXF_READBACK_MATCH
Only after G1–G8 pass may production geometry be serialized. Re-open the saved DXF and audit CUT/HOLE/BEND/KEGAKI/RIB, properties, mm units and code mapping independently from the source-semantic gates.

## 4. Mandatory solve order

`SOURCE VIEWS → witness/semantic graph → candidate FACE_GRAPH → signed adjacency → constraint closure → unfold → feature transforms → material-domain BEND trim → FOLD_BACK/reprojection → manufacturing QA → DXF → DXF read-back`.

Do not reorder this into `bbox → flat → try to explain views afterward`.

## 5. Candidate-shape recognition

Labels such as L, U, Z, hat, box, joggle, return flange or local channel are permitted only as candidate generators. They must not directly select bend order, sign, relief or feature placement. Test the candidate against G1–G8. Reject candidates that require borrowing a dimension from another face, ignore a witness, move a feature to another host face or leave a competing topology equally valid.

## 6. Reference DXF boundary

For NEW_PDF_TO_DXF, construct the graph independently from PDF/image source first. A customer-approved DXF may assert/audit the result afterward but may not fill missing source coordinates, choose a hidden face order or reverse-fit the graph.

For DIRECT_EXISTING_DXF_AUDIT, compare AI DXF ↔ approved sample first as required by the existing skill, then use PDF/source to diagnose the semantic root cause. Convert only the general cause into production rules; job-specific coordinates remain regression assertions.

## 7. Production blocker policy

- G1–G7 unresolved but independently proved source views exist → `VIEWS_ONLY` / REVIEW ONLY.
- A unique graph exists but a local feature remains uncertain → preserve proved flat, Magenta/FLAG only the unresolved feature under existing V4.11 rules.
- Any G8 failure → production FAIL; fix the graph/transform, do not tune coordinates to the reference.
- G1–G9 PASS → eligible for normal production status, subject to all other material/Nobi/R/C/relief rules.

## 8. 520929-25 approved regression intent

This job is evidence for the mechanism, not a library of reusable coordinates:
- 056942 proves that the same total flat length can hide a wrong face order/BEND placement.
- 056956 proves that perpendicular/local flanges require an actual face graph and material-domain BEND clipping.
- 057042 proves that longitudinal Z/S bends and a local transverse channel require independent signed axes/domains and feature ownership.

See `regression/qa/520929-25_V4_19_APPROVED.md` and `regression/tools/check_520929_25_v419.py`.
