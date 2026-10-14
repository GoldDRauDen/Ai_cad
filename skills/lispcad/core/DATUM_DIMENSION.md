## V4.34 typed witness node closure (2026-10-13)
For every **proved HOLE/SLOT member** in V4.34, declare `witness_required_feature_ids` and a `feature_witness_graph` for both X and Y. Every used dimension edge records a physical `from_node`/`to_node`, endpoint types (`OUTER_EDGE`, `HOLE_CENTER`, `SLOT_MIDPOINT`, `ARC_CENTER`, `TANGENT_POINT`, ...), signed axis/value, dimension kind, source page and a verifiable PDF crop/witness ref. `tools/dimension_witness.py` independently solves signed paths, rejects disconnected graphs/contradictory cycles, and cross-checks declared canonical CIRCLE coordinates. A claim `endpoint_verified=true` is not source proof by itself: source QA must inspect the crop and confirm the physical endpoints. 521013-21/059759 negative regression: taking 265 from the external RIGHT_EDGE rather than the RIGHT_HOLE_CENTER adds 10 mm to the group; sample/reference geometry cannot supply a missing witness. Old V4.31 jobs retain compatibility while V4.34 imposes the stronger evidence record.

# LISPCAD Core — Datum & Dimension Semantics

Source: approved V4.3 production baseline, with independently approved V4.10 source-origin/axis mapping. These rules apply across all topology and mode modules.

## V4.8 approved datum/feature-family regression

Regression 520709-07: for 039915, OD 30 minus local step 5 gives the external step at **25**, NOT 27.36 (Nobi-adjusted bend datum) minus 5 = 22.36; the bend zone still retains Nobi 2.64. For 039918 and PDF-mirrored 039919, printed diagonal 50 (not 100) is measured to the theoretical sharp point before R10; independently identify 2-M4 and 3-Ø5 hole families by source leaders. The correct original 039918 flattened local centers (173.2,110) and (224.2,54) are respectively M4→Ø3.3 and Ø5. These examples reinforce existing dimension-endpoint and family-isolation rules; they do not create new general coordinates.

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

#### 4.2.2a V4.16 Face-First Dimension Ownership

Before unfolding any multi-face part, reconstruct each visible formed face as its own contour/feature model. Tag every used dimension by actual witness endpoints and assign it to one semantic graph: face contour, hole/slot center-or-size, bend/face transition, or another proved local feature.

- A hole/slot-center dimension never becomes a contour or bend-axis dimension merely because it is parallel, nearby, or numerically convenient.
- Finish each face's contour and feature graph from that face's own witnesses before joining adjacent faces and deducting Nobi.
- Projection alignment may identify the owning face but does not transfer dimension ownership across faces.
- Approved 044812/044813 regression: `25` is the center distance of two `9.5×R1.75` long holes on the `28×41` face; use `28 + 21 - 3.68 = 45.32` for the proved two-face flat contribution, not `25-3.68` as a contour/bend coordinate.

#### 4.2.2b Cross-part Assembly Datum Closure (approved 2026-10-13)

When a hole, slot, locating mark or other manufacturing feature has NO directly proved local coordinate but the PDF provides an assembly/installation view and related part dimensions, **try a source-backed ASSEMBLY_DATUM_GRAPH before numeric FLAG or VIEWS_ONLY**. Do not claim the dimension is missing merely because the child part's own flat lacks a coordinate.

1. Establish the PART_IDENTITY_GRAPH first: physical part code, host face, the related mating/support parts and actual view IDs. A shared assembly view is not a separate manufactured part.
2. Choose one physically proved assembly reference frame and independently prove both signed X and Y directions. For each used dimension record its *actual* witness endpoints, type (baseline/chain/local/ordinate/contact/assembly offset), sign, host-part identity and printed/approved evidence. Only join dimension paths through the **same physical node**, not paper proximity, shared numbers, nominal symmetry or sample/reference DXF.
3. Represent each relation as `target_axis - source_axis = signed_offset_mm`, with a source witness for the corresponding edge. A contact offset of zero requires positive evidence of the mating contact; mere proximity or a presumed flush fit is not a constraint. Across oriented/bent faces, prove the transform and physical attachment edge before adding its signed offset.
4. Solve the connected graph to express `feature - target_part_datum` as a signed sum; independently check every available alternate dimension path/cycle and the assembly fit. A contradicted or disconnected graph is **not** a 50%-confidence coordinate: retain the local FLAG and ask about the *missing physical relationship*.
5. Transform the assembly result to the feature's own physical face frame, then to the final flat through the routed face/bend rules. Run fold-back and hole count/diameter/host QA in the same frame. A mathematically correct assembly offset does not alone prove an unfolded feature location.
6. Retain feature ID, source dimension witnesses, source node and target node, `frame_id`, axis, signed formula, result, applicable face transform and any unresolved degrees of freedom. A later customer/sample DXF can challenge a solution but must not become its missing witness.

