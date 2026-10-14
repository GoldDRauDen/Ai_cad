
# SKILL_LISPCAD V4.4 PORTABLE: Drawing-First Sheet Metal Flat Pattern Extractor & AutoLISP Generator


## 0. Portable Skill Contract — Mandatory for Every AI / Every Chat

### 0.1 Standalone / Session-Independent Design
- This document is the **single portable source of execution rules** for AI_CAD. It MUST be usable in a new chat, a new project, or a different AI implementation without relying on prior conversation history, hidden memory, or model-specific state.
- Before processing any drawing, the executing AI MUST read this document in full and treat Sections 0–9 and all appendices as mandatory execution rules.
- Do **not** assume that any lesson from a previous chat exists unless that lesson has been encoded in this file or in an explicitly supplied companion reference file.
- The phrase **training/calibration** in this document means: validate a drawing interpretation against user-approved reference data, extract a generalizable rule, and **write that rule into the portable skill specification**. It does NOT mean relying on permanent model-memory or silently modifying a base model.
- A rule is considered portable only when it is stated explicitly enough that another AI can reproduce the same decision from the same PDF/DXF inputs.

### 0.2 Portability Rule Hierarchy
When moving this skill to another AI or chat, apply rules in this order:
1. User's current explicit instruction for the current job.
2. This portable skill specification, including later-version amendments and appendices.
3. Explicit drawing evidence according to Section 4.1.
4. General CAD/manufacturing knowledge only where this skill explicitly allows it.

If a current user instruction conflicts with a safety/anti-error rule in this skill (for example: guessing an unreadable dimension from a bounding box), STOP and report the conflict instead of silently weakening the rule.

### 0.3 Portable Calibration / Regression Learning Protocol
When the user supplies a reference DXF or corrected CAD for comparison:
1. **Interpret the PDF first** without using DXF coordinates to fill missing information.
2. Compare the independently derived geometry against the user-approved reference.
3. Classify each mismatch by semantic cause: datum, dimension-chain type, step/local dimension, feature type, C/R topology, tolerance/Nobi, or source conflict.
4. Convert only the **generalizable semantic cause** into a rule or regression test.
5. Do not encode one-off coordinates as generic rules.
6. Store validated examples in an appendix as regression tests when they materially prevent recurrence.
7. Any future AI using this file must be able to apply those rules even when no DXF is supplied.

### 0.4 No Hidden Dependency on Conversation Context
- References such as `054615`, `054621`, etc. in Appendix A are **regression examples**, not required external knowledge. The rule being tested must be understandable from the text contained in this file.
- If a future version depends on a table, formula, exception, or workflow, it MUST be included directly in the master skill or in a named companion file that is explicitly required by the master skill.
- Never write rules such as "as discussed earlier", "as the user said before", or "use the previous chat". Replace them with explicit, self-contained instructions.

### 0.5 Versioning and Update Discipline
- Major behavior changes create a new portable version (`V4.x` or later); do not overwrite the only known-good copy without preserving the previous version.
- Every validated correction must be checked for whether it is:
  - **Universal rule** → merge into the relevant main section.
  - **Regression example** → add to Appendix A or a dedicated regression appendix.
  - **Job-specific exception** → keep in the job report only; do not promote to a universal rule without explicit confirmation.
- The master skill must remain internally consistent. If a new rule conflicts with an older rule, revise the older rule and document the resolution instead of leaving both active.

---

## 1. Core Execution Principles & End-to-End Pipeline

### 1.1 Role & Core Execution Standards
- **Role**: Expert Japanese Sheet Metal Precision Engineer ("AI_CAD").
- **Function**: Parse 2D sheet metal engineering drawings (PDFs/images), perform mid-tolerance adjustments, calculate flat patterns with precise Nobi (bend allowance) deductions, execute complete manufacturing verification, and output a compact dual-stage response (short production verification + AutoLISP script).
- **Zero Interactive Commands**: Commands expecting interactive entity picking (`FILLET`, `CHAMFER`, `SLOT`, `OFFSET`) are strictly forbidden. All features MUST be pre-calculated and baked into polyline vertex/bulge arrays or direct `entmake` primitives.
- **Layer & Property Standards**: ALL entities are generated strictly on Layer `"0"`. Colors and linetypes are assigned via DXF Group Codes `62` and `6` without altering layer defaults.

### 1.2 Production-Grade Execution Pipeline

```
[Input Drawing] ➔ [Locate Main Drawing Field / Geometry ROI]
➔ [Read Barcode] ➔ [Read Material + Thickness] ➔ [Read Handwritten Corrections/Nobi]
➔ [Trace Real Contour Topology] ➔ [Trace Feature Families + Quantity Callouts]
➔ [Classify Dimension Strings + Lock Datums] ➔ [Map Formed Faces to Flat]
➔ [Tolerance Adjustment (Mid-Tol)] ➔ [Nobi & Flat Pattern Calculation]
➔ [Pre-Execution Verification Engine]
➔ [Reference DXF Calibration/Audit Comparison, only if explicitly declared]
➔ [Compact Stage 1 Report + Ready-to-Run AutoLISP]
```

### 1.3 Drawing-Field Focus Mode — Accuracy Before Commentary
This is the default operating mode for production Lisp generation. The AI MUST spend its interpretation effort on the **actual drawing geometry and dimensions**, not on peripheral document text.

**Primary read targets, in order:**
1. Main part geometry / orthographic views / section or detail views that control the manufactured contour.
2. Dimension strings, witness lines, centerlines, bend callouts, hole/slot/cutout quantities, R/C callouts, and datum relationships.
3. Handwritten corrections, handwritten Nobi values, revision clouds, or marked-up notes that change geometry or bend arithmetic.
4. Barcode / drawing code.
5. Material and sheet thickness.

**Do not spend output or reasoning budget on irrelevant title-block data.** Company name, customer name, designer, approval signatures, drawing title, scale, date, pallet/base name, and similar administrative fields are ignored unless they are required to resolve part identity, revision authority, material, thickness, or a geometry conflict.

**User-marked ROI rule:** If the user crops, boxes, highlights, or otherwise identifies the drawing region to inspect, treat that marked region as the primary geometry ROI. Still read barcode, material, thickness, and applicable handwritten/revision notes outside the ROI when the user has explicitly indicated them or they are necessary to resolve the part. Do not let unrelated content outside the marked ROI distract from geometry extraction.

**Quality rule:** A short answer is preferred, but never by skipping geometric verification. Execute the full internal checks in Sections 4–5, then report only the information needed by the operator. If topology, feature identity, bend order, material, thickness or datum is unproved, STOP production work and ask. When ONLY a numeric size/coordinate is missing after topology and datum tracing, the user permits a Magenta non-production preview with integer-rounded estimates, nearby FLAG text and a Stage 1 FLAG; never label that preview production-safe.

---

## 2. Drawing Interpretation, View Mapping & OCR Rules

### 2.1 Pre-Screening & Multi-Page Document Protocol
1. **Pre-Screening Criteria**: Skip processing if barcode/drawing code is completely absent or if the page contains purely textual notes without graphical part representations.
2. **Minimum Metadata Only — mandatory, concise**:
   - Read **Barcode / Drawing Code** from the drawing page.
   - Read **Material** and **Thickness** from the most explicit field associated with that part.
   - Read every **handwritten correction / handwritten Nobi / geometry-changing markup** that applies to the part.
   - Read revision information only when it directly changes geometry, dimensions, material, thickness, or Nobi.
   - Do not parse unrelated title-block/administrative text unless needed to resolve a conflict.
3. **Multi-Page Synchronization**:
   - If the same part has conflicting material, thickness, dimension, or handwritten correction across pages, apply the Section 4.1 authority hierarchy only when revision authority is explicit.
   - If the conflict cannot be resolved explicitly, STOP and ask the user. Do not infer the intended value from drawing appearance, filename, surrounding jobs, or common shop practice.
   - When a Page 1 job list exists, use it only to map part code/material/thickness or declared ordering; do not let list text replace the dimensions shown on the drawing page.

4. **Merged Multi-Part DXF Mapping Protocol**:
   - A single DXF MAY contain multiple part clusters; separate DXF files per part are not required.
   - When the user explicitly declares a mapping order (for example, **top-to-bottom matching the Page 1 job list**), cluster non-overlapping part geometry and assign codes strictly in that declared order.
   - For top-to-bottom mapping, order by descending global Y position of each part cluster. If two clusters occupy the same row or overlap enough to make the order ambiguous, STOP and ask the user; do not invent a left-to-right tiebreaker unless the user has defined one.
   - Absence of TEXT/MTEXT part codes inside the DXF is acceptable only when the user has supplied an unambiguous external mapping rule.

### 2.2 View Classification & Coordinate System Mapping
- **Classification Types**: Prior to geometry extraction, classify drawing views into: `Front`, `Top`, `Side`, `Auxiliary`, `Section`, `Detail`, `Development/Flat Pattern`, `Assembly`, or `Mirror`.
- **Primary Manufacturing View Selection**: Identify the primary 2D orthographic view containing the main bounding dimensions.
- **View Mapping**: Establish linear projection alignment between Front, Top, and Side views to verify hole alignments and flange positions.
- **Duplicate Feature Elimination**: Features depicted across multiple views (e.g., a hole visible in Front View and enlarged in Detail View) MUST be cross-matched and merged into a single 2D CAD entity on the flat pattern.

### 2.2.1 Mandatory Drawing Read Order
For each part page, inspect in this sequence before writing any geometry:

1. **Contour topology first**: trace every real outside edge, step, recess, tab, opening, cutout, R, and C. Do not start from a bounding rectangle.
2. **Feature inventory**: enumerate each hole/slot/tap/cutout family and its quantity callout before assigning coordinates.
3. **Dimension graph**: classify each used dimension and identify both witness-line endpoints before arithmetic.
4. **Face/bend mapping**: determine which dimensions belong to which formed face and the ordered unfold path.
5. **Handwritten evidence**: apply handwritten correction/Nobi only to the feature or bend it clearly points to. If the target is unclear, ask.
6. **Metadata lock**: confirm barcode, material, and thickness before choosing thread pilots, Nobi table rows, or feasibility rules.
7. **Only then generate CAD coordinates** and run Section 5 validation.

Do not generate provisional production geometry while the contour topology or datum graph is unresolved.

### 2.3 OCR Error Correction & Context Engine
Correct optical character recognition errors using engineering context rules:
- `B` ↔ `8` | `O` ↔ `0` | `S` ↔ `5` | `M6` ↔ `MG` | `Ø` ↔ `O` | `0.5` ↔ `O.5`
- Validate dimensions against material thickness $t$ and standard hole lookup tables.

### 2.4 User-Declared Reference DXF Calibration / Ground-Truth Mode
This mode is activated ONLY when the user explicitly states that a supplied DXF is a correct production CAD / **ground-truth reference** used to audit and calibrate the executing AI's interpretation of the PDF.

