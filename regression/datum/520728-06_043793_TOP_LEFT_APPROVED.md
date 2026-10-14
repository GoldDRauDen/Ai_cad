# Approved regression — 520728-06 / 043793: source-origin and axis direction (V4.10)

**Direct user approval:** 2026-09-26. This is an independently approved semantic rule and a self-contained job-specific regression, not a license to infer dimensions from DXF or from conversational history. Source: original PDF page 4 and the user's explanation of the drawing's absolute datum; corrected reference DXF was used only after interpreting that PDF.

## PDF-first source evidence

- Drawing code: `043793`. Three separate `Ø7` hole centers are on one proven physical row.
- The drawing's **absolute coordinate origin is the actual top-left part corner** in the relevant orthographic drawing, NOT the bottom-left origin normally selected for DXF export.
- The part height is explicitly `H=138 mm` from that same top/bottom edge pair.
- The source ordinate is `Y_source=-30 mm`, with source positive Y **up**; physically the row lies 30 mm below the upper edge.
- Local DXF frame for this regression has positive Y up and zero Y at the same part's physical bottom edge. Therefore the source top-left datum is located at CAD `Y0_cad=138 mm`; the aligned source Y positive is `sy=+1`.

```
Y_cad = Y0_cad + sy * Y_source
      = 138 + (+1)*(-30)
      = 108 mm
```

**Required result:** ALL THREE independently traced Ø7 centers have `Y_cad=108 mm`. Wrong previous reading `Y_cad=88 mm` MUST fail; copying signed `-30` directly to target CAD also fails. This regression does not provide the X values; X positions require independent source-X origin, extension-line identity and dimension paths.

## Generalizable rule — not job-specific coordinates

For EACH orthographic/flat/formed source view with absolute/ordinate callouts:

1. Prove the REAL source origin's physical material edge/feature and positive X/Y directions from the drawing, not the PDF page margins or customary CAD convention.
2. Prove the physical source-origin location in target CAD and the target CAD positive axes. With axes physically aligned but possibly reversed, `X_cad=X0_cad+sx*X_source` and `Y_cad=Y0_cad+sy*Y_source`, `sx,sy=±1`. Mirror/rotation or X/Y swaps require separately proved transforms, not the simple aligned-axis formula.
3. For a proven top-left source origin and bottom-left CAD origin on the SAME part, if source +Y **up**, an ordinate `-d` gives `H-d`; if source +Y **down**, ordinate `+d` also gives `H-d`. The source number and its SIGN change with the axis convention even though the physical point is the same.
4. Record for each feature family: view/face ID; source origin physical entity; source X/Y directions; signed source values; CAD origin; explicit source→CAD transform; any further Section 4.2.7 face→global-flat transform; independent extent closure when available.
5. Do not invent the source datum or take an unknown `H` from a pixel bbox. Unproved origin/axis means FLAG and no production PASS. A reference DXF confirms an independently proven PDF interpretation; it may not replace missing PDF coordinates.

## Executable synthetic assertions

`tools/datum_coordinates.py` offers an OPTIONAL pure signed-ordinate transform after the upstream drawing has proved origin and axis sign; it does NOT discover origin from an image.

`tests/test_datum_coordinates.py` asserts all 043793 Y results, negative/positive axis variants and invalid/incomplete source frame rejection. These synthetic tests validate arithmetic only. Production PASS still requires actual PDF evidence and Section 5 manufacturing validation.

**Approval scope:** does not resolve customer-pending Z bend lengths 043796, 2-Ø? 043797 or 165° Nobi 043799. V4.9 single labeled top-to-bottom composite output remains default. V4.9 and earlier immutable skill versions remain untouched.