`tools/assembly_datum_solver.py` provides a deterministic, source-proof-gated graph solver for the arithmetic and cycle consistency. The L3 holistic guard independently recomputes any **declared** `assembly_indirect_candidates` from corresponding `assembly_datum_traces`, and fails incorrect/unattempted proof for production. **Source census must declare the candidates**; the tool cannot discover them by itself.

This procedure is conditional: do not create a fictitious assembly for standalone flat parts or override a genuinely explicit source feature dimension. The fixture `regression/datum/521013-04_059636_assembly_graph.json` tests this class of error only; its offsets are not general rules.

#### 4.2.3 Required Datum Trace Record
For every hole row, notch, step, or repeated feature pattern, retain a trace record containing: `axis`, `datum entity`, `dimension type`, `equation`, and `result`. This trace must be auditable in Stage 1 for any feature that was previously ambiguous or that disagrees with a reference DXF.

#### 4.2.4 Dimension Endpoint Identity — MUST NOT Borrow a Neighboring Endpoint
Every dimension endpoint/witness line must be tagged by the **actual geometry it terminates on** before arithmetic. At minimum distinguish: `OUTER_EDGE`, `CONTOUR_EDGE/STEP`, `HOLE_CENTER`, `CENTERLINE`, `THEORETICAL_SHARP_CORNER`, and `REFERENCE_DATUM`.

- Two parallel dimensions drawn beside each other may terminate on different targets even when they share the same axis or appear visually aligned. Never reuse the endpoint of a neighboring dimension without proving the witness line lands on the same node.
- A hole-center dimension and a contour-edge dimension are different graph edges even if their values are printed in the same local area.
- Example pattern: if one horizontal dimension is from a step to the **outer edge** and an adjacent dimension is between two **hole centers**, do not subtract both from the same right-side X coordinate.
- Example pattern: if vertical dimensions `389` and `404` terminate respectively at a hole center and a step ledge, they define two different Y nodes; they are not interchangeable.
- Record the endpoint identity in the datum trace whenever a crowded drawing contains multiple nearby extension lines.

#### 4.2.4.1 V4.32 Radius/notch depth endpoint semantics

For an edge-open notch or recess containing an arc/radius, classify whether a printed dimension terminates on the **physical deepest contour point**, the arc center, a tangent point, or another explicit witness node before converting it to geometry.

- `OVERALL_DEPTH` to the physical deepest point is not `CENTER_SETBACK`.
- If source proves radius `R` and overall depth `D` measured to the deepest arc point, then a same-axis center setback may be derived as `D - R`; do not copy `D` directly to the arc center.
- Conversely, if the witness proves the center location, do not silently reinterpret that center dimension as physical overall depth.
- Regression 521006-18 058649/058650: `R3` with source overall depth `8` gives center setback `5`; treating center setback as `8` creates wrong physical depth `11`. These values are regression evidence only.

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
Features dimensioned on a bent flange/face MUST be transformed from the **local face coordinate system** into the **global unfolded blank coordinate system** before verified global-flat coordinates are emitted.

1. Assign each formed face an ordered identity along the unfold path: `FACE_1 -> BEND_1 -> FACE_2 -> ...`.
2. Establish the flat start/end coordinates of that face from the sequential OD/Nobi equations in Section 4.7.
3. Preserve the dimension direction. If local coordinate `u` is measured from the face start datum, use `U_flat = FACE_START_flat + u`. If it is measured from the opposite/free edge, use `U_flat = FACE_END_flat - u`.
4. A feature coordinate printed on a formed face MUST NOT be copied directly as a global flat coordinate unless the face datum is proven to coincide with the global flat datum.
5. Record `face_id`, `local datum`, `local equation`, and `global flat equation` in the datum trace for holes/slots/notches that cross a bend mapping.

