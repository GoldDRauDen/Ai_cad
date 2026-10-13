# Bend-tooling minimum L/Z — manufacturing WARN only
Source: `伸び下穴経路一覧.xlsx` / `旭26-9-18` rows 8–9, 17–18 (SS), 28–29, 38–39, 49 (SUS), 62, 71 (AL), 81 (Cu).

**This is a feasibility check, not a CAD dimension rule.** Look up the **already selected physical V die** for each proved bend. A leg shorter than the listed `L_min`, or a comparable Z leg shorter than a printed `Z_min`, creates **WARN only** when PDF geometry is otherwise complete, not REVIEW or re-sized CUT. The dash means the original sheet does not supply the corresponding Z value, NOT zero. Never infer unknown values from adjacent material/rows; preserve source witness and tooling evidence.

| Material family | thickness t | selected V die | L_min (mm) | Z_min (mm) |
|---|---:|---|---:|---:|
| SS | 0.5 | V8 | 7.5 | 8.5 |
| SS | 0.8 | V8 | 7.5 | 8.8 |
| SS | 1 | V8 | 7.5 | 9 |
| SS | 1.2 | V8 | 7.5 | 9.2 |
| SS | 1.5 | V8 | 7.5 | 9.5 |
| SS | 1.6 | V8 | 7.5 | 9.6 |
| SS | 2 | V12 | 8.5 | 12.1 |
| SS | 2.3 | V12 | 8.5 | 12.7 |
| SS | 3 | V12 | 8.5 | 14.6 |
| SS | 3 | V18 | 12.8 | 17.6 |
| SS | 3 | V25 | 17.8 | 21.6 |
| SS | 3.2 | V18 | 12.8 | 18 |
| SS | 3.2 | V25 | 17.8 | 22 |
| SS | 4 | V18 | 12.8 | 19.6 |
| SS | 4.5 | V25 | 17.8 | 26 |
| SS | 4.5 | V32 | 22.7 | 30 |
| SS | 4.5 | V40 | 28.4 | 34 |
| SS | 5 | V25 | 17.8 | 28 |
| SS | 5 | V32 | 22.7 | 32 |
| SS | 5 | V40 | 28.4 | 36 |
| SS | 6 | V25 | 17.8 | 30 |
| SS | 6 | V32 | 22.7 | 34 |
| SS | 6 | V40 | 28.4 | 38 |
| SS | 9 | V40 | 28.4 | 44 |
| SS | 9 | V80 | 57 | - |
| SS | 12 | V80 | 57 | - |
| SUS | 0.5 | V8 | 7.5 | 8.5 |
| SUS | 0.8 | V8 | 7.5 | 8.8 |
| SUS | 1 | V8 | 7.5 | 9 |
| SUS | 1.2 | V8 | 7.5 | 9.2 |
| SUS | 1.5 | V8 | 7.5 | 9.5 |
| SUS | 2 | V12 | 8.5 | 12.1 |
| SUS | 2 | V18 | 12.8 | 15.6 |
| SUS | 2.5 | V12 | 8.5 | 13.6 |
| SUS | 2.5 | V18 | 12.8 | 16.6 |
| SUS | 2.5 | V25 | 17.8 | 20.6 |
| SUS | 3 | V12 | 8.5 | 14.6 |
| SUS | 3 | V18 | 12.8 | 17.6 |
| SUS | 3 | V25 | 17.8 | 21.6 |
| SUS | 3 | V40 | 28.4 | 29.6 |
| SUS | 4 | V18 | 12.8 | 19.6 |
| SUS | 4 | V25 | 17.8 | 23.6 |
| SUS | 4 | V40 | 28.4 | 31.6 |
| SUS | 4.5 | V18 | 12.8 | 20.6 |
| SUS | 5 | V25 | 17.8 | 25.6 |
| SUS | 5 | V32 | 22.7 | 29.6 |
| SUS | 5 | V40 | 28.4 | 33.6 |
| SUS | 6 | V32 | 22.7 | 34 |
| SUS | 6 | V40 | 28.4 | 38 |
| SUS | 8 | V40 | 28.4 | - |
| SUS | 8 | V80 | 57 | - |
| SUS | 9 | V80 | 57 | - |
| AL | 0.8 | V8 | 7.5 | - |
| AL | 1 | V8 | 7.5 | - |
| AL | 1.5 | V8 | 7.5 | - |
| AL | 2 | V12 | 8.5 | - |
| AL | 3 | V12 | 8.5 | - |
| AL | 3 | V18 | 12.8 | - |
| AL | 3 | V25 | 17.8 | - |
| AL | 4 | V18 | 12.8 | - |
| AL | 4 | V25 | 17.8 | - |
| AL | 4 | V32 | 22.7 | - |
| AL | 4 | V40 | 27.4 | - |
| AL | 5 | V25 | 17.8 | - |
| AL | 5 | V32 | 22.7 | - |
| AL | 5 | V40 | 28.4 | - |
| AL | 6 | V25 | 17.8 | - |
| AL | 6 | V32 | 22.7 | - |
| AL | 6 | V40 | 28.4 | - |
| AL | 8 | V40 | 28.4 | - |
| AL | 8 | V80 | 57 | - |
| AL | 9 | V40 | 28.4 | - |
| AL | 9 | V80 | 57 | - |
| AL | 10 | V80 | 57 | - |
| CU | 3 | V18 | 12.8 | - |

The SS t4.5 V18 special cell is `要確認` and has no automatic Nobi application; do not promote it to the standard V25 row. SUS430 uses the SS material group for Nobi/tooling; for Laser R and hole processing it still uses SUS/他. Customer 646 uses its dedicated tooling/profile `AIKOKU_646_NOBI.md`, never fallback to this shop sheet. An explicit PDF/tooling instruction controls the selected die; don't switch dies merely because a listed L/Z minimum is violated. Source sheet feasibility notes concerning maximum width/depth remain WARN, not hard geometric redesign.

If bend length/leg ownership is unproved, that is a *geometry or source-evidence* REVIEW independently of a machine-feasibility WARN. Never calculate Nobi or min-leg checks from CAD bounding boxes instead of the locked physical bend edge.
