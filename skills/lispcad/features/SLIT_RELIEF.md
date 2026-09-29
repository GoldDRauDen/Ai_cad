# LISPCAD Feature — SLIT / bend relief routing

**V4.20 approved.**

First classify whether a source feature is ordinary CUT slot/notch, bend relief slit, BOXMET slit, lance, KEGAKI or another process. Similar appearance or Green color does not prove process identity.

## 90-degree bend slit
Retain the approved 90° relief depth:
`D90 = t + 0.2 mm`.

## Bend angle greater than 90 degrees
For the approved >90° bend-relief family, with included physical bend angle `theta` satisfying `90° < theta < 180°`:
`D = t * sin(theta)`.

Equivalent reflex form: `D = t * abs(sin(phi))` when `phi = 360°-theta`.

Approved t=3.2 examples:
- 150° -> 1.600000 mm
- 130° -> 2.45134221798 mm
- 110° -> 3.00701638651 mm

The 150° value equals t/2 only because sin(150°)=0.5; do NOT generalize t/2. Exactly 90° uses the separate t+0.2 rule. Slit depth is not Nobi.

Preserve source-proved slit direction/connectivity and applicable local fillet/tangent construction. Do not universalize a local R0.5 unless the source/existing mechanism proves it. Green LINE/ARC geometry may be slit/relief; Green is supporting evidence only. A Green POINT with proved PIASU semantics is a different family.

Existing crossing-bend, opposite-fold R=t, 055958 and BOXMET mechanisms remain independent. Do not replace their trigger/orientation rules with this >90° formula unless the actual feature is this approved family.

QA: correct depth/direction/connectivity, no duplicate/coincident paths, no helper geometry in manufacturing CUT, and correct BEND interaction.