This rule applies independently on both axes. Projection alignment may identify which face a feature belongs to, but may not replace the required unfold transform.

#### 4.2.7.1 V4.32 Physical edge identity survives the transform

For any edge-based datum on a bent face, record the physical edge identity before unfold, for example `FACE_2.BEND_EDGE`, `FACE_2.FREE_EDGE`, `FACE_2.LEFT_EDGE`, or `FACE_2.RIGHT_EDGE`.

- The identity comes from the source-supported face graph and `BEND_ATTACHMENT_EDGE_LOCKED`, not from page direction or nearest-view proximity.
- Rotation/reflection/local-axis reversal may change the coordinate equation but must not silently swap `BEND_EDGE` with `FREE_EDGE`.
- Every feature positioned from such an edge must retain `face_id | physical datum edge id | local equation | attachment transform | global flat equation`.
- If the same local numeric coordinate can be obtained from two different edge identities, numeric equality does not close the ambiguity. The physical owner must still be proved.
- Fold-back must reproduce both the feature offset and the owning physical edge identity.

#### 4.2.7.2 V4.14 approved symmetry/explicit-edge-dimension precedence

If actual PDF geometry PROVES a symmetry axis and there is NO controlling outer-edge dimension for a repeated feature family, use that axis to construct the symmetric centers/positions and retain a datum trace. When the same feature family has an explicit physical outside-edge dimension, **DRAW ACCORDING TO THE PRINTED EDGE DIMENSION** even if a centerline is also shown. A printed axis that coexists with source-proved actual asymmetry or mutually inconsistent witnesses is a specific FLAG/question after fully tracing all source evidence; do not silently force visual symmetry. For features on bent faces, source-frame lock and the independent per-face local→global-flat transform remain mandatory. User-approved 010420 Q03 documents this priority.

#### 4.2.8 Bend Sequence / Face Order Is Non-Commutative
The total flat length equation may be numerically unchanged when two flange lengths are swapped, but **bend positions, feature transforms, and material topology are not**. Therefore:

- Determine the ordered face sequence from the visible formed topology, bend callouts, section/detail views, and proven witness-line connectivity before calculating bend-line coordinates.
- Do not validate bend order merely because `sum(OD) - sum(Nobi)` matches the overall blank length.
- Double bend lines MUST be positioned from the ordered sequence in Section 4.7 and MUST exist only over material regions that actually cross that bend. For U-shaped, legged, stepped, or cut-away parts, split/trim bend lines around voids; never draw a bend line continuously through empty space.
- If two face orders remain equally plausible after explicit trace exhaustion, STOP and ask the user. Magenta is not permission to choose an arbitrary bend order.

#### 4.2.9 Mandatory Source-Origin and Axis-Direction Lock (V4.10 — approved)

**Before converting any absolute/ordinate drawing dimensions into CAD coordinates, prove the SOURCE coordinate frame for EACH affected view.** Identify (a) the physical source origin O and the actual two edges/features that define it, (b) the direction of source +X and +Y from printed arrows, coordinate signs, dimension witness lines or explicit drawing annotations, (c) which actual material edge/feature becomes the TARGET CAD datum, and (d) the source-view-to-CAD orientation. Neither the paper/page upper-left corner nor a habitual DXF lower-left origin is evidence by itself. Never assume that a negative source ordinate means a negative CAD ordinate.

For an axis-aligned view with no X/Y exchange, let `(X0_cad,Y0_cad)` be the VERIFIED CAD coordinates of the drawing's source origin and `sx,sy ∈ {+1,-1}` represent the respective source-positive axis directions relative to CAD-positive right/up. Use the general explicit transform:

```
X_cad = X0_cad + sx * X_source
Y_cad = Y0_cad + sy * Y_source
```

Lock **both** source origin and each axis sign independently. When a source view is mirrored, rotated or exchanges X and Y, first prove the actual mapping from its view/face to the intended CAD face and apply the correctly oriented axis mapping; do not force this simple aligned-axis formula onto an unresolved view. Section 4.2.7 local-formed-face → global-flat unfolding is an ADDITIONAL transform after the source frame is established, not a substitute for it.

