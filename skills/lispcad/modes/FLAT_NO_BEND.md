# LISPCAD Mode — Flat / No Bend

## Scope

Use this mode when the drawing requires no bend-unfold calculation.

This module intentionally adds **no new manufacturing rule** beyond the approved core and applicable topology/feature modules. Do not import bend-specific Nobi, ID→OD, face-order, or unfold calculations unless the drawing explicitly requires them.

Always apply:
- `../core/DRAWING_READING.md`
- `../core/DATUM_DIMENSION.md`
- `../core/VALIDATION.md`
- `../core/CAD_OUTPUT.md`
