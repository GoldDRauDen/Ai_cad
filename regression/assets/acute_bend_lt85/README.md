# Acute bend <85° regression assets

These assets support the directly approved V4.15 outside-OD construction.

## Provenance

Original user-supplied calibration evidence:
- `HD.dxf` SHA256: `0753cd133e639491eb17b263041f0d090e80db7591a8cd77736cd775bfa19311`
- `TEST.dxf` SHA256: `c55790bad2897f0e5040f4a96fee0a92e902acf5012cae481d4615c9c010ff73`

`ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf` is a compact normalization of the exact physical formed geometry from the approved TEST case. It intentionally uses LINE packaging for both faces; physical geometry, not raw entity count, controls the regression.

`ACUTE_BEND_LT85_OD_PROOF.dxf` is non-production proof geometry generated from the approved method and must never be used as a hidden dimension source.

`ACUTE_BEND_LT85_CONSTRUCTION.svg` is the human-readable construction diagram. The executable source-to-result check is `regression/tools/check_acute_bend_lt85.py`.
