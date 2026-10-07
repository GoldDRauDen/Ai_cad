# V4.33 holistic re-solve and complete source-view fallback

Before accepting `VIEWS_ONLY`, run `references/HOLISTIC_ENGINEERING_CHALLENGE.md`. A first failed interpretation is not source exhaustion. Re-open all relevant PDF views, DATA physical curves, witness chains, handwritten flat/Nobi arithmetic, part identity and candidate FACE_GRAPH relationships, then record the specific unresolved degree of freedom.

If a defensible flat still cannot be proved but independently proved source/orthographic views exist, the executable fallback is **DRAW THE PROVED VIEWS**: preserve every proved source-view member as separate labeled review subgroups under the correct code, preserve physical DATA curves, keep all proved features, and FLAG only the unresolved relationship. Do not stop at a text report and do not emit a small representative subset.

For multi-barcode / ①② / welded constituent drawings, build the routed `PART_IDENTITY_GRAPH` before assigning source views or DATA clusters to manufacturing codes.

# LISPCAD Core — Drawing Reading & Execution Contract

## V4.19 FACE_GRAPH_CAPTURE — mandatory source representation for bent/multi-face parts

Before Nobi arithmetic or global-flat coordinates, create an evidence-equivalent FACE_GRAPH as defined in `../../../references/FACE_GRAPH_UNFOLD_PROTOCOL.md`. Every used dimension must record both physical witness endpoints, semantic family and owner face/bend; every feature must record its host face/local datum; every bend must record both adjacent faces, shared edge, signed orientation and material domain. Shape labels (U/Z/box/etc.) may propose a graph but never prove it.

Do not proceed to production unfold while an ownership field is unresolved or while two materially different graphs satisfy the same source evidence.



## V4.18 approved 520929-18 — detailed-source bundle authority hardening

**V4.18 DETAILED_SOURCE_BUNDLE:** A Page-1/job-list row is a summary/mapping source, not an automatic override of the detailed drawing page. For the same barcode/code, when the detailed page contains a mutually consistent bundle of (a) matching code identity, (b) explicit material/thickness, (c) dimension-witnessed formed geometry, and (d) handwritten/printed Nobi or flat arithmetic that closes those dimensions, and there is no later revision/red correction/cancellation with higher authority, use that detailed bundle to resolve a contradictory summary row without asking. This is NOT a rule that “barcode page always wins”: if the detailed evidence does not close, identity is uncertain, or a higher-authority revision conflicts, FLAG/ask. In NEW_PDF_TO_DXF, a later reference DXF may verify the resolution but must not supply missing construction dimensions.

Source: approved V4.3 production baseline. This file preserves the portable contract, execution pipeline, drawing interpretation rules, and Japanese drawing terminology.

**Modular compatibility note:** inherited V4.3 wording such as “this document” refers to the complete approved LISPCAD rule set loaded through `AI_ENTRYPOINT.md`. The single-file portable form remains `../portable/SKILL_LISPCAD_CURRENT.md`.

## V4.13 approved 520315-18 additions — existing slot/shop rules NOT duplicated

**Reference SOURCE_UNIT_CONFLICT:** A reference DXF $INSUNITS header is metadata, not automatic geometric truth. Before comparing sample geometry, verify actual numeric units against independently read PDF witness-line dimensions and the user's explicit unit confirmation. The approved 520315-18_ss.dxf has a misleading inch header but actual mm numbers: DO NOT multiply/divide by 25.4. If a different sample's true units remain unresolved, FLAG and ask. Newly generated DXF still uses $INSUNITS=4.

**Each code is independently declared; MIRROR is source scoped:** Only construct a reflected partner when the drawing/user establishes original and target codes, axis/orientation and the exact reflection scope. Reflect the complete proven geometry including contour, distinct hole families, slots, R/C, bends and markings; then revalidate the partner. If only the original is requested, do not invent a second code. A mirror of INSIDE views within one part does not create an undeclared part code.

**Already-approved rules:** Exhaust whole slot dimension strings and verify END-CENTER versus OUTSIDE-TIP witnesses before asking (existing §§3.1 and 4.2.4); do not reintroduce routine shop-spacing approval questions (existing V4.12 §5.2). See new examples 018295/018304 and case 018297 in regression/qa/520315-18_V4_13_APPROVED.md.

## V4.12 approved drawing-reading refinements (deduplicated against V4.11)

For sheet-metal designation families, recognize case-insensitive `SUS…→SUS`, `SP…/SS…→SS`, `A…→AL`, while preserving the full printed grade, thickness and the approved SUS430 SS-Nobi/SUS-laser split. A family match does not assert that distinct source grades are chemically identical.

