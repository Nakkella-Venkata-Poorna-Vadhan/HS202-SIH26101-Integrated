"""
Automated Test Suite for Human Adjudication Packet (Stage 3.4.2).

Verifies:
  1. Structural integrity and existence of mapping_adjudication_packet.json and .csv.
  2. Exactly 26 benchmark cases present without duplication.
  3. Referential integrity against ACBP course catalogue and KCM dataset.
  4. Human reviewer decision fields strictly blank/null by default.
  5. No case marked human-adjudicated without recorded decision, reviewer, and rationale.
  6. Exact-course evidence is not inferred from related institutional material (is_exact_course_evidence == False).
  7. Domain cases (HCES, ASI) are not auto-assigned no_applicable_kcm_competency.
  8. Full JSON/CSV parity across all 26 cases.
  9. Immutability of baseline source datasets and production registry.
  10. Deterministic packet generation.
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
MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
AUDIT_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_provenance_audit.json"
ACBP_COURSES_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_COMPETENCIES_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
PRODUCTION_MAPPINGS_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.json"

EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"

ALLOWED_BENCHMARK_LABELS = {
    "supported_mapping",
    "plausible_insufficient_evidence",
    "incorrect_mapping",
    "unresolved_insufficient_source",
    "no_applicable_kcm_competency",
}

ALLOWED_ADJUDICATION_STATUSES = {
    "pending_review",
    "review_in_progress",
    "adjudicated",
    "requires_more_evidence",
}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def packet_json_data():
    with open(PACKET_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def packet_csv_data():
    with open(PACKET_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture(scope="module")
def manifest_data():
    with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def audit_data():
    with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def courses_dict():
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)["records"]
        return {c["record_id"]: c for c in raw}


@pytest.fixture(scope="module")
def kcm_dict():
    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
        return {k["competency_id"]: k for k in raw}


def test_baseline_dataset_immutability():
    """Verify source datasets and production registry remain untouched during Stage 3.4.2."""
    assert compute_sha256(ACBP_COURSES_PATH) == EXPECTED_COURSE_HASH
    assert compute_sha256(KCM_COMPETENCIES_PATH) == EXPECTED_KCM_HASH

    # Ensure production mappings registry has 226 records and no automatic validated promotions
    with open(PRODUCTION_MAPPINGS_PATH, "r", encoding="utf-8") as f:
        prod_data = json.load(f)
        assert prod_data["total_courses_evaluated"] == 226
        assert len(prod_data["mappings"]) == 226
        for r in prod_data["mappings"]:
            assert r["validation_status"] != "validated", "No candidate should be automatically validated"


def test_adjudication_packet_files_exist_and_valid(packet_json_data, packet_csv_data):
    """Verify packet JSON and CSV exist, are non-empty, and contain 26 cases."""
    assert packet_json_data["packet_id"] == "ADJ-PACKET-BM-PILOT-MOSPI-2026-V1"
    assert packet_json_data["benchmark_id"] == "BM-PILOT-MOSPI-2026-V1"
    assert packet_json_data["total_cases"] == 26
    assert len(packet_json_data["cases"]) == 26
    assert len(packet_csv_data) == 26


def test_all_26_cases_present_and_unique(packet_json_data):
    """Verify all 26 cases BM-CASE-001 through BM-CASE-026 are present exactly once."""
    case_ids = [c["benchmark_case_id"] for c in packet_json_data["cases"]]
    assert len(case_ids) == 26
    assert len(set(case_ids)) == 26

    expected_ids = [f"BM-CASE-{i:03d}" for i in range(1, 27)]
    assert case_ids == expected_ids


def test_referential_integrity(packet_json_data, manifest_data, courses_dict, kcm_dict):
    """Verify all course IDs and KCM IDs resolve to real baseline records."""
    manifest_by_id = {m["benchmark_case_id"]: m for m in manifest_data["cases"]}

    for case in packet_json_data["cases"]:
        case_id = case["benchmark_case_id"]
        assert case_id in manifest_by_id

        # Verify course ID exists in acbp_courses.json
        course_id = case["course_record_id"]
        assert course_id in courses_dict
        course_record = courses_dict[course_id]
        assert case["course_name"] == course_record["course_name"]
        assert case["cadre_role"] == course_record["cadre_role"]
        assert case["acbp_competency_category"] == course_record["competency_category"]
        assert case["duration"] == course_record["duration"]

        # Verify candidate KCM ID if present
        candidate_kcm_id = case.get("candidate_kcm_id")
        if candidate_kcm_id is not None:
            assert candidate_kcm_id in kcm_dict
            kcm_record = kcm_dict[candidate_kcm_id]
            assert case["candidate_kcm_name"] == kcm_record["competency_name"]
            assert case["kcm_verbatim_definition"] == kcm_record["description"]


def test_blank_human_review_fields_by_default(packet_json_data):
    """Verify that all human decision fields remain strictly blank/null by default."""
    for case in packet_json_data["cases"]:
        assert case["adjudication_status"] == "pending_review"
        assert case["adjudicated_label"] is None
        assert case["adjudicated_target_kcm_id"] is None
        assert case["adjudicated_target_kcm_name"] is None
        assert case["adjudicated_subtheme"] is None
        assert case["evidence_sufficiency_verdict"] is None
        assert case["depth_assessment"] is None
        assert case["reviewer_id"] is None
        assert case["reviewer_role"] is None
        assert case["adjudication_date"] is None
        assert case["reviewer_rationale"] is None
        assert case["confidence_rating"] is None
        assert case["second_reviewer_required"] is None
        assert case["consensus_status"] is None


def test_no_unsupported_human_adjudicated_claims(packet_json_data):
    """Verify no case is marked adjudicated without an actual human reviewer decision."""
    for case in packet_json_data["cases"]:
        if case["adjudication_status"] == "adjudicated":
            assert case["adjudicated_label"] in ALLOWED_BENCHMARK_LABELS
            assert case["reviewer_id"] is not None
            assert case["reviewer_rationale"] is not None
            assert case["confidence_rating"] in {1, 2, 3, 4, 5}
        else:
            assert case["adjudicated_label"] is None


def test_exact_course_evidence_not_inferred(packet_json_data):
    """Verify is_exact_course_evidence is False for all cases and not falsely claimed."""
    for case in packet_json_data["cases"]:
        assert case["is_exact_course_evidence"] is False
        # Verify Question 1 finding is non-empty and explicit
        q1 = case["question_1_course_identity_finding"]
        keywords = ["exact", "inaccessible", "unmirrored", "unverified", "behind sso", "parichay sso"]
        assert any(k in q1.lower() for k in keywords)


def test_domain_gap_cases_not_auto_labeled_as_gap(packet_json_data):
    """Verify HCES and ASI cases are not auto-labeled as domain gaps without expert review."""
    hces_case = next(c for c in packet_json_data["cases"] if c["benchmark_case_id"] == "BM-CASE-022")
    asi_case = next(c for c in packet_json_data["cases"] if c["benchmark_case_id"] == "BM-CASE-023")

    # Guidance should retain unresolved_insufficient_source and note Data Analytics (KCM-FUNC-11)
    assert hces_case["triage_guidance_label"] == "unresolved_insufficient_source"
    assert "KCM-FUNC-11" in hces_case["alternative_kcm_candidates"]
    assert "KCM-FUNC-11" in hces_case["question_3_competency_alignment_finding"]

    assert asi_case["triage_guidance_label"] == "unresolved_insufficient_source"
    assert "KCM-FUNC-11" in asi_case["alternative_kcm_candidates"]
    assert "KCM-FUNC-11" in asi_case["question_3_competency_alignment_finding"]


def test_json_and_csv_parity(packet_json_data, packet_csv_data):
    """Verify 1-to-1 parity between JSON records and CSV rows."""
    assert len(packet_json_data["cases"]) == len(packet_csv_data)

    csv_by_id = {row["benchmark_case_id"]: row for row in packet_csv_data}

    for json_case in packet_json_data["cases"]:
        cid = json_case["benchmark_case_id"]
        assert cid in csv_by_id
        csv_row = csv_by_id[cid]

        assert json_case["course_record_id"] == csv_row["course_record_id"]
        assert json_case["course_name"] == csv_row["course_name"]
        assert json_case["cadre_role"] == csv_row["cadre_role"]
        assert json_case["acbp_competency_category"] == csv_row["acbp_competency_category"]
        assert json_case["duration"] == csv_row["duration"]
        assert json_case["current_evidence_status"] == csv_row["current_evidence_status"]
        assert json_case["triage_guidance_label"] == csv_row["triage_guidance_label"]

        # Boolean conversion
        assert ("true" if json_case["is_exact_course_evidence"] else "false") == csv_row["is_exact_course_evidence"]

        # Null human decision fields in CSV should be empty string
        assert csv_row["adjudicated_label"] == ""
        assert csv_row["reviewer_id"] == ""
        assert csv_row["reviewer_rationale"] == ""
        assert csv_row["confidence_rating"] == ""
        assert csv_row["adjudication_status"] == "pending_review"


def test_builder_determinism():
    """Verify build_adjudication_cases produces identical deterministic outputs."""
    from scripts.build_adjudication_packet import build_adjudication_cases

    run1 = build_adjudication_cases()
    run2 = build_adjudication_cases()

    assert json.dumps(run1, sort_keys=True) == json.dumps(run2, sort_keys=True)
