# ACUTE_BEND_LT85_METHOD — Approved production reference

**Status:** USER APPROVED on 2026-09-28.  
**Scope:** Sheet-metal bends whose included bend angle is **strictly `<85°`**, when the drawing/approved shop method requires the acute-bend outside-dimension construction demonstrated by `HD.dxf`.

## 0. Implementation requirement — derive from source, not answer

Before using this rule in production or regression, read `ACUTE_BEND_LT85_FROM_SOURCE.md`.

A valid implementation must execute the complete chain:

`source formed faces → identify free edges/inside surfaces → offset each inside surface by Rin → intersect offsets to get C → Rout=Rin+t → outside-envelope support measurement → OD1/OD2 → Nobi → flat/bend pair`

The approved OD numbers are **outputs/assertions only**. They must never be treated as source dimensions or fed back into construction.

## 1. Trigger and precedence

Apply this rule only when all of the following are true:

1. The real bend included angle is **<85°**.
2. The formed geometry and thickness are proved.
3. The applicable inside bend radius is proved by the approved shop method/drawing; for the approved regression below `Rin=0.6 mm`.
4. The bend is being converted to flat length using outside dimensions and Nobi.

If angle, thickness, radius, face identity, or free-edge datum is unresolved, FLAG instead of inventing an OD.

This rule is **not** the same as the existing generic §4.6 ID→OD tangent-offset formula. For this acute case, the controlling method is geometric construction of the real rounded bend followed by measurement of the two **外寸法 (outside dimensions)**.

## 2. Mandatory construction

For each affected bend:

1. Reconstruct the two formed faces from exact PDF dimensions/witnesses.
2. Replace the theoretical sharp intersection with the proved **inside bend radius `Rin`**.
3. Construct the outer surface with  
   `Rout = Rin + t`.
4. Preserve the real free edges and face directions.
5. **Do not use the theoretical sharp-line intersection as the OD datum.**
6. Measure the two physical outside dimensions from the real outer envelope after the bend radius has been constructed:
   - `OD1`: outside dimension of face 1.
   - `OD2`: outside dimension of face 2.
7. Use the applicable Nobi:
   `L_flat = OD1 + OD2 - Nobi`.
8. If unfolding from face 1:
   - `BEND_LINE_1 = OD1 - Nobi`
   - `BEND_LINE_2 = OD1`
   - separation = `Nobi`.
9. Clip the double bend lines to the actual material width crossing that bend.

## 3. Prohibited shortcuts

FAIL if the AI:
- extends the straight faces to a theoretical sharp corner and measures to that intersection;
- copies OD values from a reference DXF when they can be reconstructed from the PDF/shop method;
- treats a reference DXF as the source of missing PDF dimensions;
- substitutes the generic non-90° tangent-offset formula for this approved `<85°` geometric outside-envelope method;
- rounds printed source dimensions before construction;
- places bend lines through voids or beyond the material region.

## 4. Approved TEST regression

Source: `ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf`; method evidence: `HD.dxf`.

- Included bend angle: **75°**
- Thickness: **3.0 mm**
- `Rin = 0.6 mm`
- `Rout = Rin + t = 3.6 mm`

Approved reconstructed outside dimensions:

- **OD1 = 182.014217 mm → report 182.01 mm**
- **OD2 = 49.712236 mm → report 49.71 mm**

The generated proof file `ACUTE_BEND_LT85_OD_PROOF.dxf` contains the rounded bend and the two OD dimensions as non-cut annotation. A future AI should be able to recreate the same two physical OD values from `ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf` using this method.

## 5. Reference-audit behavior

When a user-approved DXF sample is also supplied:

- Derive OD1/OD2 independently from the PDF/shop method first.
- Then compare with the approved sample.
- A matching sample confirms the interpretation; it does not become the hidden dimension source.
- Report a conflict if the sample geometry cannot be reconciled with the proved formed geometry/radius/Nobi.

## 6. Regression assets

- `regression/assets/acute_bend_lt85/TEST.dxf` — independent test geometry.
- `regression/assets/acute_bend_lt85/TEST_OD_MINH_HOA.dxf` — generated proof geometry.

## Repository provenance

Original approved source hashes and the normalization boundary are recorded in `regression/assets/acute_bend_lt85/README.md`. The compact fixture preserves physical formed geometry but deliberately does not preserve irrelevant raw DXF entity packaging.
