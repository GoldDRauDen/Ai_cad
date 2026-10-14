from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_qa_entrypoint_is_not_wired_into_normal_router():
    router = (ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8")
    assert "QA_ENTRYPOINT.md" not in router


def test_qa_entrypoint_declares_explicit_role_switch_and_audit_only():
    qa = (ROOT / "QA_ENTRYPOINT.md").read_text(encoding="utf-8")
    required = [
        "explicit opt-in QA role only",
        "ROLE = QA_AUDITOR",
        "AUDIT_TARGET",
        "OUTPUT_FREEZE -> QA",
        "READ -> COMPARE -> CHALLENGE -> REPORT",
        "A normal creation request such as E2E does not activate this entrypoint.",
    ]
    for marker in required:
        assert marker in qa


def test_qa_pdf_numeric_policy_cannot_excuse_customer_data_drift():
    qa = (ROOT / "QA_ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "abs(DXF_generated - PDF_numeric) < 0.1 mm -> not a QA defect" in qa
    assert "Do not use the PDF 0.1 mm QA acceptance policy to excuse redraw drift from customer DATA." in qa
    assert "QA acceptance policy only" in qa


def test_qa_reuses_current_engineering_rules_instead_of_copying_authority():
    qa = (ROOT / "QA_ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "QA does not maintain a second copy of TrainAiCad engineering rules." in qa
    assert "Read the current AI_ENTRYPOINT.md" in qa
    assert "Load only the current routed production modules/references" in qa
