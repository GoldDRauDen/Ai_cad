#!/usr/bin/env python3
"""TrainAiCad V4.9: serialize checked source geometry to ONE labeled combined DXF.

Input is canonical geometry that has ALREADY passed the approved drawing
interpretation, tolerance, material, unfold and manufacturing checks.  This
serializer adds structural/packaging checks; it does NOT read or interpret PDFs.
Requires ezdxf>=1.4. See tools/DXF_INPUT_SCHEMA.md.
"""
import argparse
import json
import math
import re
from pathlib import Path

import ezdxf
from ezdxf import bbox

CHECKS = ("contour_topology", "datum", "feature_count", "unfold", "containment",
          "bend_domain", "material_rules", "slot_semantics")
TYPES = {"LWPOLYLINE", "CIRCLE", "LINE", "ARC", "POINT", "TEXT"}
CUT_ROLES = {"outer", "cutout", "hole", "slot"}


def fail(message):
    raise ValueError(message)


def number(value, context):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail(f"{context}: finite numeric value required")
    return float(value)


def point(value, context):
    if not isinstance(value, list) or len(value) != 2:
        fail(f"{context}: expected [x, y]")
    return (number(value[0], context), number(value[1], context))


def safe_name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
        fail("job_id/code: use 1-64 ASCII letters, digits, underscore or hyphen")
    return value


def signed_poly_area(vertices):
    """Exact signed area of closed bulged LWPOLYLINE (straight + circular segment)."""
    area = 0.0
    for v, w in zip(vertices, vertices[1:] + vertices[:1]):
        x, y, bulge = v
        xx, yy = w[:2]
        area += (x * yy - xx * y) / 2
        if bulge:
            chord = math.hypot(xx - x, yy - y)
            theta = 4 * math.atan(bulge)
            radius = chord / (2 * abs(math.sin(theta / 2)))
            area += radius * radius * (theta - math.sin(theta)) / 2
    return area