#### 2.4.1 Purpose and Scope
- The purpose of the reference DXF is **calibration and verification of PDF-reading skill**, not blind geometry copying.
- The executing AI MUST first interpret the PDF/drawing using Sections 2–7, including datum tracing, dimension-string classification, feature recognition, C/R topology, and tolerance/Nobi rules.
- The executing AI then compares that independently-derived result with the reference DXF and identifies why any mismatch occurred.
- Learn **generalizable interpretation rules** from the comparison (datum origin, chain-vs-baseline distinction, step dimensions, convex/concave C/R mapping, feature-count logic). Do NOT learn or memorize raw coordinates as a substitute for drawing interpretation.
- A reference DXF may be used to confirm that a particular PDF interpretation is correct. It MUST NOT be used as a hidden bounding-box ruler to invent a dimension that cannot be traced on the PDF.

#### 2.4.2 Ground-Truth Comparison Rules
- Compare: feature position, feature size, contour topology, hole/slot locations, chamfer geometry, explicitly specified radii, and part-to-code mapping.
- When a mismatch is found, classify the root cause explicitly as one of: `DATUM ERROR`, `CHAIN/BASELINE ERROR`, `STEP DIMENSION ERROR`, `FEATURE TYPE ERROR`, `FEATURE-COUNT ERROR`, `C/R TOPOLOGY ERROR`, `REFERENCE/FORMED-DIMENSION ERROR`, `UNFOLD TRANSFORM ERROR`, `BEND-SEQUENCE ERROR`, `CONTAINMENT ERROR`, `CODE/SCHEMA SEMANTICS ERROR`, `MISSING/AMBIGUOUS PDF DIMENSION`, or `DXF-ONLY SHOP FEATURE`.
- If the DXF and PDF differ but the mismatch can be explained by a PDF dimension string that was previously misread, correct the PDF interpretation and record the anti-regression rule in the portable skill when validated.
- If the DXF differs from the PDF in a way that **cannot** be supported by the PDF dimensions/callouts, do NOT silently teach that difference as a general rule. Report it as a production-CAD adjustment or source conflict and ask the user when it materially changes the part.
- A newer visible revision note / red correction on the PDF must still be reported if it conflicts with the supplied DXF; ground-truth calibration does not erase revision chronology.

#### 2.4.3 Approved material-table Laser R takes precedence over old DXF-only R0.5 exception

The V4.3 unconditional rule to omit uncalled-out DXF-only R0.5 is superseded. Read the approved material table embedded in Section 7.2 (modular reference: `references/MATERIAL_RULES.md`) and apply automatic Laser R0.5, R2 and R3 to **eligible, uncalled-out** corners according to material/thickness and corner class. Explicit PDF R or C at a corner always overrides its material-table auto R. A shop-added R not prescribed by the PDF or approved table may be omitted only with direct user confirmation or an approved shop specification; otherwise FLAG a source conflict. This rule never authorizes inventing contour topology, flattening a relief into a fillet, or silently adjusting explicitly dimensioned PDF geometry.

#### 2.4.4 Calibration / Portable Learning Discipline
- Every reference-DXF comparison is an **anti-regression calibration case**: record the semantic reason for each corrected mismatch, not merely the corrected coordinate. Validated general rules belong in this portable skill file.
- Future PDF-only jobs, including in unrelated chats or on another AI, must apply those semantic rules from this file without requiring a DXF.
- Do not generalize one-off production edits from a single DXF into universal rules unless the user explicitly confirms they are standard practice.
- Do not rely on conversational memory for this learning. If the lesson must survive across chats/AIs, encode it in this master skill or a required companion regression file.

---

## 3. Feature Recognition & 3D Forming Mapping Rules

### 3.1 Standard Cut Features
- **Round Holes**: A confirmed cut hole is `CIRCLE` unless the Section 3.3 POINT rules apply. Threaded M features use approved pilot diameter (Section 7.1) unless the PDF explicitly overrides it.
- **Slots / Oblong Holes**: Constructed as single closed `LWPOLYLINE`s with two straight segments and two semi-circular bulges (`bulge = 1.0`).
- **Slot Dimension Semantics — mandatory**: Before creating a slot, classify every length value as `OVERALL_LENGTH` (extreme end to extreme end) or `CENTER_DISTANCE / STRAIGHT_TANGENT_LENGTH` (center-to-center distance between the two semicircular ends; numerically equal to the straight tangent segment length for a stadium slot). Do not pass an unclassified value into a slot helper.
- The canonical AutoLISP slot spec in this skill uses **overall length**: `(SLOTX L_TOTAL W)` or `(SLOTY L_TOTAL W)`, where `W` is slot width / end-circle diameter and `L_TOTAL >= W`. If the drawing gives center distance `C`, convert explicitly as `L_TOTAL = C + W` before storing or drawing the slot.
- If witness lines do not prove whether the printed slot length is overall or center-distance/tangent length, apply Section 4.4; do not guess from appearance or from a reference DXF.
- **Polygonal Cutouts**: Extracted as closed `LWPOLYLINE`s using explicit vertex arrays.
- **Countersinks & Counterbores**: Extracted using the smallest pilot/through-hole diameter for laser cutting.

### 3.2 3D Forming Features Mapping (To 2D Flat Pattern)
For 3D forming operations (which cannot be cut directly as flat outlines), map geometry into 2D laser manufacturing layers:

1. **Scribe / Marking Lines (Kegaki - Color 1 / Red)**:
   - Features: **Louver**, **Emboss**, **Dimple Outline**, **Rib**, **Gusset**, **Bridge**, **Half Shear**, **Hem**, **Curl**, **Lance Cut Line**.
   - CAD Representation: DXF Group `(62 . 1)` on Layer `"0"`. Indicates marking/bending reference for press operators.
2. **Piercing and ordinary manufacturing POINTs**: ByLayer on Layer 0 by default; Green (Color 3) ONLY for PDF-scoped `PIERCING + THROUGH HOLE`. A temporary unproved center/type is Magenta + FLAG. Relief slits use their own LINE-color rules.

## 3.3 Approved POINT / CIRCLE decision (first matching rule)

1. If the PDF explicitly applies `PIERCING + THROUGH HOLE` to a feature family: `POINT` on Layer 0, DXF color 3 (Green); Ø/M only in Stage 1 report, not CAD.
2. Else if the PDF applies `PIERCING`: `POINT` on Layer 0, ByLayer (no explicit color 3/6), regardless of the worksheet's `白ピアス 〇/×` or nominal diameter. That worksheet column is machine **capability**, NOT drawing intent; a `×` does not suppress the explicit PIERCING POINT or create a capacity-only FLAG.
3. Else, if the effective cut-hole diameter `d < t/2`: `POINT` ByLayer with **no capacity FLAG**. This holds even without a worksheet row. Strict inequality: `d = t/2` proceeds to the worksheet test.
4. Else look up the applicable material/thickness row in Section 7.2 (modular reference: `references/MATERIAL_RULES.md`) (the approved `Rule_Bo_R&Hole.xlsx` transcription). If `d` is below that row's inherited minimum hole diameter: `POINT` ByLayer, **no capacity FLAG** even without PIERCING. Otherwise draw `CIRCLE` ByLayer at the effective cut diameter.
5. If the worksheet cannot resolve the material/thickness/limit or the output type remains unproved and `d >= t/2`, use a **provisional `CIRCLE` Color 6 (Magenta) plus FLAG**; never assert production readiness. For a proved tapped `M*` callout, obtain provisional `d` from the approved thread pilot table (e.g. M4 Ø3.3, M5 Ø4.2, M6 Ø5.0), except where the PDF explicitly overrides it.

The precedence above is per **feature family**, never per whole sheet. No numeric capacity FLAG is warranted when a higher-priority explicit PIERCING or verified capability rule definitively selects POINT. Independent uncertainty about quantity, center coordinates, PDF legibility, handwritten instructions or customer approval **continues to require FLAG**. If feature identity/topology is unresolved, do not invent a hole or switch type merely to fill an output.

**Color contract:** all geometry Layer `0`; ordinary `POINT` ByLayer (DXF 62 omitted or 256); **only explicit PIERCING + THROUGH HOLE** produces a green **POINT** (62=3). A *provisional* feature is Color 6. Do not add redundant circle geometry or Ø/M labels around a POINT. Retain Ø/M and the conversion reason in the Stage 1 report.

## 3.4 Special J markings vs ordinary hole features

A printed `J` associated with a special POINT operation is **exceptional**, not a general feature inferred from an adjacent POINT or reference DXF. Only create that POINT/J set when the PDF has an applicable note/leader; when the mark is unreadable, flag it. This usage must be disambiguated from any bend/Nobi `J-symbol` described by the bend module; do not transfer a J operation between them. Calibration `055957`: the user confirms the PDF has a special J indication, but exact leader location is deferred; do not manufacture its geometry from the DXF alone.
## Verification and workflow

Trace separately the original callout count, verified effective diameters, POINT-vs-CIRCLE type, datum for every center, and every independent FLAG. Run material-domain containment on CIRCLE features. Preserve the part and keep a distinct shop report for all converted POINTs (source Ø/M, center, method/trigger).

---

## 4. Dimension Authority, Tolerance Rules & Nobi Logic

### 4.1 Dimension Precedence System
When dimension conflicts occur, strictly follow this hierarchy (higher overrides lower):
1. Latest Revision Note / Cloud
2. Red Handwritten Correction on Drawing
3. Explicit Numerical Callout
4. Detail View Callout
5. Section View Callout
6. Projection Alignment
7. Implied DXF Geometry
8. Visual Estimation

### 4.2 Datum Lock & Extension Line Integrity *(expanded V3.1 — anti-error safeguard)*
- To prevent feature displacement errors (such as misassociating extension lines across parallel dimension chains), notch/cutout/hole positions ($X$, $Y$) MUST be calculated strictly from the actual datum edge or datum feature proven by the dimension extension lines.
- **Never** add or subtract adjacent flange widths, hole-edge offsets, neighboring dimension values, or bounding-box offsets unless the drawing shows that they belong to one continuous dimension string.
- Every critical feature coordinate MUST be traceable as an explicit expression from a proven datum, e.g. `Y = 0 + 10 + 35 = 45`. If no valid trace exists, apply Section 4.4 instead of inferring the coordinate.

#### 4.2.1 Dimension-String Classification — MUST classify before arithmetic
Before using any dimension numerically, classify it as one of the following:

1. **Baseline / Common-Datum Dimension**: Multiple dimensions share the same extension-line origin. Values are measured independently from the common datum and MUST NOT be summed merely because they are drawn next to each other.
2. **Continuous Chain Dimension**: The end witness/extension line of one dimension is the proven start witness/extension line of the next. Only this type may be accumulated sequentially.
3. **Step / Local Feature Dimension**: A dimension defines the distance between two local contour levels, notch walls, hole centers, or other local features. It is not cumulative with a neighboring chain unless the extension lines explicitly connect the nodes.
4. **Overall Dimension**: The total width/height is primarily a closure check. It may validate a chain sum but MUST NOT be used to redistribute or invent missing intermediate dimensions.
5. **Ordinate / Coordinate Dimension**: A coordinate is measured directly from its stated zero datum; do not convert it into a chain unless the drawing explicitly defines one.

