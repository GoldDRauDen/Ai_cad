# TrainAiCad — DXF-first production (V4.13)

TrainAiCad is a user-calibrated CAD production skill repository, **not an automatic training environment**. Only user-approved rules enter the production skill. Begin with [AI_ENTRYPOINT.md](AI_ENTRYPOINT.md).

## Approved V4.13 deduplicated calibration — 520315-18 (2026-09-27)

The user approved all L01–L08 generally, and the ten-code 520315-18_ss.dxf reference as intended geometry with actual **mm** coordinates despite an inch header. Deduplication against V4.12 removed already-established slot center-vs-overall witness rules, the need to exhaust explicit PDF calculations before questioning, and ordinary shop-spacing acceptance-question suppression. Only NEW V4.13 rules: reference INPUT unit conflict without blind 25.4 scaling; per-code original/mirror relationship and reflected feature scope; assembling inner bent faces before any proven final reflection; a J/handwritten-Nobi-versus-applicable-table mismatch FLAG while retaining the handwritten geometry; and derived-only numerical comparison tolerance **strictly <0.01 mm** while retaining exact printed dimensions. Case IDs such as 018300 are regression EXAMPLES, not universal part dimensions. The approved reference does not certify a newly regenerated AI DXF.

[Self-contained approved regression](regression/qa/520315-18_V4_13_APPROVED.md) · [Current V4.13 portable](skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md) · [Immutable V4.13 release](skills/lispcad/versions/V4.13/SKILL_LISPCAD_V4_13_PORTABLE.md) · [Preserved V4.12](skills/lispcad/versions/V4.12/SKILL_LISPCAD_V4_12_PORTABLE.md).

## Approved V4.12 deduplicated calibration — 520217-27 (2026-09-27)

V4.11 already contained the generic Magenta DRAW → FLAG → CONFIRM workflow and separate VIEWS_ONLY projections when no defensible flat can be built; those are retained, not duplicated. The user directly approved the following specific refinements: sheet-material-family prefixes `SUS→SUS`, `SP/SS→SS`, `A→AL` with the existing SUS430 exception; an unconfirmed proven round hole remains an explicitly Magenta estimated **CIRCLE Ø?**, not an unjustified POINT; `4-R` on two stadium slots of width 12 derives four semicircular **R6** ends; unique printed/handwritten flat calculations are not repeatedly queried, and an unresolved independent hole does not suppress a fully proved flat. Routine PDF-faithful shop spacing advisories are not customer clarification questions, while true production validation remains mandatory. **No reference DXF was supplied and no revised 520217-27 production export was certified** in this calibration.

[Approved Q&A regression](regression/qa/520217-27_V4_12_APPROVED.md) · [Historical V4.12](skills/lispcad/versions/V4.12/SKILL_LISPCAD_V4_12_PORTABLE.md) · [Immutable V4.11](skills/lispcad/versions/V4.11/SKILL_LISPCAD_V4_11_PORTABLE.md).

## Approved V4.11 DRAW → FLAG → CONFIRM and 520625-15 QA (2026-09-26)

The user directly approved drawing plausible provisional geometry when source evidence is incomplete, marking **each uncertain portion Magenta (Layer 0 / color 6)** with an adjacent specific FLAG, and asking for confirmation **after producing the preview**. Preserve separately proved geometry precisely. If an unfolded flat cannot be established responsibly, draw independently proved orthographic/source views as separate labeled groups (`VIEWS_ONLY`) under the correct code instead. Any open FLAG makes the single output `*_ALL_REVIEW_ONLY.dxf` with global **NO CUT**; production PASS still requires confirmed dimensions, full Section 5 manufacturing validation and saved-DXF read-back. This expands preview permission only, not automatic production acceptance.

The user reports QA PASS of the previously delivered seven-code `520625-15` job and explicitly confirmed `036575`: two Ø5 holes lie opposite one another on a diameter of its Ø300 disk, center-to-center distance 180 mm, and one Ø9 is at the disk center. The specific three-hole question is closed; this does **not** automatically certify a subsequently modified DXF. See [approved V4.11 QA regression](regression/qa/520625-15_V4_11_APPROVED.md) and [current portable skill](skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md).

## V4.8 approval — 520709-07 (2026-09-26)

The user approved one narrowly scoped manufacturing interpretation rule: a clearly struck-out COMPLETE hole-family callout with an unambiguous leader deletes all its holes even when obsolete circle symbols remain visible. Crossing out only tolerance/finish never automatically deletes holes; unclear scope requires a question. Regression 039915 requires an OD external-step datum (25, not 22.36); 039918/039919 require slope 50, correct printed M4/Ø5 groups and exact corrected reflection; 040006 requires deleting its entire 2-Ø8H7 group, preserving 6-M8 and 4-Ø9. See [approved regression](regression/datum/520709-07_APPROVED.md). V4.7 export and V4.6 engineering remain unchanged; V4.7 snapshot is preserved.

## Approved V4.10 drawing-origin and axis rule (2026-09-26)

