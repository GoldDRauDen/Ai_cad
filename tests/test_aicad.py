"""AICad completeness, routing parity and retrieval quality tests.

Run:  python3 -m pytest -q tests/test_aicad.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import aicad  # noqa: E402

CLI = [sys.executable, str(ROOT / "tools/aicad.py")]


@pytest.fixture(scope="module", autouse=True)
def built_index():
    subprocess.run(CLI + ["build"], check=True, capture_output=True, cwd=ROOT)


@pytest.fixture(scope="module")
def rows():
    return aicad.build_rows()


def test_verify_passes_on_clean_tree():
    proc = subprocess.run(CLI + ["verify"], capture_output=True, text=True, cwd=ROOT)
    report = json.loads(proc.stdout)
    assert proc.returncode == 0, report["failures"]
    assert report["status"] == "PASS"


def test_every_text_file_reconstructs_byte_exact(rows):
    chunks_by_path: dict[str, list[str]] = {}
    for c in rows["chunks"]:
        chunks_by_path.setdefault(c["path"], []).append(c["text"])
    checked = 0
    for f in rows["files"]:
        if f["binary"]:
            continue
        disk = (ROOT / f["path"]).read_text(encoding="utf-8")
        assert "".join(chunks_by_path.get(f["path"], [])) == disk, f["path"]
        checked += 1
    assert checked > 200


def test_no_silent_rule_gaps(rows):
    declared = {g["path"] for g in rows["gaps"]["rule_gaps"]}
    unrouted = {f["path"] for f in rows["files"]
                if f["route_state"] in ("UNROUTED", "known_gap")}
    assert unrouted == declared, (unrouted - declared, declared - unrouted)


def test_every_router_path_is_indexed_and_routed(rows):
    indexed = {f["path"]: f for f in rows["files"]}
    for p in rows["routed"]:
        assert p in indexed, p
        if indexed[p]["kind"] == "rule":
            assert indexed[p]["route_state"] == "routed", p
        else:
            assert indexed[p]["kind"] in ("router", "entry", "tool", "schema", "doc"), p


def test_every_tool_has_declared_role(rows):
    declared = {a["path"]: a["role"] for a in rows["gaps"]["tool_acks"]}
    tools = {f["path"] for f in rows["files"] if f["kind"] == "tool"}
    assert tools == set(declared)
    assert set(declared.values()) <= {"production", "audit"}


def test_resolver_output_is_indexed_and_routed(rows):
    """The inherited resolver and the index must agree on every path it returns."""
    indexed = {f["path"]: f for f in rows["files"]}
    census = {
        "source_mode": "PDF_DATA_RAW",
        "part_mode": "BEND",
        "reference_present": "NO",
        "customer_code": None,
        "source_manufacturing_notes": [],
        "features": {},
    }
    families = ("HOLE TAP SLOT_STRAIGHT CURVED_SLOT KEGAKI PIASU SLIT_RELIEF RIB "
                "FORMING_FEATURES L_PROFILE U_PROFILE MULTI_FACE_PROFILE STEPPED_NOTCHED "
                "CHAMFER_FILLET HEMMING Z_BEND ACUTE_BEND_LT85 BOXMET MATERIAL_RULES "
                "NOBI REVISION_CANCELLATION").split()
    for fam in families:
        census["features"][fam] = {"state": "NO", "evidence": []}
    for fam in ("HOLE", "KEGAKI", "MATERIAL_RULES", "NOBI"):
        census["features"][fam]["state"] = "YES"
    census_path = ROOT / "build" / "census_test.json"
    census_path.parent.mkdir(exist_ok=True)
    census_path.write_text(json.dumps(census), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/resolve_rules.py"), str(census_path)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    paths = set(plan["rule_paths"])
    assert paths, "resolver returned no rule paths"
    for p in paths:
        assert p in indexed, f"resolver path not indexed: {p}"
    census_path.unlink()


def test_rule_command_returns_exact_chunk(rows):
    chunk = next(c for c in rows["chunks"] if c["path"] == "references/NOBI_TABLES.md")
    proc = subprocess.run(CLI + ["rule", chunk["id"]], capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0
    assert chunk["text"].rstrip("\n") in proc.stdout


def _search(q: str, k: int) -> tuple[list[str], float]:
    t0 = time.perf_counter()
    proc = subprocess.run(CLI + ["search", q, "-k", str(k), "--json"],
                          capture_output=True, text=True, cwd=ROOT)
    elapsed = time.perf_counter() - t0
    assert proc.returncode == 0, proc.stderr
    return [h["path"] for h in json.loads(proc.stdout)], elapsed


GOLDEN = yaml.safe_load((ROOT / "tests/golden_queries.yaml").read_text(encoding="utf-8"))["queries"]


@pytest.mark.parametrize("case", GOLDEN, ids=lambda c: c["q"])
def test_golden_query_hits_expected_rule(case):
    paths, _ = _search(case["q"], case["k"])
    assert case["expect"] in paths, f"{case['q']!r} top-{case['k']}: {paths}"


def test_golden_recall_is_100_percent_and_latency_is_low():
    timings, misses = [], []
    for case in GOLDEN:
        paths, elapsed = _search(case["q"], case["k"])
        timings.append(elapsed)
        if case["expect"] not in paths:
            misses.append(case["q"])
    assert not misses, misses
    median = sorted(timings)[len(timings) // 2]
    assert median < 0.5, f"median search latency {median:.3f}s"


def test_archive_excluded_from_default_search():
    paths, _ = _search("V4.24 PORTABLE", 20)
    assert not any(p.startswith(("skills/lispcad/versions/", "skills/lispcad/portable/",
                                 "docs/history/")) for p in paths)