Before asking, exhaust explicit witness lines, handwritten Nobi, width-derived slot-end radius and local-face transforms. If the flat is independently proved, draw it even if an unrelated round-hole Ø/center is still uncertain; isolate that feature as Magenta `CIRCLE Ø?` / coordinate FLAG instead of changing its unknown Ø to POINT. Reuse existing V4.11 VIEWS_ONLY only when the actual unfold is not supportable. Do not require sample DXF for a clearly marked preview or ask for routine PDF-conforming shop-spacing acceptance. See portable §§2.1.1, 3.3, 4.4.2, 5.2 and approved regression `520217-27`.

## V4.11 approved preview-first override — active

**DRAW → FLAG → CONFIRM:** If actual PDF evidence supports a recognizable approximation but a dimension, feature type or topology remains unproved, render the provisional portion Magenta (Layer 0, DXF 62=6), add an adjacent explicit assumption/FLAG and ask the user AFTER showing it. Keep every independently proved entity exact. If a defensible flat is not available, render independently proved orthographic/source views separately and label the code `VIEWS_ONLY`. The default combined DXF is `*_ALL_REVIEW_ONLY.dxf` with global **NO CUT** whenever any FLAG remains. Only absent identifiable source views or ambiguous part-code identity stops all drawing. This V4.11 preview rule overrides the inherited V4.3/V4.10 blanket STOP-before-any-drawing wording for **review-only** output; it never weakens Section 5 production PASS or allows silent geometry invention. See [QA regression](../../../regression/qa/520625-15_V4_11_APPROVED.md) and portable §4.4.1.

## V4.8 approved hole-family cancellation — active override

