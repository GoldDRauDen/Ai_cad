---
name: sheet-metal-extractor
description: |
  Extract 2D unfolded flat pattern data from sheet metal fabrication drawings for laser cutting.
  Trigger when user says "read drawing", "extract flat pattern", "laser cutting data", "unfold",
  "Nobi calculation", "sheet metal", "t=*", "出金図", "blank drawing", "展開図", or provides
  a drawing image/PDF for manufacturing. Do NOT use for general PDF/image reading (use pdf/docx skills),
  CAD file editing, or requests that only need dimension extraction without flat pattern data.
---
# Sheet Metal Flat Pattern Extractor
Extracts 2D unfolded flat pattern data from Japanese/English sheet metal fabrication drawings for laser cutting.
## Inputs to collect
- The drawing file (image or PDF) to analyze
- Language context if mixed (Japanese/English)
## GEOMETRY & FILLET EXECUTION RULES
### 1. Dimension Authority & Coordinate Integrity
- **Strict Dimension Primacy**: Always derive vertex coordinates directly from numerical dimension callouts. NEVER modify or guess dimensions based on visual estimation or image overlay.
- **Preserve Notch Depths**: Keep notch and cutout depths exactly as dimensioned (e.g., $Y_{\text{notch}} = 20.0\text{ mm}$).
### 2. Selective Corner Filleting
- **NO Global Polyline Fillets**: Do NOT apply global fillet commands (e.g., `fillet polyline`) to outer boundaries containing internal notches.
- **Explicit Radius Placement**: Apply fillet radius ($R$) ONLY to vertices explicitly marked with an $R$-callout on the drawing.
- **Internal Corners Default to R0**: Internal corners of $U$-shaped notches, tabs, or slots MUST remain sharp 90° corners ($R = 0$) unless an internal radius is explicitly specified.
### 3. Pre-Execution Coordinate Mapping Protocol
- Prior to outputting LISP code, map out the exact vertex sequence $(X, Y)$ and fillet status:
  - Outer Corners (e.g., $P_1, P_2, P_3, P_4, P_7, P_8$) $\rightarrow$ Apply the $R$-value from that vertex's explicit R-callout, if any (e.g. $R2.0$). If no callout exists at that vertex, keep it sharp ($R = 0$) — never assume a default radius.
  - Internal Notch Corners (e.g., $P_5, P_6$) $\rightarrow$ Keep $R0.0$ (Sharp 90°) unless an internal radius is explicitly specified, in which case record it in `internal_fillets` (see Section 5).
## Pre-Screening Rules
**Skip the drawing if ANY of these apply:**
1. No drawing code present (neither barcode nor alphanumeric part number)
2. Drawing contains ONLY text/notes with no graphical representation of the part
## Multi-Page Reading
Drawings may span multiple pages. Apply this rule:
- **Material & thickness**: Read from the FIRST page (e.g., CAD依頼書 / CAD Request Form)
- **Drawing code (barcode)**: Located on the drawing page itself
- **Corrections**: If a later page corrects earlier values, apply the LATEST correction
  - Example: Page 1 says `T3.2 SS`, Page 4 title block says `T3 SUS304` → use T3 SUS304
- The two codes MUST match: page 1 `作業No` (e.g., 26-041919) ↔ page 4 barcode (`*041919*`)

## J Symbol (Bend Marker)

If a circled "J" appears near the barcode:
- Indicates a third-party bending company is responsible for performing the bend.
- **The J symbol does NOT change how Nobi is extracted.** It only changes who performs the bend. The Nobi value still comes from the drawing or the reference table.

**Nobi lookup priority (apply regardless of J symbol):**
1. **Handwritten Nobi on the drawing** (e.g., `-4.8`, `135° -1.71`): use it directly. This is the highest-priority source.
2. **Reference table** `references/nobi-standards.md` (by material, thickness, bend length, angle): use when the drawing has no handwritten value.
3. **No formula and no table match**: keep the flat blank at its Outside Dimension (OD) and draw the bend line at the OD design position. Set `is_flagged=true` on the bend and `has_missing_dimensions=true` on the output.

