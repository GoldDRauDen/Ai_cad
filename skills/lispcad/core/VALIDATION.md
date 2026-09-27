# LISPCAD Core — Validation

## V4.13 approved 520315-18 independent checks

- Before comparing a reference DXF, reconcile $INSUNITS metadata with independently established PDF/user-confirmed actual numeric units. If contradictory and unresolved, FLAG SOURCE_UNIT_CONFLICT; do not automatically scale by 25.4. Output DXF remains mm, $INSUNITS=4.
- Treat original and mirrored drawing CODES as separate records. A mirror requires an established original/target relation, axis and feature scope, including actual holes/slots/R/C/bends, then independent count/containment validation. When inner formed faces are shown, assemble the proved INSIDE_VIEW first, apply only the evidenced reflection and compare hole family/center only in a shared final frame.
- If bend J, legible handwritten Nobi and a genuinely comparable table row ALL exist, draw with N_hand and FLAG HANDWRITTEN_NOBI_DIFFERS_FROM_TABLE when the prescribed values disagree. Comparing a 165° note to a 90° table is an invalid conflict; no compatible row does not override handwriting.
- EXACT printed PDF inputs never receive a comparison tolerance. Only absolute differences strictly <0.01 mm caused by internal precision/rounding in an already-correct DERIVED result can pass an arithmetic-only comparison with reference DXF. Exactly 0.01 fails this test. This does not waive feature/datum/topology/bend/manufacturing checks. V4.12 already prohibits routine shop-spacing customer approval questions; do not duplicate that rule.


Source: approved V4.3 production baseline.

## V4.11 PREVIEW vs production validation — active

The user approved **DRAW → FLAG → CONFIRM**: draw a reasonable PDF-supported provisional shape in Magenta with adjacent assumptions, or separate independently proved source/orthographic views when no defensible flat is possible; ask targeted questions after drawing. Record uncertain type/topology/size/datum as `FLAGGED` and mark such parts `PREVIEW` or `VIEWS_ONLY`, never `PASS`. Any such part makes the entire default composite `*_ALL_REVIEW_ONLY.dxf` / **NO CUT**. A previous user QA PASS on a delivered file does not certify any later changed file. The original Section 5 geometry, datum, counts, containment, material and bend-domain production gates remain fully mandatory once uncertainties are resolved. The earlier 'numeric-only Magenta' restriction is historical for previews but remains superseded by this user-approved review-only rule. See [approved regression](../../../regression/qa/520625-15_V4_11_APPROVED.md).

## V4.8 required cancellation and regression audit

Classify each source feature-family callout as ACTIVE or unequivocally CANCELED before count closure. Require original quantity for each active family and ZERO produced entities for confirmed full-family deletions; include individual and translated composite DXF read-back. Ambiguous/partial strike-through blocks deletion and requires clarification. Apply approved regression/datum/520709-07_APPROVED.md for 039915 external-step datum, 039918/039919 diagonal/hole family and full reflection, and 040006 deletion of the complete 2-Ø8H7 family with active 6-M8 and 4-Ø9 retained. Matching overall extents alone cannot PASS these checks.

## 5. Error Detection & Manufacturing Validation Engine

Before exporting ANY production DXF or optional AutoLISP, run the following automated checks:

