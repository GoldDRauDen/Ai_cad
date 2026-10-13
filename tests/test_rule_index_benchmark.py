"""Scoped generated RAG index and byte benchmark; no duplicate rule authority."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_rule_index import build_index  # noqa: E402
from benchmark_rule_routes import benchmark  # noqa: E402
from audit_rule_coverage import audit  # noqa: E402


def test_index_is_generated_from_live_router_and_complete_coverage():
    index = build_index()
    cov = audit()
    router = yaml.safe_load(
        (ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8")
    )
    assert index["production"]["active_modules"] == cov["active_modules"]
    assert index["production"]["feature_routes"] == router["feature_routes"]
    assert index["production"]["stages"] == router["stage_routes"]
    assert index["router_sha256"] == hashlib.sha256(
        (ROOT / "skills/lispcad/router/ROUTER.yaml").read_bytes()
    ).hexdigest()
    assert "QA_ENTRYPOINT.md" not in index["production"]["active_modules"]
    assert all(not p.startswith(("regression/", "skills/lispcad/versions/",
            "skills/lispcad/portable/", "services/trainaicad-mcp/"))
               for p in index["production"]["active_modules"])
    assert len(index["history_audit_only"]["paths"]) >= 24
    assert len(index["regression_evidence"]["paths"]) >= 20
    assert index["experimental_mcp"]["policy"] == "RESEARCH_ONLY_NO_DEFAULT_PRODUCTION"


def test_rag_index_cli_outputs_reproducible_manifest(tmp_path):
    output = tmp_path / "RAG_INDEX.yaml"
    result = subprocess.run([sys.executable, str(ROOT / "tools/build_rule_index.py"),
                             "--output", str(output)],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    report = json.loads(result.stdout)
    data = output.read_bytes()
    assert report["sha256"] == hashlib.sha256(data).hexdigest()
    assert "regression_evidence:" in data.decode("utf-8")
    assert "active_modules:" in data.decode("utf-8")


def test_benchmark_measures_real_file_bytes_without_claiming_total_token_savings():
    b = benchmark()
    assert b["metric"] == "EXACT_UTF8_BYTES_NOT_LLM_TOKENS"
    assert b["stage_invariant"] == "L0_L1_L2_L3_ALL_MANDATORY"
    assert len(b["cases"]) == 5
    for case in b["cases"]:
        assert case["first_two_stages_bytes"] < case["all_stages_unique_bytes"]
        assert sum(case["stage_breakdown"].values()) == case["all_stages_unique_bytes"]
        assert case["route_count"] > 0
    # Gate for the planned optimization: startup/context reading of ordinary
    # flat and bend jobs must be at least 30% smaller than eager L0–L3 loads.
    ordinary = [c for c in b["cases"] if c["scenario"] in {"flat", "bend_nobi"}]
    assert all(c["initial_context_reduction_pct_vs_eager_load"] >= 30 for c in ordinary)


def test_no_exact_cross_module_rule_paragraph_duplicates():
    """The current approved canonical modules have no repeated long paragraphs.

    This does not prove the absence of semantic contradictions or short
    repeated policy wording; those still need human/source rule review.
    """
    from audit_rule_duplicates import scan
    report = scan(min_chars=170)
    assert report["repeated_cross_module_paragraphs"] == 0
