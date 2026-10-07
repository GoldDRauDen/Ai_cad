# BEND_ATTACHMENT_EDGE_OWNERSHIP — V4.32 physical bend-edge attachment hard gate

**Approved:** 2026-10-07 from calibration/audit job `521006-18`.  
**Scope:** every `BEND`, `MULTI_FACE`, or unresolved bend candidate before production unfold.

## 1. Purpose

A correct face count or face order is not enough. Every bend must prove **which physical material edge of face A is joined to which physical material edge of face B**, and the orientation of that attachment.

The mandatory lock is:

`FACE_A.edge_i <-> physical BEND <-> FACE_B.edge_j`

This is `BEND_ATTACHMENT_EDGE_LOCKED`.

A wrong edge attachment can preserve the same total flat length while reversing a flange and moving every feature referenced from its bend/free edge. Therefore bend attachment is a topology gate, not a cosmetic orientation choice.

## 2. Required edge identities

Before unfold, retain an evidence-equivalent record containing at least:

```text
bend_id
face_A
face_A_shared_edge
face_B
face_B_shared_edge
face_A_free_edge(s)
face_B_free_edge(s)
edge_orientation / attachment_transform
source_evidence
alternative_attachment_state
```

`shared_edge` must identify the physical material edge on **both** faces. A generic statement such as `FACE_A adjacent to FACE_B` is insufficient.

## 3. Valid source evidence

Use mutually consistent source evidence. No single cue below is mandatory in every drawing.

Valid evidence may include:

- formed/profile/side/section geometry that proves the L/U/Z/joggle/return/flexible-bend topology;
- projection/view correspondence that identifies which physical edge of one face continues into another;
- dimension/witness connectivity tied to actual face edges;
- bend/J/angle/radius notation scoped to the transition;
- thickness or hidden-line representation **when present**;
- authoritative customer DATA geometry when applicable;
- another explicit source cue that uniquely proves the material connection.

Thickness/hidden lines are supporting evidence, not a prerequisite. When they are absent, formed-profile topology and view correspondence may be the controlling evidence.

## 4. Forbidden attachment shortcuts

The following do **not** prove a bend attachment edge:

- `NEAREST_VIEW_EDGE`;
- paper/page proximity between views;
- assuming the upper/lower/left/right paper edge is the bend edge;
- visual symmetry;
- choosing the attachment that makes the flat easiest to close;
- reference/sample geometry used to fill source-missing topology in a new construction job.

Never apply a drawing-specific lesson such as "always attach the top edge". The physical edge must be solved again for every source.

## 5. Measurement-construction views

A formed/profile view may be a `MEASUREMENT_CONSTRUCTION_VIEW`: source evidence used to prove topology, bend sign, edge attachment, or outside dimensions.

Such a view is **not manufacturing CUT geometry merely because it appears on Layer 0 or beside the flat in a reference DXF**. Output semantics remain controlled by the canonical manufacturing model.

## 6. Feature datum propagation

After `BEND_ATTACHMENT_EDGE_LOCKED`, local feature datums must retain physical edge identity, for example:

- `FACE_2.BEND_EDGE`
- `FACE_2.FREE_EDGE`
- `FACE_2.LEFT_EDGE`
- `FACE_2.RIGHT_EDGE`

If the attachment transform rotates or reflects the face, holes/cutouts/notches/chamfers transform with that face and keep their source-owned datum identity. `BEND_EDGE` and `FREE_EDGE` may never be swapped merely because the view is drawn nearer another view.

## 7. Ambiguity policy

If two different edge attachments remain source-compatible after source exhaustion, the bend is unresolved. Keep proved geometry local and use existing FLAG/VIEWS_ONLY policy. Do not choose by confidence or nearest-edge heuristics.

## 8. Regression intent

Job `521006-18` proves the mechanism:

- `058648`: the source/reference audit demonstrated a wrong flange reversal caused by attaching the graphical nearest edge rather than the physical shared bend edge. This is regression evidence only; its page orientation is not a universal rule.
- `058652`: a whole-part 180-degree representation can still be physically equivalent, so paper orientation alone is not an error.

See `regression/qa/521006-18_V4_32_APPROVED.md` and `regression/tools/check_521006_18_v432.py`.
