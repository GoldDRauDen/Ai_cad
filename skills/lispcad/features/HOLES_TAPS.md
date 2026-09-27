# LISPCAD Feature — Holes / Taps / Piercing

Approved calibration 520924-19, 2026-09-25. Uses `../../../references/MATERIAL_RULES.md` (transcribed approved workbook) and `../../../references/THREAD_PILOT_TABLE.md`.

## 3.1 Cutting features
- A verified cut round hole is a `CIRCLE`. A tapped M feature uses the standard **pilot hole** diameter, not the nominal thread diameter, unless the drawing explicitly specifies another effective hole diameter. Countersink/counterbore cut geometry uses the proven through-hole/pilot opening; do not cut the countersink's outer diameter.
- Slots and polygonal cutouts follow the separate `SLOTS.md` module and topology rules. A POINT is NOT a small circle, and converting an M callout does not change the required feature count.
- Trace the arrow/leader/note scope before applying PIERCING. A large PIERCING label elsewhere on a sheet is not blanket authorization for every feature family.

## V4.12 unresolved circular-hole diameter gate — before numeric POINT/CIRCLE tests

When the source confirms a feature is a ROUND HOLE but its Ø is customer-pending, draw a source-supported, integer-rounded estimated **CIRCLE** on Layer `0`, Color `6` (Magenta) with adjacent `Ø? / CONFIRM DIAMETER` note and independent FLAG. Preserve separately proved centers, quantity and flat contour. Set PREVIEW / NO CUT. Do **not** apply `d<t/2` or capacity-based POINT rules using guessed Ø; those require a known effective diameter. Explicitly scoped PIERCING remains independently authoritative. Unknown round-hole identity or center follows V4.11 source-supported preview/VIEWS_ONLY and separate flags, not a fabricated verified hole.

## 3.3 Approved POINT / CIRCLE decision (first matching rule)

**L09:** For **SUS430**, apply **SUS, 他** rows to cut-hole minimum and 白ピアス capability, independently of SS/SUS430/BRASS Nobi. At t6 the inherited minimum hole threshold is t/2 and White Piercing is 〇 (capability only).

1. If the PDF explicitly applies `PIERCING + THROUGH HOLE` to a feature family: `POINT` on Layer 0, DXF color 3 (Green); Ø/M only in Stage 1 report, not CAD.
2. Else if the PDF applies `PIERCING`: `POINT` on Layer 0, ByLayer (no explicit color 3/6), regardless of the worksheet's `白ピアス 〇/×` or nominal diameter. That worksheet column is machine **capability**, NOT drawing intent; a `×` does not suppress the explicit PIERCING POINT or create a capacity-only FLAG.
3. Else, if the effective cut-hole diameter `d < t/2`: `POINT` ByLayer with **no capacity FLAG**. This holds even without a worksheet row. Strict inequality: `d = t/2` proceeds to the worksheet test.
4. Else look up the applicable material/thickness row of `references/MATERIAL_RULES.md` (the approved `Rule_Bo_R&Hole.xlsx` transcription). If `d` is below that row's inherited minimum hole diameter: `POINT` ByLayer, **no capacity FLAG** even without PIERCING. Otherwise draw `CIRCLE` ByLayer at the effective cut diameter.
5. If the worksheet cannot resolve the material/thickness/limit or the output type remains unproved and `d >= t/2`, use a **provisional `CIRCLE` Color 6 (Magenta) plus FLAG**; never assert production readiness. For a proved tapped `M*` callout, obtain provisional `d` from the approved thread pilot table (e.g. M4 Ø3.3, M5 Ø4.2, M6 Ø5.0), except where the PDF explicitly overrides it.

The precedence above is per **feature family**, never per whole sheet. No numeric capacity FLAG is warranted when a higher-priority explicit PIERCING or verified capability rule definitively selects POINT. Independent uncertainty about quantity, center coordinates, PDF legibility, handwritten instructions or customer approval **continues to require FLAG**. If feature identity/topology is unresolved, do not invent a hole or switch type merely to fill an output.

**Color contract:** all geometry Layer `0`; ordinary `POINT` ByLayer (DXF 62 omitted or 256); **only explicit PIERCING + THROUGH HOLE** produces a green **POINT** (62=3). A *provisional* feature is Color 6. Do not add redundant circle geometry or Ø/M labels around a POINT. Retain Ø/M and the conversion reason in the Stage 1 report.

## 3.4 Special J markings vs ordinary hole features

A printed `J` associated with a special POINT operation is **exceptional**, not a general feature inferred from an adjacent POINT or reference DXF. Only create that POINT/J set when the PDF has an applicable note/leader; when the mark is unreadable, flag it. This usage must be disambiguated from any bend/Nobi `J-symbol` described by the bend module; do not transfer a J operation between them. Calibration `055957`: the user confirms the PDF has a special J indication, but exact leader location is deferred; do not manufacture its geometry from the DXF alone.

## Verification and workflow

Trace separately the original callout count, verified effective diameters, POINT-vs-CIRCLE type, datum for every center, and every independent FLAG. Run material-domain containment on CIRCLE features. Preserve the part and keep a distinct shop report for all converted POINTs (source Ø/M, center, method/trigger).
