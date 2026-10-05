# FACE_CREATION_BEND_EVIDENCE — V4.28 topology anti-overclassification gate

**Approved:** 2026-10-05 from calibration/audit job `521005-02`.

## Purpose

Prevent over-classifying a complex 2D contour as multiple formed faces. This module adds no Nobi, material, thread, tolerance, or DATA/PDF numeric rule. It is loaded for `BEND`, `MULTI_FACE`, and `UNKNOWN` mode candidates before final FACE_GRAPH closure.

## 1. FACE_CREATION_REQUIRES_BEND_EVIDENCE

A contour direction change, slope, step, recess, protrusion, radius, chamfer, or silhouette break **does not by itself prove a bend or a new material face**.

Create a new FACE/BEND adjacency only when source evidence proves material changes plane/orientation. Acceptable evidence includes one or more mutually consistent items such as:

- explicit bend/J/Nobi callout attached to the transition;
- section/side/detail geometry that proves two adjacent material planes;
- thickness representation or formed-edge representation that proves a fold;
- projection/witness relationships that uniquely establish adjacent faces and a shared bend edge;
- customer DATA physical geometry when DATA is authoritative for source geometry;
- another explicit source cue that uniquely proves a formed transition.

Color, contour angle, slope, a step-looking silhouette, visual familiarity, bbox, or resemblance to a known U/Z/box profile is not enough.

## 2. SAME_FACE_FIRST candidate test

Before splitting a visible profile into multiple faces, first test whether the source can be represented as one planar face with a complex contour while preserving all proved witnesses, feature ownership, sections/details, and formed constraints.

- If the same-face model satisfies the source and no independent bend evidence exists at the contour break, retain one FACE.
- Split only where positive bend evidence requires it.
- If both same-face and multi-face models remain materially possible after source exhaustion, keep the topology unresolved; do not choose by confidence or visual familiarity.

This is an anti-overclassification gate, not a rule that all sloped/stepped geometry is flat.

## 3. LOCAL_BEND_DOMAIN_BEFORE_UNFOLD

After a bend is proved, lock the exact material domain that crosses it **before** using the bend in unfold arithmetic.

- A local flange may occupy only a sub-span of the part width/height.
- Do not extend the bend pair through neighboring material that remains on the main face.
- Bend line length/domain must come from the actual shared edge/material crossing, not from overall part bbox.
- Existing `BEND_DOMAIN_LOCKED` and material-void clipping remain mandatory downstream.

## 4. THEORETICAL_SHARP_CLOSURE_FOR_R_CONTOURS

When an overall or summary dimension refers to the theoretical sharp intersection of two source-proved straight edges that are physically trimmed by an explicit radius/chamfer, do not reject the source/reference merely because the physical bbox is smaller.

1. Preserve the explicit R/C physical contour.
2. Reconstruct the theoretical sharp intersection only when the source witnesses/extension geometry prove that semantic.
3. Compare the theoretical overall to the theoretical sharp point and the physical bbox to the actual R/C contour separately.
4. Never replace the physical R/C with a sharp corner solely to make bbox equal the theoretical dimension.

## 5. TRAIN_REFERENCE boundary

A sample/approved DXF may diagnose whether the PDF-derived topology candidate was over-classified, but it does not supply hidden construction dimensions for a new job. Compare physical geometry, then return to PDF/source evidence to identify the general cause.

## 6. Required validation record

For every proposed face boundary retain:

`boundary_id | source evidence | SAME_FACE_FIRST result | bend_proved YES/NO/UNKNOWN | shared-edge/material-domain | resulting FACE ids`

Production PASS is forbidden when a created FACE lacks positive bend evidence, or when a proved local bend has been expanded to a larger bbox-derived domain without source support.

## 7. 521005-02 regression intent

- `26-057867`: control case — one source-proved bend; simple full-width flange remains valid.
- `26-057869` / `26-057870`: local flange only; approved/reference bend pair spans 555 mm, not the whole 1025 mm part width. Complex neighboring contour remains on the main face.
- `26-057871` / `26-057872`: sloped outer contour is part of the same planar face; only the proved bottom flange becomes a new face. The R10-trimmed physical bbox is smaller than the theoretical-sharp overall, so bbox mismatch alone is not a source/reference error.

Job-specific coordinates are regression evidence only and must never become generic construction coordinates.