## Analysis Procedure

### 1. Drawing Code
- **Barcode** on the drawing page (e.g., `*041919*`) is the primary code — extract all numbers
- **作業No / Job No** on the first page must match the barcode
- Do NOT use internal title block codes (e.g., `BS-2024-001`) as the drawing code — those are for internal tracking only
- Examples: `041919`, `040007`, `035821`

### 2. Material & Thickness
- Material: e.g., `SUS304`, `SPCC`, `SPHC(酸洗)`, ` aluminum`, ` copper`
- Thickness (t): e.g., `t=1.2`, `t=4.0`
- **Always apply the latest correction across pages** (see Multi-Page Reading)

### 3. Unfolded Length

**Find the handwritten unfolded length formula on the drawing and parse each component.**

When the formula has the form `A + B + C - (N × Nobi) = Total` (or equivalent):
- `A`, `C`: Nominal flange lengths (cánh gập trái / phải hoặc trên / dưới).
- `B`: Nominal body length (lòng thân, đoạn nằm giữa 2 cánh).
- `N`: Number of bend lines that the Nobi deduction applies to.
- `Nobi`: Deduction per bend (mm), as written on the drawing.
- `Total`: Computed flat length (write this to `unfolded_length`).

**Coordinate rule (mandatory):**
- Body interior coordinates are **always fixed** at `X_1 = A - Nobi` to `X_2 = X_1 + B` (or analogous for the Y-axis).
- The body dimension `B` is **NEVER** reduced by Nobi. Nobi only lives inside the bend zone between the two parallel bend lines.

Steps:
1. Find the handwritten unfolded length formula on the drawing.
2. Parse each component (A, B, C, N, Nobi) and verify they match the dimensions on the drawing.
3. Calculate the RESULT (do not just copy the formula).
4. Save the raw formula into `raw_nobi_formula`.

### 4. Width
- Read the flat pattern width (Y-axis dimension)

### 5. Corners & Chamfers
- **Fillet radius (`fillet_radius`, OUTER corners only)**: Use the exact value from an explicit R-callout on an outer corner. If NO R-callout exists at that outer corner, do NOT apply a default — keep the corner sharp (`fillet_radius = 0`). Never assume 3.0mm or any other default value.
- **Internal fillets (`internal_fillets[]`)**: If an R-callout appears at an INTERNAL corner/notch (not an outer corner) — e.g. "Inside fillet R4 R2" — record each one separately as `{x, y, radius}` in the `internal_fillets` array. Do NOT collapse multiple internal fillet values into `fillet_radius`; that field is reserved for outer corners only.
- **Chamfer**: Identify `C` values (e.g., C2.0, C3.0)

### 6. Bend Lines & Nobi

**Two-line rule (mandatory for laser-cutting flat pattern output):**
- Every bend is represented by **two parallel lines** separated by exactly the Nobi distance.
- The bend zone (width = Nobi) lives **between** the body and the flange. It is NOT allowed to overlap the body interior.
- Body interior dimensions (`B`) are **NEVER** reduced by Nobi. Hole centers are kept at the same offset from the body reference edge as in the 3D drawing.

**Coordinate formulas** for a flange of nominal length `L_flange` bent from a body of nominal length `L_body`:
- `inner_position` (line at the body side / giáp thân, the datum line): `X = L_flange`
- `outer_position` (line on the flange side / sát cánh, offset into the flange by Nobi): `X = L_flange - Nobi`
- The two lines span the full extent of the body where the bend zone exists.
- Distance between the two lines = `Nobi`.

