# LISPCAD Feature — Slots

Source: approved V4.3 production baseline.

- **Slots / Oblong Holes**: Constructed as single closed `LWPOLYLINE`s with two straight segments and two semi-circular bulges (`bulge = 1.0`).
- **Slot Dimension Semantics — mandatory**: Before creating a slot, classify every length value as `OVERALL_LENGTH` (extreme end to extreme end) or `CENTER_DISTANCE / STRAIGHT_TANGENT_LENGTH` (center-to-center distance between the two semicircular ends; numerically equal to the straight tangent segment length for a stadium slot). Do not pass an unclassified value into a slot helper.
- The canonical direct-DXF slot uses overall `L_TOTAL` and end width `W` for a SINGLE closed Layer-0 LWPOLYLINE with two straight tangent segments and two true semicircular bulges; optional AutoLISP retains its existing spec: `(SLOTX L_TOTAL W)` or `(SLOTY L_TOTAL W)`, where `W` is slot width / end-circle diameter and `L_TOTAL >= W`. If the drawing gives center distance `C`, convert explicitly as `L_TOTAL = C + W` before storing or drawing the slot.
- If witness lines do not prove whether the printed slot length is overall or center-distance/tangent length, apply Section 4.4; do not guess from appearance or from a reference DXF.
- **V4.12 count-only n-R with proved slot width:** If `4-R` clearly targets FOUR semicircular ends of TWO depicted stadium slots with width `W=12`, each end has `R=W/2=6`. Build exactly four R6 semicircular ends (two per slot), not four slots or an unanswered radius. Generalize ONLY when slot identity, semicircular ends, leader count and dimensioned width are independently proved. Otherwise retain normal topology/size FLAG. Preserve independent slot overall-versus-center-distance semantics.


#### 8.4.1 Canonical Slot Spec — No Ambiguous `len` Parameter
Inside `HOLES`, slots MUST use one of these canonical forms:

```lisp
(x y (SLOTX L_TOTAL W))
(x y (SLOTY L_TOTAL W))
```

- `L_TOTAL` = total end-to-end slot length.
- `W` = slot width and diameter of each semicircular end.
- Internal helper geometry must use center offset `(L_TOTAL - W) / 2`.
- If the drawing supplies center-to-center / tangent length `C`, convert before storage: `L_TOTAL = C + W`.
- Reject/flag any slot where `L_TOTAL < W`, or where source length semantics are not proven.
- Do not use a generic helper argument named only `len` unless the function contract explicitly states `len = L_TOTAL`; ambiguous helper semantics are prohibited.

---


**V4.7 DXF default:** serialize each proved inner slot as exactly ONE closed CW `LWPOLYLINE` with semicircular bulge magnitude `1`, original proven `L_TOTAL`/`W`, exact tangent points and no faceted approximations, overlapping circles or independent calculations for composite output. The legacy `SLOTX`/`SLOTY` contract is request-only Lisp and must consume the same canonical derived geometry. Validate real containment, count and source length classification before production DXF.
