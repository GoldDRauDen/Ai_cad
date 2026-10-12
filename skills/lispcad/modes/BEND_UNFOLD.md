# LISPCAD Mode — Bend / Unfold

## V4.32 — physical bend-edge attachment + formed-profile OD gate

For every `BEND`, `MULTI_FACE`, or unresolved bend candidate, load:

- `../../../references/BEND_ATTACHMENT_EDGE_OWNERSHIP.md`
- `../../../references/FORMED_PROFILE_OD_MEASUREMENT.md` when actual outside face length must be established from formed/profile geometry.

Before any production unfold, prove `BEND_ATTACHMENT_EDGE_LOCKED`: the exact physical edge of each adjacent face participating in each bend, not merely the face pair/order.

`NEAREST_VIEW_EDGE`, paper proximity, view-above/view-below assumptions and visual symmetry are forbidden attachment evidence. Thickness/hidden-line evidence is optional; formed/profile/side/section topology, projection/view correspondence, witness connectivity and other explicit source cues may prove the shared edge.

A formed/profile view used to reconstruct topology or measure outside length is a `MEASUREMENT_CONSTRUCTION_VIEW`, not automatic CUT geometry.

Production unfold is blocked until `TOPOLOGY_LOCKED`, `BEND_ATTACHMENT_EDGE_LOCKED`, `DIMENSION_WITNESS_LOCKED`, `FEATURE_OWNERSHIP_LOCKED`, `FACE_ORDER_LOCKED`, `BEND_SIGN_LOCKED`, `BEND_DOMAIN_LOCKED` and `CONSTRAINTS_CLOSED` pass. Fold-back must reproduce the same physical attachment edges and bent-face datum identities.

## V4.23 — mandatory per-bend witness ledger

In addition to the V4.19 FACE_GRAPH, every bend must close a `PER_BEND_WITNESS_LEDGER` before its double lines are accepted. Record ordered faces, controlling source witnesses, ID/OD semantics, every thickness term and where it is consumed, Nobi, sign, material domain and final pair coordinates. Enforce `THICKNESS_SINGLE_USE`: no thickness contribution may be silently consumed twice for the same transition.

Do not place a bend from total-flat closure alone. If a candidate bend pair differs from source/reference diagnosis by exactly ±t, treat that only as evidence of a possible thickness/datum ownership error and re-trace the ledger; do not auto-shift by t as a generic formula.

Source: approved V4.3 production baseline.

Load shared Nobi values from `../../../references/NOBI_TABLES.md`.

## V4.19 — Mandatory constraint-closed FACE_GRAPH before unfold

For **every bent/multi-face part**, load `../../../references/FACE_GRAPH_UNFOLD_PROTOCOL.md` before calculating production flat coordinates. The source-first graph must lock dimension witnesses/owners, feature host faces/local datums, ordered adjacency, signed bend orientation and actual material domains. `sum(OD)-sum(Nobi)` or a matching flat bbox is not a substitute for graph closure.

Production unfold is blocked until `TOPOLOGY_LOCKED`, `BEND_ATTACHMENT_EDGE_LOCKED`, `DIMENSION_WITNESS_LOCKED`, `FEATURE_OWNERSHIP_LOCKED`, `FACE_ORDER_LOCKED`, `BEND_SIGN_LOCKED`, `BEND_DOMAIN_LOCKED` and `CONSTRAINTS_CLOSED` pass. After unfold, `FOLD_BACK_MATCH` against source-proved formed constraints is mandatory before DXF serialization. If competing face graphs or attachment edges remain, use existing FLAG/VIEWS_ONLY policy rather than selecting by confidence.

## V4.13 520315-18 — only nonduplicate approved additions