**Sign convention flips with flange direction:**
- `inner_position` is always the datum line adjacent to the body interior; `outer_position` is always offset from it by exactly `Nobi`, toward the flange's open end — but which direction that offset goes depends on which side the flange is on:
  - **Left or bottom flange** (opens toward smaller X/Y): `outer_position = inner_position − Nobi` (outer < inner).
  - **Right or top flange** (opens toward larger X/Y): `outer_position = inner_position + Nobi` (outer > inner).
- Do NOT apply `outer = inner − Nobi` uniformly to every flange — that is only correct for the left/bottom case. See "Master Algorithm" below for a worked left/right example where the sign flips.

**Step-by-step:**
1. Identify ALL bends: X-axis and Y-axis bends.
2. For each bend, record `inner_position` and `outer_position` using the formulas above.
3. For Y-axis bends: both positions are measured from the bottom edge (Y = 0 at the bottom of the flat blank).
4. **Standard Nobi lookup**: If no drawing Nobi provided, consult `references/nobi-standards.md` based on material and thickness.
5. **For non-90° bends**:
   - If nobi is provided on the drawing (e.g., handwritten `135° -1.71`): use it directly.
   - If nobi is NOT provided: draw that bend separately with a 10mm gap, to be combined later.
   - The 10mm gap is FIXED regardless of thickness.
### 6.1 Multi-Direction / Multi-Angle Bends
Drawings may have bends in BOTH X and Y axes, with mixed angles (90° + 135°, etc.):
- Identify each bend by axis + angle + `inner_position` / `outer_position`
- Apply Nobi per bend according to the angle
- For Y-axis bends, the positions are measured from the bottom edge
- See "Worked Example" below
### 6.2 Stepped / Notched Flanges
Some parts have flanges that step inward (a notch / gap) before reaching the main body — e.g. a 20mm tab that leaves a 10mm gap before the main 140mm body. Handle a Y-axis stepped flange like this:
- `Y_flange_flat = L_flange_nominal - Nobi_Y`  *(flat height of the tab portion only — e.g. 20.0 - 4.8 = 15.2 mm)*
- `Y_bend = Y_flange_flat`  *(bend line, measured from the bottom of the flat blank)*
- `Y_notch = Y_flange_flat + L_notch_gap`  *(where the cut-out ends and the main body begins — e.g. 15.2 + 10.0 = 25.2 mm)*
- `Y_body_flat = L_body_nominal`  *(kept untouched, equal to the original 3D body height — e.g. 140.0 mm or 150.0 mm)*
Do NOT reduce `L_body_nominal` by Nobi_Y. The step cut itself is drawn as a horizontal cut from `X = 0` to `X = X_tab` at `Y = Y_notch`.
This rule is described in the SKILL.md only. The JSON schema for `bend_lines` is unchanged — step notches are emitted in the geometry output (DXF) by following the coordinates above, and the agent may add a free-text note if needed.
### 6.3 Bend Line Positioning Formula (Coordinate from Origin 0)
  For sequential flanges along an axis with Outside Dimensions ($OD_1, OD_2, \dots, OD_n$) and Nobi values ($N_1, N_2, \dots, N_{n-1}$):
- **Total Unfolded Length**: 
  $$L_{\text{total}} = \sum_{i=1}^{n} OD_i - \sum_{i=1}^{n-1} N_i$$
- **Exact Y-Coordinates for Double Lines of Bend $k$ (from Origin $0$)**:
  - **Lower Line (Line 1)** = $\left(\sum_{i=1}^{k} OD_i\right) - \left(\sum_{i=1}^{k} N_i\right)$
  - **Upper Line (Line 2)** = $\left(\sum_{i=1}^{k} OD_i\right) - \left(\sum_{i=1}^{k-1} N_i\right)$
  - **Gap between Line 1 & Line 2** = $N_k$