When an entire hole callout is clearly struck out and its leader clearly identifies a complete family, omit the whole family from DXF regardless of remaining legacy drawn circles. Log canceled source quantity and prove zero output entities; active nearby groups are unchanged. If only a tolerance/finish fragment is crossed or target/revision scope is unclear, DO NOT delete holes; ask. Case 040006 on 520709-07 deletes both 2-Ø8H7 while retaining 6-M8 and 4-Ø9. The full authoritative rule is portable Section 2.5, case Appendix F.

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
When the user supplies a reference DXF or corrected CAD for PDF-interpretation calibration (NOT a specifically requested direct audit of an already created AI DXF):
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
- **Function**: Parse 2D sheet metal engineering drawings (PDFs/images), perform mid-tolerance adjustments, calculate flat patterns with precise Nobi (bend allowance) deductions, execute complete manufacturing verification, and output a compact production report and individual + combined direct DXFs with a manifest; optional AutoLISP only on explicit request.
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
➔ [Compact Report + Direct Individual DXFs + Combined DXF + Manifest]
```

### 1.3 Drawing-Field Focus Mode — Accuracy Before Commentary
This is the default operating mode for direct production DXF generation. The AI MUST spend its interpretation effort on the **actual drawing geometry and dimensions**, not on peripheral document text.

**Primary read targets, in order:**
1. Main part geometry / orthographic views / section or detail views that control the manufactured contour.
2. Dimension strings, witness lines, centerlines, bend callouts, hole/slot/cutout quantities, R/C callouts, and datum relationships.
3. Handwritten corrections, handwritten Nobi values, revision clouds, or marked-up notes that change geometry or bend arithmetic.
4. Barcode / drawing code.
5. Material and sheet thickness.

**Do not spend output or reasoning budget on irrelevant title-block data.** Company name, customer name, designer, approval signatures, drawing title, scale, date, pallet/base name, and similar administrative fields are ignored unless they are required to resolve part identity, revision authority, material, thickness, or a geometry conflict.

**User-marked ROI rule:** If the user crops, boxes, highlights, or otherwise identifies the drawing region to inspect, treat that marked region as the primary geometry ROI. Still read barcode, material, thickness, and applicable handwritten/revision notes outside the ROI when the user has explicitly indicated them or they are necessary to resolve the part. Do not let unrelated content outside the marked ROI distract from geometry extraction.

**Quality rule:** A short answer is preferred, but never by skipping geometric verification. Execute the full internal checks in Sections 4–5, then report only the information needed by the operator. If contour topology, feature identity, bend order, handwritten-note target, material, thickness, or datum is unresolved, STOP production geometry and ask. If only numeric size/position is missing AFTER the topology and datum have been traced, the user permits an explicitly non-production, Magenta estimated preview with nearby FLAG text, rounded integer estimates and a Stage 1 FLAG; preserve proven geometry verbatim. Never call that preview production-safe.

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
   - If the same part has conflicting material, thickness, dimension, or handwritten correction across pages, first apply the Section 4.1 authority hierarchy. For a Page-1/job-list summary conflicting with the same-code detailed drawing page, also apply the V4.18 **DETAILED_SOURCE_BUNDLE** rule below.
   - If neither the authority hierarchy nor the detailed-source bundle resolves the conflict, STOP and ask the user. Do not infer the intended value from drawing appearance, filename, surrounding jobs, or common shop practice.
   - When a Page 1 job list exists, use it primarily to map part code/material/thickness and declared ordering; list text must not silently replace dimension-witnessed detailed geometry.
   - **V4.18 DETAILED_SOURCE_BUNDLE resolution:** for the same barcode/code, if the detailed page independently closes code identity + explicit material/thickness + dimension-witnessed formed geometry + applicable Nobi/flat arithmetic, and no higher-authority revision/red correction/cancellation contradicts it, that internally closed detailed bundle resolves a contradictory summary row. Record the conflict and the closure evidence. Do not generalize this into “barcode page always wins”; incomplete or non-closing bundles remain FLAGGED. A customer/reference DXF is audit evidence only after the PDF-derived resolution in NEW_PDF_TO_DXF.

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
   **Mandatory source-frame lock (V4.10):** before applying ANY absolute/ordinate value, identify the coordinate origin's actual source-view feature/edge, +X/+Y arrow/sign conventions, and target CAD datum. A printed absolute top-left origin overrides the usual bottom-left CAD assumption; an unproved origin/axis blocks production geometry (see DATUM_DIMENSION.md §4.2.9).
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

#### 2.4.2b V4.14 approved DIRECT AUDIT of pre-existing AI DXF against a reference

If the user's objective is to evaluate **the AI's already-exported DXF** against a customer-approved reference DXF, compare **those TWO DXFs FIRST**, matching only proved drawing-code clusters and actual user/PDF-confirmed coordinate units, then normalizing layout-only translation and any independently proved orientation. Audit full physical outer/inner boundaries, each hole/slot/cutout family (type, diameter, original quantity and coordinates), true R/C, complete unfolded extent, each double-line bend-pair coordinate and its clipping to real material. ARC+LINE in the reference and exact, closed LWPOLYLINE/bulge in the AI output are geometrically equivalent; raw entity counts alone are not a failure. A source/orthographic face is only PARTIAL if the reference has a complete flat, irrespective of its locally correct holes. Report MATCH/PARTIAL/DIFF **per code**, protect MATCHed parts from later edits, and **only THEN** revisit the PDF to identify why the AI made each error. This is distinct from creating a NEW PDF-based drawing: existing PDF-FIRST rules are unchanged, and sample DXF is never a hidden replacement for an unproved PDF dimension. Approved case: `regression/qa/520217-26_V4_14_APPROVED.md`.

#### 2.4.3 Approved material-table Laser R takes precedence over old DXF-only R0.5 exception

The V4.3 unconditional rule to omit uncalled-out DXF-only R0.5 is superseded. Read the approved `references/MATERIAL_RULES.md` and apply automatic Laser R0.5, R2 and R3 to **eligible, uncalled-out** corners according to material/thickness and corner class. Explicit PDF R or C at a corner always overrides its material-table auto R. A shop-added R not prescribed by the PDF or approved table may be omitted only with direct user confirmation or an approved shop specification; otherwise FLAG a source conflict. This rule never authorizes inventing contour topology, flattening a relief into a fillet, or silently adjusting explicitly dimensioned PDF geometry.

#### 2.4.4 Calibration / Portable Learning Discipline
- Every reference-DXF comparison is an **anti-regression calibration case**: record the semantic reason for each corrected mismatch, not merely the corrected coordinate. Validated general rules belong in this portable skill file.
- Future PDF-only jobs, including in unrelated chats or on another AI, must apply those semantic rules from this file without requiring a DXF.
- Do not generalize one-off production edits from a single DXF into universal rules unless the user explicitly confirms they are standard practice.
- Do not rely on conversational memory for this learning. If the lesson must survive across chats/AIs, encode it in this master skill or a required companion regression file.

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


## V4.7 DXF-first output mode (approved 2026-09-26)
After executing ALL approved V4.6 drawing/material rules and real geometric verification, build ONE checked canonical part-local model. The same coordinates generate direct individual and combined DXFs and optional request-only Lisp; never independently recalculate for either. See `CAD_OUTPUT.md`. Critical missing source evidence blocks production; numeric-only uncertainty on proved topology can be Magenta non-production PREVIEW only on request. No V4.6 engineering lesson is changed by this output migration.
