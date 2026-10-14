# LISPCAD Feature — SLIT / bend relief routing

**V4.29 custom source-slit gate; V4.20 base formulas retained.**

## V4.29 — custom source-instructed slit

A printed/handwritten `スリット`, `SLIT`, or equivalent explicit slit instruction may define a **custom source-instructed slit**.

- This custom branch is instruction-driven. Do **not** add it merely because a bend exists, because a slit would be mechanically useful, or because a reference/sample contains one.
- The source value is drawing-specific. For example, `スリット 8` means the controlling explicit slit value for that scoped feature is 8 in that drawing. It does not establish a universal 8 mm rule.
- Read quantity, host edge/face, position, direction, and relation to BEND from the actual instruction, witnesses, leaders, and geometry. Such slits are often used around bend regions to reduce deformation, but that purpose does not prove that the slit lies at the bend center.
- Never hardcode a centerline or copy a reference-DXF coordinate into a new drawing.
- When the custom slit has an explicit controlling dimension, preserve it. Do not replace it with the generic `D90=t+0.2` or `D=t*sin(theta)` formulas below.
- If slit identity/scope is proved but a required numeric/position field remains unresolved, retain the feature and FLAG the unresolved field; do not silently drop `SLIT_RELIEF`.
- Load/close `references/SOURCE_MANUFACTURING_NOTE_CENSUS.md` for source-note provenance.

Existing crossing-bend, opposite-fold `R=t`, `055958`, BOXMET and other separately-triggered relief mechanisms remain independent. This section does not require an explicit `スリット` note for those already-approved mechanisms and does not change their trigger/orientation rules.

## Base classification

First classify whether a source feature is ordinary CUT slot/notch, custom source slit, bend relief slit, BOXMET slit, lance, KEGAKI or another process. Similar appearance or Green color does not prove process identity.

## 90-degree bend slit

For the approved generic 90° bend-relief family, and only when that mechanism is actually the routed controlling mechanism rather than an explicit custom slit dimension, retain:

`D90 = t + 0.2 mm`.

## Bend angle greater than 90 degrees

For the approved >90° bend-relief family, with included physical bend angle `theta` satisfying `90° < theta < 180°`:

`D = t * sin(theta)`.

Equivalent reflex form: `D = t * abs(sin(phi))` when `phi = 360°-theta`.

Approved t=3.2 examples:
- 150° -> 1.600000 mm
- 130° -> 2.45134221798 mm
- 110° -> 3.00701638651 mm

The 150° value equals t/2 only because sin(150°)=0.5; do NOT generalize t/2. Exactly 90° uses the separate `t+0.2` rule when the generic 90° relief mechanism applies. Slit depth is not Nobi.

Preserve source-proved slit direction/connectivity and applicable local fillet/tangent construction. Do not universalize a local R0.5 unless the source/existing mechanism proves it. Green LINE/ARC geometry may be slit/relief; Green is supporting evidence only. A Green POINT with proved PIASU semantics is a different family.

QA: close source-note provenance when applicable, correct quantity/value/position/direction, correct mechanism/connectivity, no duplicate/coincident paths, no helper geometry in manufacturing CUT, correct BEND interaction, and saved-DXF physical read-back.