**Top-left source datum cases:** If the drawing's proven origin is at its material top-left, its explicitly dimensioned part height is `H`, and CAD Y=0 is the SAME material bottom edge, then `Y0_cad=H`. If source +Y points **up** and a hole is given as `Y_source=-d`, `Y_cad=H-d`; if source +Y points **down** and the hole is `Y_source=+d`, `Y_cad=H-d`. These are two equivalent physical layouts with DIFFERENT source signs; do not mix their conventions. Use `H` only when that height and both controlling top/bottom edges are actually proven for the SAME view/face; never use an arbitrary picture/image bounding box or a formed-view overall for a different flat face.

**Mandatory audit trace** for any ordinate-based feature family: source view/face ID, source origin's actual geometry, source +X/+Y directions, source signed X/Y of each family or row, target CAD datum, view transform (including any mirror/rotation), the explicit coordinate equations, and an independently dimensioned closure check where supplied. A row of repeated holes shares a Y result only when the source witness/ordinate data prove a common physical row. If origin or either needed axis direction is unproved after tracing all explicit drawing evidence, mark the affected coordinates FLAG and ask; keep independently proved source views separate rather than emitting guessed production coordinates. A visually plausible row or a matching total bbox is NOT evidence of a correct datum.

### 4.3 Mid-Tolerance Strategy (Tolerance Calculation)
For coordinates governed by asymmetric tolerances or limit dimensions, calculate the flat pattern feature position using the **Mid-Tolerance Value**:

$$X_{\text{mid}} = X_{\text{nominal}} + \frac{\text{Tolerance}_{\text{upper}} + \text{Tolerance}_{\text{lower}}}{2}$$

- **Example**: A dimension specified as $50.0^{+0.2}_{+0.1}\text{ mm}$ is computed as:
  $$X_{\text{mid}} = 50.0 + \frac{0.2 + 0.1}{2} = 50.15\text{ mm}$$
- **Symmetric Tolerances** ($\pm 0.1\text{ mm}$): Mid-tolerance equals nominal value.
- **Reference Dimensions** (参考 / marked as reference, no tolerance band): Do NOT apply mid-tolerance adjustment — use nominal value as-is (see Section 6, term "Reference").

### 4.4 Ambiguous, Unclear, or Missing Dimension Handling
- **Flag only after explicit-trace exhaustion**: A crowded/overlapping print is not automatically ambiguous. Before flagging, zoom/re-read the witness lines and test all explicit dimension paths, endpoint identities, feature diameters, feature counts, projection relationships, and overall closure. If the PDF contains a unique trace, use it; do not use Magenta as an escape from difficult dimension parsing.
- **Magenta is not permission to invent topology**: Use estimated/Magenta geometry only when the entity identity and contour/feature topology are already certain but a numeric dimension remains unreadable/ambiguous. If multiple topologies, feature types, bend orders, or physical attachment edges are possible, STOP and ask the user rather than fabricating a bounding rectangle, generic slot, or arbitrary flange order/edge.
- **Integer Value Enforcement applies only to estimated/assumed values**: Any truly estimated dimension MUST be rounded to the nearest integer (e.g., `256` or `258`, never `256.4`). Explicit dimensions and deterministic formula results (for example `182.70`, `159.26`, or a Nobi-derived bend coordinate) MUST retain their calculated precision and MUST NOT be rounded to an integer merely because another part of the same feature/part is flagged.
- **Known/unknown separation**: Flagging an unresolved feature does not authorize changing dimensions that are already proven. Keep all proven edges, lengths, hole sizes, and coordinates exact; isolate only the unresolved quantity/entity.
- **No bounding-box substitution**: A known overall width/height may be reported as a bounding extent, but MUST NOT be emitted as a closed rectangular outline unless the contour trace proves that all four rectangle edges actually exist.
- **Color Code 6 (Magenta)**: Assign DXF Group `(62 . 6)` to any line, circle, or polyline whose size/position was estimated or ambiguous.
- **Adjacent Text Annotation**: Add a `TEXT` entity on DXF Group `(62 . 6)` immediately adjacent to the ambiguous feature (e.g., `"(ESTIMATED GEOMETRY - CHECK DRAWING)"` or `"(M6 OR M8)"`).