### 5.1 Geometry & Dimension-Semantic Integrity Engine
- **Closed Polyline Check**: Outer boundary vertices must form a continuous loop that explicitly closes at $P_{\text{start}} = P_{\text{end}}$.
- **Self-Intersection Check**: Ensure no overlapping edges or intersecting outer polyline loops exist.
- **Vertex Ordering**: Outer boundaries must follow Counter-Clockwise (CCW) orientation; internal cutouts must follow Clockwise (CW) orientation.
- **Source-Origin/Axis Mapping Check (V4.10):** For every absolute or ordinate-based feature, confirm the actual source-view origin and positive X/Y directions from drawing evidence BEFORE any DXF coordinate assignment; record its target CAD datum and signed source→CAD equation, then verify an independent edge/overall closure when available. Negative source Y is NOT a CAD Y coordinate. Transferring `Y=-30` from a proved top-left origin on a view 138 mm high to a bottom-left CAD datum MUST give `Y=108`, not `-30` or `88`. Missing origin/axis evidence is FLAGGED and prevents production PASS; do not borrow an adjacent hole/contour datum.
- **Datum Graph Connectivity Check**: Every critical hole/notch/step coordinate must have a connected dimension path from an identified datum per Section 4.2.
- **Dimension-Type Check**: Each used dimension must be classified as baseline, chain, step/local, overall, or ordinate before arithmetic.
- **Dimension Endpoint Identity Check**: For every crowded or parallel dimension group, verify that each dimension's start/end node targets the correct entity type (`OUTER_EDGE`, `CONTOUR_EDGE/STEP`, `HOLE_CENTER`, etc.). Reusing a neighboring endpoint is a semantic FAIL.
- **Contour Topology Check**: Verify that the ordered visible boundary (including steps/recesses/protrusions) is reproduced before numerical closure. A geometrically closed but topologically wrong rectangle/step is FAIL.
- **Reference-Datum Check**: Parenthesized/reference dimensions must retain their actual extension-line datum; using the nominal value directly as a global coordinate without datum proof is FAIL.
- **Chain Closure Check**: Where an overall width/height is present, verify that the proven chain closes to the overall dimension. A closure failure is a semantic FAIL even if the CAD polyline itself is perfectly closed.
- **Reference DXF Comparison Check**: When Section 2.4 is active, compare feature coordinates and topology against the master DXF after PDF interpretation. First apply the approved material-table automatic Laser R rule for eligible corners; do not exclude matching DXF-only R0.5/R2 simply because PDF omitted the callout. Only explicitly approved downstream shop-only differences may be excluded.
- **Feature Count Closure Check**: For every explicit quantity callout (`n-Ø`, `n-M*`, `n-slot`, `n-R`, `n-C`, repeated notch family, etc.), the generated family count MUST equal `n`. Thread-to-pilot conversion changes diameter representation, not the required count. Missing or extra members are FAIL, not WARN.
- **Connected primitives are not separate manufacturing features (approved `055958` regression)**: Count by proved topology, actual manufacturing operation, and endpoint connectivity, **not** by the number of same-colored DXF LINE/ARC entities. One approved `055958` Section 4.10 slit contains Green `LINE 55A` + `ARC 55B R0.5` + `LINE 55C`, which meet at their endpoints: feature count **1**, constituent entity count **3**. Common color alone does not prove that unrelated entities form one feature. The local R0.5 in this specific case is not a universal requirement of all slit reliefs. Remove only this slit method/count FLAG; independently uncertain customer sizes/datum still FLAG.
- **Feature Family Isolation Check**: Keep each family (`Ø5.5`, `M4→Ø3.3`, `M5→Ø4.2`, slots, cutouts, etc.) independently counted and datum-traced. Do not use one family's centerline/dimension to create or position another family without explicit evidence.
- **Local-Face → Flat Transform Check**: Every feature dimensioned on a bent face must have a proven Section 4.2.7 transform into global flat coordinates. Copying a local formed-face coordinate directly into the flat pattern is FAIL.
- **Bend Sequence Check**: Verify face order independently of total-length closure. Matching overall blank length does not PASS bend order. Bend coordinates must follow the proven sequence in Sections 4.2.8 and 4.7.
- **Feature Containment Check**: Every closed hole/slot/internal cutout must lie fully inside the material region unless the drawing explicitly defines an open-edge notch/slot. Any closed feature wholly or partly outside the outer boundary is FAIL.
- **Bend-Line Material-Domain Check**: Bend lines may exist only where material crosses the bend. A line passing through a void, center cutout, open gap, or outside the part is FAIL; split the bend line into valid material segments when required.
- **Slot-Semantics Check**: Verify that every generated slot uses a classified source length and the canonical `L_TOTAL` semantics in Section 3.1. A center-distance value passed as overall length (or vice versa) is FAIL.
- **No Placeholder Bounding Rectangle Check**: If the source contour contains a step, protrusion, recess, leg, or open center, a bounding rectangle is not an acceptable placeholder. Closed geometry that has the right bounding box but the wrong topology is FAIL.
- **PASS Evidence Rule**: Never mark a checklist item `PASS` merely because the generated entity exists or looks plausible. `PASS` requires that the corresponding semantic/geometric validation was actually executed and succeeded. If the check cannot be executed from available evidence, use `FLAGGED`, `WARN`, or `N/A` as allowed by Section 9.

- **Point/Circle semantic check (V4.4):** enforce per-feature PIERCING scope, strict Ø<t/2, effective pilot Ø for M, approved Excel threshold inheritance and ordinary POINT ByLayer vs PIERCING+THROUGH HOLE POINT Green. Missing capacity data must not silently be treated as cuttable.
- **Laser R automatic check (V4.4):** verify material row, eligible convex/concave corner class, correct R0.5/R2/R3 only on otherwise uncalled-out corners, precedence of explicit PDF R/C, and independent R=t bend reliefs.
- **Unknown numeric preview isolation (V4.4):** a known-topology estimated size/coordinate may be Magenta, integer-rounded and FLAGGED if the user wants preview output; a feature of unknown identity or invented topology cannot PASS or be output as speculative production geometry.
- **Retained inner piece semantics (V4.4):** a PDF note to retain a cut-out piece must not automatically clone a second detached cut-out.

