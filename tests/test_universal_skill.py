"""Universal entrypoint and reproducible modular rulepack contract."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_rule_bundle", ROOT / "tools/build_rule_bundle.py"
)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def test_universal_skill_is_single_workflow_entrypoint():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for term in ("AI_BOOTSTRAP.md", "AI_ENTRYPOINT.md", "ROUTER.yaml",
                 "Geometry JSON", "saved-DXF", "REVIEW", "SOURCE"):
        assert term.casefold() in skill.casefold()
    assert "Implemented canonical production artifact contract" in skill


def test_bundle_contains_current_approved_rule_modules_without_history():
    release, paths = builder.approved_paths()
    assert release
    assert paths[0] == "SKILL.md"
    assert len(paths) == len(set(paths))
    assert "skills/lispcad/modes/BEND_UNFOLD.md" in paths
    assert "skills/lispcad/features/REVISION_CANCELLATION.md" in paths
    assert "references/NOBI_TABLES.md" in paths
    assert all(not p.startswith(builder.EXCLUDED) for p in paths)


def test_bundle_has_content_hash_and_is_reproducible():
    bundle = builder.build_bundle()
    assert bundle == builder.build_bundle()
    assert '"sha256"' in bundle
    assert "BEGIN SOURCE: AI_ENTRYPOINT.md" in bundle
    assert "BEGIN SOURCE: skills/lispcad/core/VALIDATION.md" in bundle
    assert "END SOURCE: skills/lispcad/features/REVISION_CANCELLATION.md" in bundle
    assert "BEGIN SOURCE: skills/lispcad/versions/" not in bundle


def test_invalid_route_to_regression_is_rejected(tmp_path):
    import shutil
    root = tmp_path / "r"
    shutil.copytree(ROOT / "skills", root / "skills")
    shutil.copyfile(ROOT / "AI_ENTRYPOINT.md", root / "AI_ENTRYPOINT.md")
    (root / "SKILL.md").write_text("placeholder")
    (root / "AI_BOOTSTRAP.md").write_text("placeholder")
    # There is no reference tree; failure must be explicit rather than
    # silently bundling partial contents.
    with pytest.raises(builder.BundleError, match="Missing or unsafe"):
        builder.approved_paths(root)


def test_rulepack_cli_writes_one_file_with_manifest_hash(tmp_path):
    """Exercise the actual one-file portability entry point, not only its pure helper."""
    import hashlib
    import json
    import subprocess
    import sys

    outfile = tmp_path / "TrainAiCad_E2E_RULEPACK.md"
    cmd = [sys.executable, str(ROOT / "tools/build_rule_bundle.py"),
           "--repo-root", str(ROOT), "--output", str(outfile)]
    process = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    record = json.loads(process.stdout)
    data = outfile.read_bytes()
    assert record["bytes"] == len(data)
    assert record["sha256"] == hashlib.sha256(data).hexdigest()
    assert "BEGIN SOURCE: AI_ENTRYPOINT.md" in data.decode("utf-8")
    assert "BEGIN SOURCE: skills/lispcad/versions/" not in data.decode("utf-8")
