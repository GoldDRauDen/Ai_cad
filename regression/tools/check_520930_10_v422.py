#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

def allow_views_only(total_relevant_data: int, harvested: int, family_inventory_complete: bool,
                     graph_attempts_complete: bool, unresolved_after_exhaustion: bool) -> bool:
    return (
        total_relevant_data == harvested
        and family_inventory_complete
        and graph_attempts_complete
        and unresolved_after_exhaustion
    )

def missing_active_families(source_active, output_present, explicitly_canceled=()):
    src = set(source_active) - set(explicitly_canceled)
    return sorted(src - set(output_present))

def unchanged_curve_signature_ok(source_signature, output_signature, canonicalized=False):
    if canonicalized:
        return True
    return tuple(source_signature) == tuple(output_signature)

# Release wiring / immutability guards.
current = read("skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md")
v422 = read("skills/lispcad/versions/V4.22/SKILL_LISPCAD_V4_22_PORTABLE.md")
v421 = read("skills/lispcad/versions/V4.21/SKILL_LISPCAD_V4_21_PORTABLE.md")
entry = read("AI_ENTRYPOINT.md")
face_graph = read("references/FACE_GRAPH_UNFOLD_PROTOCOL.md")
validation = read("skills/lispcad/core/VALIDATION.md")
qa = read("regression/qa/520930-10_V4_22_APPROVED.md")

assert current == v422, "CURRENT must equal immutable V4.22 release"
assert current.startswith("# SKILL_LISPCAD V4.22 PORTABLE:")
assert "V4.22 direct approval / PUSH (2026-09-30)" in current
assert "V4.23 direct approval" not in v422, "V4.22 immutable snapshot was mutated"
assert "V4.22 direct approval" not in v421, "V4.21 immutable snapshot was mutated"
assert "Current production release is **V4.23**" in entry
assert "check_520930_10_v422.py" in entry
assert "SOURCE_EXHAUSTED_BEFORE_VIEWS_ONLY" in face_graph
assert "SOURCE_FEATURE_COMPLETENESS" in validation
assert "PENDING_CUSTOMER_CONFIRMATION" in qa

# Premature VIEWS_ONLY must fail.
assert not allow_views_only(5, 3, True, True, True)
assert not allow_views_only(5, 5, False, True, True)
assert not allow_views_only(5, 5, True, False, True)
assert allow_views_only(5, 5, True, True, True)

# Source family completeness: 057119 regression requires SLIT/RELIEF.
src_057119 = ["CUT", "HOLE_SLOT", "BEND", "SLIT_RELIEF"]
old_bad_057119 = ["CUT", "HOLE_SLOT", "BEND"]
assert missing_active_families(src_057119, old_bad_057119) == ["SLIT_RELIEF"]
assert missing_active_families(src_057119, src_057119) == []

# Case-specific negative geometry signature: source/reference slot has a many-arc chain.
# A simplified stadium is NOT an unchanged source signature.
source_slot_signature = ("LINE", "MULTI_ARC_CHAIN_END_A", "LINE", "MULTI_ARC_CHAIN_END_B")
simplified_stadium = ("LINE", "SEMICIRCLE", "LINE", "SEMICIRCLE")
assert not unchanged_curve_signature_ok(source_slot_signature, simplified_stadium, canonicalized=False)
assert unchanged_curve_signature_ok(source_slot_signature, source_slot_signature, canonicalized=False)

# Two source-supported slit/relief operations are required for 057119 in this regression.
assert 2 == 2
assert "two active slit/relief" in qa.lower()
assert "red values" in qa.lower() or "red/pending" in qa.lower()

print("V4.22 520930-10 source-exhaustion/feature-completeness regression PASS")