def validate_entity(entity, part_code, preview):
    t = entity.get("type")
    role = entity.get("role")
    if t not in TYPES or not isinstance(role, str) or not role:
        fail(f"{part_code}: invalid entity type/role")
    if entity.get("layer", "0") != "0":
        fail(f"{part_code}: all entities must use Layer 0")
    col = entity.get("color", 256)
    if col not in (1, 3, 6, 256):
        fail(f"{part_code}: unsupported color {col}; V4.6 legend is mandatory")
    if role in ("outer", "cutout", "hole", "slot") and col not in (256, 6):
        fail(f"{part_code}: cut geometry cannot be red/green")
    if role == "ordinary_point" and (t != "POINT" or col != 256):
        fail(f"{part_code}: ordinary POINT must be ByLayer")
    if role == "through_piercing" and (t != "POINT" or col != 3):
        fail(f"{part_code}: PIERCING + THROUGH HOLE must be Green POINT")
    if role == "kegaki" and col != 1:
        fail(f"{part_code}: Kegaki must be Red")
    if role == "bend" and (t != "LINE" or entity.get("linetype") != "DASHED"):
        fail(f"{part_code}: bend must be double DASHED LINEs")
    if role == "estimated" and col != 6:
        fail(f"{part_code}: estimated geometry must be Magenta")
    if t == "TEXT" and (not preview or col != 6 or role != "estimated_note"):
        fail(f"{part_code}: source TEXT only for adjacent Magenta preview notes; code labels are generated in AI_META")
    if t == "LWPOLYLINE":
        vertices = entity.get("vertices")
        if not isinstance(vertices, list) or len(vertices) < 2:
            fail(f"{part_code}: polyline requires vertices")
        for v in vertices:
            if not isinstance(v, list) or len(v) != 3:
                fail(f"{part_code}: vertex requires [x,y,bulge]")
            for n in v:
                number(n, f"{part_code} polyline")
        if role in ("outer", "cutout", "slot") and (not entity.get("closed") or len(vertices) < 3):
            fail(f"{part_code}: outer, cutout and slot must be closed polylines")
        if entity.get("closed") and vertices[0][:2] == vertices[-1][:2]:
            fail(f"{part_code}: omit duplicate closing vertex; use closed=true")
        if entity.get("closed") and role in ("outer", "cutout", "slot"):
            area = signed_poly_area(vertices)
            if (role == "outer" and area <= 0) or (role in ("cutout", "slot") and area >= 0):
                fail(f"{part_code}: wrong winding or degenerate closed {role} polyline")
    elif t == "CIRCLE":
        point(entity.get("center"), f"{part_code} circle")
        if number(entity.get("radius"), f"{part_code} radius") <= 0:
            fail(f"{part_code}: radius must be positive")
    elif t == "POINT":
        point(entity.get("point"), f"{part_code} POINT")
    elif t == "LINE":
        a = point(entity.get("start"), f"{part_code} line")
        b = point(entity.get("end"), f"{part_code} line")
        if a == b:
            fail(f"{part_code}: zero-length LINE")
    elif t == "ARC":
        point(entity.get("center"), f"{part_code} arc")
        if number(entity.get("radius"), f"{part_code} arc radius") <= 0:
            fail(f"{part_code}: arc radius must be positive")
        number(entity.get("start_angle"), f"{part_code} arc start")
        number(entity.get("end_angle"), f"{part_code} arc end")
    elif t == "TEXT":
        point(entity.get("insert"), f"{part_code} text")
        if not entity.get("text") or number(entity.get("height", 2.5), f"{part_code} text height") <= 0:
            fail(f"{part_code}: invalid TEXT")
    if role == "slot" and t != "LWPOLYLINE":
        fail(f"{part_code}: slot must be one closed LWPOLYLINE")
    if role == "outer" and t != "LWPOLYLINE":
        fail(f"{part_code}: outline must be a LWPOLYLINE")
    if role == "cutout" and t != "LWPOLYLINE":
        fail(f"{part_code}: cutout must be a LWPOLYLINE")
    if role == "hole" and t != "CIRCLE":
        fail(f"{part_code}: round hole must be a CIRCLE")
    if col == 6 and not preview:
        fail(f"{part_code}: Magenta FLAG geometry cannot enter production DXF")


def validate_job(job):
    jid = safe_name(job.get("job_id"))
    parts = job.get("parts")
    if not isinstance(parts, list) or not parts:
        fail("Job must contain a nonempty ordered parts list")
    codes = set()
    for part in parts:
        code = safe_name(part.get("code"))
        if code in codes:
            fail(f"Duplicate code {code}; use unique code for each manufacturing part")
        codes.add(code)
        if not isinstance(part.get("material"), str) or not part["material"].strip():
            fail(f"{code}: material required")
        if number(part.get("thickness_mm"), f"{code} thickness") <= 0:
            fail(f"{code}: thickness must be positive")
        state = part.get("status")
        if state not in ("PASS", "PREVIEW", "VIEWS_ONLY", "REVIEW"):
            fail(f"{code}: invalid status, expected PASS/PREVIEW/VIEWS_ONLY/REVIEW")
        checks = part.get("checks")
        permitted = ("PASS", "N/A", "FLAGGED") if state == "VIEWS_ONLY" else ("PASS", "N/A")
        if not isinstance(checks, dict) or any(checks.get(key) not in permitted for key in CHECKS):
            fail(f"{code}: all eight upstream semantic checks require explicit PASS/N/A (or VIEWS_ONLY FLAGGED) evidence")
        if state == "PASS" and (part.get("flags") or any(e == "N/A" for e in (checks[k] for k in ("contour_topology", "datum", "feature_count", "containment", "material_rules")))):
            fail(f"{code}: production PASS requires no flags and applicable critical checks")
        if state == "PREVIEW" and (not part.get("flags") or part.get("preview_reason") != "numeric_only_known_topology"):
            fail(f"{code}: preview permitted ONLY for numeric uncertainty on proved topology with flags")
        if state == "REVIEW" and (
            part.get("review_reason") != "HL_DIRECTION_UNPROVED" or not part.get("flags") or
            not part.get("grain", {}).get("is_hl") or
            part.get("grain", {}).get("direction_xy") is not None
        ):
            fail(f"{code}: REVIEW requires unresolved HL direction, not guessed geometry")
        if state == "VIEWS_ONLY" and (not part.get("flags") or part.get("preview_reason") != "separate_source_views"):
            fail(f"{code}: VIEWS_ONLY requires independently proved source views, reason and unresolved flags")
        ents = part.get("entities")
        if not isinstance(ents, list) or not ents:
            fail(f"{code}: entities required")
        for ent in ents:
            validate_entity(ent, code, state != "PASS")
            if state == "VIEWS_ONLY" and ent["type"] != "TEXT":
                safe_name(ent.get("view_id"))
        if state != "VIEWS_ONLY" and sum(ent.get("role") == "outer" for ent in ents) != 1:
            fail(f"{code}: exactly one proved closed outside contour required")
        if state == "VIEWS_ONLY" and not any(ent["type"] != "TEXT" for ent in ents):
            fail(f"{code}: no proved source-view geometry")
        if state == "PREVIEW" and not (any(e.get("color") == 6 for e in ents) and any(e.get("type") == "TEXT" for e in ents)):
            fail(f"{code}: preview requires Magenta geometry AND adjacent Magenta TEXT")
    return jid