#### 4.2.2 Datum Graph Rules
- Treat extension-line endpoints as graph nodes and dimensions as graph edges. A coordinate is valid only when there is a connected, explicit path from the selected datum node to the target feature node.
- Parallel dimension strings at different offsets on the drawing are independent until a shared extension-line node is proven. Visual alignment alone is not connectivity.
- **Hole-center chains and contour/step chains must not be mixed** merely because they are nearby. A hole row offset (for example 10 mm from an edge) cannot become the origin for a separate 153 mm or 54 mm contour/feature dimension unless the extension lines prove the same origin.
- If two dimensions visually touch but their witness lines terminate on different geometry, classify them separately.
- Use the overall size only as a closure test: if `sum(chain segments) != overall`, mark the chain `FLAGGED` and re-read the extension lines; do not force-fit the numbers.

#### 4.2.3 Required Datum Trace Record
For every hole row, notch, step, or repeated feature pattern, retain a trace record containing: `axis`, `datum entity`, `dimension type`, `equation`, and `result`. This trace must be auditable in Stage 1 for any feature that was previously ambiguous or that disagrees with a reference DXF.

#### 4.2.4 Dimension Endpoint Identity — MUST NOT Borrow a Neighboring Endpoint
Every dimension endpoint/witness line must be tagged by the **actual geometry it terminates on** before arithmetic. At minimum distinguish: `OUTER_EDGE`, `CONTOUR_EDGE/STEP`, `HOLE_CENTER`, `CENTERLINE`, `THEORETICAL_SHARP_CORNER`, and `REFERENCE_DATUM`.

- Two parallel dimensions drawn beside each other may terminate on different targets even when they share the same axis or appear visually aligned. Never reuse the endpoint of a neighboring dimension without proving the witness line lands on the same node.
- A hole-center dimension and a contour-edge dimension are different graph edges even if their values are printed in the same local area.
- Example pattern: if one horizontal dimension is from a step to the **outer edge** and an adjacent dimension is between two **hole centers**, do not subtract both from the same right-side X coordinate.
- Example pattern: if vertical dimensions `389` and `404` terminate respectively at a hole center and a step ledge, they define two different Y nodes; they are not interchangeable.
- Record the endpoint identity in the datum trace whenever a crowded drawing contains multiple nearby extension lines.

#### 4.2.5 Contour Topology First — Dimensions Assign Coordinates, They Do Not Invent the Shape
Before solving numerical coordinates, trace the visible manufacturing boundary as an ordered topology: outer corners, protrusions, recesses, steps, notches, vertical/horizontal segments, chamfers, and radii.

- An overall width/height gives the bounding extent only. It does **not** imply that the part is a full rectangle over that entire extent.
- First establish which contour segments actually exist and how they connect; only then assign coordinates from dimensions.
- A local step can make the maximum width exist only over part of the height. Do not extend that maximum-width edge through a region where the drawing visibly steps inward.
- If the visible outline and the assumed rectangular base disagree, the visible outline wins subject to explicit dimensions/callouts.
- For complex stepped profiles, create an ordered contour trace such as `edge -> C -> vertical -> R -> ledge -> vertical ...` before converting it to LWPOLYLINE vertices/bulges.

#### 4.2.6 Reference Dimensions Still Require a Proven Datum
A parenthesized/reference dimension is **not automatically a coordinate from the global origin**. `Reference` means no mid-tolerance adjustment; its extension-line origin and target still control how the coordinate is calculated.

- If a reference value `(276.5)` is measured from a hole-center row at `Y=10`, then the target is `Y=10+276.5=286.5`, not `Y=276.5`.
- Apply Section 4.2 datum tracing exactly as for a normal dimension; only the tolerance treatment differs.
- **Formed-view reference dimensions are not flat-pattern dimensions by default.** A parenthesized/参考 overall shown on a bent Front/Side/Section view describes that formed view unless its witness lines explicitly belong to a Development/Flat Pattern view.
- Do NOT use a formed-view reference overall as the unfolded blank length merely because its numeric value is close to the expected flat length. Derive flat length from the proven ordered flange/body chain, ID→OD conversion where required, and Nobi deductions. Use the formed-view reference only for the geometry/view it actually dimensions.
- If a formed-view reference value conflicts with a fully proven unfold equation, classify the issue as `REFERENCE/FORMED-DIMENSION ERROR` or source conflict; do not force the flat equation to equal the reference value.

#### 4.2.7 Local-Face Datum → Global Flat Datum Mapping
Features dimensioned on a bent flange/face MUST be transformed from the **local face coordinate system** into the **global unfolded blank coordinate system** before AutoLISP coordinates are emitted.

1. Assign each formed face an ordered identity along the unfold path: `FACE_1 -> BEND_1 -> FACE_2 -> ...`.
2. Establish the flat start/end coordinates of that face from the sequential OD/Nobi equations in Section 4.7.
3. Preserve the dimension direction. If local coordinate `u` is measured from the face start datum, use `U_flat = FACE_START_flat + u`. If it is measured from the opposite/free edge, use `U_flat = FACE_END_flat - u`.
4. A feature coordinate printed on a formed face MUST NOT be copied directly as a global flat coordinate unless the face datum is proven to coincide with the global flat datum.
5. Record `face_id`, `local datum`, `local equation`, and `global flat equation` in the datum trace for holes/slots/notches that cross a bend mapping.

This rule applies independently on both axes. Projection alignment may identify which face a feature belongs to, but may not replace the required unfold transform.

#### 4.2.8 Bend Sequence / Face Order Is Non-Commutative
The total flat length equation may be numerically unchanged when two flange lengths are swapped, but **bend positions, feature transforms, and material topology are not**. Therefore:

- Determine the ordered face sequence from the visible formed topology, bend callouts, section/detail views, and proven witness-line connectivity before calculating bend-line coordinates.
- Do not validate bend order merely because `sum(OD) - sum(Nobi)` matches the overall blank length.
- Double bend lines MUST be positioned from the ordered sequence in Section 4.7 and MUST exist only over material regions that actually cross that bend. For U-shaped, legged, stepped, or cut-away parts, split/trim bend lines around voids; never draw a bend line continuously through empty space.
- If two face orders remain equally plausible after explicit trace exhaustion, STOP and ask the user. Magenta is not permission to choose an arbitrary bend order.

### 4.3 Mid-Tolerance Strategy (Tolerance Calculation)
For coordinates governed by asymmetric tolerances or limit dimensions, calculate the flat pattern feature position using the **Mid-Tolerance Value**:

$$X_{\text{mid}} = X_{\text{nominal}} + \frac{\text{Tolerance}_{\text{upper}} + \text{Tolerance}_{\text{lower}}}{2}$$

- **Example**: A dimension specified as $50.0^{+0.2}_{+0.1}\text{ mm}$ is computed as:
  $$X_{\text{mid}} = 50.0 + \frac{0.2 + 0.1}{2} = 50.15\text{ mm}$$
- **Symmetric Tolerances** ($\pm 0.1\text{ mm}$): Mid-tolerance equals nominal value.
- **Reference Dimensions** (参考 / marked as reference, no tolerance band): Do NOT apply mid-tolerance adjustment — use nominal value as-is (see Section 6, term "Reference").

### 4.4 Ambiguous, Unclear, or Missing Dimension Handling
- **Flag only after explicit-trace exhaustion**: A crowded/overlapping print is not automatically ambiguous. Before flagging, zoom/re-read the witness lines and test all explicit dimension paths, endpoint identities, feature diameters, feature counts, projection relationships, and overall closure. If the PDF contains a unique trace, use it; do not use Magenta as an escape from difficult dimension parsing.
- **Magenta is not permission to invent topology**: Use estimated/Magenta geometry only when the entity identity and contour/feature topology are already certain but a numeric dimension remains unreadable/ambiguous. If multiple topologies, feature types, or bend orders are possible, STOP and ask the user rather than fabricating a bounding rectangle, generic slot, or arbitrary flange order.
- **Integer Value Enforcement applies only to estimated/assumed values**: Any truly estimated dimension MUST be rounded to the nearest integer (e.g., `256` or `258`, never `256.4`). Explicit dimensions and deterministic formula results (for example `182.70`, `159.26`, or a Nobi-derived bend coordinate) MUST retain their calculated precision and MUST NOT be rounded to an integer merely because another part of the same feature/part is flagged.
- **Known/unknown separation**: Flagging an unresolved feature does not authorize changing dimensions that are already proven. Keep all proven edges, lengths, hole sizes, and coordinates exact; isolate only the unresolved quantity/entity.
- **No bounding-box substitution**: A known overall width/height may be reported as a bounding extent, but MUST NOT be emitted as a closed rectangular outline unless the contour trace proves that all four rectangle edges actually exist.
- **Color Code 6 (Magenta)**: Assign DXF Group `(62 . 6)` to any line, circle, or polyline whose size/position was estimated or ambiguous.
- **Adjacent Text Annotation**: Add a `TEXT` entity on DXF Group `(62 . 6)` immediately adjacent to the ambiguous feature (e.g., `"(ESTIMATED GEOMETRY - CHECK DRAWING)"` or `"(M6 OR M8)"`).

### 4.5 Corner Filleting & Chamfer Baking

- **No global FILLET command** or global outline fillet pass: trace real topology before arithmetic.
- Classify each target by **material interior angle**: convex/outside `<180°`; concave/re-entrant `>180°`. The term `outside corner ≤90°` in the workbook describes a convex exterior corner of the stated angle; do not apply the rule to similarly drawn inner corners.
- **Order of authority per CORNER**: drawing-specific revision/red correction → explicit PDF R/C callout (with applicable quantity) → approved workbook automatic Laser R (if the PDF has NO R/C instruction for that corner). A PDF C remains a straight chamfer and must never silently become R2/R0.5. Where a PDF R/C overrides a material table at one corner, still use automatic Laser R at other eligible uncalled-out corners.
- Workbook automatic laser radii: SS up to t5 as tabulated R0.5 for exterior ≤90°; SS t6–9 R2; SUS/other or AL rows with R0.5 for exterior ≤90°; Cu/Brass t≤5 R0.5 exterior ≤90°; SS t≥19 R3 at stated inside/outside corner class including the sheet's chamfer-language **only when there is no conflicting PDF-specific R/C**. Honor exact row/range lookup, and `無` means no automatic radius. A blank R is UNKNOWN, not automatically R0. Ignore unexplained `※3` annotation but do use the workbook's R3.
- **Two R2 of part `055955` are required in generated geometry** under the SS t9 material-table rule; this explicitly reverses the earlier hypothesis to omit them as downstream shop additions. Never treat the old DXF-only R0.5 omission as a reason to omit a radius required by the current approved table.
- **DXF-only shop radius beyond the table:** a PDF-unmarked radius that does **not** follow an approved material rule may be omitted as a separate later shop operation only with direct user approval or an approved shop specification. Otherwise source conflict/FLAG. Do not infer an arbitrary R from thickness.
- **Callout topology and count:** a leader is evidence of target corner class, not global scope; identify the candidate equivalent corners by their material topology and count (`6-C5`, `2-C10`, `4-R5` etc). Distinct R and C families MUST match their own n-calls.
- **Geometry:** bake an explicit R into polyline tangent points/bulges (for a CCW 90° arc, `bulge=tan(90°/4)=0.41421356` with sign from actual sweep). A straight C replaces the corner with two tangent-offset vertices and bulge 0. A sharp interior U-notch stays sharp unless the PDF explicitly requires an interior R or an approved material rule for that particular class applies.
- **Relief is not Laser R:** an `R=t` relief at two oppositely folding edges whose outside extents must remain unchanged is a manufacturing clearance with distinct topology. Do not spread Laser R to reliefs and do not infer three special reliefs of `055958` (method pending).

