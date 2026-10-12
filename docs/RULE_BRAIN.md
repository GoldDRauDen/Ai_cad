# TrainAiCad rule brain — deterministic retrieval, not embedding RAG

## Responsibility boundary

**Production authority**: `AI_BOOTSTRAP.md` -> current `AI_ENTRYPOINT.md` ->
`FEATURE_CENSUS.md` -> `ROUTER.yaml` -> routed core/mode/feature/reference
modules -> canonical/export contracts. Pin the repository revision per job.

**Evidence**: `regression/qa/`, `regression/datum/`, `regression/assets/`,
`regression/error_catalog/`. Evidence can test or explain an approved rule,
but cannot supply new customer dimensions or become universal geometry.
`ERROR_INDEX.yaml` is passive and never automatically changes production.

**Compatibility/history**: `skills/lispcad/portable/`,
`skills/lispcad/versions/` and `docs/history/`. Excluded from the normal
load path. Old versions remain in the tree because CI regression tests refer
to them directly. Migrate those tests to immutable references before removing
their checked-in fixtures; do not break existing coverage to shrink the repo.

**Experimental runtime**: `services/trainaicad-mcp/`; separately tested,
no default CAD production authority.

## Source-driven retrieval

1. Inspect actual source pages, views, manufacturing notes and DXF physical
   curves. Produce a complete per-code feature census with every Router family
   explicitly marked `YES`, `NO` or `UNKNOWN`.
2. Call `python tools/resolve_rules.py census.json` when Python/PyYAML are
   available, or apply `ROUTER.yaml` manually. Missing features fail closed;
   `UNKNOWN` loads the feature route.
3. Deduplicate file paths while preserving Router-declared order and dependency
   closure. A feature routes only to approved rules, never to a case-specific
   regression or obsolete portable release.
4. Read the resulting rules; carry out source interpretation, FACE_GRAPH and
   dimensional evidence, canonical member completeness, mandatory post-route
   checks, exporter and actual saved-DXF read-back.
5. Preserve ambiguity locally; unproved geometry cannot be marked PASS.
   Changes to active rule authority require user approval and regression.

## Example complete census

```python
import json
import yaml
from pathlib import Path

router = yaml.safe_load(Path("skills/lispcad/router/ROUTER.yaml").read_text())
features = {name: {"state": "UNKNOWN"} for name in router["feature_routes"]}
# Populate each state from the inspected source; do NOT default unseen features to NO.
census = {"source_mode": "PDF_ONLY", "part_mode": "UNKNOWN", "features": features}
Path("census.json").write_text(json.dumps(census, indent=2))
```

Example above loads all unknown routes intentionally; real jobs should use
source-grounded YES/NO/UNKNOWN to narrow safely.

## Scope of this refactor

This refactor does not change material formulas, bend/Nobi algorithms or
the TrainAiCad-CANONICAL-V4.31 input schema. It extends packaging only after
the composite canonical/member/XDATA read-back: every code is stored as an
independently readable canonical JSON and PASS codes receive contour-only
LINE/ARC/CIRCLE DXF derived from exactly those same entities. PREVIEW and
VIEWS_ONLY parts receive no individual production DXF. The generated cut-only
DXF is reopened to verify every physical primitive and derived identity.
These structural checks do not substitute for actual PDF/engineering QA.

Older versioned portable snapshots remain immutable, excluded from normal
routing and retained because existing CI checks their historical contents.
They are not competing current production rules.

No vector index, embeddings, auto-learning from output or automatic rule
promotion is required.
