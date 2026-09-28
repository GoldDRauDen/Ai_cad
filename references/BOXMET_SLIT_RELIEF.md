# BOXMET_SLIT_RELIEF — V4.16 approved box-corner slit construction

**Status:** USER APPROVED 2026-09-28.  
**Scope:** Only source-proved BOXMET-style sheet-metal boxes with a central/base rectangle and four adjacent bent flanges.

## 1. Trigger / no-trigger gate

Apply this reference when the source topology proves all of:
- one central/base rectangle `L × W`;
- four adjacent bent flanges;
- adjacent flange bend directions meet at the box corners;
- a BOXMET corner slit is required to prevent corner bend interference/deformation.

In this topology, do **not** omit a required slit merely because the outer CUT contour already closes.

Do **not** auto-apply this reference to:
- ordinary L/U/Z profiles;
- a single flange or free edge;
- a non-crossing bend;
- an unrelated slit/relief/seam topology;
- a drawing-specific alternate or explicitly cancelled relief.

For these cases, “no BOXMET trigger” means the BOXMET slit is not added; evaluate any other explicit/approved relief rule independently.

## 2. Orientation: which flaps retreat by t

Let `L` and `W` be the proved base-rectangle dimensions.

### Case A — L >= W
Bottom and Top flaps retreat by `t`; Right and Left flaps remain full. Slit base points in a local base frame:
`(t,0)`, `(L-t,0)`, `(L-t,W)`, `(t,W)`.

### Case B — W > L
Right and Left flaps retreat by `t`; Bottom and Top remain full. Slit base points:
`(L,t)`, `(L,W-t)`, `(0,W-t)`, `(0,t)`.

The signs/orientations of the slit and lead rays follow the corresponding physical corner.

## 3. Parameters from approved BOXMET tool

- `SlitLen = t + 0.2`
- `LeadVal = 3.0` only when the BOXMET tool material value is exactly `SS` and `t < 6.0`
- otherwise `LeadVal = 6.0`
- local fillet radius `R = 0.5`
- Layer `0`
- slit color ACI `3` Green

Do not silently remap a different material string into the tool's exact `SS` branch. TrainAiCad material-family rules remain separate unless an approved conversion explicitly controls this tool input.

## 4. One slit = one connected three-primitive feature

Each BOXMET slit is ONE manufacturing feature: `LINE + ARC R0.5 + LINE`.

Let `B` be the theoretical corner/base point, `E1` the slit end with `|B→E1|=SlitLen`, `E2` the lead end, `θ` the included ray angle, `R=0.5`.
- `tangentDist = R / tan(θ/2)`
- `centerDist = R / sin(θ/2)`
- tangent point 1 = `B + unit(B→E1) × tangentDist`
- tangent point 2 = `B + unit(B→E2) × tangentDist`
- arc center = `B + unit-bisector × centerDist`

Output the trimmed LINE, tangent ARC R0.5, trimmed LINE. The arc is not a separate relief and not automatic Laser R.

## 5. CUT/BEND interaction

Where the solid BOXMET slit/CUT occupies the same local corner segment as dashed bend/reference geometry, interrupt the dashed segment. Do not overlay BEND/reference through slit CUT.

## 6. 520801-04 / 044858-044859 approved regression

Source recognition: box-corner bend transition around `285 | 43`; purpose: prevent bend deformation/interference.

For `t=1.5`:
- `SlitLen=1.7`
- `LeadVal=6`
- `θ=135°`
- `R=0.5`
- tangentDist `0.207106781186...`
- short straight `1.492893218813...`
- diagonal straight `8.278174593052...`

Both `044858` and `044859` require the corresponding mirrored slit.

## 7. Deduplication with 055958

Older `055958` already proves one relief may be connected `LINE + ARC R0.5 + LINE`. V4.16 adds only BOXMET trigger/omission, L/W retreat selection, exact parameters, analytic construction, four-corner placement, bend interruption and 044858/044859 regression.
