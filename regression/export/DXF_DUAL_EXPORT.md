# V4.7 DXF output migration — approved export regression

**Approved by user 2026-09-26:** DXF is default; Lisp is optional by explicit request; export BOTH separate per-code DXFs and consolidated DXF; direct main update; preserve complete approved V4.6 geometry/material/regression rules and immutable V4.6 snapshot. This is output contract approval only, NOT a new manufacturing/geometric lesson.

1. From one independently checked canonical data model, produce individual JOB_CODE.dxf per PASS part, combined JOB_ALL.dxf with EXACT translated copies in declared source order top-to-bottom and >=10 mm layout-only bbox clearance, plus JOB_MANIFEST.json mapping code/material/thickness/status/count/bbox/XY translation. No normal production Modelspace part-code TEXT.
2. Reopen each actual DXF; validate millimeters, Layer 0, approved V4.6 color/POINT/CIRCLE/slot bulges, real contour closure and entity counts. Combined global entity count equals sum; each inverse-translated combined entity equals its individual source. No independently recalculated holes, automatic R or bend lines.
3. User-requested numeric-only uncertain positions on proven topology may be Magenta + adjacent TEXT as separate _PREVIEW.dxf and _PREVIEW_ALL.dxf, **never** inside production ALL.dxf. Critical unknown topology/feature type/bend order/material/datum prevents generation.
4. Optional Lisp only if asked, c:DRAW dynamic DCL, from SAME canonical vertices/POINT decisions. No automatic fallback when DXF writing fails.
5. V4.6 technical regressions MUST remain: scope of PIERCING; material Laser R including SUS430 L09 and Cu/Brass L10; 055958 ONE approved connected Green LINE+ARC R0.5+LINE slit (3 entities, 1 operation); earlier datum, topology, unfold and slot tests with current-version precedence. Do not reintroduce superseded V4.3 global DXF-only R0.5 omission.

tests/test_export_dxf.py uses synthetic boxes to test *only serialization/packaging/roundtrip*; it does NOT certify PDF-reading or manufacturing shape accuracy. Full Section 5 and actual ground-truth drawing regression remain mandatory before production PASS.
