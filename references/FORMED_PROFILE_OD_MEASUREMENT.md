# FORMED_PROFILE_OD_MEASUREMENT — V4.32 formed-profile outside-length contract

**Approved:** 2026-10-07 from calibration/audit job `521006-18`.  
**Scope:** bent/multi-face parts where flat arithmetic needs outside face lengths that are not already unambiguously supplied as usable OD values.

## 1. Purpose

A formed/profile/side view can be a **measurement construction** for the real bent part. It is used to reconstruct the material planes and measure the actual outside dimensions required for unfold.

Do not serialize a measurement construction as CUT merely because it is present in a source/reference DXF.

## 2. Required order

When applicable:

```text
SOURCE FORMED VIEWS
-> FACE_GRAPH + BEND_ATTACHMENT_EDGE_LOCKED
-> source dimensions/witness semantics
-> construct actual formed faces and bend transitions
-> establish outside material envelope
-> measure OD_actual for each ordered face contribution
-> assign each thickness/ID->OD term to exactly one owner
-> apply Nobi
-> unfold
-> fold-back / source reprojection
```

The general flat equation remains:

`L_flat = sum(OD_actual) - sum(Nobi)`

but the `OD_actual` terms must be physically proved.

## 3. Measuring OD_actual

Measure along the owning face direction between the physical source-defined free/boundary edge and the applicable outside bend envelope/tangent/formed boundary.

Do not substitute:

- a bbox extent;
- an inside dimension as if it were already outside;
- a theoretical sharp intersection when the physical outside envelope is the controlled endpoint;
- a reference/sample coordinate for a source-missing OD.

For non-90-degree bends, retain existing routed ID->OD and acute-bend rules. This module controls **ownership and measurement meaning**: offsets/thickness terms must land on the correct face contribution and must not be consumed twice.

## 4. THICKNESS_SINGLE_USE remains mandatory

If a thickness or ID->OD offset is already represented in a constructed outside extent, do not add it again during sequential flat arithmetic.

For every contribution retain:

`face_id | source witnesses | ID/OD semantic | thickness/offset owner | OD_actual | Nobi transition`.

## 5. Measurement view versus manufacturing view

Use explicit semantic states when needed:

- `SOURCE_VIEW`
- `MEASUREMENT_CONSTRUCTION_VIEW`
- `MANUFACTURING_GEOMETRY`

A measurement construction may support topology/OD/fold-back QA but does not become production geometry automatically.

## 6. Ambiguity and reference boundary

If source geometry cannot uniquely establish the outside envelope or the required OD term, keep the affected bend/flat locally unresolved. An approved/reference DXF may diagnose an AI error after comparison, but it cannot silently supply a missing parameter for a new drawing.

## 7. Regression intent

`521006-18` provides approved audit facts for the mechanism:

- `058653`: source/profile reconstruction requires actual outside contributions before Nobi; directly summing the apparent inside/formed numbers produces a short flat.
- `058655`: the same error occurs on a mixed 155-degree/90-degree chain.
- `058654`: customer-confirmation-pending geometry remains unresolved and must not be reverse-fit from the sample.

The numeric regression values are calibration assertions only, never construction values for another drawing.
