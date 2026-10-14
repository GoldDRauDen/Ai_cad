# TrainAiCad

TrainAiCad is a user-approved sheet-metal CAD production rule repository. It is **not an automatic training store** and historical files are not production authority.

For any AI/agent starting a CAD job, **START HERE: [SKILL.md](SKILL.md)**.
It is the single human/AI-facing workflow entry point; `AI_BOOTSTRAP.md`,
`AI_ENTRYPOINT.md`, and routed modules remain the actual production authority.

A concise request such as `E2E` or `Read TrainAiCad and do E2E` means: bootstrap from the current repo, read the current `AI_ENTRYPOINT.md` + Router, then execute the repo-direct production flow to its executable limit.

The agent must actually have access to this repo and the required source/CAD tools; otherwise it must report the concrete blocker rather than pretend the repo was read.

For ChatGPT Web Projects, use the concise pointer template in `PROJECT_INSTRUCTIONS_GPT_WEB.md`; do not copy the engineering rules into Project Instructions.

## Connect to another AI

Attach this repository (or a checkout that the AI can actually read), then say:
`Read SKILL.md from TrainAiCad and perform E2E on the supplied CAD source.`
The AI must have image/PDF inspection and code/file execution tools to create
and verify DXF; text-only AI cannot produce production CAD merely by reading rules.

To create a **single, generated portable document** containing the current
E2E process and all Router-approved modules, without maintaining a second
independent source of rules:

```sh
python tools/build_rule_bundle.py --output ../TrainAiCad_E2E_RULEPACK.md
```

The generated document is a point-in-time, read-only artifact. Source modules
and the pinned repository revision remain authoritative for CAD production.
See `SKILL.md` for the full stage contract.

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
            +-- regression/              approved tests/evidence (not universal rules)
            +-- portable/                complete compatibility snapshot; not default
            +-- versions/                CI-pinned historical snapshots; never production input
```

## Canonical E2E artifacts

Normal `python tools/export_canonical_dxf.py job.json OUT/` first checks
source-to-canonical members and composite XDATA read-back, then writes:

```text
OUT/
  geometry_json/<CODE>.json           every code, including REVIEW
  parts_dxf/<PASS_CODE>.dxf           PASS only; LINE/ARC/CIRCLE cut geometry
  <JOB>_ALL.dxf                       when all PASS
  <JOB>_ALL_REVIEW_ONLY.dxf           otherwise (all codes + warnings)
```

Individual DXFs are generated analytically from the canonical members and
reopened with XDATA/geometry checks; they contain no text, bend, marking,
points or polyline. The existing lower-level `tools/export_dxf.py` remains
only a compatibility packager. Semantic PDF/source correctness still requires
actual independent engineering QA.

## Staged, coverage-checked deterministic routing

Active engineering authority is still the Router and its approved modules.
`tools/audit_rule_coverage.py` rejects an active `core/`, `features/`,
`modes/`, `topology/` or `references/` file without a live route; this
includes the stepped/notched flange rules that were formerly unreachable.
The resolver now produces a per-code, **mandatory L0–L3** stage plan:
L0 bootstrap; L1 source inspection and feature census; L2 routed geometry;
L3 full validation/canonical/export/read-back. All stages must execute before
PASS. Inherited V4.26 physical curve decoding, V4.31 completeness and V4.33
holistic/reference-firewall requirements remain loaded before census.

Read initial stages first; read later rule files just before their execution.
This optimizes **initial context**, not necessarily cumulative whole-job tokens.
If a feature becomes YES/UNKNOWN after source reinspection, rerun the resolver.
Never change an unproved UNKNOWN into NO to save tokens.

Generated scoped RAG index, single-file portable rulepack and benchmark:

```sh
python tools/audit_rule_coverage.py
python tools/build_rule_index.py --output ../ROUTE_INDEX.yaml
python tools/build_rule_bundle.py --output ../TrainAiCad_E2E_RULEPACK.md
python tools/benchmark_rule_routes.py
```

`ROUTE_INDEX.yaml` is an on-demand derivative of Router; it is **not**
another manually maintained source of production authority. Regression
documents and history remain evidence, not live rule context; experimental
MCP stays isolated. Exact duplicate-paragraph analysis is available via
`python tools/audit_rule_duplicates.py`, but never auto-deletes formulas.

## Deterministic rule retrieval

After inspecting the source and completing `FEATURE_CENSUS.md`, an executor with Python
can resolve exactly which modules to read:

```sh
python tools/resolve_rules.py path/to/feature_census.json
```

The JSON census must provide `source_mode`, `part_mode`, and every
`ROUTER.yaml` feature with `YES`, `NO`, or `UNKNOWN`. Missing features are
errors (not silently treated as `NO`). The resolver never searches historical
snapshots, portable skills, or regression documents for production rules.
See `docs/RULE_BRAIN.md`. The AI still has to inspect the actual source,
perform geometry interpretation, apply mandatory gates, and verify saved DXF.

Historical portable releases remain checked in because existing immutable-release
regressions currently read them directly. Removing them safely requires migrating
those tests first, not deleting the evidence.

## Important

- `UNKNOWN` is not `NO`.
- Do not search `skills/lispcad/versions/**` for normal production.
- Do not read the full portable skill unless diagnosing a router coverage gap or explicitly auditing portability.
- New engineering lessons require direct user approval before production promotion.
- Production CAD is repo-direct by default.

The active release number and load order belong only in `AI_ENTRYPOINT.md` and router files, not in this README.