The user **directly approved** the previously proposed source-frame lesson using original drawing `520728-06` code `043793` (page 4): the absolute coordinate origin is the part's **top-left**, its proven height is `138 mm`, and all three Ø7 holes on the source `Y=-30 mm` row are at target bottom-left DXF `Y=138-30=108 mm` (NOT `88 mm`). For EVERY future absolute/ordinate drawing, first prove the source origin's real material edge/feature, source +X/+Y direction, target CAD datum, and then transform signed source ordinates; the location cannot be inferred from page position or CAD habits. Different views/formed faces require independently proved frames. Ambiguous frames stay FLAGGED; reference DXF is calibration after PDF interpretation, not a missing-coordinate source. See [approved regression](regression/datum/520728-06_043793_TOP_LEFT_APPROVED.md), [core rule](skills/lispcad/core/DATUM_DIMENSION.md), [arithmetic helper](tools/datum_coordinates.py) and [tests](tests/test_datum_coordinates.py). This approval does NOT resolve customer-pending `043796` Z lengths, `043797` two Ø? or `043799` 165° Nobi.

## Approved V4.9 output mode (2026-09-26)

**One DXF total by default**, not one DXF per code. It includes every code in the page-1 order, top-to-bottom, as nonoverlapping clusters with >=10 mm layout-only clearance and the exact code visibly labeled on non-cut `AI_META`. No default external manifest or individual files. If any source Ø/Nobi/unfold datum is unresolved, the one output becomes `<JOB>_ALL_REVIEW_ONLY.dxf` including all part groups, separate proved source views if no safe flat is possible, Magenta estimated numeric features/FLAGs where authorized, and global **NO CUT** warning. A production `<JOB>_ALL.dxf` is possible only when ALL included codes independently PASS. Operators exclude `AI_META` labels from CAM cutting. Optional individual DXFs, manifest, legacy dual output and `c:DRAW` Lisp require explicit requests.

**Output-only change:** V4.9 leaves all V4.8 and earlier approved geometry/manufacturing rules intact: PDF-first contour/datum/count verification, Nobi, material Laser R, SUS430 process-specific routing, Cu/Brass t6, scoped POINT/CIRCLE, and confirmed 055958 single connected Green slit. A customer-uncertain value in 520728-06 remains a case-specific FLAG, not a new universal rule. V4.8 and V4.7 historical releases are immutable. See [V4.9 export regression](regression/export/DXF_SINGLE_COMPOSITE.md).

## Current modules and implementation

- [Portable current V4.13](skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md), identical to [immutable V4.13 release](skills/lispcad/versions/V4.13/SKILL_LISPCAD_V4_13_PORTABLE.md); [historical immutable V4.12](skills/lispcad/versions/V4.12/SKILL_LISPCAD_V4_12_PORTABLE.md); [historical V4.11](skills/lispcad/versions/V4.11/SKILL_LISPCAD_V4_11_PORTABLE.md); [historical V4.10](skills/lispcad/versions/V4.10/SKILL_LISPCAD_V4_10_PORTABLE.md) preserved; [historical V4.9](skills/lispcad/versions/V4.9/SKILL_LISPCAD_V4_9_PORTABLE.md) preserved; [historical V4.8](skills/lispcad/versions/V4.8/SKILL_LISPCAD_V4_8_PORTABLE.md) preserved; [historical V4.7](skills/lispcad/versions/V4.7/SKILL_LISPCAD_V4_7_PORTABLE.md) preserved. [Historical V4.6](skills/lispcad/versions/V4.6/SKILL_LISPCAD_V4_6_PORTABLE.md) preserved.
- `skills/lispcad/core/`: DRAWING_READING, DATUM_DIMENSION, VALIDATION, CAD_OUTPUT; load all before working.
- `skills/lispcad/{modes,topology,features}/`: load all applicable composable manufacturing rules.
- `references/`: full approved material, Nobi and metric-thread pilot tables.
- `regression/`: approved drawing cases and `export/DXF_SINGLE_COMPOSITE.md` for approved V4.9 default (`export/DXF_DUAL_EXPORT.md` is historical legacy).
- `tools/DXF_INPUT_SCHEMA.md` and `tools/export_dxf.py`: independently verified geometry interface and DXF serialization/read-back; `tests/test_export_dxf.py` uses synthetic input.

## Production sequence

Interpret the PDF independently, calculate manufacturing geometry once, and run real Section 5 validation BEFORE declaring canonical data PASS. Serialize identical checked part-local data as translated clusters into ONE code-labeled top-down DXF, then verify its source-to-cluster equivalence, metadata labels and review status. Optional requested individual DXFs/manifest must use the SAME data. Prove the absolute drawing source origin/axis signs before calculating coordinates, as in V4.10's 043793 regression. V4.11 uncertain but source-supported geometry is previewed with Magenta assumptions/FLAGs, or displayed as separate VIEWS_ONLY source groups if the flat cannot be inferred. Confirm the outstanding questions and rerun all checks before production release. A reference DXF is calibration ground truth only after user declaration. Optional `c:DRAW` Lisp uses that SAME verified model if requested. A structural file audit or synthetic exporter test never substitutes for PDF-specific datum, material or geometric containment verification.

```bash
python -m pip install -r requirements.txt
python tools/export_dxf.py job.json out/  # one labeled ALL.dxf or ALL_REVIEW_ONLY.dxf
python -m pytest tests/ -q
```

New engineering lessons require separate direct user approval. GitHub is a portable storage for approved production skills, not a substitute for that review.