### 5.1.1 Full Internal Verification, Minimal External Noise
- Every check in Section 5.1 remains mandatory even when the user asks for a short report.
- Do not print a long PASS checklist by default. Internally execute the checks, then expose only:
  - one compact overall validation line when all required checks pass; and
  - every `FAIL`, `FLAGGED`, actionable `WARN`, unresolved ambiguity or needed user confirmation; exclude nonblocking shop-distance-only advisories under §5.2.
- A concise report MUST NOT hide an unresolved production risk. Brevity controls presentation, not engineering rigor.
- Do not narrate exploratory reasoning, discarded hypotheses, or general sheet-metal theory unless the user asks for an audit/explanation.

### 5.2 Manufacturing Feasibility Rules

| Feasibility Parameter | Constraint Rule | Violation Action |
| :--- | :--- | :--- |
| **Minimum Cut Hole Diameter** | Use the applicable, inherited minimum from `references/MATERIAL_RULES.md` after approved thickness selection; the unconditional `Ø<t/2` POINT rule is checked before the table | Verified below-capacity hole becomes POINT ByLayer **without a capacity FLAG**; unresolved table/material becomes provisional CIRCLE Magenta + FLAG |
| **Minimum Bridge / Web Width** | Distance between hole edge & part boundary $\ge t$ | Flag low confidence warning |
| **Laser Piercing Accessibility** | Distance between adjacent piercings $\ge 10\text{ mm}$ | Group piercing locations |
| **Bend Line Collision** | Distance between hole edge & bend line $\ge 2 \times t + R_{\text{bend}}$ | Flag potential hole deformation |

**V4.12 shop-distance question suppression:** Treat minimum bridge/web, inter-piercing spacing and hole-to-bend proximity as optional/internal nonblocking **advisories** for geometry drawn as printed in the PDF. Do not shift/remove such geometry, block a source-faithful preview, or ask routine customer clearance acceptance solely for these heuristics. Maintain mandatory PDF-specific clearances, actual self-intersection and containment, source datum, hole-capacity rules, unproved dimensions and real demonstrated production conflicts; a genuine conflict still receives an actionable FLAG.

---


## Historical V4.7 saved-DXF dual-export audit (explicit-request legacy only)
Before declaring the canonical model PASS, actually execute every preceding V4.6 PDF-semantic, source/material, true contour topology, datum, feature-count, containment and bend-domain check. A serializer's structural validations cannot prove these engineering facts.
Under explicit-request **legacy V4.7 dual export** only, for EACH individual and combined DXF reopen the SAVED file and audit: real mm DXF, Layer 0 only, correct V4.6 entity/linetype/color/POINT/CIRCLE and bulges, geometry/count against the canonical source, no extra code-label TEXT. Combined drawing MUST contain exactly one translated copy of each production-PASS part, in explicitly declared code order descending Y, separated by at least 10 mm layout-only bbox clearance; record/check all offsets in the manifest. Keep numeric-only user-requested Magenta _PREVIEW outside production _ALL.dxf and do not mark preview PASS. Unknown topology/type/bend/material/datum blocks export. Count the `055958` Green LINE+ARC+LINE as ONE slit operation, not three.

## V4.9/V4.10 current output precedence

Default output is **ONE** top-to-bottom code-labeled composite, or `_ALL_REVIEW_ONLY.dxf` with all source-view groups/FLAGs and global NO CUT when any code is not independently production PASS. Exclude `AI_META` non-cut labels from the Layer-0 manufacturing audit. The historical V4.7 dual-export section above does NOT require default individual DXFs or manifest. The V4.10 source-origin/axis check in Section 5.1 is mandatory upstream BEFORE a production PASS or composite entity serialization.

### V4.14 direct existing-output audit and overlapping-cut QA

When explicitly asked to compare a PREVIOUSLY EXPORTED AI DXF with a user-approved reference, compare **AI DXF vs reference DXF FIRST**, not PDF vs sample. Normalize only independently proved source-unit interpretation, source orientation and layout translations; compare actual machining curves, typed hole/slot families and original source-callout counts, cut unions, complete unfold coordinates, all bend-pair coordinates and bend-line clipping to material. Geometric identity accepts ARC+LINE versus equivalent exact closed LWPOLYLINE/bulge; raw entity counts are not semantic feature counts. A partial source/orthographic view does not pass against a reference completed flat. Classify MATCH/PARTIAL/DIFF per code and test originally matched codes again after any rebuild. THEN inspect PDF to diagnose mismatches; independent PDF-FIRST interpretation remains the creation procedure. For truly overlapping cut holes require one non-self-intersecting Boolean-union contour and separate family quantity closure, rather than several overlapping interior cut circles. Strict `<0.01 mm` arithmetic residual is permitted ONLY for already-correct derived values per existing V4.13; every PRINTED source number remains exact. Six-code test: `regression/qa/520217-26_V4_14_APPROVED.md`.