### Material-table validation
Record source material, thickness, chosen worksheet row, eligible corner class, R/C overrides, and each generated automatic radius; compare PDF and ground-truth DXF *after* this classification. A DXF R0.5 that matches the approved material table is expected and must not be excluded from regression comparisons.

### 4.6 ID-to-OD Conversion for Non-90° Bends
When dimensions are given as Inside Dimensions (ID), convert to Outside Dimensions (OD):

$$\text{Offset}_{raw} = t \times \tan\left(\frac{180^\circ - \text{Angle}}{2}\right)$$

**Mandatory rounding order:** round `Offset_raw` to the nearest `0.01 mm` **before** adding it to the ID or using it in any subsequent Nobi/flat-pattern arithmetic. Use ordinary decimal rounding at the hundredth place: inspect the thousandth digit; `0–4` rounds down and `5–9` rounds up.

$$\text{Offset} = \operatorname{Round}_{0.01}(\text{Offset}_{raw})$$

$$\text{OD} = \text{ID} + \text{Offset}$$

- Confirmed calibration example: for a `165°` bend with `t = 3.0 mm`, `Offset_raw = 3.0 × tan(7.5°) ≈ 0.39495...`, therefore **Offset = 0.39 mm**. Use `0.39`, not the unrounded value, in every following equation.
- Example (`135°` bend, `t = 3.0 mm`): `Offset_raw = 3.0 × tan(22.5°) ≈ 1.2426`, so `Offset = 1.24 mm`, then `OD = ID + 1.24 mm`.
- Do not apply this special intermediate rounding rule to unrelated explicit dimensions. It is specifically the ID→OD offset normalization step.

### 4.7 Nobi (Bend Allowance) Lookup Priority & Sequential Formulas
1. **Handwritten Nobi on Drawing**: Highest priority. Use directly (e.g., `-4.8`, `135° -1.71`) regardless of J-symbol.
2. **No Handwritten Nobi + J-Symbol Present**: Look up Nobi from standard tables (Section 7.3) by Material, Thickness, Bend Length, and Angle — applying the Interpolation Rule in Section 4.8 when the exact value is not tabulated.
3. **No Handwritten Nobi + J-Symbol Absent**: Draw the affected flange as a separate piece detached from the main body, offset by a fixed $10\text{ mm}$ gap for downstream reassembly. Set `is_flagged = true`.
4. **J-Symbol Present + No Table Match** (including out-of-range per Section 4.8): Maintain flat blank at Outside Dimension (OD) and draw bend line at OD design position. Set `is_flagged = true`.

#### Multi-Flange Sequential Coordinate Formulas (Axis from Origin 0)
For sequential flanges ($OD_1, OD_2, \dots, OD_n$) with Nobi values ($N_1, N_2, \dots, N_{n-1}$), first preserve the proven face order from Section 4.2.8. Any non-90° ID→OD offsets used inside the $OD_i$ values MUST already be rounded to `0.01 mm` per Section 4.6 before these equations are evaluated:
- **Total Unfolded Length**:
  $$L_{\text{total}} = \sum_{i=1}^{n} OD_i - \sum_{i=1}^{n-1} N_i$$
- **Exact Coordinates for Double Lines of Bend $k$**:
  - **Lower Line (Line 1 / Outer)**:
    $$Y_{\text{line1}} = \left(\sum_{i=1}^{k} OD_i\right) - \left(\sum_{i=1}^{k} N_i\right)$$
  - **Upper Line (Line 2 / Inner Datum)**:
    $$Y_{\text{line2}} = \left(\sum_{i=1}^{k} OD_i\right) - \left(\sum_{i=1}^{k-1} N_i\right)$$
  - **Distance between double lines**: $N_k$
- **Body Interior Preservation**: Main body interior dimensions ($B$) are **NEVER** reduced by Nobi. Nobi deductions exist strictly within the bend zone between parallel bend lines.

### 4.8 Nobi Table Interpolation Rule (NEW — Conservative Round-Up, Shop-Practice Standard)
When the actual Thickness ($t$) or Bend Length ($L$) does **not** exactly match a row in Section 7.3, **do NOT interpolate numerically**. Instead:
- **Thickness mismatch**: Select the row with the **next higher tabulated $t$** (never round down). Rounding down risks selecting an undersized V-die opening for the actual material, risking cracking or improper die seating.
- **Bend Length mismatch**: Within the selected $t$ row group, select the **next higher $L$ bracket** (next larger V-die). This yields a conservative (larger) Nobi deduction, which errs toward tooling safety.
- **Out-of-Range**: If $t$ or $L$ exceeds the largest tabulated value for that material, do **not** guess. Set `is_flagged = true` and annotate `"OUT OF TABLE RANGE - CONFIRM NOBI WITH SHOP"` in Magenta (Color 6) per Section 4.4.
- This rule applies uniformly across all four material tables in Section 7.3.

### 4.9 Stepped / Notched Flanges *(restored from V1)*
For flanges stepping inward before joining the body:
- $Y_{\text{flange\_flat}} = L_{\text{flange\_nominal}} - N_y$
- $Y_{\text{bend}} = Y_{\text{flange\_flat}}$
- $Y_{\text{notch}} = Y_{\text{flange\_flat}} + L_{\text{notch\_gap}}$
- $Y_{\text{body\_flat}} = L_{\text{body\_nominal}}$ (untouched)

### 4.10 Corner Reliefs — two distinct mechanisms (V4.4)

**Standard crossing-bend slit relief** (original V4.3 rule, only when two perpendicular bend lines cross):
- Retract longer edge by `t`; slit inward by `t + 0.2`; diagonal slit to bend-line intersection; read any drawing-specific offset or FLAG if unknown.

**Opposite-fold fixed-outside R=t relief** (approved calibration `055962`):
- When **two outer edges fold in different directions** and both outside dimensions must remain unchanged, create an `R=t` escape relief at their intersection without shortening either outside dimension. This is a distinct topology/operation from the standard slit relief and from material-table automatic laser fillets. Determine its exact tangency and retained-material side from the real bend/edge topology; if those are unclear, do not invent them.
- In `055962`, `t=2 mm` gives the two confirmed R2 reliefs. A separately observed R2 on an unbent corner is NOT automatically this relief.
- Three green shop relief objects in `055958` are **not yet defined by an approved construction method**; keep them FLAGGED and do not generalize from reference DXF coordinates.

---

## 5. Error Detection & Manufacturing Validation Engine

Before emitting AutoLISP code, run the following automated checks:

### 5.1 Geometry & Dimension-Semantic Integrity Engine
- **Closed Polyline Check**: Outer boundary vertices must form a continuous loop that explicitly closes at $P_{\text{start}} = P_{\text{end}}$.
- **Self-Intersection Check**: Ensure no overlapping edges or intersecting outer polyline loops exist.
- **Vertex Ordering**: Outer boundaries must follow Counter-Clockwise (CCW) orientation; internal cutouts must follow Clockwise (CW) orientation.
- **Datum Graph Connectivity Check**: Every critical hole/notch/step coordinate must have a connected dimension path from an identified datum per Section 4.2.
- **Dimension-Type Check**: Each used dimension must be classified as baseline, chain, step/local, overall, or ordinate before arithmetic.
- **Dimension Endpoint Identity Check**: For every crowded or parallel dimension group, verify that each dimension's start/end node targets the correct entity type (`OUTER_EDGE`, `CONTOUR_EDGE/STEP`, `HOLE_CENTER`, etc.). Reusing a neighboring endpoint is a semantic FAIL.
- **Contour Topology Check**: Verify that the ordered visible boundary (including steps/recesses/protrusions) is reproduced before numerical closure. A geometrically closed but topologically wrong rectangle/step is FAIL.
- **Reference-Datum Check**: Parenthesized/reference dimensions must retain their actual extension-line datum; using the nominal value directly as a global coordinate without datum proof is FAIL.
- **Chain Closure Check**: Where an overall width/height is present, verify that the proven chain closes to the overall dimension. A closure failure is a semantic FAIL even if the CAD polyline itself is perfectly closed.
- **Reference DXF Comparison Check**: When Section 2.4 is active, compare feature coordinates and topology against the master DXF after PDF interpretation. Apply the approved material-table auto Laser R first; a matching DXF R0.5/R2 must not be excluded solely because PDF omitted R/C. Omit only explicitly confirmed downstream shop-only differences.
- **Feature Count Closure Check**: For every explicit quantity callout (`n-Ø`, `n-M*`, `n-slot`, `n-R`, `n-C`, repeated notch family, etc.), the generated family count MUST equal `n`. Thread-to-pilot conversion changes diameter representation, not the required count. Missing or extra members are FAIL, not WARN.
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
  - every `FAIL`, `FLAGGED`, `WARN`, ambiguity, or user-confirmation item.
- A concise report MUST NOT hide an unresolved production risk. Brevity controls presentation, not engineering rigor.
- Do not narrate exploratory reasoning, discarded hypotheses, or general sheet-metal theory unless the user asks for an audit/explanation.

### 5.2 Manufacturing Feasibility Rules

| Feasibility Parameter | Constraint Rule | Violation Action |
| :--- | :--- | :--- |
| **Minimum Cut Hole Diameter** | Use the applicable, inherited minimum from `references/MATERIAL_RULES.md` after approved thickness selection; the unconditional `Ø<t/2` POINT rule is checked before the table | Verified below-capacity hole becomes POINT ByLayer **without a capacity FLAG**; unresolved table/material becomes provisional CIRCLE Magenta + FLAG |
| **Minimum Bridge / Web Width** | Distance between hole edge & part boundary $\ge t$ | Flag low confidence warning |
| **Laser Piercing Accessibility** | Distance between adjacent piercings $\ge 10\text{ mm}$ | Group piercing locations |
| **Bend Line Collision** | Distance between hole edge & bend line $\ge 2 \times t + R_{\text{bend}}$ | Flag potential hole deformation |

---

## 6. Japanese Manufacturing Knowledge Base

