# ACUTE_BEND_LT85_FROM_SOURCE — Implementation contract

**Purpose:** Make the `<85°` acute-bend method reproducible by another AI **from source geometry**, without reading the approved OD answers from the proof DXF.

This document is the implementation companion to `ACUTE_BEND_LT85_METHOD.md`.

---

## 1. Inputs that MUST exist before calculation

For one acute bend, lock these source facts first:

- `t`: sheet thickness.
- `alpha`: included bend angle, with this rule triggered only when `alpha < 85°`.
- `FACE_1`, `FACE_2`: the two formed sheet faces.
- `FREE_EDGE_1`, `FREE_EDGE_2`: the physical free-end planes of those faces.
- `INNER_FACE_1`, `INNER_FACE_2`: the two real inside-surface straight lines before inserting the bend radius.
- `Rin`: applicable inside bend radius from the approved tooling/shop rule or explicit drawing.
- `Nobi`: applicable handwritten/table bend deduction, only needed **after** OD1/OD2 are derived.

Do not start from an approved reference DXF OD value. A reference DXF is comparison evidence only.

For the approved `ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf` regression, source geometry itself proves:
- two rectangular formed faces;
- face lengths `180 mm` and `50 mm`;
- `t=3 mm`;
- angle between the two face directions = `75°`.

`Rin=0.6 mm` comes from the approved acute-bend shop method (`HD.dxf`), not from an invented measurement of `ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf`.

---

## 2. Source-topology lock

Treat each formed face as a thickness-bearing strip, not as one centerline.

For each face identify:

- the two long parallel surfaces;
- the free-end short edge;
- which long surface is the **inside bend surface**;
- the unit direction vector `d_i` pointing **from its free edge toward the bend**.

The inside-surface choice is a topology decision. In the regression fixture, the inside surface of each face is the long face closest to the body/interior wedge of the other face. A future drawing must establish this from the actual formed topology/views; do not choose a side merely to match the reference answer.

---

## 3. Construct the real bend center — no sharp-intersection shortcut

Let `L1` and `L2` be the two proved inside-surface lines.

For each line construct a parallel line offset by exactly `Rin` **toward the center of curvature**.

In vector form:

- Let `n1`, `n2` be unit normals from `L1`, `L2` toward the bend center.
- Pick any points `p1 ∈ L1`, `p2 ∈ L2`.
- Offset lines are:

`L1_R: p = p1 + Rin*n1 + s*d1`

`L2_R: p = p2 + Rin*n2 + u*d2`

The bend center is their intersection:

`C = L1_R ∩ L2_R`

Validation before continuing:

- perpendicular distance `dist(C,L1) = Rin`;
- perpendicular distance `dist(C,L2) = Rin`;
- center lies on the topology-proved curvature side of both faces.

If the sign of either normal is unresolved, STOP/FLAG that bend. Do not select the candidate that merely reproduces the sample.

---

## 4. Construct outer radius

The physical outer bend radius is:

`Rout = Rin + t`

This gives two concentric arcs:

- inside arc: center `C`, radius `Rin`;
- outside arc: center `C`, radius `Rout`.

Tangency to the straight faces must be exact. The old theoretical sharp intersection is no longer a measurement datum.

---

## 5. Measure OD1 and OD2 from the outside envelope

For each face `i`:

- `d_i`: unit direction from free edge toward bend.
- `q_i`: any point on the corresponding physical free-edge plane.
- The outer bend circle's furthest support point in direction `d_i` has scalar coordinate:

`S_i = dot(C, d_i) + Rout`

- The free-edge plane has scalar coordinate:

`F_i = dot(q_i, d_i)`

Therefore the physical outside dimension is:

`OD_i = S_i - F_i`

So:

`OD1 = dot(C,d1) + Rout - dot(q1,d1)`

`OD2 = dot(C,d2) + Rout - dot(q2,d2)`

This is the portable mathematical statement of **外寸法を出す。（交点ではない）**: measure the real outside envelope, not the theoretical line intersection.

---

## 6. Only after OD is proved: unfold using Nobi

For a two-face bend:

`L_flat = OD1 + OD2 - Nobi`

If the flat origin starts at `FREE_EDGE_1`, then:

`BEND_LINE_1 = OD1 - Nobi`

`BEND_LINE_2 = OD1`

and:

`BEND_LINE_2 - BEND_LINE_1 = Nobi`

Trim both bend lines to the actual material domain.

---

## 7. Fully reproducible TEST regression from raw geometry

`ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf` contains:

### Face 1
A `180 × 3` vertical rectangular strip.

### Face 2
A `50 × 3` rectangular strip inclined so the included face angle is `75°`.

The regression runner must derive those dimensions from geometry. The following output values are **assertions only**, never input values:

- expected `t = 3.0`
- expected face lengths = `180.0`, `50.0`
- expected included angle = `75.0°`
- method input `Rin = 0.6`
- therefore `Rout = 3.6`

After constructing the offset-line intersection `C` and evaluating the outside-envelope equations:

- `OD1 = 182.014217199... mm`
- `OD2 = 49.712236235... mm`

Report:
- `OD1 = 182.01 mm`
- `OD2 = 49.71 mm`

The script `regression/tools/check_acute_bend_lt85.py` implements this chain. It reads the normalized source fixture, derives both face strips/thickness/angle, constructs `C`, calculates the two ODs, then compares them against the approved outputs. It does not read the proof DXF.

---

## 8. Mandatory audit trace for production use

For every future `<85°` bend record:

`source_view | face_1 | face_2 | t | alpha | free_edge_1 | free_edge_2 | inner_line_1 | inner_line_2 | Rin source | center construction | Rout | OD1 | OD2 | Nobi source | flat | bend pair`

This trace is what lets another AI or engineer verify the result without needing the original conversation.

---

## 9. Anti-cheating regression rule

A regression run is invalid if it:

- reads `182.014217` or `49.712236` from `ACUTE_BEND_LT85_OD_PROOF.dxf`;
- uses those values as constants in the geometric calculation;
- reverse-fits `Rin` from the approved outputs;
- chooses inner-face/normal signs solely because they minimize residual against the answer.

The approved OD values may appear only in the **final assertion/comparison block**.
