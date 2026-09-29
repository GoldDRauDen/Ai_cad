#!/usr/bin/env python3
"""Thin MCP bridge around TrainAiCad's approved DXF serializer.

Commands:
  export <input_json> <output_dir>
  audit <dxf_path>

All JSON output is single-line on stdout. Errors are raised to stderr/nonzero.
"""
import json
import sys
from pathlib import Path

import ezdxf

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from export_dxf import export_job  # noqa: E402


def cmd_export(input_json: str, output_dir: str):
    payload = json.loads(Path(input_json).read_text(encoding="utf-8"))
    manifest = export_job(payload, Path(output_dir), mode="single", write_manifest=True)
    print(json.dumps({
        "ok": True,
        "manifest": manifest,
        "dxf_path": str((Path(output_dir) / manifest["filename"]).resolve()),
        "manifest_path": str((Path(output_dir) / f'{manifest["job_id"]}_MANIFEST.json').resolve()),
    }, ensure_ascii=False))


def cmd_audit(dxf_path: str):
    path = Path(dxf_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    doc = ezdxf.readfile(path)
    auditor = doc.audit()
    msp = list(doc.modelspace())
    layers = {}
    labels = []
    by_type = {}
    for ent in msp:
        by_type[ent.dxftype()] = by_type.get(ent.dxftype(), 0) + 1
        layer = ent.dxf.layer
        layers[layer] = layers.get(layer, 0) + 1
        if layer == "AI_META" and ent.dxftype() == "TEXT":
            labels.append(ent.dxf.text)

    ai_meta_plot = None
    if "AI_META" in doc.layers:
        ai_meta_plot = int(doc.layers.get("AI_META").dxf.get("plot", 1))

    print(json.dumps({
        "ok": not auditor.has_errors,
        "audit_error_count": len(auditor.errors),
        "audit_fix_count": len(auditor.fixes),
        "insunits": int(doc.header.get("$INSUNITS", 0)),
        "entity_count": len(msp),
        "layers": layers,
        "entity_types": by_type,
        "labels": labels,
        "ai_meta_plot": ai_meta_plot,
        "path": str(path),
    }, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: dxf_bridge.py export <json> <outdir> | audit <dxf>")
    cmd = sys.argv[1]
    if cmd == "export" and len(sys.argv) == 4:
        cmd_export(sys.argv[2], sys.argv[3])
    elif cmd == "audit" and len(sys.argv) == 3:
        cmd_audit(sys.argv[2])
    else:
        raise SystemExit("invalid command/arguments")


if __name__ == "__main__":
    main()