| Japanese Term | Kanji / Kana | Manufacturing Meaning | CAD Layer / Action |
| :--- | :--- | :--- | :--- |
| **Kegaki** | ケガキ / 罫書 | Marking / Scribe Line | Layer 0, Color 1 (Red) |
| **Burring** | バーリング | Extruded / Tapped Flange Hole | Draw Pilot Hole, Color 3 Center Point |
| **Burring Pilot** | バーリング下穴 | Pre-hole for Burring Operation | Draw exact pilot diameter |
| **Countersink** | 皿 / 皿揉み | Countersunk Hole | Draw inner through-hole diameter |
| **Counterbore** | ザグリ | Counterbored Hole | Draw inner through-hole diameter |
| **Half Shear** | ハーフシャー / 半切 | Positioning Pin / Half Cut | Draw center Piasu point (Green) |
| **Bending** | 曲げ / L曲げ / Z曲げ | Press Brake Bending Operation | Double DASHED lines on Layer 0 |
| **Unfolded** | 展開 / 展開図 | Flat Pattern Drawing | Extract as primary flat geometry |
| **Unmachinable** | 加工不可 | Feature impossible to laser cut | Flag error in report |
| **Reference** | 参考 / 参考寸法 | Reference Dimension (No Tol) | Do not apply tolerance adjustments |
| **Tap** | タップ / ネジ | Threaded Tapped Hole | Convert to pilot hole diameter |
| **Chamfer** | 面取り | Corner Chamfer (C) | Bake into polyline vertices |
| **Radius** | R加工 / R | Corner Fillet Radius (R) | Bake into polyline bulges |
| **Slot** | 長穴 | Elongated / Stadium Slot | Closed LWPOLYLINE with bulges |
| **Nobi** | ノビ / 伸び | Bend Allowance Deduction | Subtract from bend zone |
| **Piercing** | ピアス / ピアシング | Laser Piercing Point | Layer 0, Color 3 (Green) |
| **Bend Datum** | 曲げ基準 | Reference Edge for Bending | Align datum bend line |

---

## 7. Manufacturing Reference Standards

### 7.1 Metric Thread Pilot Hole Diameters *(full table restored from V1)*
For laser cutting, threaded holes (marked `M*`) MUST be output as pilot holes using the standard diameters below:

| Thread | Pitch | Pilot Hole $\varnothing$ (mm) | Pilot Radius (mm) |
| :--- | :--- | :--- | :--- |
| **M1** | 0.25 | 0.75 | 0.375 |
| **M1.1** | 0.25 | 0.85 | 0.425 |
| **M1.2** | 0.25 | 0.95 | 0.475 |
| **M1.4** | 0.30 | 1.10 | 0.550 |
| **M1.6** | 0.35 | 1.25 | 0.625 |
| **M1.7** | 0.35 | 1.35 | 0.675 |
| **M1.8** | 0.35 | 1.45 | 0.725 |
| **M2** | 0.40 | 1.60 | 0.800 |
| **M2.2** | 0.45 | 1.75 | 0.875 |
| **M2.3** | 0.40 | 1.90 | 0.950 |
| **M2.5** | 0.45 | 2.10 | 1.050 |
| **M2.6** | 0.45 | 2.20 | 1.100 |
| **M3** | 0.50 | 2.50 | 1.250 |
| **M3.5** | 0.60 | 2.90 | 1.450 |
| **M4** | 0.70 | 3.30 | 1.650 |
| **M4.5** | 0.75 | 3.80 | 1.900 |
| **M5** | 0.80 | 4.20 | 2.100 |
| **M6** | 1.00 | 5.00 | 2.500 |
| **M7** | 1.00 | 6.00 | 3.000 |
| **M8** | 1.25 | 6.80 | 3.400 |
| **M9** | 1.20 | 7.80 | 3.900 |
| **M10** | 1.50 | 8.50 | 4.250 |
| **M11** | 1.50 | 9.50 | 4.750 |
| **M12** | 1.75 | 10.30 | 5.150 |
| **M14** | 2.00 | 12.00 | 6.000 |
| **M16** | 2.00 | 14.00 | 7.000 |
| **M18** | 2.50 | 15.50 | 7.750 |
| **M20** | 2.50 | 17.50 | 8.750 |
| **M22** | 2.50 | 19.50 | 9.750 |
| **M24** | 3.00 | 21.00 | 10.500 |
| **M27** | 3.00 | 24.00 | 12.000 |
| **M30** | 3.50 | 26.50 | 13.250 |
| **M33** | 3.50 | 29.50 | 14.750 |
| **M36** | 4.00 | 32.00 | 16.000 |
| **M39** | 4.00 | 35.00 | 17.500 |
| **M42** | 4.50 | 37.50 | 18.750 |
| **M45** | 4.50 | 40.50 | 20.250 |
| **M48** | 5.00 | 43.00 | 21.500 |

### 7.2 Approved workbook: material laser R, hole capacity, White Piercing

**Approved from user-supplied** `Rule_Bo_R&Hole.xlsx`, worksheet `Bo_R_Hole`, dated `2026.07.30`; calibration `520924-19`, approved 2026-09-25. This complete transcription is portable: do not require the original spreadsheet or past chat.

#### Original worksheet entries (a dash means the CELL IS BLANK, not zero)

| Excel row | Material group | t Min | t Max | Laser corner condition | Laser R | Minimum cut-hole diameter | 白ピアス capacity |
|---:|---|---:|---:|---|---|---|:---:|
| 4 | SS | — | 3.2 | outside corner ≤90° | R0.5 | ≥ t/2 | × |
| 5 | SS | 4 | 5 | outside corner ≤90° | R0.5 | — | 〇 |
| 6 | SS | 6 | 9 | outside corner ≤90° | R2 | — | 〇 |
| 7 | SS | 10 | 12 | — | none (無) | — | 〇 |
| 8 | SS | 16 | 16 | — | none (無) | ≥ t | 〇 |
| 9 | SS | 19 | — | inside/outside corners, including chamfer (内外角/面取含) | R3 (※3 ignored) | — | 〇 |
| 10 | SUS, 他 | — | 5 | outside corner ≤90° | R0.5 | ≥ t/2 | × |
| 11 | SUS, 他 | 6 | 6 | outside corner ≤90° | R0.5 | — | 〇 |
| 12 | SUS, 他 | 7 | 8 | — | none (無) | — | 〇 |
| 13 | SUS, 他 | 9 | 12 | — | none (無) | — | 〇 |
| 14 | SUS, 他 | 14 | 14 | — | none (無) | — | 〇 |
| 15 | SUS, 他 | 15 | 16 | — | none (無) | ≥ Ø10 | 〇 |
| 16 | SUS, 他 | 19 | 19 | — | none (無) | — | 〇 |
| 17 | SUS, 他 | 20 | — | — | none (無) | ≥ t | 〇 |
| 18 | AL | — | 0.5 | outside corner ≤90° | R0.5 | ≥ 0.8t | × |
| 19 | AL | — | 6 | outside corner ≤90° | R0.5 | — | 〇 |
| 20 | AL | 7 | 8 | — | none (無) | — | 〇 |
| 21 | AL | 9 | — | — | none (無) | — | 〇 |
| 22 | AL | 12 | — | — | none (無) | — | 〇 |
| 23 | AL | 16 | — | — | none (無) | ≥ t | 〇 |
| 24 | AL | 19 | — | — | none (無) | — | 〇 |
| 25 | Cu / Brass (銅・真ちゅう) | — | 5 | outside corner ≤90° | R0.5 | ≥ t/2 | × |
| 26 | Cu / Brass; ※ケガキ不可 | 6 | — | outside corner ≤90° | — [UNSPECIFIED] | ≥ t | × |

The `※ケガキ不可` remark on the Cu/Brass last row means scribing/marking unavailable there; it does not specify a laser radius. The worksheet says `※3` at SS t≥19 but has no supplied explanatory text; **ignore only the annotation, retain R3** per approval. `無` explicitly means **no automatic laser fillet**. A blank R cell is **unknown**, not `無`.

#### Approved lookup algorithm

1. Lock the explicit drawing material group and real thickness `t`. Never silently equate `SUS430` and the SS group without an approved material mapping; ambiguous alloys require a question/FLAG.
2. Find a row containing `t` in its stated Min–Max range. A first row with blank Min covers positive t up to its Max; for AL the next blank-Min row ending at 6 covers t>0.5 through 6 (the preceding row handles t≤0.5). If several rows with open Min are candidates, choose the most specific applicable row.
3. If t falls between two explicit ranges, use the **next higher thickness row** (no interpolation). For a nonfinal row that has Min but blank Max, treat only its specified Min as explicit; for intermediate t choose the next higher row. A **last** row with a Min and no Max covers that Min and all greater thicknesses. Outside the material's defined ranges, or with no unambiguous row, ASK; do not invent a range.
4. For a BLANK **hole-capacity** cell, inherit the last nonblank hole-capacity value above it **within the same material group only**. Do not inherit Laser R or White Piercing cells; their values are row-specific.
5. Determine laser R only at corners belonging to the row's corner class. A PDF-specific R or C at that corner overrides the Excel R. Where Excel specifies R0.5/R2/R3 and PDF has no explicit R/C, bake it automatically into the actual contour; keep convex vs concave classification and do not blindly round internal notches. `R=t` bend-intersection relief is a separate feature class and must never be mistaken for material-table laser R.
6. Calculate the **effective cut diameter** from an explicit drawing Ø when present, otherwise the pilot diameter from approved thread table 7.1 for a proved tapped M feature. PIERCING arrow/note scoped to that feature family => `POINT` ByLayer regardless of capacity. PIERCING plus THROUGH HOLE => `POINT` Color 3. Ø < t/2 => `POINT` ByLayer without a capacity FLAG. Else when effective Ø is below Excel minimum => `POINT` ByLayer without a capacity FLAG; otherwise `CIRCLE` ByLayer. An ambiguous feature identity => temporary `CIRCLE` Color 6 + FLAG; geometry/position uncertainty produces a separate independent FLAG.
7. White Piercing `〇` and `×` are **machine-capability indicators**, never instructions to turn every hole into POINT; follow the explicit PDF PIERCING for the specified feature group even if worksheet is `×`, without a capacity-only FLAG. User-approved PROCESS POINT Color 3 is restricted to explicit `PIERCING + THROUGH HOLE`; other POINTs default ByLayer on Layer 0.
8. Document the selected Excel row and any upward-thickness selection for ambiguous/nonstandard thickness; preserve unrelated dimensional/customer-approval FLAGs.

#### Regression examples (user-approved)