*Example for 3 flanges ($OD_1=22.39, OD_2=25.39, OD_3=25.00$) with $N_1=0.52, N_2=4.80$:*
- **Bend 1 (N1=0.52)**: 
  - Line 1 = $22.39 - 0.52 = 21.87\text{ mm}$
  - Line 2 = $22.39 - 0 = 22.39\text{ mm}$
- **Bend 2 (N2=4.80)**: 
  - Line 1 = $(22.39 + 25.39) - (0.52 + 4.80) = 42.46\text{ mm}$
  - Line 2 = $(22.39 + 25.39) - 0.52 = 47.26\text{ mm}$
- **Total Height**: $22.39 + 25.39 + 25.00 - 0.52 - 4.80 = 67.46\text{ mm}$

**Mapping to schema fields**: `Line 1 (lower)` = `outer_position` (the side already accounting for the accumulated Nobi from earlier flanges), and `Line 2 (upper)` = `inner_position` (the datum line). This mapping applies to every bend `k` in a chain of ≥3 sequential flanges.

### 7. Corner Reliefs
**Only create a corner relief where two bend lines actually intersect/cross** — i.e., a bend on the X-axis meets a bend on the Y-axis at that corner. Do NOT create a relief at every rectangular corner of the flat pattern; a corner with only one bend line (or no bend line) running through it gets no relief.

1. Retract one edge by exactly material thickness (t) — prioritize longer edge
2. Create slit inward by `t + 0.2`
3. From inner point, draw diagonal slit outward to bend line intersection
4. **Offset rules**:
   - SS material, t ≤ 3.2mm → offset = 3.0mm
   - All other cases → offset = 6.0mm

## 8. Dimensions
- **Always use Outside Dimensions (OD) in the flat pattern output**
- If drawing specifies Inside Dimension (ID), convert to OD by offsetting outward by thickness
- **ID → OD offset calculation for non-90° bends**:
  - Formula: `Offset = t * tan((180° - Angle) / 2)` (rounded to 2 decimal places).
  - Example: For a 135° bend with `t = 3`, `Offset = 3 * tan(22.5°) = 1.24` mm. 
  - Therefore, `OD = ID + 1.24` (e.g., ID 275 → OD 276.24, ID 50 → OD 51.24).
- **If the dimension is already measured at the outside**: no conversion needed

### 9. Holes & Formed Features

**Two-step cross-check (mandatory for threaded holes):**
1. **OCR read** the symbol carefully (M3, M4, M5, M6, M8, M10, M12). Note: handwritten digits like `6` vs `8` or `5` vs `8` are easy to confuse.
2. **Pilot hole table** — standard values to write into the JSON `diameter` field:

| Thread | Pilot hole Ø | Pilot radius |
|--------|--------------|--------------|
| M5     | 4.2 mm       | 2.1 mm       |
| M6     | 5.0 mm       | 2.5 mm       |
| M8     | 6.8 mm       | 3.4 mm       |
| M10    | 8.5 mm       | 4.25 mm      |

For thread sizes not listed above (M3, M4, M12), consult `references/pilot-holes.md` for the standard pilot hole diameter and radius — do not guess or leave the value blank.

If the OCR result does not match the pilot hole that the reference table would predict for the same thread, re-read the drawing before finalizing.

**Output rules:**
- For countersink, dimple, or formed holes: extract ONLY the smallest pilot hole diameter.
- For threaded holes (M*): the `diameter` field MUST be the pilot hole diameter (per the table above) — this is what the laser cutter will drill.
- **Pilot hole lookup**: For threaded holes (M*), consult `references/pilot-holes.md` for standard pilot diameters.
- Hole types:
  - `round`: circular (e.g., Ø5.5, M4) — use diameter field
  - `slot`: elongated/stadium — extract hole_length, hole_width, hole_radius (default R=0)
  - `rect`: square/rectangular hole
- Threaded holes (start with `M`): set `is_thread=true`, diameter = pilot hole
- For each hole:
  - `dist_from_edge_X`: distance from reference edge
  - `reference_side_X`: `'left'` or `'right'`
  - `y_positions`: list of Y coordinates from bottom up
