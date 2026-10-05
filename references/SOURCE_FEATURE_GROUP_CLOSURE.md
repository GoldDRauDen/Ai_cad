# SOURCE_FEATURE_GROUP_CLOSURE — leader/callout group closure + reference parameter identity

**Status:** USER APPROVED 2026-10-05 from calibration job `521005-05`.

## Purpose

Prevent same-family features from being collapsed into one dimension graph, and prevent false PDF/reference conflicts caused by comparing different physical parameters or different witness frames.

This reference is always-on source parsing before final preliminary Feature Census. It adds no hole size, Nobi, material, tolerance, or slit formula.

## 1. FEATURE_FAMILY versus SOURCE_FEATURE_GROUP

A **FEATURE_FAMILY** is the manufacturing class such as `HOLE`, `TAP`, `SLOT_STRAIGHT`, `CHAMFER_FILLET`, `SLIT_RELIEF`, etc.

A **SOURCE_FEATURE_GROUP** is one source-scoped cluster controlled by its own callout/leader/quantity and dimension ownership. Two groups may have the same family and the same nominal size and still remain separate groups.

Required group record:

`group_id | family | source callout | quantity | leader/target scope | source view | host face | X witness graph | Y witness graph | local datum | size semantics | evidence status`

Do not merge source groups merely because they share:
- the same diameter/thread/slot size;
- a continuous or nearby X dimension string;
- visual alignment;
- projection proximity;
- a common family label;
- a convenient aggregate count.

### Group closure rule

Close each source group independently:

`leader/callout -> quantity -> feature size -> X witnesses -> Y witnesses -> datum -> host face -> canonical members`.

A dimension string may be shared by multiple groups only where the actual witness graph proves that shared ownership. A shared X chain does **not** authorize borrowing another group's Y chain, and vice versa.

`GROUP_COUNT_CLOSURE` is mandatory before aggregate family count closure. If the final total count is numerically correct but one source group is short and another is over-produced, the result is FAIL.

### 057862 regression intent

For calibration code `057862`, the source contains separate `2-Ø9` left, `6-Ø9`, and `2-Ø9` right source groups. They are the same broad HOLE/Ø9 family but have independent leader/quantity/dimension ownership. Those job-specific groups are regression evidence only; they do not establish universal coordinates.

## 2. DETAIL_VIEW_MAPPING

The paper location of a Detail/Section/Auxiliary view may be arbitrary. Its placement on the sheet is not a manufacturing coordinate.

Use the detail identifier/leader and projection/source mapping to bind the detail back to the actual physical target. Dimensions inside the detail retain their own witness endpoints and local feature ownership. Do not transfer the detail's page position into part geometry.

## 3. CUSTOMER_CONFIRMATION_PENDING boundary

A customer/sample/reference DXF does not automatically resolve a source value that is explicitly or genuinely `CUSTOMER_CONFIRMATION_PENDING`.

- Keep every independently proved geometry exact.
- Keep the unresolved source field locally FLAGGED.
- A TRAIN_REFERENCE may diagnose likely intent, but it may not promote the pending value into production authority unless the user/customer explicitly confirms that value or the active source authority itself resolves it.

Calibration examples `057861` and the `8-R5` corner family on `057864` remain local customer-confirmation cases; their sample geometry must not become a universal or silent source substitute.

## 4. SAME_PHYSICAL_PARAMETER_BEFORE_REFERENCE_CONFLICT

Before declaring a PDF/source value to conflict with customer DATA or an approved/sample/reference DXF, prove that both measurements describe the **same physical parameter**.

At minimum lock:

`code + source group + host face + physical witness A + physical witness B + dimension semantics + inside/outside state + source/local frame + units`.

Only after those fields match may a numeric difference be classified as an actual source/reference parameter conflict.

Do not compare:
- an inside bend dimension with a measurement from an outside/free edge;
- a formed-face local dimension with a global-flat coordinate;
- a hole-center distance with a contour-edge distance;
- a theoretical-sharp dimension with the trimmed physical R/C bbox;
- two visually similar values whose witness endpoints differ.

If parameter identity is not closed, re-trace the source/reference witnesses. Use `UNVERIFIED`/local FLAG as applicable; do not report `SOURCE_CONFLICT` merely because two numbers differ.

### 057865 regression intent

For calibration code `057865`, `10.5 / 8.5` are inside bend dimensions. A reference measurement of `10.0 / 8.0` taken from an outside edge is not the same physical parameter. The earlier comparison was an `AI_RULE_MISAPPLICATION`, not evidence that the source and sample disagreed.

## 5. Feature Census interaction

Before a family may be `NO`, first determine whether source leaders/callouts imply one or more unresolved source groups. A proved group makes the family `YES`; an apparent group with unresolved family/scope/quantity/host/datum makes the relevant family at least `UNKNOWN`.

For bent parts, if a bend-end/corner junction may require a relief decision but the signed bend-end offset has not yet been closed, retain `SLIT_RELIEF = UNKNOWN` until the routed 90-degree bend-end relief gate is evaluated. Do not require the literal word `SLIT` for topology-triggered relief mechanisms already approved elsewhere.

## 6. QA

Before production PASS:

- every active source group has a closed quantity and datum/witness record;
- no group borrows an unproved X/Y chain from another group;
- aggregate family count equals the sum of independently closed groups;
- Detail views map to their physical target rather than page position;
- customer-pending fields remain pending unless source/user authority resolves them;
- every claimed source/reference numeric conflict passes `SAME_PHYSICAL_PARAMETER_BEFORE_REFERENCE_CONFLICT`.