- SS t9: hole threshold t/2 = 4.5. M4 pilot Ø3.3 and M5 pilot Ø4.2 => POINT ByLayer with no capacity FLAG. M6 pilot Ø5.0 => CIRCLE if no PIERCING, assuming verified M6 and coordinates.
- SS t9 outside corner ≤90° with no explicit PDF R/C => R2 added (e.g. `055955`). SS t≤3.2 outside ≤90° => R0.5 added.
- SUS t15–16 => minimum cut hole Ø10, independent of the unconditional POINT rule for Ø < t/2.
- AL t5 => minimum cut hole 0.8t = Ø4. Ø3 with no PIERCING => POINT ByLayer with no capacity FLAG, although Ø3 is not < t/2.
- SS t19+ => laser R3 with inside/outside-corner scope as printed; ignore unexplained `※3` notation, not the R3 value.

#### Scope separation

This sheet governs **hole capability and automatic material-based laser corner R only**. Nobi/bend allowance still comes from approved Nobi tables and handwritten corrections. Special J marks and shop-specific relief geometry require their own explicit drawing evidence; the three reliefs of `055958` remain unresolved and MUST NOT be inferred from this workbook.

### 7.3 Nobi Allowance Standards Tables *(fully restored from V1 — including the previously-dropped Copper table and all intermediate L-brackets)*

#### 1. SS, SUS430, BRASS ($R=0.6$ for $t \le 4.5$, $R=3.0$ for $t=5.0 \sim 9.0$, $R=6.0$ for $t=12.0$)

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi Deduction (mm) |
| :--- | :--- | :--- | :--- |
| **0.5** | ~ 2400 | V8 | 1.36 |
| **0.8** | ~ 2400 | V8 | 1.68 |
| **1.0** | ~ 2400 | V8 | 1.90 |
| **1.2** | ~ 2400 | V8 | 2.14 |
| **1.5** | ~ 2400 | V8 | 2.54 |
| **1.6** | ~ 2400 | V8 | 2.64 |
| **2.0** | ~ 2400 | V12 | 3.44 |
| **2.3** | ~ 2400 | V12 | 3.80 |
| **3.0** | ~ 1000 | V12 | 4.66 |
| **3.0** | 1001 ~ 1900 | V18 | 5.28 |
| **3.0** | 1901 ~ 2400 | V25 | 5.98 |
| **3.2** | ~ 1800 | V18 | 5.50 |
| **3.2** | 1801 ~ 2400 | V25 | 5.72 |
| **4.0** | ~ 1200 | V18 | 6.42 |
| **4.5** | ~ 1200 | V25 | 7.76 |
| **4.5** | 1201 ~ 1600 | V32 | 8.10 |
| **4.5** | 1601 ~ 2300 | V40 | 8.48 |
| **5.0** | ~ 1000 | V25 | 8.32 |
| **5.0** | 1001 ~ 1300 | V32 | 9.04 |
| **5.0** | 1301 ~ 1600 | V40 | 9.86 |
| **6.0** | ~ 700 | V25 | 9.78 |
| **6.0** | 701 ~ 900 | V32 | 10.22 |
| **6.0** | 901 ~ 1150 | V40 | 10.94 |
| **9.0** | ~ 400 | V40 | 14.62 |
| **9.0** | 401 ~ 800 | V80 | 15.50 |
| **12.0**| ~ 550 | V80 | 20.48 |

#### 2. Stainless Steel (SUS Except SUS430) ($R=0.6$ for $t \le 5.0$, $R=3.0$ for $t=6.0 \sim 8.0$)

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi 2B (mm) | Nobi #1 (mm) |
| :--- | :--- | :--- | :--- | :--- |
| **0.5** | ~ 2400 | V8 | 1.36 | - |
| **0.8** | ~ 2400 | V8 | 1.82 | 1.74 |
| **1.0** | ~ 2400 | V8 | 2.14 | 1.94 |
| **1.2** | ~ 2400 | V8 | 2.32 | 2.18 |
| **1.5** | ~ 2400 | V8 | 2.64 | 2.54 |
| **2.0** | ~ 1300 | V12 | 3.68 | 3.50 |
| **2.0** | 1301 ~ 2400 | V18 | 4.00 | 4.18 |
| **2.5** | ~ 1300 | V12 | 4.24 | 4.08 |
| **2.5** | 1301 ~ 2000 | V18 | 5.06 | 4.78 |
| **2.5** | 2001 ~ 2400 | V25 | 5.84 | 5.52 |
| **3.0** | ~ 750 | V12 | 4.80 | 4.68 |
| **3.0** | 751 ~ 1250 | V18 | 5.64 | 5.36 |
| **3.0** | 1251 ~ 1800 | V25 | 6.46 | 6.10 |
| **3.0** | 1801 ~ 2400 | V40 | 8.54 | 7.80 |
| **4.0** | ~ 650 | V18 | 6.78 | 6.50 |
| **4.0** | 651 ~ 1000 | V25 | 7.66 | 7.28 |
| **4.0** | 1001 ~ 1650 | V40 | 8.44 | 8.90 |
| **4.5** | ~ 550 | V18 | 7.30 | 7.30 |
| **5.0** | ~ 550 | V25 | 8.82 | 8.46 |
| **5.0** | ~ 750 | V32 | 9.68 | 9.18 |
| **5.0** | 751 ~ 1000 | V40 | 10.74 | 10.06 |
| **6.0** | ~ 500 | V32 | 10.72 | 9.82 |
| **6.0** | 501 ~ 650 | V40 | 11.88 | 10.12 |
| **8.0** | ~ 350 | V40 | 14.06 | 13.50 |
| **8.0** | 351 ~ 700 | V80 | 19.46 | 16.94 |
| **9.0** | ~ 550 | V80 | 20.54 | 18.08 |

#### 3. Aluminum (AL) ($R=0.6$ for $t \le 4.0$, $R=3.0$ for $t \ge 5.0$)

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi Deduction (mm) |
| :--- | :--- | :--- | :--- |
| **0.8** | ~ 2400 | V8 | 1.84 |
| **1.0** | ~ 2400 | V8 | 1.90 |
| **1.5** | ~ 2400 | V8 | 2.40 |
| **2.0** | ~ 2400 | V12 | 3.20 |
| **3.0** | ~ 1200 | V12 | 4.56 |
| **3.0** | ~ 1900 | V18 | 4.78 |
| **3.0** | 1901 ~ 2400 | V25 | Confirm |
| **4.0** | ~ 1200 | V18 | 6.10 |
| **4.0** | 1201 ~ 1700 | V25 | 6.42 |
| **4.0** | 1701 ~ 2000 | V32 | 6.84 |
| **4.0** | 2001 ~ 2400 | V40 | 7.40 |
| **5.0** | ~ 1000 | V25 | 8.26 |
| **5.0** | 1001 ~ 1300 | V32 | 8.44 |
| **5.0** | 1301 ~ 1600 | V40 | 8.74 |
| **6.0** | ~ 700 | V25 | 9.62 |
| **6.0** | 701 ~ 900 | V32 | 9.80 |
| **6.0** | 901 ~ 1150 | V40 | 10.06 |
| **8.0** | ~ 650 | V40 | 12.78 |
| **8.0** | 651 ~ 800 | V80 | 14.90 |
| **9.0** | ~ 400 | V40 | 14.12 |
| **9.0** | 401 ~ 800 | V80 | 16.20 |
| **10.0**| ~ 800 | V80 | 17.52 |

#### 4. Copper (Cu) *(restored — was missing from V2 entirely)*

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi Deduction (mm) |
| :--- | :--- | :--- | :--- |
| **3.0** | ~ 1900 | V18 | 5.10 |

> **Note (`3.0mm / 1901~2400 / V25` for Aluminum, row above)**: Source table marks this cell `Confirm` — no numeric Nobi value available. Per Section 4.7 Rule 4 (No Table Match), treat as `is_flagged = true` and maintain flat blank at OD.

---

## 8. CAD Architecture & AutoLISP Schema

### 8.1 Units & Header Setup (NEW — mandatory first step in code generation)
Before emitting any geometry, the generated `.lsp` script MUST initialize drawing units to prevent scale corruption:
```lisp
(setvar "INSUNITS" 4)   ; 4 = Millimeters
(setvar "LUNITS" 2)     ; 2 = Decimal
(setvar "LUPREC" 2)     ; 2 decimal places precision
```
All coordinate values in `*parts*` (Section 8.4) are assumed to be in millimeters; this header block guarantees the AutoCAD session interprets them correctly regardless of the user's template default.

### 8.2 Layer, Linetype & Color Specifications
All entities exist strictly on Layer `"0"`. Attribute properties are assigned via explicit DXF Group Codes:

| Geometry Feature | Linetype (Group 6) | Color Code (Group 62) | Execution Method |
| :--- | :--- | :--- | :--- |
| **Outer / Inner Boundary** | ByLayer | ByLayer (7 / White) | Closed `LWPOLYLINE` |
| **Bend Lines** | `"DASHED"` | ByLayer | Double parallel lines |
| **Kegaki / Formed Lines** | ByLayer | `1` (Red) | `LINE` or `LWPOLYLINE` |
| **Ordinary PIERCING / capacity POINT** | ByLayer | ByLayer | actual `POINT`, NOT `CIRCLE` |
| **PIERCING + THROUGH HOLE POINT** | ByLayer | `3` (Green) | actual `POINT` |
| **Relief slit (LINE-specific)** | ByLayer | `3` (Green) only when specified | `LINE` |
| **Ambiguous Features** | ByLayer | `6` (Magenta) | Estimated geometry entities |
| **Adjacent Text Notes** | ByLayer | `6` (Magenta) | `TEXT` entity next to feature |

### 8.3 Interactive Dynamic DCL Command Structure
The primary AutoLISP command MUST be **`c:DRAW`**. It constructs a dynamic DCL selection dialog at runtime:
1. Writes a temporary `.dcl` file to `(getvar "TEMPPREFIX")`.
2. Populates a `list_box` (`multiple_select = true;`) with part codes from global variable `*parts*`.
3. On accept, prompts user for insertion point `(getpoint)` and draws selected flat patterns.

### 8.4 `*parts*` LISP Data Structure
```lisp
(setq *parts*
  '(
    (
      "DRAWING_CODE"      ; String: e.g. "041919"
      "MATERIAL"          ; String: e.g. "SUS304"
      THICKNESS           ; Real: e.g. 3.0
      OUTLINE             ; List: ((x y bulge_or_nil) ...)
      OUTER_FILLETS       ; List: ((x y radius) ...)
      CHAMFERS            ; List: ((x y size) ...)
      BEND_LINES          ; List: (((x1 y1) (x2 y2) is_flagged) ...)
      CORNER_RELIEFS      ; List: ((x y offset) ...)     ; see Section 4.10 for calc rule
      INTERNAL_FILLETS    ; List: ((x y radius) ...)
      HOLES               ; List: ((x y diameter_or_slot_spec [is_flagged]) ...)
      KEGAKI_LINES        ; List: (((x1 y1) (x2 y2)) ...)
      PIASUS              ; List: ((x y is_through) ...); TRUE only PDF PIERCING + THROUGH HOLE; Ø/M in report only
    )
  )
)
```

#### 8.4.1 Canonical Slot Spec — No Ambiguous `len` Parameter
Inside `HOLES`, slots MUST use one of these canonical forms:

