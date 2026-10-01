# TrainAiCad Feature Census — production routing gate

## Purpose

This file classifies what is present in the actual source drawing before specialized CAD rules are loaded. It adds **no engineering formula** and does not replace source evidence, the core modules, or any routed feature module.

The census is mandatory for every repo-direct production job.

## Required order

1. Load the always-on core and source-classification files declared in `ROUTER.yaml`.
2. Inspect every relevant source page/view/section/detail and, when supplied, the corresponding customer DATA.
3. Record a preliminary census using only `YES`, `NO`, or `UNKNOWN`.
4. Load every route whose state is `YES` **or** `UNKNOWN`.
5. Re-check the source with the routed rules available.
6. Produce a final census and run source-family completeness + cross-feature validation before DXF export.

**UNKNOWN is never equivalent to NO.** A suspected feature with unresolved identity, scope, datum, quantity, process, or ownership must route to the relevant module.

## Evidence required before NO

Do not mark a family NO merely because a keyword was not found. Check, as applicable:

- real contour and internal geometry;
- dimension witnesses, leaders and symbols;
- Japanese/English notes and handwritten/red revisions;
- section/detail/development views;
- barcode/code/material/thickness blocks;
- crossed-out/cancelled callouts;
- customer DATA entities, layers, views and physical duplicates;
- source-view host face and formed/unfolded relationships.

Color, linetype, proximity, symmetry, code adjacency, or model confidence alone never proves a feature family.

## Census schema

Record at minimum:

```yaml
source_mode: PDF_ONLY | PDF_DATA_RAW | TRAIN_REFERENCE | DIRECT_EXISTING_DXF_AUDIT
part_mode: FLAT_NO_BEND | BEND | MULTI_FACE | UNKNOWN
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

## Final completeness gate

Before production export:

`SOURCE ACTIVE FAMILIES -> FINAL CENSUS -> LOADED ROUTES -> CANONICAL FAMILIES -> SERIALIZED OUTPUT`

must close without an unexplained missing family. A valid DXF file or correct bounding box does not compensate for a missing manufacturing family.
