#!/usr/bin/env python3
"""V4.31 source-group/member -> canonical-entity completeness contract."""
from __future__ import annotations

import re
from collections import defaultdict

from weld_kegaki_guard import WeldKegakiError, validate_weld_kegaki

CONTRACT = "TrainAiCad-CANONICAL-V4.31"
SOURCE_STATUSES = {"PROVED", "FLAGGED", "CANCELED"}
CANON_SOURCE_STATUSES = {"PROVED", "PREVIEW", "FLAGGED_NO_GEOMETRY", "SOURCE_VIEW"}
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class CanonicalContractError(ValueError):
    pass


def fail(message: str) -> None:
    raise CanonicalContractError(message)


def ident(value, context: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        fail(f"{context}: stable ASCII id required")
    return value


def _members_of(group):
    members = group.get("members")
    if not isinstance(members, list):
        fail(f"{group.get('group_id', '?')}: members list required")
    return members


def validate_part(part: dict, customer_code: str | None = None) -> dict:
    code = ident(part.get("code"), "part code")
    entities = part.get("entities")
    if not isinstance(entities, list) or not entities:
        fail(f"{code}: canonical entities required")

    entity_ids = []
    entity_by_id = {}
    for ent in entities:
        eid = ident(ent.get("entity_id"), f"{code} entity_id")
        if eid in entity_by_id:
            fail(f"{code}: duplicate entity_id {eid}")
        entity_ids.append(eid)
        entity_by_id[eid] = ent

    groups = part.get("source_groups")
    if not isinstance(groups, list) or not groups:
        fail(f"{code}: source_groups ledger required")

    source_member = {}
    source_group = {}
    group_member_ids = defaultdict(list)
    unknown_quantity_groups = set()
    for group in groups:
        gid = ident(group.get("group_id"), f"{code} group_id")
        if gid in source_group:
            fail(f"{code}: duplicate source group {gid}")
        status = group.get("status")
        family = group.get("family")
        if status not in SOURCE_STATUSES or not isinstance(family, str) or not family:
            fail(f"{code}/{gid}: family and source status required")
        source_group[gid] = group
        members = _members_of(group)
        qty = group.get("source_quantity")
        if qty is None:
            unknown_quantity_groups.add(gid)
        elif not isinstance(qty, int) or isinstance(qty, bool) or qty < 0:
            fail(f"{code}/{gid}: source_quantity must be non-negative integer or null")
        elif qty != len(members):
            fail(f"{code}/{gid}: GROUP_COUNT_CLOSURE source_quantity={qty} members={len(members)}")
        for member in members:
            mid = ident(member.get("member_id"), f"{code}/{gid} member_id")
            if mid in source_member:
                fail(f"{code}: duplicate source member {mid}")
            mstatus = member.get("status", status)
            if mstatus not in SOURCE_STATUSES:
                fail(f"{code}/{gid}/{mid}: invalid source member status")
            source_member[mid] = {"group_id": gid, "status": mstatus, "family": family}
            group_member_ids[gid].append(mid)

    canonical = part.get("canonical_members")
    if not isinstance(canonical, list):
        fail(f"{code}: canonical_members ledger required")

    canonical_ids = set()
    source_backed = {}
    entity_owners = defaultdict(list)
    for member in canonical:
        cid = ident(member.get("canonical_member_id"), f"{code} canonical_member_id")
        if cid in canonical_ids:
            fail(f"{code}: duplicate canonical_member_id {cid}")
        canonical_ids.add(cid)
        origin = member.get("origin")
        status = member.get("status")
        eids = member.get("entity_ids", [])
        if not isinstance(eids, list) or len(eids) != len(set(eids)):
            fail(f"{code}/{cid}: entity_ids must be a unique list")
        for eid in eids:
            ident(eid, f"{code}/{cid} entity_id")
            if eid not in entity_by_id:
                fail(f"{code}/{cid}: canonical member references missing entity {eid}")
            entity_owners[eid].append(cid)

        if origin == "SOURCE":
            mid = ident(member.get("source_member_id"), f"{code}/{cid} source_member_id")
            if mid not in source_member:
                fail(f"{code}/{cid}: unknown source member {mid}")
            if mid in source_backed:
                fail(f"{code}: source member {mid} mapped more than once")
            if member.get("group_id") != source_member[mid]["group_id"]:
                fail(f"{code}/{cid}: source group ownership mismatch for {mid}")
            if status not in CANON_SOURCE_STATUSES:
                fail(f"{code}/{cid}: invalid source-backed canonical status")
            src_status = source_member[mid]["status"]
            if src_status == "PROVED" and status != "PROVED":
                fail(f"{code}/{mid}: PROVED source member is not PROVED canonical")
            if src_status == "FLAGGED" and status not in {"PREVIEW", "FLAGGED_NO_GEOMETRY", "SOURCE_VIEW"}:
                fail(f"{code}/{mid}: FLAGGED source member lost its uncertainty state")
            if src_status == "CANCELED":
                fail(f"{code}/{mid}: canceled source member emitted into canonical model")
            if status == "PROVED" and not eids:
                fail(f"{code}/{mid}: PROVED canonical member requires physical entity_ids")
            if status in {"PREVIEW", "SOURCE_VIEW"} and not eids:
                fail(f"{code}/{mid}: {status} canonical member requires entity_ids")
            if status == "FLAGGED_NO_GEOMETRY" and eids:
                fail(f"{code}/{mid}: FLAGGED_NO_GEOMETRY cannot own fabricated geometry")
            source_backed[mid] = member
        elif origin == "DERIVED_RULE":
            if not isinstance(member.get("controlling_rule"), str) or not member["controlling_rule"]:
                fail(f"{code}/{cid}: DERIVED_RULE requires controlling_rule")
            source_ids = member.get("source_member_ids")
            if not isinstance(source_ids, list) or not source_ids:
                fail(f"{code}/{cid}: DERIVED_RULE requires source_member_ids")
            for mid in source_ids:
                if mid not in source_member or source_member[mid]["status"] == "CANCELED":
                    fail(f"{code}/{cid}: invalid DERIVED_RULE source member {mid}")
            if status not in {"PROVED", "PREVIEW"} or not eids:
                fail(f"{code}/{cid}: DERIVED_RULE requires physical PROVED/PREVIEW entities")
        else:
            fail(f"{code}/{cid}: origin must be SOURCE or DERIVED_RULE")

    active_source = {mid for mid, rec in source_member.items() if rec["status"] != "CANCELED"}
    if active_source != set(source_backed):
        missing = sorted(active_source - set(source_backed))
        extra = sorted(set(source_backed) - active_source)
        fail(f"{code}: SOURCE_FEATURE_COMPLETENESS_FAIL missing={missing} extra={extra}")

    proved_source = {mid for mid, rec in source_member.items() if rec["status"] == "PROVED"}
    proved_canonical = {mid for mid, rec in source_backed.items() if rec.get("status") == "PROVED"}
    if proved_source != proved_canonical:
        fail(f"{code}: PROVED_SOURCE_MEMBERS_EQ_CANONICAL failed")

    # Every manufacturing Layer-0 input entity must belong to a canonical member.
    # Adjacent preview note TEXT is annotation, not a manufacturing operation.
    for eid, ent in entity_by_id.items():
        annotation = ent.get("type") == "TEXT" and ent.get("role") == "estimated_note"
        if not annotation and eid not in entity_owners:
            fail(f"{code}: orphan canonical manufacturing entity {eid}")

    # Independent weld-site census is checked against real KEGAKI source
    # members and canonical RED marking, not merely source/canonical equality.
    try:
        weld_closure = validate_weld_kegaki(part, customer_code)
    except WeldKegakiError as exc:
        fail(str(exc))

    return {
        "code": code,
        "weld_kegaki_closure": weld_closure,
        "source_group_count": len(groups),
        "source_member_count": len(source_member),
        "proved_source_member_count": len(proved_source),
        "canonical_member_count": len(canonical),
        "canonical_entity_count": len(entity_ids),
        "entity_ids": entity_ids,
        "entity_owners": {k: list(v) for k, v in entity_owners.items()},
        "unknown_quantity_groups": sorted(unknown_quantity_groups),
    }


def validate_canonical_job(job: dict) -> dict:
    if job.get("canonical_contract") != CONTRACT:
        fail(f"job canonical_contract must be {CONTRACT}")
    parts = job.get("parts")
    if not isinstance(parts, list) or not parts:
        fail("canonical job requires parts")
    raw_customer_code = job.get("customer_code")
    if raw_customer_code is not None:
        if isinstance(raw_customer_code, bool) or not str(raw_customer_code).strip().isdigit():
            fail("customer_code must be the numeric code from job statistics")
        customer_code = str(int(str(raw_customer_code).strip()))
    else:
        customer_code = None
    records = [validate_part(part, customer_code=customer_code) for part in parts]
    all_ids = []
    for rec in records:
        all_ids.extend(rec["entity_ids"])
    if len(all_ids) != len(set(all_ids)):
        fail("entity_id must be globally unique across the composite job")
    return {"contract": CONTRACT, "parts": records, "entity_ids": all_ids}