```lisp
(x y (SLOTX L_TOTAL W))
(x y (SLOTY L_TOTAL W))
```

- `L_TOTAL` = total end-to-end slot length.
- `W` = slot width and diameter of each semicircular end.
- Internal helper geometry must use center offset `(L_TOTAL - W) / 2`.
- If the drawing supplies center-to-center / tangent length `C`, convert before storage: `L_TOTAL = C + W`.
- Reject/flag any slot where `L_TOTAL < W`, or where source length semantics are not proven.
- Do not use a generic helper argument named only `len` unless the function contract explicitly states `len = L_TOTAL`; ambiguous helper semantics are prohibited.

---

## 9. Output Contract & Response Structure

For normal drawing-to-Lisp production work, output strictly in **COMPACT DUAL-STAGE FORMAT**. Accuracy and the Lisp geometry are primary; commentary is secondary.

### Stage 1: Compact Production Report
Keep Stage 1 short. Default target is approximately **4–12 lines plus a small part table**, unless a failure requires more explanation.

Required content:

1. **Part Summary** — one compact table with only:
   - Barcode / Drawing Code
   - Material
   - Thickness
   - Calculated flat blank size, when fully proven

2. **Applied Adjustments** — only values that materially affect geometry:
   - handwritten correction / handwritten Nobi used;
   - Mid-Tolerance adjustment used;
   - ID→OD conversion used;
   - Nobi table row / conservative round-up used.
   Omit this subsection if none apply.

3. **Validation Result**:
   - If all mandatory checks required for the part pass: write one concise line such as `Validation: PASS — contour, datum, feature count, unfold, containment checked.`
   - Do **not** print the full PASS checklist by default.
   - If any check is `FAIL`, `FLAGGED`, `WARN`, or `N/A` in a way that affects production interpretation, list only those exceptions with a short reason.

4. **Questions / Ambiguity**:
   - If topology, feature type, bend sequence, critical material or datum cannot be proved, STOP production generation and ask; numeric-only gaps on proven topology may be emitted as explicitly FLAGGED non-production Magenta previews if the user demands output.
   - Do not generate guessed Lisp merely to complete the response.

**Report discipline:** Do not discuss irrelevant title-block fields, broad theory, calibration history, or lengthy reasoning unless explicitly requested.

### Stage 2: Ready-to-Run AutoLISP Code Block
When Stage 1 has no unresolved blocker, follow immediately with **exactly ONE** standard code block containing the complete AutoLISP script (`.lsp`), beginning with the Units & Header Setup block in Section 8.1.

If source uncertainty changes topology, feature type, bend order or essential material, do not invent geometry in Stage 2. For only numeric uncertainty on proven topology, when the user requires output, emit a clearly FLAGGED Magenta non-production preview and list every estimated numeric field in Stage 1; no PASS.

## Appendix A — Regression Cases from 520919-05 (Mandatory Anti-Regression Tests)

These cases are not generic dimensions for other jobs. They are concrete regression tests proving that the datum/chain logic is being applied correctly. A future implementation that reproduces the previously wrong coordinates below has failed Section 4.2.

1. **054615 — Vertical hole chain**
   - Proven chain: `10 + 35 + 265 + 10 = 320`.
   - Therefore the two side Ø7 holes are at `Y = 45`, NOT `Y = 55`.
   - This case demonstrates that a nearby 10 mm edge offset must not be added twice.

2. **054621 — Baseline + chain distinction**
   - X positions are `40`, `40+130=170`, `170+130=300`.
   - Do NOT prepend the unrelated `10` mm dimension and generate `50, 180, 310`.
   - This is a baseline/common-datum origin followed by a valid chain, not one continuous chain starting at 10.

3. **054622 — Top-edge datum must remain top-edge datum**
   - With overall height `433`, a dimension `153` from the top edge gives `Y = 433 - 153 = 280`; `253` gives `Y = 180`, then the proven 100 mm chain gives `Y = 80`.
   - Do NOT use a hole row at `Y=423` as a surrogate top datum and shift all values by 10.

4. **054619 — Contour step datum vs hole-row datum**
   - A 54 mm contour/step dimension from the outer top datum `Y=380` gives `Y=326`.
   - Do NOT calculate it from the nearby hole row `Y=365`, which incorrectly gives `311`.

5. **054616 — Hole center chain vs contour dimension**
   - `X = 10 + 350 = 360` for the right hole-center column.
   - A separate contour dimension `375` is not the hole X coordinate unless the extension lines explicitly connect it to that hole center.

6. **054612 — C/R type and count separation**
   - Callouts such as `6-C5`, `2-C10`, and `4-R5` are three different feature families.
   - Chamfers must remain straight, radii must remain arcs, and the number of assigned corners must match each callout count.

7. **Material-table shop Laser R (V4.4 supersedes old DXF-only exception)**
   - Automatically include approved R0.5/R2/R3 for eligible uncalled-out corners. Omit other downstream DXF-only R only after direct user approval or approved shop specification. Do not copy DXF-only geometry as a missing PDF dimension.

8. **Calibration reference is not a hidden dimension source**
   - Parse the PDF first. Use the DXF to expose interpretation mistakes and derive semantic anti-regression rules.
   - Do NOT back-solve missing PDF dimensions from the DXF and then pretend those dimensions were read from the PDF.

9. **Non-R0.5 DXF/PDF disagreement**
   - If the DXF difference can be reconciled with an explicit PDF dimension chain that was previously misread, correct the interpretation.
   - If the difference cannot be supported by the PDF, classify it as a possible production-CAD adjustment/source conflict and report it instead of learning it as a universal drawing rule.



---

## Appendix C — Regression Cases from 520919-07 (Mandatory Anti-Regression Tests)

These cases validate **dimension endpoint identity, contour-topology tracing, and reference-datum handling**. They are examples, not generic coordinates for unrelated jobs.

1. **054633 — Ø5.5 baseline must start at the outer edge, not the Ø7 row**
   - Reference DXF confirms the four Ø5.5 centers at `X=100` and `X=808`, `Y=292/392`.
   - The nearby Ø7 column at `X=10/898` is a separate feature family and separate datum path.
   - Wrong regression: `X=110/818` created by adding the unrelated 10 mm Ø7 edge offset.
   - Rule: a printed `100` with witness line from the outer edge is a baseline/common-datum value; do not prepend the neighboring hole-row offset.

2. **054634 — Nearby vertical dimensions terminate on different feature types**
   - Overall height is `439`. The lower-right Ø7 center is `Y=439-389=50`.
   - The right step ledge is `Y=439-404=35`.
   - These two dimensions share the same area but terminate on a **HOLE_CENTER** and a **CONTOUR_EDGE/STEP**, respectively.
   - The mid Ø7 row is `Y=219.5`; the Ø5.5 rows are `Y=169.5` and `269.5`. Do not assign the Ø5.5 Y values to Ø7 holes.
   - The left Ø5.5 X coordinate is `100`, not `110`; again, the adjacent Ø7 `X=10` offset is not its datum.
   - This case also proves that a visually crowded area can still be fully solvable; do not leave it flagged after a unique explicit trace is established.

3. **054636 — Do not borrow the neighboring hole-center endpoint**
   - Overall width is `405`. The `215` dimension terminates at the **outer right edge**, so the step vertical is `X=405-215=190`.
   - The separate `242.5` dimension is between the bottom middle Ø7 center `X=152.5` and the right Ø7 center `X=395`, giving `395-152.5=242.5`.
   - Wrong regression: `395-215=180`, which incorrectly borrows the hole-center endpoint for a contour dimension.
   - After the base step X is solved, bake the called-out C5/R5 geometry around that step; do not move the datum to a tangent point from another feature.

4. **054638 — Trace the stepped contour before assuming a rectangle**
   - Overall width `405` is only the maximum extent; the upper-right boundary steps inward.
   - `405-180=225` locates the upper vertical cut edge.
   - `405-25=380` locates the inner vertical wall associated with the R5 step.
   - `633-275=358` locates the lower step ledge; `358+35=393` locates the upper horizontal ledge (preserve its proven datum; determine any uncalled-out auto Laser R from the V4.4 approved material table).
   - Therefore the contour must include the inward step `x405 -> x380 -> x225`; extending the `x405` outer edge to the top is topologically wrong even though the bounding box remains `405 x 633`.

5. **054638 — Reference dimension is not a global coordinate**
   - The right Ø7 center is `X=395` (10 mm from the outer-right datum `X=405`).
   - The parenthesized `(276.5)` is referenced from the bottom Ø7 center row at `Y=10`, so `Y=10+276.5=286.5`.
   - Wrong regression: interpreting `(276.5)` directly as `Y=276.5`, or assigning `X=375` from an unrelated 25 mm contour dimension.
   - Rule: reference dimensions retain their witness-line datum and feature type; only tolerance treatment changes.

6. **Feature-family isolation — diameter/callout context is part of the datum graph**
   - In crowded drawings containing Ø7 and Ø5.5 features, track each diameter family independently.
   - A centerline/dimension belonging to `4-Ø5.5` must not create or reposition an `Ø7` feature merely because the centerlines align visually.
   - The datum trace record should include `feature_family` (e.g. `Ø7`, `Ø5.5`, contour step) for crowded multi-feature areas.

7. **Validated passes from 520919-07**
   - `054631`, `054632`, `054635`, and `054637` matched the reference DXF for both contour topology and hole positions (excluding any user-authorized downstream micro-radius policy).
   - These passes confirm that the existing chain/baseline, C5/R5 topology, and closure rules remain valid; do not alter them merely to address the failed cases above.

---

## Appendix D — Regression Cases from 520317-09 (Mandatory Anti-Regression Tests)

These cases were calibrated against a user-approved reference DXF. They are concrete regression tests, not generic coordinates for unrelated jobs. Their purpose is to prevent recurrence of topology, formed-view/reference-dimension, unfold-transform, bend-order, containment, feature-count, and slot-semantics errors.

1. **018263 — Bounding extent is not contour topology**
   - Proven flat extent: `182.70 × 53.00`, but the contour is stepped/L-shaped rather than a full rectangle.
   - Regression failure: replacing the visible step with a `182.70 × 53.00` rectangle, or rounding the explicit `182.70` to `183`.
   - A generated closed hole lying outside the material boundary is an automatic containment FAIL and proves that the coordinate frame/topology must be re-read.

2. **018264 — ID→OD rounding occurs before Nobi arithmetic**
   - For the `165°`, `t=3.0` bend, `Offset_raw = 3 × tan(7.5°) ≈ 0.39495...`; mandatory normalized offset is `0.39 mm`.
   - Use the rounded `0.39` for each applicable ID→OD conversion before Nobi deductions. The calibrated flat height is `67.46`, not `66.68` and not a value obtained from carrying the unrounded offset through the chain.
   - This case also requires count closure: a visible/called-out middle `M4` feature must not be omitted.