def add_entity(msp, ent, dx=0.0, dy=0.0):
    attrs = {"layer": "0"}
    if ent.get("color", 256) != 256:
        attrs["color"] = ent["color"]
    if ent.get("linetype"):
        attrs["linetype"] = ent["linetype"]
    def move(v):
        return (v[0] + dx, v[1] + dy)
    t = ent["type"]
    if t == "LWPOLYLINE":
        return msp.add_lwpolyline([(v[0] + dx, v[1] + dy, v[2]) for v in ent["vertices"]],
                                  format="xyb", close=ent.get("closed", False), dxfattribs=attrs)
    if t == "CIRCLE":
        return msp.add_circle(move(ent["center"]), ent["radius"], dxfattribs=attrs)
    if t == "LINE":
        return msp.add_line(move(ent["start"]), move(ent["end"]), dxfattribs=attrs)
    if t == "ARC":
        return msp.add_arc(move(ent["center"]), ent["radius"],
                           ent["start_angle"], ent["end_angle"], dxfattribs=attrs)
    if t == "POINT":
        return msp.add_point(move(ent["point"]), dxfattribs=attrs)
    if t == "TEXT":
        attrs["height"] = ent.get("height", 2.5)
        attrs["insert"] = move(ent["insert"])
        return msp.add_text(ent["text"], dxfattribs=attrs)
    fail(f"Unknown entity type {t}")


def new_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LUNITS"] = 2
    doc.header["$LUPREC"] = 2
    if "DASHED" not in doc.linetypes:
        doc.linetypes.new("DASHED", dxfattribs={"pattern": [4.0, 2.0, -2.0], "description": "2 mm dash, 2 mm gap"})
    return doc


def extents_of(doc):
    ext = bbox.extents(doc.modelspace(), fast=False)
    if not ext.has_data:
        fail("No bounded CAD geometry to export")
    return [round(ext.extmin.x, 6), round(ext.extmin.y, 6),
            round(ext.extmax.x, 6), round(ext.extmax.y, 6)]


