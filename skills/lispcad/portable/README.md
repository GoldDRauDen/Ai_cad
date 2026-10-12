# Portable compatibility snapshot

`SKILL_LISPCAD_CURRENT.md` is an **immutable V4.24 compatibility/audit snapshot**, despite the historical filename CURRENT. It is not current V4.33 production authority. It must not be updated independently as a second rule source. For a fresh, portable full handoff generate `TrainAiCad_E2E_RULEPACK.md` with `python tools/build_rule_bundle.py --output ../TrainAiCad_E2E_RULEPACK.md`. Historical files remain because regression tests require their exact checked-in content.

For normal repo-direct CAD production, **do not load this file by default**. Start at the repository root `AI_ENTRYPOINT.md`, then use `skills/lispcad/router/FEATURE_CENSUS.md` and `ROUTER.yaml`.

The portable snapshot may be read for:
- explicit portability/audit work;
- diagnosis of `ROUTING_COVERAGE_GAP`;
- historical comparison/rollback analysis.

It must not silently override the active modular router.
