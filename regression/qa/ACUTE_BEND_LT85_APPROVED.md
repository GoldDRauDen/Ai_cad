# ACUTE_BEND_LT85 — Approved regression case

**Approval:** Direct user approval, 2026-09-28.  
**Purpose:** Prevent recurrence of acute-bend OD errors and make the method independently reproducible by another AI.

## Expected semantic path

`formed faces → real Rin/Rout → outside envelope → OD1/OD2 → Nobi → flat → double bend lines`

## TEST assertions

| Assertion | Expected |
|---|---:|
| Included angle | 75° |
| t | 3.0 mm |
| Rin | 0.6 mm |
| Rout | 3.6 mm |
| OD1 raw | 182.014217 mm |
| OD1 reported | 182.01 mm |
| OD2 raw | 49.712236 mm |
| OD2 reported | 49.71 mm |

### PASS conditions

1. The method reconstructs a rounded bend rather than a theoretical sharp intersection.
2. OD1 and OD2 are measured from the physical outside envelope.
3. Raw recomputed values agree with the approved values within floating-point/geometry representation residual strictly `<0.01 mm`.
4. The source dimensions themselves are not loosened by the `<0.01` rule.
5. The future AI can point to the construction/proof asset and explain why the two ODs are outside dimensions, not DXF-derived hidden dimensions.

### FAIL conditions

- OD is measured to the sharp intersection.
- The AI reads 182.01/49.71 from the proof DXF instead of reproducing them.
- Generic ID→OD arithmetic is substituted without reconstructing the approved acute geometry.
- Rin/Rout, thickness, bend angle, or free-edge datum are changed silently.
- The proof DXF is treated as a production part.

## Related real-job example

`520925-03 / 056135`, angle 83.66°, t4.5, approved acute-bend method:
- construct real bend radius;
- measure two outside dimensions;
- then apply handwritten Nobi 6.70;
- resulting reference-audited values were OD1 121.93 and OD2 56.90, with flat 172.13 and bend pair 115.23 / 121.93.

The 056135 numbers are **job-specific regression evidence**, not reusable coordinates.

## Reproducibility requirement for cross-AI use

The regression is not satisfied by knowing the expected OD numbers. Another AI must begin from the formed geometry in `ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf`, derive the two face strips, thickness and included angle, obtain `Rin` from the approved acute-bend method, construct the bend center by offset-line intersection, construct `Rout`, and calculate both outside dimensions by the outside-envelope equations.

Executable proof: `regression/tools/check_acute_bend_lt85.py`.

Human-readable derivation: `references/ACUTE_BEND_LT85_FROM_SOURCE.md`.

Visual construction: `regression/assets/acute_bend_lt85/ACUTE_BEND_LT85_CONSTRUCTION.svg`.

The approved OD outputs are final assertions only. Using them as inputs, reverse-fitting `Rin`, or choosing face/normal signs by minimizing answer residual is a regression FAIL.
