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
- Indicates a third-party bending company is responsible
- **If J is present**: Do NOT look up bend rules from reference tables — the vendor handles bends
- **If J is absent**: Look up bend rules from `references/nobi-standards.md`

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
- Find the handwritten unfolded length formula
- Calculate the RESULT (not just copy the formula)
- Save raw formula into `raw_nobi_formula`

### 4. Width
- Read the flat pattern width (Y-axis dimension)

### 5. Corners & Chamfers
- **Fillet radius**: Outer corner fillet (default 3.0 if unclear)
- **Chamfer**: Identify `C` values (e.g., C2.0, C3.0)

### 6. Bend Lines & Nobi
- Represent bend lines as double lines with Nobi distance between them
- Identify ALL bends: X-axis and Y-axis bends
- For Y-axis bends: record `y_position` from bottom edge
- **Standard Nobi lookup**: If no drawing Nobi provided, consult `references/nobi-standards.md` based on material and thickness
- **For non-90° bends**:
  - If nobi is provided on the drawing (e.g., handwritten `135° -1.71`): use it directly
  - If nobi is NOT provided: draw that bend separately with a 10mm gap, to be combined later
  - The 10mm gap is FIXED regardless of thickness

### 6.1 Multi-Direction / Multi-Angle Bends
Drawings may have bends in BOTH X and Y axes, with mixed angles (90° + 135°, etc.):
- Identify each bend by axis + angle + position
- Apply Nobi per bend according to the angle
- For Y-axis bends, use `y_position` measured from the bottom edge
- See "Worked Example" below

### 7. Corner Reliefs (intersection of 2 bend lines)
1. Retract one edge by exactly material thickness (t) — prioritize longer edge
2. Create slit inward by `t + 0.2`
3. From inner point, draw diagonal slit outward to bend line intersection
4. **Offset rules**:
   - SS material, t ≤ 3.2mm → offset = 3.0mm
   - All other cases → offset = 6.0mm

### 8. Dimensions
- **Always use Outside Dimensions (OD) in the flat pattern output**
- If drawing specifies Inside Dimension (ID), convert to OD by offsetting outward by thickness
- **ID → OD offset depends on the angle and thickness**:
  - For 135° bends, the offset can be calculated as: `OD = ID + offset(angle, t)`
  - Example: 90° + 135° combo with t=3 → ID 275 → OD 276.24, ID 19 → OD 20.24
  - The offset value varies per angle/thickness combination
- **If the dimension is already measured at the outside**: no conversion needed

### 9. Holes & Formed Features
- For countersink, dimple, or formed holes: extract ONLY the smallest pilot hole diameter
- **Pilot hole lookup**: For threaded holes (M*), consult `references/pilot-holes.md` for standard pilot diameters
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
  "corner_chamfer": number | null,
  "bend_lines": [
    {
      "axis": "x" | "y",
      "position": number,
      "nobi": number,
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
- **Ambiguous dimensions**: Default to standard values (fillet_radius=3.0) and note
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
  "fillet_radius": 3.0,
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
| Bend | Axis | Angle | Position | Nobi |
|------|------|-------|----------|------|
| Left vertical | X | 90° | x = 0 | (default 90° lookup) |
| Right vertical | X | 90° | x = 275 (ID) | (default 90° lookup) |
| Bottom flap | Y | 135° | y = 19 (ID) | **-1.71** (handwritten on drawing) |

### ID → OD conversion (for this geometry, t=3)
- X-axis: `275 (ID) → 276.24 (OD)`
- Y-axis: `19 (ID) → 20.24 (OD)`
- Both offsets = 1.24 (depends on angle + thickness combo)

### J symbol check
- Drawing has circled "J" near barcode → vendor handles bending
- If J were absent → would look up nobi from `references/nobi-standards.md`

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
  "fillet_radius": 3.0,
  "corner_chamfer": 3.0,
  "bend_lines": [
    {"axis": "x", "position": 0,    "nobi": null,   "angle": 90,  "is_flagged": false},
    {"axis": "x", "position": 276.24,"nobi": null,  "angle": 90,  "is_flagged": false},
    {"axis": "y", "position": 20.24, "nobi": -1.71, "angle": 135, "is_flagged": false}
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
