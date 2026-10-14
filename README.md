# TrainAiCad

TrainAiCad is a user-approved sheet-metal CAD production rule repository. It is **not an automatic training store**; historical files are not production authority.

**Start here: [SKILL.md](SKILL.md).** It is the cross-agent workflow entry point. `AI_BOOTSTRAP.md`, `AI_ENTRYPOINT.md`, the Router and the routed modules remain the production authority. Release wiring is in [docs/RELEASE_INDEX.md](docs/RELEASE_INDEX.md).

A request such as `E2E` or `Read TrainAiCad and do E2E` means: bootstrap from the current repo, read `AI_ENTRYPOINT.md` and the Router, then run the repo-direct production flow to its executable limit. An agent without repo access or source/CAD tools must report that blocker rather than pretend the repo was read.

For ChatGPT Web Projects, use the pointer template in `PROJECT_INSTRUCTIONS_GPT_WEB.md`. Do not copy engineering rules into Project Instructions.

## Connect to another AI

Attach this repository (or a checkout the AI can read), then say:
`Read SKILL.md from TrainAiCad and perform E2E on the supplied CAD source.`
The AI needs image/PDF inspection and code/file execution tools to create and verify DXF. A text-only AI cannot produce production CAD from the rules alone.

For a single generated portable document (read-only snapshot of the current Router-approved modules):

```sh
python tools/build_rule_bundle.py --output ../TrainAiCad_E2E_RULEPACK.md
```

## Canonical artifacts

`python tools/export_canonical_dxf.py job.json OUT/` checks source-to-canonical members and XDATA read-back, then writes:

```text
OUT/
  geometry_json/<CODE>.json           every code, including REVIEW
  parts_dxf/<PASS_CODE>.dxf           PASS only; LINE/ARC/CIRCLE cut geometry
  <JOB>_ALL.dxf                       when all PASS
  <JOB>_ALL_REVIEW_ONLY.dxf           otherwise (all codes + warnings)
```

Passing structural tests does not prove customer-drawing correctness. Independent engineering QA is still required.

## Routing and audit tools

```sh
python tools/audit_rule_coverage.py                       # active rules must be routed
python tools/resolve_rules.py path/to/feature_census.json # per-code L0–L3 stage plan
python tools/aicad.py build && python tools/aicad.py verify   # scoped query index + integrity
python tools/benchmark_rule_routes.py
```

Details: `docs/RULE_BRAIN.md`. The index is a derivative of the Router, not a second source of rules.

## Important

- `UNKNOWN` is not `NO`.
- Do not search `skills/lispcad/versions/**` for normal production work.
- New engineering lessons need explicit user approval (`DUYỆT` or `PUSH`) before production promotion.
- Production CAD is repo-direct by default.
