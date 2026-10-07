#!/usr/bin/env python3
"""V4.33 source-only snapshot and post-reference provenance guard."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable

SCHEMA = "TrainAiCad-REFERENCE-EXPOSURE-V4.33"
NON_REFERENCE_PROVENANCE = {
    "PRINTED",
    "HANDWRITTEN-REVISION",
    "DERIVED",
    "CUSTOMER_DATA",
    "USER_CONFIRMED",
}
UNRESOLVED_STATES = {
    "UNKNOWN",
    "FLAGGED",
    "SOURCE_ONLY_UNRESOLVED",
    "CUSTOMER_CONFIRMATION_PENDING",
}
PROVED_STATES = {"PROVED", "SOURCE_ONLY_SOLVED"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze_snapshot(payload: Dict[str, Any], source_files: Iterable[str] = ()) -> Dict[str, Any]:
    out = dict(payload)
    out["reference_guard_schema"] = SCHEMA
    out["reference_exposed"] = False
    out["frozen"] = True
    out["source_hashes"] = {
        str(Path(p)): sha256_file(Path(p))
        for p in source_files
    }
    return out


def _claim_map(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    claims = payload.get("claims", [])
    return {str(c["claim_id"]): c for c in claims}


def audit_transition(before: Dict[str, Any], after: Dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if before.get("reference_guard_schema") != SCHEMA or not before.get("frozen"):
        errors.append("SOURCE_ONLY_SNAPSHOT_NOT_FROZEN")
        return errors
    if before.get("reference_exposed") is not False:
        errors.append("SOURCE_ONLY_SNAPSHOT_ALREADY_REFERENCE_EXPOSED")

    prior = _claim_map(before)
    later = _claim_map(after)
    for claim_id, new in later.items():
        old = prior.get(claim_id)
        if not old:
            continue
        old_state = str(old.get("status", "UNKNOWN"))
        new_state = str(new.get("status", "UNKNOWN"))
        if old_state in UNRESOLVED_STATES and new_state in PROVED_STATES:
            old_provenance = set(old.get("evidence_provenance", []))
            provenance = set(new.get("evidence_provenance", []))
            new_nonref_provenance = provenance.intersection(NON_REFERENCE_PROVENANCE) - old_provenance
            old_keys = set(old.get("evidence_keys", []))
            new_keys = set(new.get("evidence_keys", []))
            has_new_evidence_key = bool(new_keys - old_keys)
            if not new_nonref_provenance or not has_new_evidence_key:
                errors.append(f"POST_REFERENCE_SOURCE_REWRITE:{claim_id}")

    for claim_id, new in later.items():
        if new.get("sample_flagged") and new.get("status") in PROVED_STATES:
            errors.append(f"SAMPLE_FLAGGED_PROMOTED_TO_PROVED:{claim_id}")
    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    fz = sub.add_parser("freeze")
    fz.add_argument("input_json")
    fz.add_argument("output_json")
    fz.add_argument("--source-file", action="append", default=[])

    au = sub.add_parser("audit")
    au.add_argument("before_json")
    au.add_argument("after_json")

    args = ap.parse_args()
    if args.cmd == "freeze":
        payload = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        frozen = freeze_snapshot(payload, args.source_file)
        Path(args.output_json).write_text(
            json.dumps(frozen, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("PASS: SOURCE_ONLY_SNAPSHOT frozen")
        return

    before = json.loads(Path(args.before_json).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after_json).read_text(encoding="utf-8"))
    errors = audit_transition(before, after)
    if errors:
        raise SystemExit("FAIL: " + "; ".join(errors))
    print("PASS: no post-reference source rewrite")


if __name__ == "__main__":
    main()