**INSIDE_VIEW assembled before proved reflection:** When source views prove they show inner faces, identify each face's datum, view direction and fold order. Apply the existing ID→OD, handwritten/table Nobi and local-face-to-flat rules, assemble the complete proved inside-face flat, and ONLY THEN reflect the assembled geometry when the intended target blank requires the proved axis. Compare hole center, actual M/Ø family and count IN THE SAME final frame; a left/right appearance in unmatched frames is not a hole error. Never mirror every bent part by default. User-approved 018297 is the regression for a false M3/Ø7 swap conclusion.

**Handwritten/J mismatch audit:** Existing Rule 1 always draws with scoped legible N_hand, including bends marked J. Only if the approved table supplies a genuinely compatible N_table for the SAME material, thickness, bend length, angle and applicable surface state, record both and FLAG HANDWRITTEN_NOBI_DIFFERS_FROM_TABLE if their prescribed values differ. Do not borrow a 90° table row for a 165° bend; if the table has no match, never replace a proved handwritten Nobi with an OD fallback.

**Exact printed inputs versus strictly <0.01 mm DERIVED comparison:** Continue rounding each calculated ID→OD offset to 0.01 before adding it to the actual printed ID and deducting the real Nobi. Read printed dimensions EXACTLY; the <0.01 mm threshold applies only to a representation/rounding difference when auditing ALREADY CORRECT derived quantities against a reference. Exactly 0.01 is not below threshold, and a wrong source input, datum, topology, feature class, or bend order fails regardless. Approved 018300: (797+0.26)+(24+0.26)-0.37=821.15 mm; 262+61.5-3.68=319.82 mm. Its previously measured reference bbox ~821.153 differs ~0.003 mm only in derived arithmetic.

#### 4.2.6 Reference Dimensions Still Require a Proven Datum

Authoritative rule: `../core/DATUM_DIMENSION.md` §4.2.6. Interpret witness origins there; this BEND module must not copy or override it.

#### 4.2.7 Local-Face Datum → Global Flat Datum Mapping

Authoritative rule: `../core/DATUM_DIMENSION.md` §4.2.7; execute that proved local-face → global-flat coordinate transformation before any unfold output.

**V4.32 physical edge datum identity:** if the local datum is edge-based, retain the actual edge identity through the transform, e.g. `FACE_2.BEND_EDGE` or `FACE_2.FREE_EDGE`. Rotation/reflection may change coordinate direction but may not silently swap bend/free edge identity.

#### 4.2.8 Bend Sequence / Face Order Is Non-Commutative

Apply `../core/DATUM_DIMENSION.md` §4.2.8 for the canonical face-order rule. Additional bend-specific hard gates follow:

- Determine the ordered face sequence from the visible formed topology, bend callouts, section/detail views, and proven witness-line connectivity before calculating bend-line coordinates.
- Lock the physical attachment edge for every face transition under V4.32; correct face order with the wrong attached edge is still FAIL.
- Do not validate bend order merely because `sum(OD) - sum(Nobi)` matches the overall blank length.
- Double bend lines MUST be positioned from the ordered sequence in Section 4.7 and MUST exist only over material regions that actually cross that bend. For U-shaped, legged, stepped, or cut-away parts, split/trim bend lines around voids; never draw a bend line continuously through empty space.
- If two face orders or two physical attachment edges remain equally plausible after explicit trace exhaustion, STOP and ask the user. Magenta is not permission to choose an arbitrary bend order/edge.

### 4.6 ID-to-OD Conversion for Non-90° Bends
When dimensions are given as Inside Dimensions (ID), convert to Outside Dimensions (OD):

$$\text{Offset}_{raw} = t \times \tan\left(\frac{180^\circ - \text{Angle}}{2}\right)$$

**Mandatory rounding order:** round `Offset_raw` to the nearest `0.01 mm` **before** adding it to the ID or using it in any subsequent Nobi/flat-pattern arithmetic. Use ordinary decimal rounding at the hundredth place: inspect the thousandth digit; `0–4` rounds down and `5–9` rounds up.

$$\text{Offset} = \operatorname{Round}_{0.01}(\text{Offset}_{raw})$$