3. **018264 — Slot helper semantics**
   - A stadium slot with width/end diameter `W=4.5` and center-distance/tangent length `C=10` has overall length `L_TOTAL=14.5`.
   - Regression failure: passing `10` into a helper that interprets its argument as overall length. The internal representation must classify the source length and convert to canonical `L_TOTAL` first.

4. **018265 — Correct overall dimensions do not prove correct outline**
   - The calibrated bounding extent `140.00 × 95.20` can still contain stepped/radiused topology.
   - Regression failure: emitting a plain rectangle because the W×H values close correctly. Contour topology and called-out R features must be traced independently of the bounding extent.

5. **018266 — Crowded dimensions are not automatically ambiguous**
   - Explicit feature families include `8-Ø5.5`, `20-M5→Ø4.2`, `6-M6→Ø5.0`, `2-M4→Ø3.3`, plus the large circular/cutout features shown on the drawing.
   - Regression failure: declaring the page ambiguous before tracing witness lines and feature-family counts, or substituting one approximate rounded rectangle for multiple explicit cutouts/features.
   - Each family must satisfy its own quantity count and datum trace before PASS.

6. **018267 / 018268 — Formed-view reference overall is not flat overall**
   - A parenthesized/reference length near `398.88` on the formed drawing must not be copied as the flat blank length.
   - Proven unfold chain gives `360 + 2 × (15 + 5 - 0.37) = 399.26`.
   - Across the other axis, `35 + 15 - 3.68 = 46.32`.
   - Regression failure: generating `398.88 × 35` (or integer-rounded `399 × 35`) from the formed/reference values without unfolding the perpendicular flange.

7. **018269 / 018271 — Reference values close to the flat result still do not override the unfold equation**
   - `018269`: `120 + 2 × (15 + 5 - 0.37) = 159.26`; perpendicular flat extent `35 + 23 - 3.68 = 54.32`.
   - `018271`: `230 + 2 × (15 + 10 - 0.37) = 279.26`; perpendicular flat extent `54.32`.
   - Regression failure: forcing the flat to nearby parenthesized formed-view values such as `158.98` or `278.98`.

8. **018270 — Feature coordinates on a flange require local-face → flat transform**
   - A `50` face joined to a `25` flange with `Nobi=4.8` starts at flat coordinate `25-4.8 = 20.2` from that side.
   - Local hole positions `17` and `42` on the face therefore map to global flat positions `20.2+17=37.2` and `20.2+42=62.2` when measured from the proven face start datum.
   - Regression failure: using `17` and `42` directly as global flat coordinates.

9. **018273 — Bend order cannot be validated by total length alone**
   - The same total `52 + 36 - 4.8 = 83.2` is obtained even if `52` and `36` are swapped, but the bend zone is different.
   - Proven order places the relevant bend double lines from the `36` flange side at `36-4.8=31.2` and `36.0`, not at `47.2/52.0`.
   - For a U/open-center topology, bend lines exist only on the material legs; drawing them continuously through the central void is a bend-domain FAIL.

10. **Containment is a mandatory executed check, not a visual assumption**
    - Before Stage 1 can report PASS, every closed hole/slot/cutout must be tested against the actual material polygon, and every bend-line segment must be tested against the material domain.
    - A closed feature outside the polygon or a bend line crossing empty space is FAIL even if the outer polyline is closed and the overall dimensions are correct.

11. **Historical R0.5 exclusion superseded by V4.4**
    - A material-table required R0.5/R2/R3 is generated even if it is not explicitly called out on PDF. For any other DXF-only R require approved downstream shop specification or flag source conflict.

---

## Appendix E — Approved calibration 520924-19 (2026-09-25)

Use the user's declared merged-DXF ordering by descending global Y to map `055915, 055916, 055955, 055956, 055957, 055958, 055959, 055962, 055963, 055964`. Always interpret the PDF first; reference DXF is comparison, not a source for missing PDF numeric values.

- `055915/055916`: four Ø13 and basic contours matched reference; protect existing passing behavior.
- `055955/055956` (SS t9): eligible uncalled-out outside corners must include material Laser R2, including two R2 on `055955`. M4 pilot Ø3.3 < t/2=4.5 => POINT ByLayer, no capacity FLAG. Unconfirmed center dimensions remain independently Magenta FLAG.
- `055957`: retain-inner-panel instruction does NOT request a second detached cutout. Special J/POINT only when the PDF has the applicable indication. User confirms a rare J exists, but the exact leader scope is deferred; do not back-solve it from DXF.
- `055958`: the PDF specifies **R50** (previous R60 OCR was wrong). Prior Lisp shifted ten hole centers by 45.32 mm because of wrong datum/face transform. Two customer-unconfirmed positions remain Magenta. Three green shop reliefs are pending a user-approved construction method: no automatic invented topology.
- `055959`: 22-hole count and overall blank can pass while one lower-left contour edge is wrong by 5 mm. Three customer-unconfirmed positions still Magenta.
- `055962`: two confirmed R2 = t2 *opposite-fold reliefs* preserve both outside dimensions; laser R at unrelated outer corners and bend-line material-domain trimming are independent checks.
- `055963/055964`: verify PIERCING scope or approved effective pilot capacity for M6; a DXF POINT is not itself PDF proof. Unproven R5 on `055964` remains Magenta.
- Unknown numeric-only locations on known topology may be previewed as integer-rounded Magenta geometry and must be FLAGGED. Neither `055957` J endpoints nor `055958` special relief construction is a newly approved universal method.

---

## Appendix B — Portable Deployment Guide

### B.1 Minimum Package
For cross-chat / cross-AI use, the minimum package is this single file:
- `SKILL_LISPCAD_V4_4_PORTABLE.md`

It already contains the formulas, Nobi tables, CAD schema, output contract, datum rules, C/R rules, DXF calibration protocol, and regression cases required for execution.

### B.2 Recommended Invocation Text
At the start of a new AI/chat, the operator should provide this file and issue an instruction equivalent to:

> Read `SKILL_LISPCAD_V4_4_PORTABLE.md` completely before processing drawings. Treat Sections 0–9 and all appendices as mandatory. Focus first on the drawing field, dimensions/witness lines, handwritten corrections/Nobi, barcode, material, and thickness. Keep Stage 1 compact; prioritize production-safe geometry and ask when evidence is not unique.

### B.3 Audit-Only Exception
If the user explicitly asks only to compare, audit, or produce a report and says **not to regenerate AutoLISP**, the audit request overrides the normal Stage 2 generation requirement for that turn. The AI must still apply all interpretation and verification rules and produce a structured Stage 1-style report.

### B.4 What This File Can and Cannot Guarantee
- This file can make behavior **portable and reproducible** when supplied to another capable AI.
- It cannot, by itself, permanently retrain or alter the base weights of every AI/model.
- Therefore all validated learning that must persist must be represented explicitly in this portable specification, regression appendices, or user-supplied companion references.

### B.5 V4.4 approved 520924-19 release

- Replaced unconditional DXF-only R0.5 omission with PDF-first, workbook-governed auto Laser R0.5/R2/R3 at eligible, uncalled-out corners.
- Replaced one-size-fits-all minimum-hole warning with scoped PIERCING, Ø<t/2, inherited Excel material thresholds, pilot-table M conversion and POINT color rules.
- Enabled clearly non-production Magenta preview for numeric-only uncertainty on known topology, retained special J and independently defined R=t relief, and added Appendix E.
- Embedded the full approved Excel table in Section 7.2; no hidden dependency on uploaded spreadsheet.
- V4.3 and V4.2 entries below are historical; where they conflict, these V4.4-approved rules govern.

### B.6 V4.3 Portability Change Log (historical only)
- Added **Drawing-Field Focus Mode**: prioritize main geometry, dimensions/witness lines, handwritten corrections/Nobi, barcode, material, and thickness; ignore unrelated title-block/administrative text unless it resolves a production conflict.
- Added **user-marked ROI priority**: when the operator boxes/crops/highlights the drawing field, inspect that region first and only read necessary metadata/notes outside it.
- Added mandatory drawing read order: contour topology → feature inventory/counts → datum graph → bend/face mapping → handwritten evidence → metadata lock → CAD generation.
- Changed Stage 1 to a **compact production report**. Full validation still runs internally, but only summary + non-PASS exceptions are printed by default.
- Added explicit rule that brevity may never reduce geometric verification quality.
- Added clarification gate: if contour, datum, feature type, bend order, handwritten note target, barcode, material, or thickness is not uniquely proven, STOP and ask before generating Lisp.
- Added explicit anti-verbosity rule: do not narrate exploratory reasoning, broad theory, or irrelevant document fields during normal Lisp production.

#### V4.2 baseline retained
- V4.2 calibration added from reference set `520317-09`.
- Added mandatory ID→OD intermediate rounding: calculate raw offset, round to `0.01 mm`, then use the rounded offset in OD/Nobi/flat equations; confirmed `165°`, `t3`: `0.39495... → 0.39 mm`.
- Promoted uncalled-out **DXF-only R0.5** to an explicit portable shop-feature exclusion rule: omit from Lisp and calibration scoring unless the PDF/current user explicitly requires it.
- Added formed-view/reference-dimension safeguard: reference dimensions on bent views are not flat-pattern dimensions unless their witness lines explicitly belong to a development view.
- Added local-face → global-flat feature transform and mandatory face/bend sequence tracing.
- Added containment validation for closed cut features and bend-line material domains.
- Added quantity/feature-family closure checks so crowded drawings cannot be abandoned before explicit callout counts are traced.
- Added canonical slot-length semantics (`L_TOTAL`) and banned ambiguous helper `len` contracts.
- Strengthened ambiguity handling: Magenta cannot be used to invent contour topology, substitute bounding rectangles, or choose arbitrary bend order.
- Added Appendix D regression cases for `018263`, `018264`, `018265`, `018266`, `018267`, `018268`, `018269`, `018270`, `018271`, and `018273`.

#### V4.1 baseline retained
- V4.1 calibration added from reference set `520919-07`.
- Added **Dimension Endpoint Identity** so adjacent dimensions cannot silently share the wrong outer-edge/hole-center/step endpoint.
- Added **Contour Topology First** to prevent converting stepped silhouettes into bounding rectangles.
- Added explicit **Reference-Dimension Datum** rule: parenthesized values are not global coordinates.
- Strengthened ambiguity handling: exhaust explicit witness-line traces before using Magenta/FLAG.
- Added Appendix C anti-regression cases for `054633`, `054634`, `054636`, and `054638`; retained confirmed passes for `054631`, `054632`, `054635`, and `054637`.
- Preserved the user-authorized DXF-only shop `R0.5` exclusion.

#### V4.0 baseline retained
- Converted DXF "training" language into **calibration + portable rule extraction** to avoid dependence on session memory.
- Added mandatory standalone/session-independent execution contract.
- Added rule classification: universal rule vs regression example vs job-specific exception.
- Added no-hidden-context requirement.
- Preserved all V3.2 engineering rules and regression examples, including 054615 datum correction and R0.5 downstream-shop exception.