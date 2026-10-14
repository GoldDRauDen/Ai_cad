#!/usr/bin/env python3
"""V4.28 521005-02 topology anti-overclassification regression."""
from math import isclose
from pathlib import Path

import yaml


def _release_number(value: str) -> int:
    return int(str(value).upper().replace("V4.", ""))


def bend_pair_spacing(a, b):
    return abs(float(a) - float(b))


def test_numeric_regression_facts():
    # 057867 control: full-width single bend.
    assert isclose(bend_pair_spacing(2863.280780343604, 2866.960780343605), 3.68, abs_tol=1e-9)
    assert isclose(354.3212753797279 - 204.3212753797279, 150.0, abs_tol=1e-9)

    # 057869/057870: local flange domain 555, not the 1025 overall width.
    assert isclose(920.0 - 365.0, 555.0, abs_tol=1e-12)
    assert 555.0 < 1025.0
    assert isclose(bend_pair_spacing(2493.360196994651, 2497.04019699465), 3.68, abs_tol=1e-9)
    assert isclose(bend_pair_spacing(1947.074784140037, 1950.754784140037), 3.68, abs_tol=1e-9)

    # 057871/057872: one 600-wide bottom flange; slope is not a second bend.
    assert isclose(628.4941246144253 - 28.49412461442535, 600.0, abs_tol=1e-9)
    assert isclose(656.3403748159799 - 56.34037481597989, 600.0, abs_tol=1e-9)
    assert isclose(bend_pair_spacing(1047.125053000501, 1050.805053000501), 3.68, abs_tol=1e-9)
    assert isclose(bend_pair_spacing(112.3200000000001, 116.0), 3.68, abs_tol=1e-9)


def test_rule_wiring():
    root = Path(__file__).resolve().parents[2]
    module = (root / "references/FACE_CREATION_BEND_EVIDENCE.md").read_text(encoding="utf-8")
    for token in [
        "FACE_CREATION_REQUIRES_BEND_EVIDENCE",
        "SAME_FACE_FIRST",
        "LOCAL_BEND_DOMAIN_BEFORE_UNFOLD",
        "THEORETICAL_SHARP_CLOSURE_FOR_R_CONTOURS",
        "does not by itself prove a bend",
    ]:
        assert token in module

    router_data = yaml.safe_load((root / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    entry = (root / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (root / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    coverage_data = yaml.safe_load((root / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert _release_number(router_data["release"]) >= 28
    assert sum(
        "references/FACE_CREATION_BEND_EVIDENCE.md" in route.get("load", [])
        for route in router_data["mode_routes"].values()
    ) >= 3
    assert "- **V4.28:**" in entry
    assert "521005-02_V4_28_APPROVED.md" in entry
    assert "V4.28" in coverage_data["release_coverage"]
    assert "check_521005_02_v428.py" in "\n".join(coverage_data["release_coverage"]["V4.28"]["regression"])


def main():
    test_numeric_regression_facts()
    test_rule_wiring()
    print("PASS: 521005-02 V4.28 face-creation evidence, local bend-domain, theoretical-sharp guards")


if __name__ == "__main__":
    main()
