# BEND_EDGE_RELIEF_90 — bend-edge length + bend-end offset relief gate

**Status:** USER APPROVED 2026-10-05 from calibration job `521005-05` and the supplied three-example bend-relief DXF.

## Scope

This reference applies only to a **90-degree bend-end junction** where the need for a bend-relief slit is controlled by the signed edge offset at the end of a proved bend edge.

It does **not** replace or redefine:
- an explicit source-instructed custom `スリット` / `SLIT` value;
- BOXMET corner slit/relief;
- opposite-fold fixed-outside `R=t` relief;
- approved relief rules for bend angles other than 90 degrees;
- unrelated CUT notch/slot/lance/KEGAKI geometry.

If another more specific routed mechanism controls the same junction, apply that mechanism and do not double-create relief geometry.

## 1. Terminology

Use the following terms consistently:

- **cạnh uốn** = **bend edge / shared bend edge**;
- **chiều dài cạnh uốn** = **bend-edge length**;
- **độ bậc tại đầu cạnh uốn** = **bend-end offset**;
- **rạch thoát uốn** = **bend-relief slit**.

Do not call the bend-end offset `bend setback`; bend setback is a different sheet-metal term.

## 2. BEND_EDGE_LENGTH_LOCK

For every proved bend, lock the actual material shared edge before unfold/output:

`bend_id | face_A | face_B | shared-edge endpoints | bend-edge length | source witnesses | material domain`.

The **bend-edge length** is the physical length of the shared edge over which material actually bends. It is not the face bbox, not the total flat width/height, and not a convenient extension through neighboring material.

A bend pair must be clipped to this real material domain and to any real void/relief intersections.

### 057873 regression intent

For calibration code `057873`, the source proves a `248` bend-edge length for the long bend and `50` bend-edge lengths for the two end bends. These numbers are job-specific regression evidence only. They must never become generic coordinates or default bend lengths.

## 3. Signed bend-end offset S

At each relevant bend end, establish a local frame from source-proved physical edges. Define `S` as the signed **bend-end offset** between the actual material edge and the zero-offset/flush reference for that junction:

- `S > 0`: the retained material/bend-end region **protrudes** beyond the flush reference;
- `S = 0`: the two controlling edges are **flush**;
- `S < 0`: the actual material edge is **recessed** from the flush reference.

The sign and magnitude must come from actual source geometry/witnesses. Do not infer `S` from visual similarity, sample coordinates, symmetry, bbox, or Nobi arithmetic.

`S` is a local edge/topology parameter. It is not Nobi and it is not a bend allowance.

## 4. BEND_END_OFFSET_90 relief decision

Let `T` be sheet thickness. For this 90-degree mechanism:

### Case A — `S > 0`

**NO bend-relief slit is required by this mechanism.**

There is no active `T/2` threshold or intermediate FLAG branch. Any positive proved bend-end offset uses this NO-SLIT branch unless another separately routed mechanism or explicit source instruction requires relief.

### Case B — `S = 0`

Create the bend-relief slit from the **actual edge** inward by:

`D_actual = T + 0.2 mm`.

### Case C — `S < 0`

The edge is recessed. From the **actual recessed edge**, slit inward by exactly:

`D_actual = T + 0.2 mm`.

If the same endpoint is reported from the original zero-offset/outside reference, the total distance is:

`D_reference = |S| + T + 0.2 mm`.

The `|S|` term is the already-recessed edge distance; it is not an additional slit beyond the actual edge.

### Unresolved S

If the relevant 90-degree junction is proved but `S` cannot be closed after source exhaustion, retain `SLIT_RELIEF = UNKNOWN` and FLAG only that local relief decision. Do not guess NO-SLIT or insert `T+0.2` by habit.

## 5. Direction and connectivity

The formulas above determine required depth only after the local junction and relief direction are proved. Preserve source topology for:
- which edge receives the slit;
- inward direction;
- endpoint/connectivity;
- interaction with the bend-line material domain.

Do not assume a global X/Y direction, centerline location, mirror, or diagonal lead from these formulas alone.

When a physical slit intersects a BEND segment, apply the existing real-geometry intersection/clipping rules; do not leave dashed BEND geometry running through an actual CUT slit.

## 6. Approved t=2 decision matrix

For `T = 2 mm`:

- `S = -2` -> slit `2.2` from the actual recessed edge; endpoint is `4.2` from the zero/outside reference;
- `S = 0` -> slit `2.2` from the actual edge;
- `S = +1` -> NO SLIT;
- `S = +1.5` -> NO SLIT;
- `S = +2` -> NO SLIT.

This matrix supersedes the earlier provisional idea that `0 < S <= T/2` should be FLAGGED. That branch is **not active**.

For `057873`, `T=2` and the proved relevant bend-end step is `S=+2`, therefore this mechanism requires **NO SLIT**.

## 7. Mechanism precedence

For one physical junction, apply the first controlling mechanism whose scope is actually proved:

1. explicit revision/cancellation and explicit source-instructed custom slit semantics;
2. topology-specific approved mechanism such as BOXMET or opposite-fold `R=t` where its trigger is proved;
3. this `BEND_END_OFFSET_90` gate for the scoped 90-degree bend-end junction;
4. generic crossing-bend relief only when its own crossing-bend trigger remains physically true after bend-domain and material-edge closure.

Never generate duplicate reliefs from multiple mechanisms at the same junction.

## 8. QA

Before production PASS for an affected junction, verify:

- bend-edge length and endpoints are source-locked;
- bend line exists only on the true material domain;
- `T` and signed `S` are proved;
- 90-degree scope is proved;
- the controlling relief mechanism is identified and not duplicated;
- for `S=0`, slit depth is `T+0.2` from the actual edge;
- for `S<0`, slit depth is `T+0.2` from the actual recessed edge and any reference-distance report equals `|S|+T+0.2`;
- for `S>0`, no slit is added by this mechanism;
- saved DXF read-back preserves the final physical CUT/BEND interaction.