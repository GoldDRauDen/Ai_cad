# TrainAiCad

TrainAiCad is a user-approved sheet-metal CAD production rule repository. It is **not an automatic training store** and historical files are not production authority.

For any AI starting a CAD job:

1. Read `AI_ENTRYPOINT.md`.
2. Load the always-on files from `skills/lispcad/router/ROUTER.yaml`.
3. Inspect the drawing and complete `skills/lispcad/router/FEATURE_CENSUS.md`.
4. Load only the mode/feature/reference routes whose state is `YES` or `UNKNOWN`.
5. Run cross-feature validation, canonical geometry QA, DXF export and saved-DXF read-back.

## Architecture

```text
AI_ENTRYPOINT
    |
    +-- core/                    always-on small rule set
    +-- router/
    |     FEATURE_CENSUS.md      what is present?
    |     ROUTER.yaml            what must be loaded?
    |     RULE_COVERAGE.yaml     where approved release rules live
    |
    +-- modes/                   flat / bend-unfold
    +-- features/                hole, tap, slot, kegaki, slit, rib...
    +-- references/              material, Nobi, source/DATA, FACE_GRAPH...
    +-- regression/              approved tests/evidence
    +-- portable/                complete compatibility snapshot; not default
    +-- versions/                historical archive; never normal production input
```

## Important

- `UNKNOWN` is not `NO`.
- Do not search `skills/lispcad/versions/**` for normal production.
- Do not read the full portable skill unless diagnosing a router coverage gap or explicitly auditing portability.
- New engineering lessons require direct user approval before production promotion.
- Production CAD is repo-direct by default.

The active release number and load order belong only in `AI_ENTRYPOINT.md` and router files, not in this README.
