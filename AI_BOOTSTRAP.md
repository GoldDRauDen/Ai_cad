# AI_BOOTSTRAP — TrainAiCad universal E2E entry

This file is the release-independent bootstrap for any AI/agent that has access to this repository and the tools required to inspect the supplied source and create/verify DXF output.

Repository identity: `GoldDRauDen/TrainAiCad`.

## 1. Invocation contract

Treat any concise request equivalent to the following as a full production invocation:

- `E2E`
- `Read TrainAiCad and do E2E`
- `Đọc repo TrainAiCad làm E2E`
- `Use the current TrainAiCad repo for this CAD job`

When such an invocation accompanies PDF/image/customer DXF DATA, do not stop after routing, census, analysis, or a text report while executable CAD/QA work remains.

## 2. Required bootstrap sequence

1. Access the current `GoldDRauDen/TrainAiCad` repository through the available GitHub connector/plugin or a local checkout.
2. Establish repository freshness using the execution environment available to the agent. Never claim current-repo authority without actually reading the repository.
3. Read `AI_ENTRYPOINT.md` in full.
4. Read the mandatory router files named by the current entrypoint:
   - `skills/lispcad/router/FEATURE_CENSUS.md`
   - `skills/lispcad/router/ROUTER.yaml`
   - `skills/lispcad/router/RULE_COVERAGE.yaml`
5. Load the current router-declared always-on modules/references, inspect the actual source, route every `YES`/`UNKNOWN` family, and follow the current repo-direct E2E flow to its executable limit.
6. If a complete feature census is available and Python with PyYAML can run, `tools/resolve_rules.py` may calculate the deterministic, de-duplicated Router file set. This helper does not replace source inspection, mandatory routing, or any engineering gate; if unavailable, follow the Router directly.
7. Use current repository tools/contracts for canonicalization, DXF serialization, save/reopen/read-back and applicable source reprojection/fold-back.
8. Deliver only statuses/output semantics permitted by the current routed rules.

The current release number, engineering formulas, feature mechanisms and CAD output details belong to `AI_ENTRYPOINT.md`, Router and routed modules. They are deliberately not duplicated here.

## 3. Authority and freshness

Authority order for a CAD job is:

`USER TASK -> AI_BOOTSTRAP -> current AI_ENTRYPOINT -> current ROUTER -> routed modules/references -> canonical/export tools`.

Do not substitute chat memory, model memory, a previous job, regression geometry, portable snapshots or history for current repo authority.

Do not read `skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md`, `skills/lispcad/versions/**`, or `docs/history/**` by default. Use them only when the current repo explicitly permits compatibility/coverage diagnosis.

If the repository cannot actually be accessed or its required current files cannot be read, report the precise runtime blocker allowed by the current repo. Do not fabricate that the repo was read.

## 4. E2E execution requirement

For a normal CAD job, continue through every executable stage required by the current repo. A local ambiguity must remain local: preserve proved geometry, continue unaffected codes/features, and use the current FLAG/PREVIEW/SOURCE_VIEW/VIEWS_ONLY behavior where applicable.

If a full flat truly remains unresolved after the current source-exhaustion and engineering-challenge gates, execute the repo's complete source-view fallback rather than stopping at a text explanation.

Do not convert an AI interpretation failure into a claim that customer/source data are missing unless the current evidence actually proves that blocker.

## 5. Reference/sample boundary

A sample/reference does not replace source-first production interpretation.

For calibration/reference workflows, obey the current reference-exposure firewall and preserve the pre-reference source-only state. Do not reverse-fit missing source facts from sample coordinates or rewrite hindsight as prior source understanding.

Sample geometry explicitly marked FLAG/Magenta/pending remains customer-confirmation-pending unless source/user authority resolves it.

## 6. Repository-change boundary

Running E2E does not authorize changing production rules.

For calibration or repo maintenance:
- separate FACT -> ROOT_CAUSE -> PROPOSED_LESSON -> REGRESSION_CASE;
- do not promote one drawing into a universal rule;
- modify/push production repository files only after the user explicitly approves the change (for example `DUYỆT` or `PUSH`);
- run the current required tests/regressions/read-back before merge.

## 7. Tool capability boundary

This bootstrap can standardize behavior only for an AI/agent that can actually access the repository, inspect the source files and run the required CAD/file tools.

If those capabilities are unavailable, state the concrete limitation. Do not simulate a completed E2E run or invent deliverable links.