def entity_signature(ent):
    """Coordinate/attribute fingerprint including arc bulges for saved-DXF roundtrip."""
    t = ent.dxftype()
    attrs = (t, ent.dxf.layer, ent.dxf.get("color", 256), ent.dxf.get("linetype", "BYLAYER"))
    def xy(v):
        return (round(v[0], 6), round(v[1], 6))
    if t == "LWPOLYLINE":
        geometry = (ent.closed, tuple((round(x, 6), round(y, 6), round(b, 8)) for x, y, b in ent.get_points("xyb")))
    elif t == "CIRCLE":
        geometry = (xy(ent.dxf.center), round(ent.dxf.radius, 6))
    elif t == "POINT":
        geometry = xy(ent.dxf.location)
    elif t == "LINE":
        geometry = (xy(ent.dxf.start), xy(ent.dxf.end))
    elif t == "ARC":
        geometry = (xy(ent.dxf.center), round(ent.dxf.radius, 6), round(ent.dxf.start_angle, 6), round(ent.dxf.end_angle, 6))
    elif t == "TEXT":
        geometry = (xy(ent.dxf.insert), ent.dxf.text, round(ent.dxf.height, 6))
    else:
        fail(f"Unexpected written DXF entity {t}")
    return (attrs, geometry)


def write_and_audit(doc, target, expected_count):
    before = [entity_signature(ent) for ent in doc.modelspace()]
    doc.saveas(target)
    loaded = ezdxf.readfile(target)
    errors = loaded.audit()
    if errors.has_errors:
        fail(f"DXF audit failed: {target.name}")
    ents = list(loaded.modelspace())
    if len(ents) != expected_count or any(ent.dxf.layer != "0" and
            not (ent.dxf.layer == "AI_META" and ent.dxftype() == "TEXT") for ent in ents):
        fail(f"DXF read-back/layer/entity-count failure: {target.name}")
    if "AI_META" in loaded.layers and loaded.layers.get("AI_META").dxf.get("plot", 1) != 0:
        fail(f"AI_META must be non-plot annotation: {target.name}")
    if loaded.header["$INSUNITS"] != 4:
        fail(f"DXF unit failure: {target.name}")
    if [entity_signature(ent) for ent in ents] != before:
        fail(f"DXF entity/coordinate/attribute roundtrip mismatch: {target.name}")
    return extents_of(loaded)


