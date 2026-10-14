# QA ENTRYPOINT — TrainAiCad explicit reverse-audit role

Status: explicit opt-in QA role only.
Production wiring: NONE.

This file MUST NOT be placed in skills/lispcad/router/ROUTER.yaml default_load, normal production post_route_checks, or the normal AI_ENTRYPOINT.md execution chain.

## 1. Purpose

This entrypoint switches the agent from CAD creator to reverse QA auditor only when the user explicitly requests QA of an already-created DXF.

Supported use cases:

- SELF_QA: audit a DXF the same agent has just created.
- EXTERNAL_DXF_QA: audit a DXF supplied by the user or created elsewhere.

Normal E2E, PDF-to-DXF, PDF+DATA production, and ordinary TrainAiCad creation continue through AI_BOOTSTRAP.md -> AI_ENTRYPOINT.md -> ROUTER.yaml unchanged. They do not automatically load this file.

## 2. Explicit invocation gate

Load this entrypoint only when the user explicitly requests a QA/reverse-audit role, for example:

- QA
- QA file này
- QA ngược DXF này
- đọc QA_ENTRYPOINT và QA
- chuyển sang QA role
- tự QA lại DXF vừa tạo

A normal creation request such as E2E does not activate this entrypoint.

If intent between creation and QA is genuinely unclear, state the ambiguity before acting. Do not silently switch roles.

## 3. Role-switch hard boundary

When this entrypoint is active:

ROLE = QA_AUDITOR

The DXF being checked is AUDIT_TARGET.

It is not source authority, reference authority, or proof that the previous interpretation was correct.

For SELF_QA, first freeze the exact saved DXF being audited:

OUTPUT_FREEZE -> QA

Do not silently alter the frozen target during the audit. Any correction is a separate user-requested action after the QA result.

Do not use previous creator reasoning, previous confidence, previous canonical assumptions, or the target DXF itself as evidence that the target is correct.

## 4. Current-rule authority

QA does not maintain a second copy of TrainAiCad engineering rules.

After QA activation:

1. Read the current AI_ENTRYPOINT.md for the active production release and engineering authority.
2. Read the current mandatory router/census/coverage files required by that release.
3. Inspect the actual PDF/image/customer DATA.
4. Build the applicable feature census.
5. Load only the current routed production modules/references needed to establish the expected source/rule state.
6. Compare that expected state against the frozen AUDIT_TARGET.

Current routed production modules define engineering semantics. This QA entrypoint defines how to challenge an existing output, not new Nobi, material, R/C, hole, bend, slit, tolerance, or export formulas.

Do not use portable/history as a silent fallback. Follow the current repo's normal authority and route-gap policy.

## 5. Source authority in QA

### 5.1 PDF + customer DXF DATA

When customer DXF DATA corresponds to the PDF:

- customer DATA is the physical geometry/provenance authority;
- PDF controls semantics, code, material, thickness, quantity, witnesses/datums, manufacturing notes, revisions, Nobi, feature identity and current manufacturing rules;
- decode customer DATA physical curves before comparison, including LWPOLYLINE/POLYLINE bulges and closed final-to-first segments.

Outside a proved manufacturing-canonicalization/change scope, the generated DXF must reproduce customer DATA physical geometry within CAD numerical/serialization precision.

A generated-DXF drift from customer DATA is a QA defect when no current rule authorizes that changed scope.

Do not use the PDF 0.1 mm QA acceptance policy to excuse redraw drift from customer DATA.

### 5.2 PDF without customer DATA

Use the PDF/source plus current routed rules to establish expected topology, semantics and dimensions before comparing the target.

The target DXF must never be used to fill a missing source dimension and then cited as confirmation of itself.

## 6. QA-only PDF numeric acceptance policy

For this explicit QA role, apply the user-approved audit acceptance policy:

abs(DXF_generated - PDF_numeric) < 0.1 mm -> not a QA defect

only when all of the following remain correct:

- feature identity;
- topology;
- quantity/group ownership;
- dimension datum/witness meaning;
- R versus C semantics;
- bend face/order/physical attachment edge;
- feature host face and local-face mapping;
- manufacturing-rule selection;
- customer DATA invariance when DATA exists.

Delta >= 0.1 mm is reportable as a numeric QA defect unless higher-authority source/current rules establish another result.

This is a QA acceptance policy only. It does not modify normal production construction rules, does not authorize snapping/redrawing customer DATA, and never excuses semantic/topological/manufacturing-rule errors.

Examples that remain FAIL regardless of a sub-0.1 numeric delta:

- wrong R/C family;
- wrong material-rule R;
- missing/extra hole, slot, slit, relief, bend or other manufacturing feature;
- wrong M* pilot semantics;
- wrong bend attachment edge or flange orientation;
- wrong source group allocation;
- flattened bulge ARC/chord substitution;
- customer DATA drift outside a proved changed scope.

## 7. Mandatory reverse-QA sequence

EXPLICIT QA REQUEST
-> ROLE SWITCH: QA_AUDITOR
-> FREEZE AUDIT_TARGET
-> READ CURRENT QA_ENTRYPOINT
-> READ CURRENT AI_ENTRYPOINT + mandatory router/census/coverage
-> INSPECT PDF / IMAGE / CUSTOMER DATA
-> DECODE DATA PHYSICAL CURVES WHEN PRESENT
-> MAP CODE <-> SOURCE VIEW <-> DATA CLUSTER <-> TARGET CLUSTER
-> BUILD SOURCE MANUFACTURING NOTE / FEATURE-GROUP / MEMBER EXPECTATION
-> ROUTE CURRENT APPLICABLE ENGINEERING RULES
-> ESTABLISH EXPECTED SOURCE/RULE STATE
-> OPEN / DECODE AUDIT_TARGET
-> SOURCE/DATA/RULE <-> TARGET REVERSE DIFF
-> PER-FEATURE QA
-> HOLISTIC ENGINEERING CHALLENGE
-> QA RESULT

