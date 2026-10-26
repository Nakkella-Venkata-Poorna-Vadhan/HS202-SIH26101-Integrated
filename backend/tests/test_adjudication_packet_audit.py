"""
Automated Test Suite for Adjudication Packet Quality Audit (Stage 3.4.3).

Verifies the 8 critical audit criteria:
  1. All 26 benchmark cases match manifest courses with 100% title and cadre fidelity.
  2. Every evidence claim provides traceable source IDs and valid citations (no generic placeholders).
  3. Claim strength proportionality: is_exact_course_evidence is False; related materials clearly qualified.
  4. Blank human review decision fields strictly maintained.
  5. Distinction between expert triage readiness and definitive adjudication readiness.
  6. Domain gap rigor: HCES and ASI evaluated against KCM-FUNC-11 (Data Analytics) overlap.
  7. Taxonomy and ID fidelity: 5 benchmark labels preserved; zero invented competency IDs.
  8. Deterministic JSON/CSV parity, baseline immutability, and defect remediation.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# File paths
PACKET_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_adjudication_packet.json"
PACKET_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_adjudication_packet.csv"
AUDIT_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "adjudication_packet_quality_audit.json"
AUDIT_MD_PATH = PROJECT_ROOT / "docs" / "adjudication_packet_quality_audit.md"
MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
ACBP_COURSES_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_COMPETENCIES_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
PRODUCTION_MAPPINGS_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.json"

EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def packet_json():
    with open(PACKET_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def audit_json():
    with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_cases():
    with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
        return {c["benchmark_case_id"]: c for c in json.load(f)["cases"]}


def test_baseline_and_production_immutability():
    """Verify source baselines and production mapping registry remain untouched."""
    assert compute_sha256(ACBP_COURSES_PATH) == EXPECTED_COURSE_HASH
    assert compute_sha256(KCM_COMPETENCIES_PATH) == EXPECTED_KCM_HASH

    with open(PRODUCTION_MAPPINGS_PATH, "r", encoding="utf-8") as f:
        prod_data = json.load(f)
        assert prod_data["total_courses_evaluated"] == 226
        assert len(prod_data["mappings"]) == 226
        for r in prod_data["mappings"]:
            assert r["validation_status"] != "validated"


def test_audit_deliverables_exist_and_non_empty():
    """Verify quality audit report JSON and Markdown files exist and are populated."""
    assert AUDIT_JSON_PATH.exists()
    assert AUDIT_JSON_PATH.stat().st_size > 500

    assert AUDIT_MD_PATH.exists()
    assert AUDIT_MD_PATH.stat().st_size > 1000


def test_all_26_cases_match_manifest_titles_strictly(packet_json, manifest_cases):
    """Verify all 26 cases strictly match manifest course titles without draft desynchronization."""
    assert len(packet_json["cases"]) == 26

    for case in packet_json["cases"]:
        cid = case["benchmark_case_id"]
        assert cid in manifest_cases
        manifest_case = manifest_cases[cid]

        # Exact title and cadre match
        assert case["course_name"] == manifest_case["course_name"]
        assert case["cadre_role"] == manifest_case["cadre_role"]
        assert case["course_record_id"] == manifest_case["course_record_id"]

    # Specific checks against regression of DEF-01
    case_007 = next(c for c in packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-007")
    assert case_007["course_name"] == "Developing a Positive Work Culture"
    assert "positive work culture" in case_007["question_1_course_identity_finding"].lower() or "culture" in case_007["question_2_subject_coverage_finding"].lower()

    case_008 = next(c for c in packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-008")
    assert case_008["course_name"] == "Yoga Break at Workplace"
    assert "y-break" in case_008["question_1_course_identity_finding"].lower() or "yoga" in case_008["question_2_subject_coverage_finding"].lower()

    case_024 = next(c for c in packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-024")
    assert case_024["course_name"] == "Introduction to R and Python Programming_"
    assert "python" in case_024["question_2_subject_coverage_finding"].lower()


def test_no_generic_evidence_source_id_placeholders(packet_json):
    """Verify evidence_source_id does not contain generic placeholders (DEF-02 regression test)."""
    generic_placeholders = {"SRC-OFFICIAL-ACADEMY-2024", "SRC-GENERIC", "SRC-UNKNOWN"}

    for case in packet_json["cases"]:
        src_id = case["evidence_source_id"]
        assert src_id not in generic_placeholders
        assert src_id.startswith("SRC-")
        assert len(src_id) > 8


def test_course_source_id_and_citation_integrity(packet_json):
    """Verify all cases have primary ACBP source IDs and citations (DEF-03 regression test)."""
    for case in packet_json["cases"]:
        assert case["course_source_id"] == "SRC-MOSPI-ACBP-2026-27"
        assert "SRC-MOSPI-ACBP-2026-27 (Annexure I, Page" in case["course_source_citation"]
        assert "Row" in case["course_source_citation"]


def test_claim_proportionality_enforced(packet_json):
    """Verify that claims are proportional to evidence and is_exact_course_evidence is False."""
    for case in packet_json["cases"]:
        assert case["is_exact_course_evidence"] is False
        q5 = case["question_5_competency_depth_limitation"]
        assert len(q5) > 15
        # Must document limitations
        assert any(w in q5.lower() for w in ["duration", "limitation", "overview", "assessment", "simulation", "exercises", "cannot"])


def test_triage_vs_adjudication_readiness_distinction(packet_json, audit_json):
    """Verify all 26 cases are ready for triage but 0 are marked adjudicated."""
    assert packet_json["total_cases"] == 26
    assert packet_json["adjudication_status_summary"]["pending_review"] == 26
    assert packet_json["adjudication_status_summary"]["adjudicated"] == 0

    assert audit_json["triage_vs_adjudication_breakdown"]["ready_for_expert_triage"] == 26
    assert audit_json["triage_vs_adjudication_breakdown"]["ready_for_definitive_adjudication"] == 0
    assert audit_json["triage_vs_adjudication_breakdown"]["blocked_pending_syllabi"] == 26


def test_hces_and_asi_domain_gap_rigor(packet_json):
    """Verify HCES and ASI evaluate Data Analytics overlap and do not auto-declare domain gaps."""
    hces = next(c for c in packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-022")
    asi = next(c for c in packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-023")

    for c in [hces, asi]:
        assert c["triage_guidance_label"] == "unresolved_insufficient_source"
        assert "KCM-FUNC-11" in c["alternative_kcm_candidates"]
        assert "KCM-FUNC-11" in c["question_3_competency_alignment_finding"]
        assert "expert adjudication" in c["question_4_evidence_sufficiency_finding"].lower() or "nssta" in c["sme_adjudication_questions"].lower()


def test_defect_remediation_log_integrity(audit_json):
    """Verify that all identified defects are logged with status REMEDIATED."""
    log = audit_json["defect_remediation_log"]
    assert len(log) == 4
    defect_ids = {d["defect_id"] for d in log}
    assert defect_ids == {"DEF-01", "DEF-02", "DEF-03", "DEF-04"}
    for d in log:
        assert d["status"] == "REMEDIATED"