- Flag if diameter or position is missing

### 10. Kegaki / Scribe Lines
- Record `[x, y]` start and end coordinates in mm

### 11. Pierce / Piasu Points
- Record `[x, y]` position in mm
- Set `throughhole=true` if noted

### 12. Data Symbol
- Set `has_data_symbol=true` if 'DATA' symbol present (DXF already available)

### 13. Missing Dimensions
- Set `has_missing_dimensions=true` if any required dimensions absent

## Master Algorithm — Flat Pattern Coordinate Mapping

For a U-channel / C-channel with side flanges (X-axis) and a bottom tab (Y-axis):

- Design (3D) dimensions: Left flange `A`, Body `B`, Right flange `C`, Nobi X = `N_x`
- Design (3D) dimensions: Bottom tab `D`, Main body `E`, Notch gap `G`, Nobi Y = `N_y`

| Element | Flat dimension | Start coordinate | End coordinate |
| :--- | :--- | :--- | :--- |
| **Total flat width (X)** | `W_flat = A + B + C - 2*N_x` | `X = 0` | `X = W_flat` |
| **Total flat height (Y)** | `H_flat = D + E - N_y` | `Y = 0` | `Y = H_flat` |
| **Left bend line — outer** | outer edge of left bend zone | `X = A - N_x` | across the body extent |
| **Left bend line — inner (datum)** | inner edge of left bend zone | `X = A` | across the body extent |
| **Right bend line — inner (datum)** | inner edge of right bend zone | `X = A + B - N_x` | across the body extent |
| **Right bend line — outer** | outer edge of right bend zone | `X = A + B` | across the body extent |
| **Bottom bend line — outer** | outer edge of bottom bend zone | `Y = D - N_y` | across the tab extent |
| **Bottom bend line — inner (datum)** | inner edge of bottom bend zone | `Y = D` | across the tab extent |
| **Step notch cut** | bottom edge of the main body | `Y = (D - N_y) + G` | from `X = 0` to `X = X_tab` |

Notes:
- "Datum" for each bend is the `inner_position` line (the one adjacent to the body interior). The 3D dimension line is preserved on that line.
- "Outer" line is the one offset into the flange by exactly `Nobi`.
- `L_body` (= `B` for X-axis, `E` for Y-axis) is **never** reduced by Nobi.

## Pre-Output Checklist (mandatory)

Before emitting JSON / DXF, verify all of the following:

1. [ ] **Nobi source confirmed** — Recorded the origin of `nobi` for every bend: handwritten on drawing, reference table, or default-fallback (OD-only). When using the reference table, the material + thickness + bend length + angle must match.
2. [ ] **Body dimension `B` untouched** — `B` in the flat pattern equals the design body dimension. It must not be reduced by Nobi.
3. [ ] **Hole centers preserved** — Hole coordinates in the flat pattern are at the same offset from the body reference edge as in the 3D drawing.
4. [ ] **Pilot hole diameter verified** — For threaded holes (M5 / M6 / M8 / M10), the `diameter` field is the pilot hole diameter per the table in section 9, and the OCR'd thread size matches the table value.
5. [ ] **Two parallel bend lines** — Each bend in `bend_lines` has both `inner_position` and `outer_position`, separated by exactly `nobi`.
6. [ ] **No dimension annotations on flat pattern** — The DXF output contains outline geometry only; dimensions are kept as JSON reference data, never drawn on the flat pattern itself.

## Output Contract

**Output rules:**
- JSON output INCLUDES dimensions (for reference / internal use)
- DXF / actual drawing output: geometry only, **NO dimensions written on the flat pattern**
- The flat pattern is a pure outline; dimensions stay as reference data in JSON

Return ONLY JSON matching this schema:

