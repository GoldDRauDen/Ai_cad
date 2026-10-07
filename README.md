# TrainAiCad

TrainAiCad is a user-approved sheet-metal CAD production rule repository. It is **not an automatic training store** and historical files are not production authority.

For any AI/agent starting a CAD job, **START HERE: `AI_BOOTSTRAP.md`**.

A concise request such as `E2E` or `Read TrainAiCad and do E2E` means: bootstrap from the current repo, read the current `AI_ENTRYPOINT.md` + Router, then execute the repo-direct production flow to its executable limit.

The agent must actually have access to this repo and the required source/CAD tools; otherwise it must report the concrete blocker rather than pretend the repo was read.

For ChatGPT Web Projects, use the concise pointer template in `PROJECT_INSTRUCTIONS_GPT_WEB.md`; do not copy the engineering rules into Project Instructions.

## Architecture

```text
AI_BOOTSTRAP
    |
    +-- AI_ENTRYPOINT
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