$$\text{OD} = \text{ID} + \text{Offset}$$

- Confirmed calibration example: for a `165°` bend with `t = 3.0 mm`, `Offset_raw = 3.0 × tan(7.5°) ≈ 0.39495...`, therefore **Offset = 0.39 mm**. Use `0.39`, not the unrounded value, in every following equation.
- Example (`135°` bend, `t = 3.0 mm`): `Offset_raw = 3.0 × tan(22.5°) ≈ 1.2426`, so **Offset = 1.24 mm**, then `OD = ID + 1.24 mm`.
- Do not apply this special intermediate rounding rule to unrelated explicit dimensions. It is specifically the ID→OD offset normalization step.
- V4.32: assign every ID→OD offset to the physical face contribution proved by the formed profile/attachment graph. Do not add the same offset again after an outside extent already includes it.

### 4.6.2 V4.15 — Acute bend `<85°`: construct real radius, then measure outside OD

When the **proved included bend angle is strictly <85°**, this approved method takes precedence over using the generic §4.6 tangent-offset equation as the controlling OD construction for that bend.

1. Load `../../../references/ACUTE_BEND_LT85_METHOD.md` and the mandatory implementation contract `../../../references/ACUTE_BEND_LT85_FROM_SOURCE.md`.
2. Reconstruct both formed faces and their real free edges/inside surfaces from source evidence.
3. Apply the proved inside bend radius `Rin`; construct `Rout = Rin + t`.
4. Find the real bend center from the intersection of the two `Rin`-offset inside-face lines.
5. Measure `OD1` and `OD2` from the **physical outside envelope (外寸法)**. **Do not measure to the theoretical sharp intersection (交点).**
6. Only after both ODs are proved, apply the applicable Nobi: `L_flat = OD1 + OD2 - Nobi`. If unfolding starts from face 1, the double bend lines are `OD1-Nobi` and `OD1`.
7. A reference/proof DXF may confirm the independently reconstructed result but may never supply a PDF-missing OD or choose topology/normal signs.

Approved executable regression: `../../../regression/tools/check_acute_bend_lt85.py`; proof assets: `../../../regression/assets/acute_bend_lt85/`.

### 4.7 Nobi (Bend Allowance) Lookup Priority & Sequential Formulas
1. **Handwritten Nobi on Drawing**: Highest priority. Use directly (e.g., `-4.8`, `135° -1.71`) regardless of J-symbol.
2. **No Handwritten Nobi + J-Symbol Present**: Look up Nobi from standard tables (Section 7.3) by Material, Thickness, Bend Length, and Angle — applying the Interpolation Rule in Section 4.8 when the exact value is not tabulated.
3. **No Handwritten Nobi + J-Symbol Absent**: Draw the affected flange as a separate piece detached from the main body, offset by a fixed `10 mm` gap for downstream reassembly. Set `is_flagged = true`.
4. **J-Symbol Present + No Table Match** (including out-of-range per Section 4.8): Maintain flat blank at Outside Dimension (OD) and draw bend line at OD design position. Set `is_flagged = true`.

#### Multi-Flange Sequential Coordinate Formulas (Axis from Origin 0)
For sequential flanges (`OD_1, OD_2, ..., OD_n`) with Nobi values (`N_1, N_2, ..., N_{n-1}`), first preserve the proven face order from Section 4.2.8. Any non-90° ID→OD offsets used inside the `OD_i` values MUST already be rounded to `0.01 mm` per Section 4.6 before these equations are evaluated:
- **Total Unfolded Length**:
  $$L_{\text{total}} = \sum_{i=1}^{n} OD_i - \sum_{i=1}^{n-1} N_i$$
