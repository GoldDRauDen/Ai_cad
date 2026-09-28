# Error Catalog — Phase 1: passive index

This read-only catalog classifies **12 error families**, **12 existing regression documents**, and **58 scenario records**. It is repository metadata for engineering review, not a CAD production skill, a new engineering lesson, an automatic preflight system, or a production QA release gate.

## Strict phase-1 boundaries

- No change to `AGENTS.md`, `AI_ENTRYPOINT.md`, production `skills/`, `references/`, existing regressions, or `tools/export_dxf.py`.
- The catalog is **not automatically loaded** by Codex. Manual preview commands do not read PDFs, make geometry, alter DXFs, activate gates, record incidents, or push GitHub changes.
- The CURRENT user-approved production skill always takes precedence. Historical V4.3 unconditional DXF-only R0.5 and V4.7 default dual export are superseded wherever current approved rules differ.
- Old reference DXF coordinates cannot replace independent PDF reading. New technical lessons still require direct user approval.

## Optional read-only commands (Python 3.10+ and PyYAML)

```bash
python tools/error_catalog.py validate --repo .
python tools/error_catalog.py preflight --tags ABSOLUTE_ORDINATE MIRROR
python tools/error_catalog.py escalate --family DATUM_FRAME --confirmed-events 3
python -m pytest tests/test_error_catalog.py -q
```

`preflight` is a **manual hypothetical routing preview**, not live agent routing. `escalate` is a **simulation**, not a real counter update or release hold. All future automatic regression loading, persistent incident counting, or live enforcement requires separate approval and testing.

`inventory_snapshot_commit` identifies the checked source inventory only; it does **not** pin the production skill. Each new CAD job continues to resolve the current approved skill using the unchanged repo entrypoint.

Historic regression documents are not independently verified recurrence events. Prior production-escape history is **UNKNOWN**, not zero. All current counters remain untouched in phase 1.
