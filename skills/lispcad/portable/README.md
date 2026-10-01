# Portable compatibility snapshot

`SKILL_LISPCAD_CURRENT.md` is the complete self-contained V4.23 compatibility/audit snapshot retained to prevent rule loss during modularization.

For normal repo-direct CAD production, **do not load this file by default**. Start at the repository root `AI_ENTRYPOINT.md`, then use `skills/lispcad/router/FEATURE_CENSUS.md` and `ROUTER.yaml`.

The portable snapshot may be read for:
- explicit portability/audit work;
- diagnosis of `ROUTING_COVERAGE_GAP`;
- historical comparison/rollback analysis.

It must not silently override the active modular router.