- **Exact Coordinates for Double Lines of Bend k**:
  - **Lower Line (Line 1 / Outer)**:
    $$Y_{\text{line1}} = \left(\sum_{i=1}^{k} OD_i\right) - \left(\sum_{i=1}^{k} N_i\right)$$
  - **Upper Line (Line 2 / Inner Datum)**:
    $$Y_{\text{line2}} = \left(\sum_{i=1}^{k} OD_i\right) - \left(\sum_{i=1}^{k-1} N_i\right)$$
  - **Distance between double lines**: `N_k`
- **Body Interior Preservation**: Main body interior dimensions (`B`) are **NEVER** reduced by Nobi. Nobi deductions exist strictly within the bend zone between parallel bend lines.
- **V4.32 OD provenance:** each `OD_i` must retain its source/formed-profile witnesses and thickness/offset owner. A numerically closing total does not validate a wrong OD owner or reversed attachment edge.

### 4.8 Nobi Table Interpolation Rule (NEW — Conservative Round-Up, Shop-Practice Standard)
When the actual Thickness (`t`) or Bend Length (`L`) does **not** exactly match a row in Section 7.3, do **NOT** interpolate numerically. Instead:
- **Thickness mismatch**: Select the row with the **next higher tabulated t** (never round down). Rounding down risks selecting an undersized V-die opening for the actual material, risking cracking or improper die seating.
- **Bend Length mismatch**: Within the selected `t` row group, select the **next higher L bracket** (next larger V-die). This yields a conservative (larger) Nobi deduction, which errs toward tooling safety.
- **Out-of-Range**: If `t` or `L` exceeds the largest tabulated value for that material, do not guess. Set `is_flagged = true` and annotate `"OUT OF TABLE RANGE - CONFIRM NOBI WITH SHOP"` in Magenta (Color 6) per Section 4.4.
- This rule applies uniformly across all four material tables in Section 7.3.

### 4.10 Corner Reliefs — two distinct mechanisms (V4.4)

**Standard crossing-bend slit relief** (original V4.3 rule, only when two perpendicular bend lines cross):
- Retract longer edge by `t`; slit inward by `t + 0.2`; diagonal slit to bend-line intersection; read any drawing-specific offset or FLAG if unknown.

**Opposite-fold fixed-outside R=t relief** (approved calibration `055962`):
- When **two outer edges fold in different directions** and both outside dimensions must remain unchanged, create an `R=t` escape relief at their intersection without shortening either outside dimension. This is a distinct topology/operation from the standard slit relief and from material-table automatic laser fillets. Determine its exact tangency and retained-material side from the real bend/edge topology; if those are unclear, do not invent them.
- In `055962`, `t=2 mm` gives the two confirmed R2 reliefs. A separately observed R2 on an unbent corner is NOT automatically this relief.
- **`055958` (approved Q47/Q48): EXACTLY ONE standard Section 4.10 slit relief.** Its verified standalone DXF has three Green entities on Layer `0`, joined at endpoints: `LINE 55A` → `ARC 55B R0.5` → `LINE 55C`. Count **ONE connected machining feature**, NOT three reliefs. Its approved method is the existing crossing-bend slit rule (retract the longer edge by `t`, cut inward `t+0.2`, then diagonal to the proved bend intersection). The local `ARC R0.5` is **specific to this example**, not a mandatory arc for other slits or an automatic material-table Laser R. The old **slit method/count FLAG is RESOLVED**; customer-unconfirmed sizes and any independent datum/geometry FLAG remain. Never hardcode these reference coordinates as a universal construction.

#### 4.10.1 V4.16 BOXMET-style four-flange box routing

If the source proves a central/base rectangle with four adjacent bent flanges and BOXMET corner topology, load `../../../references/BOXMET_SLIT_RELIEF.md`. This reference decides which pair of flaps retreats by `t`, generates the four required slits, constructs the tangent `LINE + ARC R0.5 + LINE` geometry, and defines when the rule is not applicable. Do not omit a required BOXMET slit merely because the outer contour is already closed; do not auto-apply BOXMET slit logic to ordinary L/U/Z, single-flange/free-edge, non-crossing, or unrelated relief topology.

---
