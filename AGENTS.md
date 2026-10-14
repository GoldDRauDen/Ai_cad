# AGENTS.md — TrainAiCad execution/orchestration policy

This root file is for agents that automatically read repository instructions (for example local/Codex-style execution). It is **not** a second CAD skill and contains no engineering formulas or pinned production release.

## 1. Bootstrap

For every new CAD job:

1. Read root `SKILL.md` as the universal cross-agent workflow contract, then `AI_BOOTSTRAP.md`.
2. Resolve the current repository snapshot/freshness using the environment available to the agent.
3. Read the current `AI_ENTRYPOINT.md` and mandatory routing files: `skills/lispcad/router/FEATURE_CENSUS.md` and `skills/lispcad/router/ROUTER.yaml` (`RULE_COVERAGE.yaml` is audit-only, not read per job), then load the current Router-declared modules/references.
4. Pin that repository/routing snapshot for the job; do not silently change engineering authority halfway through an unfinished DXF.
5. Execute the current repo-direct E2E workflow on the supplied source.

If freshness/access cannot be established, report the precise blocker. Never claim that the current TrainAiCad repo was used when it was not actually read.

## 2. Authority boundary

Engineering interpretation, source classification, feature rules, FACE_GRAPH/BEND behavior, canonical contracts, output semantics and QA are controlled only by the current `AI_ENTRYPOINT.md`, Router and routed modules/references/tools.

Do not duplicate or override them from this file, conversation memory, historical releases, portable snapshots, regression coordinates or general pattern recognition.

`AGENTS.md` controls orchestration only.

## 3. Source/tool execution

Actually inspect the supplied PDF/image/DXF source with the available vision/file/CAD tools. A filename, OCR fragment, bbox or entity count is not proof that the drawing was visually/semantically inspected.

Use deterministic code/tools for arithmetic, geometry checks, canonical export and DXF read-back where the current repo requires them. Use model reasoning for source semantics, witness/leader scope, topology, ownership and ambiguity analysis.

If the current repo requires source exhaustion, holistic challenge, source-view fallback, fold-back/reprojection or saved-DXF read-back, execute those stages rather than replacing them with prose.

## 4. No-progress behavior

If the pipeline is producing placeholders, empty ledgers, representative rectangles, or otherwise making no real geometry progress, do not scale that failure to more codes. Identify the failing stage, preserve proved work, follow current repo fallback/FLAG behavior, and continue any unaffected executable work.

Never solve a no-progress condition by inventing dimensions, topology, source members or PASS status.

## 5. Reference/calibration boundary

Follow the current repo reference/sample contract. Preserve source-only state before reference exposure where required, do not reverse-fit source geometry from a sample, and do not promote sample-pending/FLAG geometry into production authority without source/user confirmation.

## 6. Repository-change boundary

A normal E2E request does not authorize repository changes.

Only modify/push production rules after explicit user approval such as `DUYỆT` or `PUSH`. Apply the current repo calibration/update discipline, add relevant executable regression/tests, run required QA, and merge only after all required checks pass.

Do not edit portable/history as a shortcut around modular production authority.
