"""Approved 2026-10-12 manufacturing and numeric customer-code routing."""
from pathlib import Path
import sys
import re

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from resolve_rules import resolve_rules, ResolutionError  # noqa: E402

ROUTER = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
CATALOG = yaml.safe_load((ROOT / "references/CUSTOMER_CAD_RULES.yaml").read_text(encoding="utf-8"))


def census(customer=None, mode="FLAT_NO_BEND"):
    return {
        "customer_code": customer,
        "source_mode": "PDF_ONLY",
        "part_mode": mode,
        "reference_present": "NO",
        "features": {k: {"state": "NO"} for k in ROUTER["feature_routes"]},
    }


def test_646_routes_only_by_explicit_numeric_customer_code_for_bends():
    x = census(646, "BEND")
    x["features"]["NOBI"]["state"] = "YES"
    result = resolve_rules(x)
    assert result["customer_code"] == "646"
    assert result["customer_rules"]["nobi_profile"] == "AIKOKU_646"
    assert "references/AIKOKU_646_NOBI.md" in result["stage_plans"]["L2_GEOMETRY"]["rule_paths"]
    assert "references/NOBI_TABLES.md" in result["rule_paths"]
    assert "references/AIKOKU_646_NOBI.md" not in resolve_rules(census(646))["rule_paths"]
    assert "references/AIKOKU_646_NOBI.md" not in resolve_rules(census(829,"BEND"))["rule_paths"]


def test_missing_customer_code_uses_general_rules_without_review():
    data = resolve_rules(census())
    assert data["customer_code"] is None and data["customer_rules"] == {}
    assert "references/CAD_CUSTOMER_POLICY.md" in data["rule_paths"]
    assert "references/AIKOKU_646_NOBI.md" not in data["rule_paths"]


@pytest.mark.parametrize("bad", [True, "646A", "アイコクアルファ", -646, "829.0"])
def test_name_and_invalid_ids_are_not_auto_inferred(bad):
    with pytest.raises(ResolutionError, match="customer_code"):
        resolve_rules(census(bad))


def test_data_authority_override_is_explicit_and_hole_qa_is_retained():
    assert resolve_rules(census(829))["customer_rules"]["data_pdf_policy"] == "DATA_NO_DIM_COMPARE"
    assert resolve_rules(census(240))["customer_rules"]["data_pdf_policy"] == "DATA_NO_DIM_COMPARE"
    assert resolve_rules(census(395))["customer_rules"]["data_pdf_policy"] == "PDF_PRIORITY"
    policy = (ROOT / "references/CAD_CUSTOMER_POLICY.md").read_text(encoding="utf-8")
    assert "hole" in policy.lower() and "REVIEW" in policy
    assert "NC is deferred" in policy


def test_646_standard_tooling_and_review_boundaries():
    txt = (ROOT / "references/AIKOKU_646_NOBI.md").read_text(encoding="utf-8")
    for expected in ("|4.5|3|V25|7.84|17.8|", "|0.8|0.6|V8|1.68|",
                     "|5|3|V40|10.20|", "7.48", "7.72", "non-90°"):
        assert expected in txt
    assert "no" in txt.lower() and "general" in txt.lower() and "REVIEW" in txt


def test_nobi_and_laser_regressions_from_approved_workbook():
    n = (ROOT / "references/NOBI_TABLES.md").read_text(encoding="utf-8")
    r = (ROOT / "references/MATERIAL_RULES.md").read_text(encoding="utf-8")
    assert "| **3.0** | 1801 ~ 2400 | V40 | 7.84 | 7.80 |" in n
    assert "without documented 2B/#1 uses **2B**" in n
    assert "OUTER material perimeter" in r and "interior holes" in r


def test_new_reference_routes_cover_hole_and_fine_tap():
    x = census()
    x["features"]["TAP"]["state"] = "YES"
    ps = resolve_rules(x)["rule_paths"]
    assert "references/THREAD_FINE_PILOT_TABLE.md" in ps
    assert "references/COUNTERSINK_COUNTERBORE.md" in ps
    fine = (ROOT / "references/THREAD_FINE_PILOT_TABLE.md").read_text(encoding="utf-8")
    assert "| M8×1 | 7 |" in fine
    assert "| M12×1.25 | 10.8 |" in fine
    holes = (ROOT / "references/COUNTERSINK_COUNTERBORE.md").read_text(encoding="utf-8")
    assert "| M6 | 6.6 | 11.0 | 12.5 |" in holes


def test_catalog_has_no_management_or_contact_fields():
    assert CATALOG["scope"] == "CAD_ONLY"
    assert len(CATALOG["customers"]) >= 20
    for code, record in CATALOG["customers"].items():
        assert re.fullmatch(r"[0-9]+", code)
        assert set(record) <= {"source", "notes", "data_pdf_policy", "nobi_profile"}
        assert not any(k in record for k in ("name", "phone", "email", "staff", "contact"))

def test_customer_technical_note_census_partitions_all_codes():
    census = CATALOG["customer_note_census"]
    included = set(CATALOG["customers"])
    excluded = set(census["excluded_non_cad_codes"])
    obsolete = set(census["fully_obsolete_codes"])
    assert len(included) == 90
    assert len(excluded) == 16
    assert obsolete == {"880"}
    assert included.isdisjoint(excluded | obsolete)
    assert excluded.isdisjoint(obsolete)
    assert len(included | excluded | obsolete) == census["source_note_bearing_codes"] == 107
    assert census["active_note_bearing_codes"] == 106
    assert CATALOG["source_workbook_sha256"] == "67851a40fc2fdde09f3ba0692cece5054ca9759d074134d8e16a1774cf7bbddb"
    assert "891" in included and "610" in included and "621" in included
    assert "old" in " ".join(CATALOG["customers"]["891"]["notes"]).lower() or "obsolete" in " ".join(CATALOG["customers"]["891"]["notes"]).lower()
    assert "OBSOLETE" in " ".join(CATALOG["customers"]["610"]["notes"])
    assert "OBSOLETE" in " ".join(CATALOG["customers"]["621"]["notes"])
