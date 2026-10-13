# HOLISTIC_ENGINEERING_CHALLENGE — V4.33

**Status:** USER APPROVED / PUSH 2026-10-07.

## 1. Purpose

This is a pre-canonical engineering challenge. It does not replace feature-specific rules, FACE_GRAPH proof, source-member completeness, fold-back, or saved-DXF read-back.

Its purpose is to catch a different failure mode: the AI may build a self-consistent but incomplete or wrongly interpreted source model and then pass downstream checks against its own bad ledger.

The challenge asks whether the current interpretation is mechanically plausible and whether all available source evidence has actually been consumed before the job is allowed to proceed, downgrade to VIEWS_ONLY, or ask the customer.

## 2. Mandatory position in the flow

Run after the first source-based solve and routed feature checks, but before final canonical serialization:

```text
SOURCE
-> census / groups / members / identity
-> first solve
-> HOLISTIC_ENGINEERING_CHALLENGE
   -> anomaly? re-open source and re-solve
   -> no anomaly? continue
-> local FLAG or proved flat / justified VIEWS_ONLY
-> FINAL_ENGINEERING_SANITY_REVIEW
-> canonical
-> DXF
```

The challenge is source-first. A later sample/reference must not be used to retroactively make this stage appear solved.

## 3. Mandatory anomaly triggers

At minimum raise `ENGINEERING_ANOMALY_DETECTED` when any applicable condition is true:

- source contains substantial physical DATA or multiple proved source views while the persisted proved-source-member inventory is empty or implausibly small;
- a source feature family is YES/UNKNOWN but no corresponding source group/member or explicit drawing-only/canceled classification exists;
- a printed/handwritten flat arithmetic or Nobi chain closes a meaningful part dimension while the part is downgraded directly to VIEWS_ONLY without testing the corresponding formed topology;
- relevant source views/faces/primitives were harvested but have no downstream role and no explicit drawing-only/duplicate/helper classification;
- two declared part codes or constituent identifiers are assigned the same whole source bundle without proved shared-assembly scope;
- a dimension classified as a shared bend-edge length is also used as a whole face/blank extent without same-physical-parameter proof;
- a local unresolved feature causes the whole part to become VIEWS_ONLY even though a defensible flat exists independently;
- VIEWS_ONLY is selected before every source-supported FACE_GRAPH candidate has been tested through the routed constraints;
- the output is materially simpler than the source inventory without a member-by-member explanation;
- a PASS depends only on ledger self-equality while upstream census/inventory/ledger cardinalities or ownership disagree.
- source assembly/welding views were available but no independent weld-site inventory or explicit negative disposition exists, or a proved KH851 weld site has no corresponding KEGAKI member/local FLAG.

An anomaly is not proof that a particular alternative answer is correct. It is a mandatory reason to re-open the source and test the interpretation.

## 4. Unresolved-cause analysis

Before a part may remain unresolved, persist an evidence-equivalent record:

```text
UNRESOLVED_OBJECT
CANDIDATES
EVIDENCE_USED
EVIDENCE_NOT_YET_USED
CONSTRAINT_RESULT_PER_CANDIDATE
TRUE_REMAINING_DOF
BLOCKER_CLASS
```

For bent/multi-face parts, candidate attachment/order/sign hypotheses must be tested against all applicable formed/profile topology, view correspondence, dimension witnesses, DATA physical curves, feature ownership, handwritten arithmetic and fold-back constraints.

Do not write only "bend unclear", "attachment unknown", or "complex part".

## 5. Blocker vocabulary

Use the most specific class supported by evidence:

- `TRUE_SOURCE_AMBIGUITY`: two or more materially different interpretations remain source-compatible after source exhaustion.
- `AI_INTERPRETATION_GAP`: source evidence exists but the current solver has not established a unique solution; do not blame the source.
- `SOURCE_MEMBER_CENSUS_GAP`: relevant source geometry/families have not been fully harvested/classified.
- `PART_IDENTITY_GAP`: barcode/code/constituent/view/DATA ownership is unresolved.
- `GEOMETRY_DECODE_GAP`: source physical curves exist but decoding/classification is incomplete.
- `ROUTING_COVERAGE_GAP`: a detected family has no current repo route.
- `CUSTOMER_CONFIRMATION_PENDING`: the source/user explicitly leaves a field pending.

`AI_INTERPRETATION_GAP` is not interchangeable with `TRUE_SOURCE_AMBIGUITY`.

## 6. VIEWS_ONLY is a last executable fallback, not a text-only stop

If no defensible flat exists after source exhaustion and this challenge, but independently proved source/orthographic views exist, execute the current DRAW -> FLAG -> CONFIRM policy:

- redraw/preserve every independently proved source-view member needed to represent the unresolved part;
- preserve physical customer-DATA curves instead of replacing them with simplified analytic lookalikes;
- keep views as separate labeled subgroups under the correct code;
- include all proved holes/slots/R/C/marks represented in those source views;
- mark only the unresolved relationship/topology/dimension as FLAGGED;
- set part status VIEWS_ONLY and whole composite REVIEW ONLY — NO CUT.

Hard fail `VIEWS_ONLY_SOURCE_VIEW_COMPLETENESS` when proved source-view members are omitted from the VIEWS_ONLY canonical representation.

## 7. Local uncertainty stays local

When a unique flat is proved but one relief, hole, slit, datum or other feature remains unresolved, retain the proved flat and proved members. FLAG/PREVIEW only the unresolved local member.

Do not use one local uncertainty to downgrade the whole part to VIEWS_ONLY.

## 8. Final engineering sanity review

Immediately before canonical serialization, ask again:

- Does every source physical/view member have a downstream role?
- Does every used dimension/note/Nobi have a semantic owner?
- Is any source view silently unused?
- Are any two codes suspiciously sharing the same complete source bundle?
- Is any shared bend-edge dimension being used as an unrelated face/blank extent?
- Is any output unexpectedly simple compared with the source inventory?
- Is any VIEWS_ONLY status still carrying an untested source-supported candidate?
- Is any PASS merely self-consistent with an incomplete ledger?

Any affirmative result returns the job to source interpretation; it does not authorize guessing.

## 9. Non-generalization

This gate creates no drawing-specific geometry, no new Nobi formula, and no rule that a complex drawing must have a complex flat. It only requires evidence accounting, challenge/re-solve behavior and an executable source-view fallback when the flat truly remains unresolved.