```json
{
  "drawing_code": "string",
  "material": "string",
  "thickness": number,
  "unfolded_length": number,
  "raw_nobi_formula": "string",
  "width": number,
  "fillet_radius": number,
  "internal_fillets": [
    {
      "x": number,
      "y": number,
      "radius": number
    }
  ],
  "corner_chamfer": number | null,
  "bend_lines": [
    {
      "axis": "x" | "y",
      "inner_position": number,
      "outer_position": number,
      "nobi": number | null,
      "angle": number,
      "is_flagged": boolean
    }
  ],
  "corner_reliefs": [
    {
      "x": number,
      "y": number,
      "offset": number
    }
  ],
  "holes": [
    {
      "type": "round" | "slot" | "rect",
      "diameter": number | null,
      "hole_length": number | null,
      "hole_width": number | null,
      "hole_radius": number | null,
      "is_thread": boolean,
      "dist_from_edge_X": number | null,
      "reference_side_X": "left" | "right" | null,
      "y_positions": number[],
      "is_missing_diameter": boolean,
      "is_missing_position": boolean
    }
  ],
  "kegaki_lines": [
    {
      "start": [number, number],
      "end": [number, number]
    }
  ],
  "piasus": [
    {
      "position": [number, number],
      "throughhole": boolean
    }
  ],
  "has_data_symbol": boolean,
  "has_missing_dimensions": boolean,
  "j_symbol_present": boolean | null
}
```

## Failure Handling
- **Unreadable elements**: Note in output with `null` values and appropriate flags
- **Ambiguous dimensions**: Do NOT default `fillet_radius`. If no R-callout is found on an outer corner, set `fillet_radius=0` (sharp) and note the ambiguity. Only use the reference tables (`nobi-standards.md`, `pilot-holes.md`) for values that have an official standard fallback.
- **No formula visible**: Set `unfolded_length=null` and `has_missing_dimensions=true`
- **Pre-screen fail**: Return empty JSON with only `skipped: true, reason: "..."`

## Examples

**Input**: Sheet metal drawing with barcode "040007", material SUS304, t=1.2, unfolded formula "50+25+30+2.4=107.4", width 40, Ø5.5 hole at left edge, y=15mm

**Output**:
```json
{
  "drawing_code": "040007",
  "material": "SUS304",
  "thickness": 1.2,
  "unfolded_length": 107.4,
  "raw_nobi_formula": "50+25+30+2.4",
  "width": 40,
  "fillet_radius": 0,
  "internal_fillets": [],
  "corner_chamfer": null,
  "bend_lines": [],
  "corner_reliefs": [],
  "holes": [{
    "type": "round",
    "diameter": 5.5,
    "hole_length": null,
    "hole_width": null,
    "hole_radius": null,
    "is_thread": false,
    "dist_from_edge_X": 10,
    "reference_side_X": "left",
    "y_positions": [15],
    "is_missing_diameter": false,
    "is_missing_position": false
  }],
  "kegaki_lines": [],
  "piasus": [],
  "has_data_symbol": false,
  "has_missing_dimensions": false
}
```

## References
- `references/nobi-standards.md` - Bend allowance tables by material, thickness, and bend length
- `references/pilot-holes.md` - Metric thread pilot holes and drilling/piercing capability

## Worked Example — Multi-Direction Multi-Angle Bends (PDF 520717-16)

**Source:** 4-page PDF for a sheet metal bracket

### Reading across pages
| Page | Content | Value |
|------|---------|-------|
| Page 1 (CAD依頼書) | 作業No / material / thickness | `26-041919` / `SPHC(酸洗)` / `T3.2` |
| Page 4 (drawing) | Barcode / title block | `*041919*` / `SUS304` / `t=3` |
| **Final (apply correction)** | Material / thickness | `SUS304` / `t=3` |

