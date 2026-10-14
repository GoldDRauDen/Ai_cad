# LISPCAD Feature — RIB routing

**V4.20 approved.**

A RIB with valid drawing/barcode/code, not cancelled/crossed out and not explicitly excluded is an independent manufacturing part and must be output/audited independently.

RIB locating KEGAKI belongs to the main part and is evaluated independently:
- it represents physical contact/position footprint after forming;
- it may span different formed faces and become separated segments in the flat;
- transform each segment with its owning face;
- fold-back must return the mark to the proved contact location.

Canceling a RIB does not automatically cancel its main-part locating KEGAKI. A separate source/revision instruction must cancel that mark.

Audit RIB CUT/HOLE geometry and main-part RIB KEGAKI as separate families.
