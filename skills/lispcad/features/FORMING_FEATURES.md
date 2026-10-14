# LISPCAD Feature — Forming & Center Markings

Approved calibration 520924-19, 2026-09-25.

### 3.2 3D formed-feature mapping to 2D manufacturing

- `Kegaki` / formed reference and explicitly required marking lines: Layer 0, Color 1 (Red), `LINE` or explicit `LWPOLYLINE` as the applicable drawing requires. Features include louver, emboss, dimple outline, rib, gusset, bridge, half shear, hem, curl and lance marks. Respect restrictions such as `※ケガキ不可` where listed by the material table.
- Manufacturing center `POINT`: Layer 0, **ByLayer by default**. Only a PDF-scoped **PIERCING + THROUGH HOLE** center is Color 3 (Green). Explicit PIERCING *without* THROUGH HOLE and material-capacity POINTs remain ByLayer. A provisional estimated center/type is Color 6 (Magenta) with an independent FLAG.
- Relief slits and other LINE geometry whose color is explicitly specified Green retain their LINE-specific legend; this does not permit arbitrary green POINTs. Do not create a circle of radius 0.5 to stand in for an AutoCAD `POINT` when the source requires POINT.
- The unusual `J`/POINT set requires an applicable explicit PDF J indication. It is not a universal shop feature and is not inferred merely because the reference DXF contains a J.
