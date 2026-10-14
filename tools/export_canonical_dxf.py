#!/usr/bin/env python3
"""V4.31 normal production entrypoint: canonical completeness -> DXF -> XDATA read-back."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import ezdxf

from canonical_contract import CONTRACT, CanonicalContractError, validate_canonical_job
from export_dxf import entity_signature, export_job
from export_job_artifacts import export_part_artifacts
from holistic_engineering_guard import canonical_job_anomalies

APPID = "TRAINAICAD"


def fail(message: str) -> None:
    raise CanonicalContractError(message)


def _owner_map(job: dict) -> dict[str, list[str]]:
    owners: dict[str, list[str]] = {}
    for part in job["parts"]:
        for member in part["canonical_members"]:
            cid = member["canonical_member_id"]
            for eid in member.get("entity_ids", []):
                owners.setdefault(eid, []).append(cid)
    return owners


def _stamp_and_verify(job: dict, manifest: dict, output_dir: Path, validation: dict) -> dict:
    target = output_dir / manifest["filename"]
    doc = ezdxf.readfile(target)
    if APPID not in doc.appids:
        doc.appids.new(APPID)
    geometry = [e for e in doc.modelspace() if e.dxf.layer == "0"]
    expected_ids = validation["entity_ids"]
    if len(geometry) != len(expected_ids):
        fail(f"CANONICAL_SERIALIZATION_COMPLETENESS_FAIL expected={len(expected_ids)} saved={len(geometry)}")

    before = [entity_signature(e) for e in geometry]
    owners = _owner_map(job)
    for ent, eid in zip(geometry, expected_ids):
        member_ids = owners.get(eid, [])
        ent.set_xdata(APPID, [
            (1000, f"ENTITY_ID={eid}"),
            (1000, "CANONICAL_MEMBER_IDS=" + ",".join(member_ids)),
        ])
    doc.saveas(target)

    loaded = ezdxf.readfile(target)
    audit = loaded.audit()
    if audit.has_errors:
        fail(f"V4.31 saved-DXF audit failed: {target.name}")
    saved = [e for e in loaded.modelspace() if e.dxf.layer == "0"]
    after = [entity_signature(e) for e in saved]
    if after != before:
        fail("V4.31 XDATA stamping changed canonical geometry")

    read_ids = []
    for ent in saved:
        try:
            tags = ent.get_xdata(APPID)
        except Exception as exc:  # ezdxf raises DXFValueError when missing
            raise CanonicalContractError("saved Layer-0 entity missing TRAINAICAD XDATA") from exc
        values = [tag.value for tag in tags if tag.code == 1000]
        eid = next((v.split("=", 1)[1] for v in values if isinstance(v, str) and v.startswith("ENTITY_ID=")), None)
        if not eid:
            fail("saved Layer-0 entity missing ENTITY_ID XDATA")
        read_ids.append(eid)
    if read_ids != expected_ids or set(read_ids) != set(expected_ids):
        fail("CANONICAL_ENTITY_IDS_EQ_SAVED_DXF_ENTITY_IDS failed")

    manifest["canonical_contract"] = validation["contract"]
    manifest["canonical_completeness"] = {
        "status": "PASS",
        "source_to_canonical": "PASS",
        "canonical_to_saved_dxf_entity_ids": "PASS",
        "parts": validation["parts"],
    }
    return manifest


def export_canonical_job(job: dict, output_dir, gap_mm=10.0, write_manifest=False,
                         composite_only=False) -> dict:
    """Validate full member ledger, serialize single composite, stamp/read back entity IDs."""
    validation = validate_canonical_job(job)
    source_anomalies = canonical_job_anomalies(job)
    if source_anomalies:
        fail("SOURCE_SEMANTIC_GUARD_FAIL: " + "; ".join(source_anomalies))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = export_job(job, out, gap_mm=gap_mm, mode="single", write_manifest=False)
    manifest = _stamp_and_verify(job, manifest, out, validation)
    manifest["artifacts"] = export_part_artifacts(job, out, composite_only=composite_only)
    # Avoid stale production composites after PASS -> REVIEW (or reverse).
    obsolete = (f"{manifest['job_id']}_ALL.dxf"
                if manifest["status"] == "REVIEW_ONLY"
                else f"{manifest['job_id']}_ALL_REVIEW_ONLY.dxf")
    (out / obsolete).unlink(missing_ok=True)
    if write_manifest:
        (out / f"{manifest['job_id']}_MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description="V4.31 canonical-member-complete single composite DXF")
    ap.add_argument("input_json", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--gap-mm", type=float, default=10.0)
    ap.add_argument("--write-manifest", action="store_true")
    ap.add_argument("--composite-only", action="store_true", help="Emit combined DXF and per-code JSON only")
    args = ap.parse_args()
    job = json.loads(args.input_json.read_text(encoding="utf-8"))
    manifest = export_canonical_job(job, args.output_dir, args.gap_mm, args.write_manifest,
                                    composite_only=args.composite_only)
    print(json.dumps({
        "job_id": manifest["job_id"],
        "file": manifest["filename"],
        "canonical_contract": manifest["canonical_contract"],
        "completeness": manifest["canonical_completeness"]["status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