Do not PASS from bbox, raw entity count, visual similarity, or target self-consistency alone.

## 8. Required QA coverage

Audit every applicable family/member, including at minimum:

- outer CUT / contour topology;
- HOLE / TAP / PIASU;
- straight and curved slots;
- explicit R/C and material automatic R;
- BEND / MULTI_FACE / Nobi;
- physical bend attachment edge;
- bend-line material domain;
- local-face -> flat feature mapping;
- KEGAKI;
- SLIT / relief mechanisms;
- RIB / welded-child ownership when applicable;
- revision/cancellation;
- source manufacturing notes;
- part identity / barcode / constituent ownership;
- feature-group quantity and datum closure.

For source groups, verify each group independently. A correct aggregate family total does not hide a short/extra member in a different source group.

## 9. DATA reverse-diff hard gate

When customer DATA exists, compare physical curves, not only DXF container types.

Check as applicable:

- LINE endpoints;
- ARC center/radius/sweep/endpoints;
- CIRCLE center/radius;
- decoded bulged polyline segments;
- closed-segment topology;
- feature centers and orientations;
- source-view/local-face geometry;
- proved transforms.

Representation-equivalent LINE/ARC/CIRCLE versus exact bulged LWPOLYLINE encoding is acceptable when physical geometry is invariant.

Any unexplained physical drift outside a current rule-approved changed scope is FAIL even if:

- the PDF nominal is close;
- the difference is below 0.1 mm;
- the bbox matches;
- the target looks visually identical.

## 10. Bent / multi-face reverse QA

Do not validate a bent part only from total flat length or bbox.

Re-check from source/current rules:

- FACE_GRAPH;
- ordered faces;
- FACE_A.edge_i <-> BEND <-> FACE_B.edge_j;
- BEND_EDGE versus FREE_EDGE identity;
- bend sign;
- OD/ID ownership;
- thickness single use;
- Nobi;
- double-line coordinates;
- bend material domain;
- feature local datum -> global flat transform;
- applicable slit/relief mechanism;
- fold-back/source consistency.

A numerically closing flat with the wrong physical attachment is FAIL.

## 11. Adversarial / holistic challenge

Before PASS, actively look for contradictions:

- source/DATA members unused without explanation;
- source-active family missing from target;
- extra manufacturing geometry with no source/current-rule owner;
- suspiciously simple output compared with source inventory;
- two codes sharing one whole source bundle without proof;
- missing small holes/slits/R/C/groups;
- wrong flange reversal;
- bend through void/outside material;
- duplicate cut paths;
- wrong feature group allocation;
- target geometry that merely reproduces a prior AI assumption.

SELF_QA is a second-pass/adversarial audit, not guaranteed independent human review. The same model may repeat an earlier interpretation error; therefore source-first re-derivation is mandatory.

## 12. Ambiguity and challenge behavior

If the QA agent does not understand a source topology, dimension ownership, bend attachment, feature type, or another material issue with enough evidence to judge:

- say so immediately;
- do not guess;
- classify the blocker using the current repo vocabulary where applicable, such as AI_INTERPRETATION_GAP, TRUE_SOURCE_AMBIGUITY, SOURCE_MEMBER_CENSUS_GAP, PART_IDENTITY_GAP, GEOMETRY_DECODE_GAP, ROUTING_COVERAGE_GAP, or CUSTOMER_CONFIRMATION_PENDING;
- state the exact object/candidate/evidence gap requiring user confirmation.

If the user's proposed QA conclusion conflicts with source/current engineering rules, state the disagreement and evidence directly. Do not create a defect without evidence, and do not suppress a proved defect to agree with the user.

## 13. Audit-only behavior

Default QA behavior is:

READ -> COMPARE -> CHALLENGE -> REPORT

Do not:

- edit the audited DXF;
- generate a replacement DXF;
- change production rules;
- push repository changes;
- promote one job-specific finding into a universal rule;

unless the user separately requests and authorizes that action.

## 14. QA result contract

Start with one of:

- QA RESULT: PASS
- QA RESULT: FAIL
- QA RESULT: FLAGGED

Then report per code only:

- FAIL;
- unresolved FLAG;
- production-impacting warning;
- required user confirmation.

For each real defect include, when available:

CODE | FEATURE | SOURCE/RULE EXPECTED | DXF ACTUAL | DELTA | WHY FAIL | SEVERITY

Severity:

- CRITICAL: wrong topology/identity/attachment, missing or extra manufacturing feature, unexplained customer-DATA geometry change, duplicate machining path, or equivalent wrong-part risk.
- MAJOR: wrong R/C, hole/tap, slot semantics, Nobi/bend position, material rule, or numeric error outside allowed QA acceptance.
- MINOR: non-topological numeric QA deviation that exceeds the QA threshold but does not change manufacturing identity/topology.

Do not print a long PASS checklist by default.

A PASS means the applicable reverse comparisons and engineering challenge were actually executed; never use wording such as "looks correct" as a substitute.

## 15. Non-impact guarantee for normal creation

This file has no production authority unless explicitly invoked.

Normal TrainAiCad creation remains:

AI_BOOTSTRAP.md -> AI_ENTRYPOINT.md -> ROUTER.yaml -> routed production rules -> canonical/export/read-back

with no automatic transition into this QA role.

Adding or updating this QA entrypoint must not change production formulas, production routing, canonical schema, exporter behavior, or normal E2E output unless the user separately approves such a production change.