def export_dual_job(job, output_dir, gap_mm=10.0):
    if any(p.get("status") == "VIEWS_ONLY" for p in job.get("parts", [])):
        fail("Legacy dual export does not support VIEWS_ONLY; use default single composite")
    jid = validate_job(job)
    gap_mm = number(gap_mm, "gap_mm")
    if gap_mm < 10:
        fail("Composite drawing requires at least 10 mm clearance between part bounding boxes")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for part in job["parts"]:
        preview = part["status"] == "PREVIEW"
        doc = new_doc()
        for ent in part["entities"]:
            add_entity(doc.modelspace(), ent)
        suffix = "_PREVIEW" if preview else ""
        name = f"{jid}_{part['code']}{suffix}.dxf"
        bounds = write_and_audit(doc, out / name, len(part["entities"]))
        records.append({"code": part["code"], "material": part["material"],
                        "thickness_mm": part["thickness_mm"], "status": part["status"],
                        "filename": name, "entity_count": len(part["entities"]),
                        "bbox_mm": bounds, "flags": part.get("flags", []),
                        "checks": part["checks"]})
    combined = {}
    for state, suffix in (("PASS", "ALL"), ("PREVIEW", "PREVIEW_ALL")):
        chosen = [(p, r) for p, r in zip(job["parts"], records) if p["status"] == state]
        if not chosen:
            continue
        total_height = sum(r["bbox_mm"][3] - r["bbox_mm"][1] for _, r in chosen) + gap_mm * (len(chosen) - 1)
        cursor = total_height
        merged = new_doc()
        positions = []
        for part, rec in chosen:
            xmin, ymin, xmax, ymax = rec["bbox_mm"]
            h = ymax - ymin
            bottom = cursor - h
            dx, dy = -xmin, bottom - ymin
            for ent in part["entities"]:
                add_entity(merged.modelspace(), ent, dx, dy)
            positions.append({"code": rec["code"], "filename": rec["filename"],
                              "translation_mm": [round(dx, 6), round(dy, 6)],
                              "combined_bbox_mm": [0, round(bottom, 6), round(xmax - xmin, 6), round(cursor, 6)]})
            cursor = bottom - gap_mm
        name = f"{jid}_{suffix}.dxf"
        write_and_audit(merged, out / name, sum(r["entity_count"] for _, r in chosen))
        combined[state] = {"filename": name, "layout": "top-to-bottom in job.parts order",
                           "clearance_mm": gap_mm, "parts": positions}
    manifest = {"contract": "TrainAiCad-DXF-V4.7", "job_id": jid,
                "coordinate_units": "mm", "layer": "0", "source": "canonical independently checked geometry",
                "parts": records, "combined": combined,
                "warning": "PREVIEW files are NOT production CAD; never mix preview parts into *_ALL.dxf"}
    (out / f"{jid}_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest



def source_view_boxes(part):
    """Source-view extents only; used to prove independently separated projections."""
    groups = {}
    for ent in part["entities"]:
        if ent["type"] != "TEXT":
            groups.setdefault(ent["view_id"], []).append(ent)
    boxes = {}
    for vid, ents in groups.items():
        doc = new_doc()
        for ent in ents:
            add_entity(doc.modelspace(), ent)
        boxes[vid] = extents_of(doc)
    ids = list(boxes)
    for i, first in enumerate(ids):
        for second in ids[i + 1:]:
            a, b = boxes[first], boxes[second]
            x_gap = max(b[0] - a[2], a[0] - b[2])
            y_gap = max(b[1] - a[3], a[1] - b[3])
            if max(x_gap, y_gap) < 10 - 1e-6:
                fail(f"{part['code']}: source views {first}/{second} must be separated by >=10 mm")
    return boxes


def export_single_job(job, output_dir, gap_mm=10.0, write_manifest=False):
    """One composite, source-order labels, all-code review downgrade on ANY FLAG."""
    jid = validate_job(job)
    gap_mm = number(gap_mm, "gap_mm")
    if gap_mm < 10:
        fail("Combined geometric cluster gap must be >=10 mm")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    parts = job["parts"]
    review = any(p["status"] != "PASS" or p.get("flags") for p in parts)
    records = []
    for p in parts:
        scratch = new_doc()
        for e in p["entities"]:
            add_entity(scratch.modelspace(), e)
        view_boxes = source_view_boxes(p) if p["status"] == "VIEWS_ONLY" else {}
        records.append({"code": p["code"], "material": p["material"],
                        "thickness_mm": p["thickness_mm"], "status": p["status"],
                        "bbox_mm": extents_of(scratch), "entity_count": len(p["entities"]),
                        "flags": p.get("flags", []), "checks": p["checks"],
                        "source_view_boxes": view_boxes})
    total_height = sum(r["bbox_mm"][3] - r["bbox_mm"][1] for r in records) + gap_mm * (len(records) - 1)
    merged = new_doc()
    merged.layers.new("AI_META", dxfattribs={"color": 8, "plot": 0})
    merged.appids.new("AICAD")
    msp = merged.modelspace()
    layout = []
    expected_geometry = []
    expected_labels = []
    cursor = total_height
    annotation_count = 0

    def label(text_value, where, color=8):
        nonlocal annotation_count
        obj = msp.add_text(text_value, dxfattribs={
            "layer": "AI_META", "color": color, "height": 3.0, "insert": where})
        obj.set_xdata("AICAD", [(1000, "NON_CUT_ANNOTATION")])
        annotation_count += 1

    for p, rec in zip(parts, records):
        xmin, ymin, xmax, ymax = rec["bbox_mm"]
        h = ymax - ymin
        bottom = cursor - h
        dx, dy = -xmin, bottom - ymin
        before_count = len(expected_geometry)
        for e in p["entities"]:
            obj = add_entity(msp, e, dx, dy)
            expected_geometry.append(entity_signature(obj))
        if len(expected_geometry) - before_count != rec["entity_count"]:
            fail(f"{p['code']}: source-to-composite entity count changed")
        status_suffix = "" if p["status"] == "PASS" else " [FLAG]"
        if p["status"] == "VIEWS_ONLY":
            status_suffix = " [VIEWS_ONLY - FLAG]"
        code_label = p["code"] + status_suffix
        label(code_label, (0.0, cursor + 2))
        expected_labels.append(code_label)
        if p.get("flags"):
            label(p["code"] + " FLAG: SEE STAGE1; NO CUT", (max(xmax - xmin, 20), cursor + 2), color=6)
        if p["status"] == "VIEWS_ONLY":
            for view_id, bounds in rec["source_view_boxes"].items():
                label(p["code"] + " VIEW " + view_id, (bounds[0] + dx, bounds[3] + dy + 2))
        placed = [0.0, bottom, xmax - xmin, cursor]
        layout.append({"code": p["code"], "status": p["status"],
                       "translation_mm": [round(dx, 6), round(dy, 6)],
                       "combined_bbox_mm": [round(v, 6) for v in placed],
                       "entity_count": rec["entity_count"]})
        cursor = bottom - gap_mm
    if review:
        label("REVIEW ONLY - NO CUT - UNRESOLVED CODES PRESENT", (0, total_height + 12), color=6)
    filename = f"{jid}_ALL_REVIEW_ONLY.dxf" if review else f"{jid}_ALL.dxf"
    target = out / filename
    write_and_audit(merged, target, len(expected_geometry) + annotation_count)
    loaded = ezdxf.readfile(target)
    actual_geometry = [entity_signature(e) for e in loaded.modelspace() if e.dxf.layer == "0"]
    if actual_geometry != expected_geometry:
        fail("Combined source geometry does not match canonical translated part-local geometry")
    labels = [e.dxf.text for e in loaded.modelspace() if e.dxf.layer == "AI_META"]
    if [x for x in labels if x in expected_labels] != expected_labels:
        fail("Missing or misordered code labels in combined DXF")
    if review and "REVIEW ONLY - NO CUT - UNRESOLVED CODES PRESENT" not in labels:
        fail("REVIEW_ONLY output missing global NO CUT label")
    for upper, lower in zip(layout, layout[1:]):
        if upper["combined_bbox_mm"][1] - lower["combined_bbox_mm"][3] < gap_mm - 1e-5:
            fail("Combined source-code clusters overlap or lack required gap")
    manifest = {"contract": "TrainAiCad-DXF-V4.9", "job_id": jid,
                "coordinate_units": "mm", "layout": "code-labeled top-to-bottom",
                "status": "REVIEW_ONLY" if review else "PASS",
                "filename": filename, "parts": records, "positions": layout,
                "source": "independently checked canonical geometry",
                "warning": "AI_META is non-cut; review-only files are NEVER production CAD"}
    if write_manifest:
        (out / f"{jid}_MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def export_job(job, output_dir, gap_mm=10.0, mode="single", write_manifest=False):
    if mode == "dual":
        return export_dual_job(job, output_dir, gap_mm)
    if mode != "single":
        fail("mode must be single or dual")
    return export_single_job(job, output_dir, gap_mm, write_manifest=write_manifest)


def main():
    ap = argparse.ArgumentParser(description="V4.9: ONE code-labeled top-to-bottom combined DXF by default")
    ap.add_argument("input_json", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--gap-mm", type=float, default=10.0)
    ap.add_argument("--mode", choices=["single", "dual"], default="single", help="dual is explicit-request legacy V4.7 export")
    ap.add_argument("--write-manifest", action="store_true", help="optional external JSON for single composite")
    args = ap.parse_args()
    manifest = export_job(json.loads(args.input_json.read_text(encoding="utf-8")), args.output_dir,
                          args.gap_mm, mode=args.mode, write_manifest=args.write_manifest)
    files = ([manifest["filename"]] if args.mode == "single" else
             [p["filename"] for p in manifest["parts"]] +
             [c["filename"] for c in manifest["combined"].values()])
    if args.mode == "single" and args.write_manifest:
        files.append(manifest["job_id"] + "_MANIFEST.json")
    print(json.dumps({"job_id": manifest["job_id"], "files": files}, ensure_ascii=False))


if __name__ == "__main__":
    main()
