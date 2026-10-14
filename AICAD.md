# AICad

AICad inherits the TrainAiCad rule tree at commit `7c78d3c` (full history kept) and adds a
verifiable query layer on top of it. The inherited `README.md` is unchanged.

- **Rules are unchanged.** This repo is a copy of TrainAiCad @ `7c78d3c` plus the files listed
  below. The rules remain the authority; routing stays in `skills/lispcad/router/ROUTER.yaml`.
- **Known gaps are declared, not hidden.** See `KNOWN_GAPS.yaml` (currently F1: the V4.34 material
  alias table is not routed). Fixing a gap changes routing and possibly CAD output, so each fix
  needs explicit approval (`DUYET` / `PUSH`).
- **Plan:** `docs/PLAN_CLAUDE_FIX.md`.

## Layers added in AICad

| Path | Purpose |
|---|---|
| `tools/aicad.py` | `build` (SQLite FTS5 index), `verify` (integrity gate), `search`, `rule` |
| `KNOWN_GAPS.yaml` | Declared rule gaps and declared tool roles (production / audit) |
| `tests/test_aicad.py` | Completeness, routing parity, golden retrieval and latency tests |
| `tests/golden_queries.yaml` | 16 golden queries (JP / VN / EN) with expected rule files |

## Usage

```bash
pip install -r requirements.txt
python3 tools/aicad.py build                       # build/aicad.sqlite (git-tracked files only)
python3 tools/aicad.py verify                      # exit 0 = PASS; checks every invariant below
python3 tools/aicad.py search "bend end offset 90" -k 5
python3 tools/aicad.py search "スリット" --json
python3 tools/aicad.py rule references/NOBI_TABLES.md
python3 -m pytest -q tests/test_aicad.py           # 25 tests
```

Routing itself is still computed by the inherited resolver:

```bash
python3 tools/resolve_rules.py census.json
```

## What `verify` guarantees

1. **No lost bytes.** For every text file, the concatenation of its indexed chunks equals the file on disk.
2. **Every router path is indexed and routed.** Routing sections only. Compatibility notices
   (`portable_compatibility`, `history_policy`) are excluded on purpose.
3. **No silent rule gap.** A rule file that is not routed must be declared in `KNOWN_GAPS.yaml`.
   A declared gap that becomes routed must be removed from the file.
4. **Every `tools/*.py` has a declared role** (`production` or `audit`). A production tool that no
   routing doc mentions produces a warning.
5. **The index is not stale.** The database must match the file hashes on disk.

## What this does not guarantee

- Engineering correctness. The index proves that rules are present, routed or declared, and
  retrievable. It does not prove that a CAD output is right.
- Retrieval over every possible question. The golden set has 16 queries; growing it is ongoing work.
- Archive files (`skills/lispcad/versions/`, `skills/lispcad/portable/`, `docs/history/`) are indexed
  for completeness but excluded from default search, as the router requires.

## Scope

Default search covers `entry`, `router`, `rule`, `schema`, `tool` and `doc` files. Tests, CI,
service code and QA evidence are excluded unless `--include-excluded` is passed. QA regression files
are evidence, not rules, and must not be used as customer dimensional input.