### Bends identified (mixed angles, both axes)
| Bend | Axis | Angle | inner_position | outer_position | Nobi |
|------|------|-------|----------------|----------------|------|
| Left vertical | X | 90° | x = 0 | x = 0 | (no source → flagged) |
| Right vertical | X | 90° | x = 276.24 | x = 276.24 | (no source → flagged) |
| Bottom flap | Y | 135° | y = 20.24 | y = 18.53 | **1.71** (handwritten `-1.71` on drawing) |

The two 90° bends have no handwritten Nobi and the reference table value is not available in this example, so the `inner_position` and `outer_position` collapse onto the OD line and the bend is flagged.

### ID → OD conversion (for this geometry, t=3)
- X-axis: `275 (ID) → 276.24 (OD)`
- Y-axis: `19 (ID) → 20.24 (OD)`
- Both offsets = 1.24 (depends on angle + thickness combo)

### J symbol check
- Drawing has circled "J" near barcode → vendor performs the bend, but Nobi is still extracted using the priority in section "J Symbol (Bend Marker)".
- In this example: the 135° bend has `-1.71` handwritten on the drawing, so it is used directly. The two 90° bends have no handwritten value and the table value is not available here, so they fall back to OD-only (flagged).

### Holes & features
- 2× slots: `6.6 × ~10` at y=49 (top edge) with 120mm spacing
- 1× slot: `6.6 × ~10` at x=15 from left
- 2× C3 chamfers on top corners
- Inside fillet R 4 R 2
- Bend lines marked as brown circles (90°) and brown (135°)

### Expected JSON
```json
{
  "drawing_code": "041919",
  "material": "SUS304",
  "thickness": 3.0,
  "unfolded_length": 290.56,
  "raw_nobi_formula": "Manual: 90°×2 + 135°(-1.71) per tinh_toan",
  "width": 20.24,
  "fillet_radius": 0,
  "internal_fillets": [
    {"x": null, "y": null, "radius": 4},
    {"x": null, "y": null, "radius": 2}
  ],
  "corner_chamfer": 3.0,
  "bend_lines": [
    {"axis": "x", "inner_position": 0,     "outer_position": 0,     "nobi": null,  "angle": 90,  "is_flagged": true},
    {"axis": "x", "inner_position": 276.24,"outer_position": 276.24,"nobi": null,  "angle": 90,  "is_flagged": true},
    {"axis": "y", "inner_position": 20.24, "outer_position": 18.53, "nobi": 1.71,  "angle": 135, "is_flagged": false}
  ],
  "corner_reliefs": [
    {"x": 0,      "y": 0,    "offset": 6.0},
    {"x": 276.24, "y": 0,    "offset": 6.0},
    {"x": 276.24, "y": 20.24,"offset": 6.0}
  ],
  "holes": [
    {"type": "slot", "diameter": null, "hole_length": 10, "hole_width": 6.6, "hole_radius": 3.3,
     "is_thread": false, "dist_from_edge_X": 15, "reference_side_X": "left",
     "y_positions": [49], "is_missing_diameter": false, "is_missing_position": false},
    {"type": "slot", "diameter": null, "hole_length": 10, "hole_width": 6.6, "hole_radius": 3.3,
     "is_thread": false, "dist_from_edge_X": 120, "reference_side_X": "left",
     "y_positions": [49], "is_missing_diameter": false, "is_missing_position": false}
  ],
  "kegaki_lines": [],
  "piasus": [],
  "has_data_symbol": false,
  "has_missing_dimensions": false,
  "j_symbol_present": true
}
```

**Note:** When this is exported to DXF, the flat pattern contains only the outline geometry — no dimension annotations.

**Note on `internal_fillets` in this example:** The source description only states "Inside fillet R4 R2" without giving explicit `(x, y)` positions, so the two entries above use `x: null, y: null` as placeholders — in a real run, the agent MUST read the actual vertex coordinates for these two internal corners off the drawing and fill them in; do not leave them null when the drawing shows the position.
