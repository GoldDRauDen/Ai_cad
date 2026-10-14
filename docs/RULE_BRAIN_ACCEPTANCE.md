# PR #24 acceptance — staged deterministic TrainAiCad rule brain

## Baseline, scope and rollback

- Source baseline: `ce4c825b7515e7c222daf665c34e3a8eaf9d4d78` on PR #24.
- Immutable rollback branch: `archive/pr24-pre-token-optimization-20261012`.
- Scope: `refactor/rule-brain-20261012` only. No main merge, no production
  formulas/Nobi changes, no experimental MCP activation.
- Target: fewer rules read **before** source classification; every stage
  and every approved manufacturing gate still executed by completion.

## Actual source-of-truth rules

Production authority order remains `SKILL.md` -> `AI_BOOTSTRAP.md` ->
`AI_ENTRYPOINT.md` -> `ROUTER.yaml` -> approved current modules.
Regressions/case geometry and frozen versions are NOT active rules.
`tools/audit_rule_coverage.py` checks every file under active
`core/`, `features/`, `modes/`, `topology/` and `references/`;
new unrouted files cause CI FAIL. The audit is module reachability only,
not a formal proof of every sentence's semantic consistency.

Added explicit routing for the previously excluded STEPPED_NOTCHED,
L_PROFILE, U_PROFILE, MULTI_FACE_PROFILE and FORMING_FEATURES families.
The **whole current active inventory has 44 modules**, all reachable.
Feature Census now requires classifying these; a missing family fails
closed, while UNKNOWN loads its production rule.

Mandatory pre-census regressions remain untouched:
- V4.26 DXF bulge/physical-curve decode;
- V4.31 canonical source/member completeness;
- V4.33 holistic engineering challenge, reference-exposure firewall and
  part identity graph.

## Byte benchmark — fixed synthetic source routing scenarios

Measured by `python tools/benchmark_rule_routes.py` in GitHub Actions.
This benchmarks exact UTF-8 text bytes selected by the Router, **not**
actual model tokenizer output. Every scenario MUST subsequently run
L2 geometry and L3 validation/export/read-back before PASS.

| Scenario | L0+L1 only (bytes) | Mandatory L0–L3 union (bytes) | Early-context reduction vs eager |
|---|---:|---:|---:|
| Flat, PDF only | 131909 | 199482 | 33.87% |
| Flat with hole/tap | 131909 | 219168 | 39.81% |
| Bent with Nobi | 131909 | 269987 | 51.14% |
| PDF with customer DATA + holes | 154271 | 239850 | 35.68% |
| Unknown, complex DATA | 154271 | 333648 | 53.76% |

**Interpretation:** The staged loader meets the 30% target for initial
load on these five synthetic routing cases. This does **not** establish
30% fewer cumulative tokens over the entire E2E job; the full mandatory
rule union is still needed and its total bytes are listed.

## Rule/index/evidence audits

- Generated `ROUTE_INDEX.yaml`: `python tools/build_rule_index.py --output ../ROUTE_INDEX.yaml`.
  Derived from active Router, separates production, QA-only, evidence,
  executable tools, archived history and MCP research.
- Generated portable one-file skill:
  `python tools/build_rule_bundle.py --output ../TrainAiCad_E2E_RULEPACK.md`.
  Includes current routed/stage modules with SHA-256 source manifest.
- Exact duplicate paragraphs (normalized, 170+ characters) detected by
  `tools/audit_rule_duplicates.py`: zero within current active modules.
  **Semantic paraphrase duplication is not proved absent**. Approved
  source-specific distinctions require human/engineering review.
- Portable legacy `SKILL_LISPCAD_CURRENT.md` is actually V4.24; kept
  only for historical regression, not regenerated as a competing rule.
- All historic snapshots, approved cases and all four older regression
  scripts remain present and protected by existing tests.

## Structural CAD and real-source limitation

Production exporter remains the same V4.31 canonical JSON contract, the
same member-closure/read-back gates and per-code PASS-only cut-only output.
CI runs existing approved V4.19–V4.33 physical/semantic regression
fixtures and tests for mixed PASS/REVIEW, DXF provenance/round-trip,
bulge ARC geometry and isolated CUT parts.

**Not established by this refactor:** new customer PDF drawings interpreted
visually by independent AIs with valid witness/dimension extraction.
Those require accessible real source pages, their associated DATA if any,
and source-vs-export engineering QA. Do not call structural CI a source-
correct production drawing acceptance test.

## CI promotion contract

The PR may be reviewed when all unit tests, V4.19–V4.33 regression
runners, coverage/index/bundle/benchmark and duplicate audit pass.
No merge to main without a separate deployment decision.
