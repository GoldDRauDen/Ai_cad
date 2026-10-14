---
name: trainaicad-e2e
description: Source-grounded mechanical sheet-metal CAD from PDF, images and customer DXF DATA through canonical Geometry JSON, validation, export and saved-DXF QA.
---

# TrainAiCad — Universal CAD E2E Skill

**This is the only cross-agent workflow entry point. It is not a second engineering
rule source.** Read this file first, then resolve current engineering authority
from the same repository revision. Repository: `GoldDRauDen/TrainAiCad`.

## 0. Compatibility and tool gate

An agent may be ChatGPT, Codex, Claude, Gemini or another model; brands do
not determine whether CAD execution is available. It must have:

- Access to the actual current repository snapshot and user-provided source.
- Capability to inspect PDF pages/regions and images visually, including
  cropping and magnification when source evidence requires it.
- For customer DATA: a way to inspect/decode DXF entity types, transforms,
  arcs, bulges, layers and units without losing physical curves.
- A runtime with filesystem, Python and the repository dependencies (or
  equivalent verified CAD tooling) to build JSON, execute deterministic
  geometry checks, save DXF and reopen the exact saved DXF.

If a capability is absent, report the precise blocked stage and preserve proved
work. Do not claim source inspected, geometry proved, PASS or DXF exported
without the corresponding actual work.

## 1. Production authority and single source of truth

`current user task -> AI_BOOTSTRAP.md -> AI_ENTRYPOINT.md -> FEATURE_CENSUS.md
-> ROUTER.yaml -> routed modules/references -> canonical/export tools`.

Pin one commit SHA and routing release for a job. Source drawings and customer
production notes govern its facts and dimensions. User-approved engineering
rules are sourced only from the current repo-direct path. `SKILL.md` specifies
the E2E workflow, never overrides engineering values or release-specific gates.
Current release is discovered from `AI_ENTRYPOINT.md` and `ROUTER.yaml`;
do not hardcode it from this file.

Default retrieval **excludes** `skills/lispcad/versions/`,
`skills/lispcad/portable/`, `docs/history/`, and `regression/`.
Regression documents are QA evidence, never new customer dimensional inputs.
MCP under `services/trainaicad-mcp/` is research-only, not the default engine.

## 2. Trigger and complete per-code workflow

A CAD source plus `E2E` or `Read TrainAiCad and do E2E` starts the full
executable job, not only a textual interpretation.

1. **Job/source census:** Identify all codes and source pages/views; associate
   barcode, material, thickness, manufacturing notes, revisions and customer
   DATA with their physical parts. Keep forbidden/user-excluded files closed.
2. **Read/exhaust source:** Inspect *every* relevant source view and detail,
   zoom/crop unclear regions, trace dimension witnesses and scope, preserve
   raw DATA physical curves, explicitly distinguish sample/reference evidence
   from original production source.
3. **Feature routing:** Build a complete census for each code using
   `skills/lispcad/router/FEATURE_CENSUS.md`. Each Router family must be
   `YES`, `NO` or `UNKNOWN`; UNKNOWN loads its rule. Consult current
   `ROUTER.yaml` and `RULE_COVERAGE.yaml`. Deterministic resolver:
   `python tools/resolve_rules.py census.json` when Python is available.
   Consume its mandatory L0 bootstrap, L1 source/physical census, L2
   selected mode/feature/geometry, and L3 validation/export/QA stage plans
   at their actual execution stages. **All four stages are mandatory**;
   reduced initial reading never permits skipping a later gate. Reroute
   any code whose source feature classification changes after zoom/DATA audit.
   Actually read the selected rule files; never treat a selected path as proof
   that its contents were loaded.
4. **Engineering geometry:** Establish part identity, datum, witness graph,
   source group/member inventory, hole/slot/R/C families and, when applicable,
   FACE_GRAPH, attachment edge, Nobi, bend relief and fold-back ownership.
   Build per-code canonical Geometry JSON using the current contract
   (`tools/CANONICAL_INPUT_SCHEMA_V434.md` for new jobs; V4.31 only for `legacy_fixture`).
   Preserve source evidence, entity IDs, flags and unresolved local members.
   Geometry JSON — not a manually repaired DXF — is the canonical model.
