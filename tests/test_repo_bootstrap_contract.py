"""Repository bootstrap contract: short E2E prompts must resolve current repo authority."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_is_release_independent_and_names_repo():
    text = (ROOT / "AI_BOOTSTRAP.md").read_text(encoding="utf-8")
    assert "GoldDRauDen/TrainAiCad" in text
    assert "AI_ENTRYPOINT.md" in text
    assert "FEATURE_CENSUS.md" in text
    assert "ROUTER.yaml" in text
    assert "RULE_COVERAGE.yaml" in text
    assert re.search(r"\\bV4\\.\\d+\\b", text) is None


def test_bootstrap_defines_short_e2e_invocation_and_full_execution():
    text = (ROOT / "AI_BOOTSTRAP.md").read_text(encoding="utf-8")
    assert "`E2E`" in text
    assert "Đọc repo TrainAiCad làm E2E" in text
    assert "do not stop after routing, census, analysis, or a text report" in text
    assert "complete source-view fallback" in text


def test_bootstrap_has_no_memory_or_history_fallback():
    text = (ROOT / "AI_BOOTSTRAP.md").read_text(encoding="utf-8")
    assert "Do not substitute chat memory" in text
    assert "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md" in text
    assert "skills/lispcad/versions/**" in text
    assert "docs/history/**" in text
    assert "Do not fabricate that the repo was read" in text


def test_repo_changes_still_require_explicit_approval():
    bootstrap = (ROOT / "AI_BOOTSTRAP.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "DUYỆT" in bootstrap and "PUSH" in bootstrap
    assert "DUYỆT" in agents and "PUSH" in agents


def test_agents_is_orchestration_only_and_release_independent():
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "AI_BOOTSTRAP.md" in text
    assert "AI_ENTRYPOINT.md" in text
    assert "orchestration only" in text
    assert re.search(r"\\bV4\\.\\d+\\b", text) is None


def test_entrypoint_accepts_e2e_invocation_without_repeating_workflow():
    text = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "## Invocation contract" in text
    assert "`E2E`" in text
    assert "complete current repo-direct production flow" in text


def test_gpt_web_project_template_is_short_bootstrap_pointer():
    text = (ROOT / "PROJECT_INSTRUCTIONS_GPT_WEB.md").read_text(encoding="utf-8")
    assert "GoldDRauDen/TrainAiCad" in text
    assert "AI_BOOTSTRAP.md" in text
    assert "`E2E`" in text
    assert "current repo" in text
    assert re.search(r"\\bV4\\.\\d+\\b", text) is None


def test_current_router_still_controls_release_and_engineering_load():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    assert router["production_mode"] == "repo_direct"
    assert "skills/lispcad/router/FEATURE_CENSUS.md" in router["default_load"]
    assert "saved_dxf_readback" in router["post_route_checks"]


def test_ci_tracks_bootstrap_files():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "'AI_BOOTSTRAP.md'" in wf
    assert "'AGENTS.md'" in wf
    assert "'PROJECT_INSTRUCTIONS_GPT_WEB.md'" in wf
