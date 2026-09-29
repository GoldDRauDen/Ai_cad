# LISPCAD Feature — KEGAKI / locating marks

**V4.20 approved.**

KEGAKI is an independent manufacturing family, not CUT/BEND/decoration. Production KEGAKI is Layer 0, Color 1 Red, LINE or proved LWPOLYLINE. Red supports identification but is not proof by itself.

Every mark needs function, host-face ownership, source/local datum and quantity. A formed-face mark follows that face through the same local-face -> flat transform. Fold-back must reproduce the intended physical locating position.

Do not join separate mark segments merely because they align in the flat. If the positioned component contacts separate faces/material regions with a gap/bend-clearance, keep the marks split.

## HD4 PL1 / PL2
Do not add a KEGAKI outline to every secondary plate by symmetry. In the approved HD4 example, PL1 is located by the proved physical material edge and has no copied equivalent mark; PL2 is positioned inside the face and has a locating KEGAKI footprint. This is a function/source rule, not permission to invent a mark merely because a part appears interior.

## RIB locating marks
RIB KEGAKI is the contact/position footprint on the MAIN part after forming, not an automatic copy of the full RIB contour. It may be separated across multiple host faces. Verify by fold-back/contact.

RIB-part cancellation and main-part KEGAKI cancellation are independent decisions; do not delete the mark without its own source/revision scope.

Audit KEGAKI independently for count, host face, datum/transform, continuity/segmentation, Red property and fold-back locating function.
