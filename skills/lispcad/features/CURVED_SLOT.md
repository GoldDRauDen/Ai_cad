# LISPCAD Feature — Curved / circular-arc slot

**V4.20 approved.**

Use when the slot center path is a circular arc rather than a straight stadium.

If source proves centerline radius `Rc`, slot width `W` and sweep `theta`:
- `Rout = Rc + W/2`
- `Rin = Rc - W/2`
- `Rcap = W/2`

Final boundary is one outer arc + one tangent end cap + the inner arc in reverse + the second tangent end cap. Exact ARC geometry or exact closed bulged LWPOLYLINE is acceptable.

**Hard gate:** final manufacturing feature is exactly ONE closed internal CUT contour.

FAIL on slot centerline/helper circle in CUT, duplicate/overlapping arcs, second lens-shaped loop, crossing arcs, open endpoints or coincident redundant toolpaths.

Raw customer DATA may contain noisy/exploded/projected geometry; clean it to the one physical slot while preserving DATA provenance and PDF-controlled parameters.

Regression 056691/056692: W6, Rc23.4, sweep 60° -> Rout26.4, Rin20.4, end caps R3. Lens-like overlapping output is FAIL.
