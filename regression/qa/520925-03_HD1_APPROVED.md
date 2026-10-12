# 520925-03 — HD1-assisted regression (2026-10-12)

## Approval and evidence boundary

The operator confirmed on 2026-10-12:

1. **HD1.dxf is an approved technical instruction for this job**, and may be
   consulted for the **method** on similar future drawings.
2. **Nobi 6.70 / 5.88 is handwriting specific to this job**. These numbers are
   NOT new rows for \`references/NOBI_TABLES.md\`.
3. The revised output \`hd1_revised.zip\` is a post-instruction reconstruction,
   not an independent PDF-only solve.

Authority remains the current repository's source and manufacturing contracts.
\`HD1.dxf\` is NOT permission to inject its specific coordinates into another
drawing. A future PDF must prove its own host faces, witnesses, radii,
Nobi, material domain and contact-footprint parameters.

**Not a blind reference test:** the revised HD1 job followed inspection of a
sample DXF. Retain the original source-only snapshot and classify these
results as \`REFERENCE_ASSISTED_UNDERSTANDING\` plus the new operator-approved
HD1 technical evidence. A future blind assessment must withhold all sample
geometry until after the source-only snapshot is frozen.

## Approved, job-specific expected assertions

| Code | Physical question | Approved derived result |
|---|---|---|
| 056135 | Rounded acute bend, inside included angle 83.66°, t4.5, Rin0.6 / Rout5.1 | OD 121.93 / 56.90, handwritten Nobi 6.70, flat 172.13, bend pair y115.23/121.93, clipped to x0..35 |
| 056138 | Oblique bend formed/profile witnesses | OD 108.60 / 49.04, handwritten Nobi 5.88, flat 151.76, bend pair y102.72/108.60, clipped to x40..75 |
| 056137 | B contact footprint, orientation under View X | Three red LINEs, x15..19.5, y0..35 |
| 056140 | B contact footprint at inclination 7° | Three red LINEs, x40..75, y20.47..25.00 |
| 056142 | B contact footprint at inclination 4°; one perimeter edge coincides | Two red LINEs, x40..75, y30.49..35.00; **do not double-mark the contour** |
| 056144 | B contact footprint at inclination 5° | Three red LINEs, x40..75, y15.52..20.04 |

There is no production KEGAKI on the four corresponding A parts. The composite
contains **11 red KEGAKI LINEs**, **4 DASHED BEND LINEs** (two bends), and
CUT entities retained separately; individual PASS DXFs remain CUT-only.

The 056135 displayed inside angle 83.66° must not be confused with the
96.34° ARC sweep when the associated DIMENSION text is overridden.

The PDF detailed part material/t4.5 remains authoritative under existing
\`DETAILED_SOURCE_BUNDLE\` precedence; conflicting page-1 summary material
must be accounted for, not unconditionally substituted.

## Generalizable mechanical lessons — existing rules, not new solvers

- Use \`SOURCE_MANUFACTURING_NOTE_CENSUS\` and \`PART_IDENTITY_GRAPH\` to
  distinguish welded constituent A from host B.
- Use \`KEGAKI.md\` to project **contact surfaces/footprint onto B**, not to
  copy the full A contour or draw guessed Magenta marks on A.
- Use \`FACE_GRAPH_UNFOLD_PROTOCOL\`, \`FORMED_PROFILE_OD_MEASUREMENT\` and
  \`ACUTE_BEND_LT85_FROM_SOURCE\` to reconstruct the physical outside
  envelope, choose the real free-edge datum and measure OD before deducting
  handwritten Nobi.
- Compare fold-back face mapping, host and contact direction separately from
  matching global 2D outlines. 056137 requires an explicit source-backed
  orientation/mirror check.
- Keep any truly unresolved field local REVIEW/FLAG. A PDF-only capability is
  not established merely because a later user-approved guide made this case
  solvable.

## Executable regression and scope

\`tests/test_520925_03_hd1_semantics.py\` contains reduced **synthetic CUT
holders** with the approved HD1 KEGAKI/BEND/OD expectations. It checks:

1. Six scoped parts' note-family ownership, 11 KEGAKI and four BEND lines,
   valid composite DXF/XDATA and individual CUT-only read-back.
2. Negative: omitted B-side KEGAKI even though the abbreviated source/member
   ledger remains internally balanced.
3. Negative: B-assigned KEGAKI emitted on A; invalid assigned destination.
4. Negative: wrong Nobi versus OD/flat/bend-pair arithmetic.
5. Negative: incomplete two-line bend member.
6. Negative: \`VIEWS_ONLY\` with only boolean claims of source exhaustion and
   no candidate/unresolved-object evidence.

**Limits:** This unit regression does **not** visually parse \`520925-03.pdf\`,
verify actual contact surfaces against all dimensions, or assert exact
Hausdorff equality with \`520925-03_SS.dxf\` (not included in the branch).
Do not label structural CI as fresh-source mechanical PASS. When reference
assets are available under an approved role, perform source-first/blind
reproduction and an independent physical-family diff separately.

## Root cause / fix location

- Rule texts already covered these mechanisms before this job. Do not add
  another Geometry Solver/Bend Solver or duplicate calculation tables.
- A canonical source-member self-equality and DXF ENTITY_ID read-back can
  pass if a production note was omitted upstream. The remaining failure is
  **source evidence ownership and runtime wiring**.
- \`tools/holistic_engineering_guard.py::canonical_job_anomalies\` verifies
  mapped manufacturing notes, target code/host assignment, source family and
  canonical member roles, per-member BEND double lines, and provided numeric
  OD/Nobi witness chains.
- \`tools/export_canonical_dxf.py\` runs the semantic gate before output.
  No canonical schema bump, no changes to material/Nobi tables or serializer.

**Residual risk:** An entirely unread/unrecorded PDF instruction is invisible
to a JSON-only guard. The upstream reader still must preserve a complete
independently challenged source census and physical witness inventory.
