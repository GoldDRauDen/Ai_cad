# TrainAiCad Canonical Input Schema — V4.31

The input schema is unchanged. The **normal E2E output packaging** of the
validated canonical job is now one JSON per part at
`geometry_json/<CODE>.json`, one individual CUT DXF per PASS code at
`parts_dxf/<PASS_CODE>.dxf` (LINE/ARC/CIRCLE only), plus the one existing
top-to-bottom composite file. REVIEW/PREVIEW/VIEWS_ONLY still receive JSON
and composite review geometry/flags, never a standalone CUT DXF.
The individual geometry is derived from source-canonical entities and
undergoes independent exact saved-DXF/XDATA read-back; no second interpretation
of PDF measurements occurs.

Normal production/review serialization uses `tools/export_canonical_dxf.py` and requires:

```json
{
  "canonical_contract": "TrainAiCad-CANONICAL-V4.31",
  "job_id": "JOB",
  "parts": [ ... ]
}
```

Each part retains the existing `tools/DXF_INPUT_SCHEMA.md` fields (`code`, `material`, `thickness_mm`, `status`, `checks`, `flags`, `entities`) and adds mandatory member provenance.

## Source groups

## Conditional weld-site/KEGAKI completeness (no schema version change)

For jobs with numeric KH851 customer_code or source-identified assembly/
weld sites, persist the source-first weld inventory before marking geometry.
Optional job-level customer_code is the explicit job-statistics numeric ID,
not a barcode suffix. Parts contain source_assembly_view_ids,
source_weld_site_ids and weld_site_census. Sites link to source-backed KEGAKI
members through mark_member_ids; the canonical validator checks their
physical RED marking or local FLAG, independently of member self-equality.
Use references/WELD_SITE_KEGAKI_CLOSURE.md for exact fields and negative
(no weld) evidence. Older jobs with no assembly/weld indicators and no
applicable KH851 scope retain their existing V4.31 canonical format.


```json
"source_groups": [
  {
    "group_id": "G_HOLE_LEFT",
    "family": "HOLE",
    "status": "PROVED",
    "source_quantity": 2,
    "evidence": "2-Ø9 leader, left group",
    "members": [
      {"member_id": "G_HOLE_LEFT_1", "status": "PROVED"},
      {"member_id": "G_HOLE_LEFT_2", "status": "PROVED"}
    ]
  }
]
```

Allowed source/member status: `PROVED`, `FLAGGED`, `CANCELED`.

`source_quantity` is an integer only when proved. If quantity is unresolved, use null and retain the group as FLAGGED. Do not manufacture a count from symmetry/sample.

## Canonical members

Source-backed:

```json
"canonical_members": [
  {
    "canonical_member_id": "CM_G_HOLE_LEFT_1",
    "origin": "SOURCE",
    "source_member_id": "G_HOLE_LEFT_1",
    "group_id": "G_HOLE_LEFT",
    "status": "PROVED",
    "entity_ids": ["E_HOLE_LEFT_1"]
  }
]
```

For a FLAGGED source member use `PREVIEW`, `SOURCE_VIEW`, or `FLAGGED_NO_GEOMETRY`. `FLAGGED_NO_GEOMETRY` has an empty `entity_ids` list; this is how uncertainty stays local without fabricating geometry.

Rule-derived member:

```json
{
  "canonical_member_id": "CM_AUTO_R_1",
  "origin": "DERIVED_RULE",
  "status": "PROVED",
  "controlling_rule": "MATERIAL_AUTO_R",
  "source_member_ids": ["OUTER_1"],
  "entity_ids": ["E_OUTER"]
}
```

A semantic member may reference multiple physical entities and multiple members may reference one shared contour entity. Manufacturing quantity is not raw entity count.

## Entities

Every input entity has a globally unique stable `entity_id` in addition to the existing V4.9 geometry fields:

```json
{"entity_id":"E_HOLE_LEFT_1","type":"CIRCLE","role":"hole","center":[10,20],"radius":4.5}
```

All Layer-0 manufacturing entities must be owned by at least one canonical member. Adjacent Magenta `estimated_note` TEXT is annotation and may be unowned.

## Hard gates

`tools/canonical_contract.py` enforces:

- `GROUP_COUNT_CLOSURE`;
- no duplicate group/member/entity IDs;
- every active enumerable source member persists in canonical ledger;
- every PROVED source member is a PROVED source-backed canonical member;
- canceled source members are absent from canonical;
- all referenced entity IDs exist;
- no orphan manufacturing entity;
- derived-rule entities name their controlling rule and source members.

`tools/export_canonical_dxf.py` then delegates composite geometric packaging to `tools/export_dxf.py`, stamps `TRAINAICAD` XDATA `ENTITY_ID` into every saved Layer-0 entity, saves again, reopens the exact DXF and proves:

`CANONICAL_ENTITY_IDS == SAVED_DXF_LAYER0_ENTITY_IDS`.

A failure blocks delivery even for REVIEW_ONLY output. REVIEW_ONLY controls cut authorization; it does not permit silently missing PROVED members.

## Normal path vs lower-level serializer

`tools/export_dxf.py` remains a lower-level geometric packaging/round-trip component for backward-compatible tests and explicit tooling. It does not by itself prove source/member completeness. New normal CAD jobs must not call it directly.