5. **Independent validation:** Challenge the proposed complete source model;
   execute all relevant checks from Router and current `VALIDATION.md`,
   including manufacturing family counts, topology, source-to-canonical
   completeness, DATA diff/reprojection when applicable, and physical
   engineering plausibility. No PASS from bbox, entity count or visually
   plausible contour alone. If still unresolved after source exhaustion,
   retain proved geometry/source views with REVIEW semantics; do not invent
   missing dimensions or terminate unrelated codes.
6. **Deterministic export:** Use the current repository canonical exporter,
   `tools/export_canonical_dxf.py` for supported jobs. Do not bypass it by
   ad hoc `ezdxf` writing. The exporter reads canonical entities; it must
   never infer geometry anew.
7. **Saved-file QA:** Reopen actual emitted DXF, validate geometry, physical
   entities and canonical Entity IDs/XDATA, then compare with original source
   and permitted reference evidence. Only an independently verified part can
   be called PASS.
8. **Deliver/report:** Deliver actual verified files, concise per-code
   PASS/REVIEW with unresolved dimensions/features and source references.
   A local flag cannot silently become an approved CUT.

Process codes independently where possible; store proved work by code so a
failed part does not force geometry reconstruction of already-verified parts.

## 3. Canonical status and artifact contracts

**Current canonical exporter behavior** (consult active
`skills/lispcad/core/CAD_OUTPUT.md` and `tools/DXF_INPUT_SCHEMA.md`):
- PASS-only job: `<JOB>_ALL.dxf`.
- Any unresolved code/flag: `<JOB>_ALL_REVIEW_ONLY.dxf` and explicit non-cut
  warnings. No unsupported local geometry should be represented as proved CUT.
- The canonical exporter stamps and verifies Layer-0 `TRAINAICAD ENTITY_ID`
  XDATA. REVIEW_ONLY output is not safe to manufacture.

**Implemented canonical production artifact contract** (after upstream
source/engineering QA and composite canonical read-back):

```text
<JOB>/
  geometry_json/<CODE>.json       # every code, including REVIEW/FLAG
  parts_dxf/<PASS_CODE>.dxf        # QA PASS only; LINE/ARC/CIRCLE CUT only
  <JOB>_ALL.dxf                    # if all PASS
  <JOB>_ALL_REVIEW_ONLY.dxf        # otherwise all codes, warnings intact
```

The canonical exporter now also persists per-code JSON for **every** code and
produces individual DXFs for PASS codes only. Contours are decomposed
analytically from their canonical bulges into LINE/ARC/CIRCLE with exact
endpoints, identity/provenance XDATA and saved-file verification. Non-cut
bends, Kegaki, POINT and warnings never enter individual CUT files.
Known REVIEW geometry stays in the combined non-production DXF only.

The historic lower-level `tools/export_dxf.py` still provides its original
one-composite/opt-in-legacy mode; it is not the default E2E producer.
Do not fabricate a claim of customer-drawing correctness merely because
the structural export tests pass. Full source-grounded multi-job acceptance
remains necessary for manufacturing PASS.

## 4. Execution and QA rules

- No fabricated geometry, dimensions, source examination or PASS.
- No promotion of a user-supplied reference/sample into source authority.
- Preserve unresolved feature provenance and never conceal it within CUT.
- Preserve all source-proved groups/members; FAIL an empty/subset ledger that
  misrepresents source completeness.
- Respect user-forbidden files: never open/read/copy/use.
- Do not modify user-approved rules while processing a normal E2E job.
  Proposed lessons become production rules only after explicit approval,
  with regression and saved-output QA.

## 5. Portable one-file use

When multi-file repository ingestion is unavailable, a code-capable executor
can run `python tools/build_rule_bundle.py --output
../TrainAiCad_E2E_RULEPACK.md` and pass the resulting single generated document
to another model. The build collects current Router-approved modules, **not**
obsolete portable snapshots. That document has a build manifest, content hash,
and snapshot context. It is a read-only handoff, not a runtime/CAD engine.
