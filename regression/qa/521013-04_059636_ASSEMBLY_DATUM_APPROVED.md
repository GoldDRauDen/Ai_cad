# 521013-04 / 059636 — Assembly datum regression (approved plan 2026-10-13)

## Failure being prevented

- Earlier PDF-to-DXF output assigned both F-part M6 centers Y=25 mm from F bottom without a source dimension path.
- Operator identified Y=20 mm by constructing the assembly geometry and tracing Cyan/installation dimensions.
- A provided sample or later HD1 DXF matching 20 mm is **corroboration, not source authority**. The solver must not import a sample coordinate to fill a missing witness.

## Case-scoped dimension graph

Frame: one Y-positive assembly datum on parent A, with independent physical nodes for G and F. Example approved regression arithmetic, **not** a universal manufacturing formula:

- A reference -> G lower edge: +41
- G lower edge -> G M6 center: +28/2 = +14
- G M6 center -> F M6 center: +290
- A reference -> F lower edge: +325

Thus `Y(F_M6 from F_BOTTOM) = 41 + 14 + 290 - 325 = 20 mm`.

The 28 mm G height belongs to G; the use of half-height as its M6 offset requires the drawing's centered-hole witness. Mating part identity, source dimensional endpoints, reference-frame signs, and any face-to-flat transformation still require **PDF-source proof for each new production job**. The regression fixture is not a way to bypass that proof.

Fixture: `regression/datum/521013-04_059636_assembly_graph.json`. Its `USER_CONFIRMED:` tags encode the operator-reviewed training case, not an automatically reusable proof for another PDF.

## Expected tests

1. Proof graph returns +20 mm for F bottom -> F M6 and -20 mm in reverse.
2. Injected +25 mm relation fails `DIMENSION_CONFLICT`; no silent average or arbitrary correction.
3. Disconnected, opposite-axis, missing-witness, sample-only, contradictory-frame or non-finite input is rejected.
4. The L3 canonical/holistic guard independently re-solves the declared candidate; an asserted result of 25 mm or an unattempted candidate blocks the production PASS.
5. Standalone single-part jobs without assembly cues retain existing datum rules and do not require this solver.

## Boundaries

- The PDF is source control; an assembly line is only usable if physical witness endpoints match the actual part/feature.
- No inferential jumping across neighboring parallel dimension strings, visual contact or unchanged appearances of other parts.
- Preserve explicit local feature dimensions when they exist; only infer indirectly when source-backed installation geometry is sufficient.
- The solver determines signed **assembly-frame** offsets. It does not eliminate the host-face-to-flat, Nobi, fold-back, material and feature-count gates.
- This change does **not** claim that the previously issued DXF has been repaired. A separate CAD re-export/QA is required.
