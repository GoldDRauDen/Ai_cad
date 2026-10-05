# TrainAiCad Feature Census — production routing gate

## Purpose

This file classifies what is present in the actual source drawing before specialized CAD rules are loaded. It adds **no engineering formula** and does not replace source evidence, the core modules, or any routed feature module.

The census is mandatory for every repo-direct production job.

## Required order

1. Load the always-on core and source-classification files declared in `ROUTER.yaml`.
2. If any DXF participates as DATA/reference/audit source, apply `references/DXF_PHYSICAL_CURVE_DECODING.md` first and build a physical-curve view of all relevant `POLYLINE`/`LWPOLYLINE` segments, including bulges and closed final->first segments.
3. Inspect every relevant source page/view/section/detail and, when supplied, the corresponding customer DATA.
4. Run `references/SOURCE_MANUFACTURING_NOTE_CENSUS.md` and account for every production-affecting printed/handwritten/revision instruction before allowing an affected feature family to be `NO`.
5. Record a preliminary census using only `YES`, `NO`, or `UNKNOWN`.
6. Load every route whose state is `YES` **or** `UNKNOWN`.
7. Re-check the source with the routed rules available.
8. Produce a final census and run source-note completeness + source-family completeness + cross-feature validation before DXF export.

**UNKNOWN is never equivalent to NO.** A suspected feature with unresolved identity, scope, datum, quantity, process, ownership, or source-instruction mapping must route to the relevant module.

## Evidence required before NO

Do not mark a family NO merely because a keyword was not found. Check, as applicable:

- real contour and internal geometry;
- dimension witnesses, leaders and symbols;
- Japanese/English notes and handwritten/red revisions;
- the V4.29 source-manufacturing-note ledger, including unresolved local instructions even when the geometry is small or edge-open;
- section/detail/development views;
- barcode/code/material/thickness blocks, including process symbols immediately associated with a barcode;
- crossed-out/cancelled callouts;
- customer DATA entities, layers, views and physical duplicates;
- decoded physical curve type for DXF `POLYLINE`/`LWPOLYLINE` segments, including nonzero bulge ARC geometry rather than endpoint chords;
- source-view host face and formed/unfolded relationships.

Color, linetype, proximity, symmetry, code adjacency, endpoint/chord appearance, mechanical usefulness, or model confidence alone never proves a feature family. In particular, equal X/Y offsets between two polyline vertices do not prove a chamfer when the source segment has nonzero bulge.

## V4.29 source-manufacturing-note gate before family = NO

Apply `references/SOURCE_MANUFACTURING_NOTE_CENSUS.md`.

- Every production-affecting printed/handwritten/revision note must resolve to a scoped manufacturing family/status before production PASS.
- A note that proves a family and scope makes that family `YES`.
- If a note plausibly indicates a known manufacturing family but its scope/quantity/host/value/location/direction is not fully resolved, the relevant family is at least `UNKNOWN`; it must not be prematurely classified `NO`.
- A custom `スリット` / `SLIT` instruction routes `SLIT_RELIEF`. Do not create that custom slit from bend geometry alone, and do not hardcode its value or position from another drawing/reference.
- `スリット 8` is evidence for the scoped drawing's slit value `8`; it is not a universal size rule and does not authorize assuming a bend-center location.
- Existing separately-triggered relief families remain governed by their own routed mechanisms.

## V4.27 weld-cue gate before KEGAKI = NO

When a reversed-e mark is proved immediately above a barcode, record the scoped process evidence as `REVERSED_E_ABOVE_BARCODE -> WELD_REQUIRED_CUE` for that barcode's code/detail cluster only.

- `WELD_REQUIRED_CUE` is process evidence, not a new routable feature family and not geometric KEGAKI by itself.
- If the scoped cluster contains a RIB / gusset / support or other welded child that cannot self-locate, `KEGAKI` must be `YES` when the locating marks are source-proved, otherwise at least `UNKNOWN` until locating/contact function, host face, datum and quantity have been checked. It must not be prematurely classified `NO`.
- A specific KEGAKI instruction independently makes `KEGAKI = YES` even when the reversed-e barcode cue is absent.
- If neither the reversed-e barcode cue nor a specific KEGAKI instruction exists for the scoped code/cluster, do not infer welding or create KEGAKI solely because a secondary RIB / gusset / support exists.
- Do not copy the cue across adjacent barcodes/codes, and do not copy a full child contour into KEGAKI without proved locating/contact evidence.

## Census schema

Record at minimum:

```yaml
source_mode: PDF_ONLY | PDF_DATA_RAW | TRAIN_REFERENCE | DIRECT_EXISTING_DXF_AUDIT
part_mode: FLAT_NO_BEND | BEND | MULTI_FACE | UNKNOWN
source_manufacturing_notes:
  - {note_text: "...", code_scope: "...", candidate_family: "...", resolution: ROUTED|CANCELLED|IRRELEVANT_TO_MANUFACTURING|UNRESOLVED}
features:
  HOLE: {state: YES|NO|UNKNOWN, evidence: []}
  TAP: {state: YES|NO|UNKNOWN, evidence: []}
  SLOT_STRAIGHT: {state: YES|NO|UNKNOWN, evidence: []}
  CURVED_SLOT: {state: YES|NO|UNKNOWN, evidence: []}
  KEGAKI: {state: YES|NO|UNKNOWN, evidence: []}
  PIASU: {state: YES|NO|UNKNOWN, evidence: []}
  SLIT_RELIEF: {state: YES|NO|UNKNOWN, evidence: []}
  RIB: {state: YES|NO|UNKNOWN, evidence: []}
  CHAMFER_FILLET: {state: YES|NO|UNKNOWN, evidence: []}
  HEMMING: {state: YES|NO|UNKNOWN, evidence: []}
  Z_BEND: {state: YES|NO|UNKNOWN, evidence: []}
  ACUTE_BEND_LT85: {state: YES|NO|UNKNOWN, evidence: []}
  BOXMET: {state: YES|NO|UNKNOWN, evidence: []}
  MATERIAL_RULES: {state: YES|NO|UNKNOWN, evidence: []}
  NOBI: {state: YES|NO|UNKNOWN, evidence: []}
  REVISION_CANCELLATION: {state: YES|NO|UNKNOWN, evidence: []}
```

Evidence items should identify source page/view/region or DATA entity group and the observed cue. Do not invent evidence IDs.

## Hard stop

If a source-supported family is discovered after routing but no route exists, emit `ROUTING_COVERAGE_GAP`. Do not silently treat it as generic CUT and do not continue to production PASS until the route is resolved.

If a relevant DXF polyline segment has nonzero bulge but its physical curve has not been decoded/accounted, the census is incomplete and production PASS is forbidden.

If a production-affecting source note remains `UNRESOLVED` while its plausible family is marked `NO`, the census is invalid; route that family as `UNKNOWN` and continue under local FLAG policy.

## Final completeness gate

Before production export:

`SOURCE MANUFACTURING NOTES -> SOURCE ACTIVE FAMILIES -> FINAL CENSUS -> LOADED ROUTES -> CANONICAL FAMILIES -> SERIALIZED OUTPUT`

must close without an unexplained missing note/family. A valid DXF file or correct bounding box does not compensate for a missing manufacturing instruction, missing manufacturing family, or a source ARC flattened into its chord.
