# LISPCAD Feature — KEGAKI / locating marks

**V4.20 approved; V4.27 weld-cue scope approved.**

KEGAKI is an independent manufacturing family, not CUT/BEND/decoration. Production KEGAKI is Layer 0, Color 1 Red, LINE or proved LWPOLYLINE. Red supports identification but is not proof by itself.

Every mark needs function, host-face ownership, source/local datum and quantity. A formed-face mark follows that face through the same local-face -> flat transform. Fold-back must reproduce the intended physical locating position.

Do not join separate mark segments merely because they align in the flat. If the positioned component contacts separate faces/material regions with a gap/bend-clearance, keep the marks split.

## V4.27 barcode weld cue / locating requirement

`REVERSED_E_ABOVE_BARCODE` is the approved visual cue for a reversed-e mark immediately above a part barcode. When proved, record `WELD_REQUIRED_CUE` and scope it only to the code / detail cluster identified by that barcode. Do not propagate the cue to an adjacent barcode, neighboring code, or the whole sheet.

`WELD_REQUIRED_CUE` proves the welding process expectation for that scoped cluster; it is **not** itself KEGAKI geometry and does not supply a footprint, dimensions, datum, quantity, or host face.

- If a scoped welded child part (for example a RIB / gusset / support) cannot self-locate during fit-up, locating KEGAKI on the main part is required. The mark geometry must come from explicit source KEGAKI evidence or from a proved contact/locating function and host-face transform. If that locating geometry remains unresolved after source exhaustion, keep `KEGAKI = UNKNOWN` / FLAG the affected geometry; never silently omit it.
- If a specific KEGAKI instruction is present, treat that as an independent welding/locating instruction even when `REVERSED_E_ABOVE_BARCODE` is absent.
- If neither `REVERSED_E_ABOVE_BARCODE` nor a specific KEGAKI instruction is present for the scoped code/cluster, do not infer welding or add KEGAKI solely from the presence, shape, symmetry, or proximity of a RIB / gusset / support.
- A welded child that is already mechanically self-locating does not acquire invented KEGAKI geometry merely because the barcode weld cue is present.

The barcode cue changes process/routing evidence only. It never authorizes copying the full secondary-part contour as KEGAKI.

## HD4 PL1 / PL2
Do not add a KEGAKI outline to every secondary plate by symmetry. In the approved HD4 example, PL1 is located by the proved physical material edge and has no copied equivalent mark; PL2 is positioned inside the face and has a locating KEGAKI footprint. This is a function/source rule, not permission to invent a mark merely because a part appears interior.

## RIB locating marks
RIB KEGAKI is the contact/position footprint on the MAIN part after forming, not an automatic copy of the full RIB contour. It may be separated across multiple host faces. Verify by fold-back/contact.

RIB-part cancellation and main-part KEGAKI cancellation are independent decisions; do not delete the mark without its own source/revision scope.

Audit KEGAKI independently for count, host face, datum/transform, continuity/segmentation, Red property and fold-back locating function.
