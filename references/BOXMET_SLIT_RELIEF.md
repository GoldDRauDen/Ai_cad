# BOXMET_SLIT_RELIEF — V4.16 construction + V4.18 signed-orientation hardening

**Status:** USER APPROVED 2026-09-28.  
**V4.18 hardening:** USER APPROVED / PUSH 2026-09-29 from 520929-18 direct audit. The V4.16 topology/parameters are unchanged; V4.18 makes the four local slit direction signs executable and makes BEND trimming depend on actual geometric intersection rather than corner proximity.

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

### V4.18 BOXMET_SIGNED_ORIENTATION — executable local directions

Use a local base frame with `+X` right and `+Y` up. Let `S` be the short slit-ray direction of length `SlitLen`; let `D` be the lead endpoint delta using `LeadVal` on each signed axis. Construct the local slit with these signs before any proved whole-part rotation/reflection.

For **Case A — L >= W**:
- bottom-left `B=(t,0)`: `S=(0,+1)`, `D=(-LeadVal,-LeadVal)`
- bottom-right `B=(L-t,0)`: `S=(0,+1)`, `D=(+LeadVal,-LeadVal)`
- top-right `B=(L-t,W)`: `S=(0,-1)`, `D=(+LeadVal,+LeadVal)`
- top-left `B=(t,W)`: `S=(0,-1)`, `D=(-LeadVal,+LeadVal)`

For **Case B — W > L**:
- bottom-right `B=(L,t)`: `S=(-1,0)`, `D=(+LeadVal,-LeadVal)`
- top-right `B=(L,W-t)`: `S=(-1,0)`, `D=(+LeadVal,+LeadVal)`
- top-left `B=(0,W-t)`: `S=(+1,0)`, `D=(-LeadVal,+LeadVal)`
- bottom-left `B=(0,t)`: `S=(+1,0)`, `D=(-LeadVal,-LeadVal)`

These signs are part of the BOXMET construction, not an optional visual mirror. A different final orientation is allowed only through an independently proved part/view transform; do not flip a single slit across a bend line because the result “looks symmetric.”


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

Construct the solid BOXMET slit/CUT first, then intersect its actual LINE+ARC+LINE geometry with each dashed BEND/reference segment. Interrupt/split BEND only where the slit truly crosses or overlaps the INTERIOR of that BEND segment. Empty intersection keeps the BEND continuous; endpoint-only contact terminates at the common endpoint and MUST NOT create an artificial gap. Do not trim by corner proximity, retreat-point proximity, or assumed symmetry. Do not overlay BEND/reference through an actual slit CUT.

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
