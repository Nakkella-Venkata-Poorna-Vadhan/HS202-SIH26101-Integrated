"""
tests/test_competency_mapping.py — Regression Test Suite for Stage 3.2 Mapping Registry

Tests:
1. All 226 courses represented without loss or duplication.
2. The six existing candidate mappings remain unvalidated with null confidence scores.
3. Domain courses strictly receive zero invented KCM IDs and retain unresolved_domain_gap.
4. Referential integrity of courses and competencies.
5. JSON and CSV parity for registry and review queue.
6. Validation module error detection (schema, approvals, referential integrity, duplicate IDs).
7. Safe review operation state machine rules (valid vs invalid transitions, rejection preservation).
8. Determinism and input dataset immutability.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

from scripts.validate_competency_mappings import (
    compute_sha256,
    run_full_validation,
    validate_single_record,
)
from scripts.review_mapping import execute_review, ALLOWED_TRANSITIONS


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

ACBP_COURSES_PATH = DATA_PROCESSED / "acbp_courses.json"
KCM_COMPETENCIES_PATH = DATA_PROCESSED / "competencies_kcm.json"
CANDIDATE_MAPPINGS_PATH = DATA_PROCESSED / "acbp_kcm_candidate_mappings.json"
MAPPINGS_JSON_PATH = DATA_PROCESSED / "acbp_kcm_mappings.json"
MAPPINGS_CSV_PATH = DATA_PROCESSED / "acbp_kcm_mappings.csv"
REVIEW_QUEUE_JSON_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.json"
REVIEW_QUEUE_CSV_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.csv"

# Immutable Baseline Hashes
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"
EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_CANDIDATE_HASH = "966cabebbcc02f5cc96f5879fdbe3c7af126adfdf57ad5c5219aae580656b801"

CANDIDATE_COURSE_IDS = {
    "ACBP-CRS-017",
    "ACBP-CRS-036",
    "ACBP-CRS-040",
    "ACBP-CRS-041",
    "ACBP-CRS-060",
    "ACBP-CRS-061",
}


@pytest.fixture(scope="module")
def registry_data() -> Dict[str, Any]:
    with open(MAPPINGS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def queue_data() -> Dict[str, Any]:
    with open(REVIEW_QUEUE_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def courses_data() -> List[Dict[str, Any]]:
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("records", data) if isinstance(data, dict) else data


@pytest.fixture(scope="module")
def kcm_data() -> List[Dict[str, Any]]:
    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_input_dataset_immutability():
    """Verify that Stage 3.2 did not alter or re-extract any input dataset."""
    assert compute_sha256(KCM_COMPETENCIES_PATH) == EXPECTED_KCM_HASH, "Frozen KCM dataset altered!"
    assert compute_sha256(ACBP_COURSES_PATH) == EXPECTED_COURSE_HASH, "ACBP course dataset altered!"
    assert compute_sha256(CANDIDATE_MAPPINGS_PATH) == EXPECTED_CANDIDATE_HASH, "Candidate mappings artifact altered!"


def test_all_226_courses_represented_without_loss(registry_data, courses_data):
    """Verify exact 226 records without omissions or duplicate course representations."""
    mappings = registry_data["mappings"]
    assert len(mappings) == 226
    assert registry_data["total_courses_evaluated"] == 226

    mapped_course_ids = [m["course_record_id"] for m in mappings]
    source_course_ids = [c["record_id"] for c in courses_data]

    assert len(mapped_course_ids) == len(set(mapped_course_ids)), "Duplicate course IDs found in registry!"
    assert mapped_course_ids == source_course_ids, "Course sequence or identity mismatch with source dataset!"


def test_unique_mapping_ids(registry_data):
    """Verify all mapping_id strings are unique and properly formatted."""
    mappings = registry_data["mappings"]
    map_ids = [m["mapping_id"] for m in mappings]
    assert len(map_ids) == 226
    assert len(set(map_ids)) == 226
    for idx, mid in enumerate(map_ids, 1):
        assert mid == f"MAP-ACBP-KCM-{idx:03d}"


def test_candidate_mappings_remain_unvalidated(registry_data):
    """Verify the 6 candidates carry forward with pending_review and null confidence."""
    mappings = registry_data["mappings"]
    cand_mappings = [m for m in mappings if m["course_record_id"] in CANDIDATE_COURSE_IDS]

    assert len(cand_mappings) == 6
    for cm in cand_mappings:
        assert cm["validation_status"] == "pending_review", f"Candidate {cm['course_record_id']} illegally validated!"
        assert cm["candidate_kcm_competency_id"] is not None
        assert cm["confidence_score"] is None, f"Candidate {cm['course_record_id']} has uncalibrated confidence score!"
        assert cm["confidence_metric"] is None
        assert cm["reviewer_id"] is None, "Candidate must not have reviewer_id prior to formal review"


def test_domain_courses_segregation(registry_data):
    """Verify all 51 Domain courses have zero invented KCM IDs and proper unresolved method."""
    mappings = registry_data["mappings"]
    domain_mappings = [m for m in mappings if m["acbp_competency_category"] == "Domain"]

    assert len(domain_mappings) == 51
    for dm in domain_mappings:
        assert dm["candidate_kcm_competency_id"] is None, f"Domain course {dm['course_record_id']} illegally mapped!"
        assert dm["mapping_type"] == "unresolved"
        assert dm["mapping_method"] == "unresolved_domain_gap"
        assert dm["validation_status"] == "unresolved"
        assert "zero Domain competencies" in dm["evidence_or_rationale"]


def test_functional_and_behavioural_unresolved_courses(registry_data):
    """Verify all non-candidate functional/behavioural courses are unresolved with no_match."""
    mappings = registry_data["mappings"]
    non_cand_fb = [
        m for m in mappings
        if m["course_record_id"] not in CANDIDATE_COURSE_IDS and m["acbp_competency_category"] in ("Functional", "Behavioural")
    ]

    # 226 total - 6 candidates - 51 domain = 169
    assert len(non_cand_fb) == 169
    for m in non_cand_fb:
        assert m["candidate_kcm_competency_id"] is None
        assert m["mapping_type"] == "unresolved"
        assert m["mapping_method"] == "unresolved_no_match"
        assert m["validation_status"] == "unresolved"


def test_referential_integrity(registry_data, courses_data, kcm_data):
    """Verify referential integrity to courses and KCM competencies."""
    courses_by_id = {c["record_id"]: c for c in courses_data}
    kcm_by_id = {k["competency_id"]: k for k in kcm_data}

    for m in registry_data["mappings"]:
        cid = m["course_record_id"]
        assert cid in courses_by_id, f"Foreign key violation: course {cid} does not exist!"
        c_src = courses_by_id[cid]
        assert m["cadre_role"] == c_src["cadre_role"]
        assert m["course_name"] == c_src["course_name"]
        assert m["acbp_competency_category"] == c_src["competency_category"]
        assert m["course_source_page"] == c_src["source_page"]
        assert m["course_source_row"] == c_src["source_row"]

        kid = m["candidate_kcm_competency_id"]
        if kid is not None:
            assert kid in kcm_by_id, f"Foreign key violation: competency {kid} does not exist!"
            k_src = kcm_by_id[kid]
            assert m["candidate_kcm_competency_name"] == k_src["competency_name"]
            assert m["candidate_kcm_competency_type"] == k_src["competency_type"]
            assert m["kcm_source_id"] == "SRC-CBC-KCM-2024"


def test_json_and_csv_parity_registry(registry_data):
    """Verify exact record count and field value parity between JSON and CSV registry."""
    with open(MAPPINGS_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    mappings = registry_data["mappings"]
    assert len(mappings) == len(csv_rows)

    for j_rec, c_rec in zip(mappings, csv_rows):
        for k, v in j_rec.items():
            expected = "" if v is None else str(v)
            assert c_rec[k] == expected, f"Parity mismatch on {j_rec['mapping_id']} field {k}"


def test_json_and_csv_parity_review_queue(queue_data):
    """Verify exact parity for review queue JSON and CSV."""
    with open(REVIEW_QUEUE_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    queue = queue_data["queue"]
    assert len(queue) == len(csv_rows)
    for j_rec, c_rec in zip(queue, csv_rows):
        for k, v in j_rec.items():
            expected = "" if v is None else str(v)
            assert c_rec[k] == expected, f"Parity mismatch on queue item {j_rec['queue_id']} field {k}"


def test_review_queue_categories(queue_data):
    """Verify review queue categorizes the 226 items properly."""
    queue = queue_data["queue"]
    assert len(queue) == 226

    title_cands = [q for q in queue if q["queue_category"] == "title_reference_candidate"]
    domain_gaps = [q for q in queue if q["queue_category"] == "unresolved_domain_gap"]
    no_matches = [q for q in queue if q["queue_category"] == "unresolved_no_match"]

    assert len(title_cands) == 6
    assert len(domain_gaps) == 51
    assert len(no_matches) == 169


def test_validator_detects_clean_baseline():
    """Verify validate_competency_mappings reports 100% pass on unmodified baseline."""
    is_valid, errors = run_full_validation()
    assert is_valid, f"Validator failed on clean baseline with errors: {errors}"
    assert len(errors) == 0


def test_validator_catches_domain_course_mapping_violation(courses_data, kcm_data):
    """Verify validator flags illegal assignment of KCM ID to Domain course."""
    courses_by_id = {c["record_id"]: c for c in courses_data}
    kcm_by_id = {k["competency_id"]: k for k in kcm_data}

    bad_rec = {
        "mapping_id": "MAP-ACBP-KCM-999",
        "course_record_id": "ACBP-CRS-001",
        "cadre_role": courses_by_id["ACBP-CRS-001"]["cadre_role"],
        "course_name": courses_by_id["ACBP-CRS-001"]["course_name"],
        "acbp_competency_category": "Domain",
        "candidate_kcm_competency_id": "KCM-FUNC-05",  # Illegal mapping
        "candidate_kcm_competency_name": "Project Management",
        "candidate_kcm_subtheme": None,
        "candidate_kcm_competency_type": "functional",
        "mapping_type": "exact_title_reference",
        "mapping_method": "verbatim_title_containment",
        "evidence_or_rationale": "Fabricated test rationale for domain course mapping test.",
        "course_source_id": "SRC-MOSPI-ACBP-2026-27",
        "course_source_page": 2,
        "course_source_row": "1",
        "kcm_source_id": "SRC-CBC-KCM-2024",
        "kcm_source_page_def": 74,
        "kcm_source_page_sub": 75,
        "confidence_score": None,
        "confidence_metric": None,
        "validation_status": "pending_review",
        "reviewer_id": None,
        "reviewer_role": None,
        "reviewed_at": None,
        "reviewer_notes": "",
        "creation_method": "automated_pipeline",
        "pipeline_version": "3.2.0",
        "created_at": "2026-10-18T14:40:00+00:00",
        "source_hash_course": EXPECTED_COURSE_HASH,
        "source_hash_kcm": EXPECTED_KCM_HASH,
    }

    errors = validate_single_record(bad_rec, courses_by_id, kcm_by_id, set(), set())
    assert any("Domain course 'ACBP-CRS-001' illegally mapped" in e for e in errors)


def test_validator_catches_uncalibrated_confidence_score(courses_data, kcm_data):
    """Verify validator flags non-null confidence scores on title references."""
    courses_by_id = {c["record_id"]: c for c in courses_data}
    kcm_by_id = {k["competency_id"]: k for k in kcm_data}

    bad_rec = {
        "mapping_id": "MAP-ACBP-KCM-998",
        "course_record_id": "ACBP-CRS-017",
        "cadre_role": courses_by_id["ACBP-CRS-017"]["cadre_role"],
        "course_name": courses_by_id["ACBP-CRS-017"]["course_name"],
        "acbp_competency_category": "Behavioural",
        "candidate_kcm_competency_id": "KCM-BEH-06",
        "candidate_kcm_competency_name": "Collaboration",
        "candidate_kcm_subtheme": None,
        "candidate_kcm_competency_type": "behavioural",
        "mapping_type": "exact_title_reference",
        "mapping_method": "verbatim_title_containment",
        "evidence_or_rationale": "Valid length rationale testing confidence score constraint check.",
        "course_source_id": "SRC-MOSPI-ACBP-2026-27",
        "course_source_page": 2,
        "course_source_row": "17",
        "kcm_source_id": "SRC-CBC-KCM-2024",
        "kcm_source_page_def": 49,
        "kcm_source_page_sub": 50,
        "confidence_score": 0.85,  # Uncalibrated float prohibited
        "confidence_metric": None,
        "validation_status": "pending_review",
        "reviewer_id": None,
        "reviewer_role": None,
        "reviewed_at": None,
        "reviewer_notes": "",
        "creation_method": "automated_pipeline",
        "pipeline_version": "3.2.0",
        "created_at": "2026-10-18T14:40:00+00:00",
        "source_hash_course": EXPECTED_COURSE_HASH,
        "source_hash_kcm": EXPECTED_KCM_HASH,
    }

    errors = validate_single_record(bad_rec, courses_by_id, kcm_by_id, set(), set())
    assert any("uncalibrated heuristic score prohibited" in e for e in errors)


def test_validator_catches_unapproved_validation_status(courses_data, kcm_data):
    """Verify validator flags 'validated' status lacking reviewer approval metadata."""
    courses_by_id = {c["record_id"]: c for c in courses_data}
    kcm_by_id = {k["competency_id"]: k for k in kcm_data}

    bad_rec = {
        "mapping_id": "MAP-ACBP-KCM-997",
        "course_record_id": "ACBP-CRS-017",
        "cadre_role": courses_by_id["ACBP-CRS-017"]["cadre_role"],
        "course_name": courses_by_id["ACBP-CRS-017"]["course_name"],
        "acbp_competency_category": "Behavioural",
        "candidate_kcm_competency_id": "KCM-BEH-06",
        "candidate_kcm_competency_name": "Collaboration",
        "candidate_kcm_subtheme": None,
        "candidate_kcm_competency_type": "behavioural",
        "mapping_type": "validated",
        "mapping_method": "expert_curricular_review",
        "evidence_or_rationale": "Valid rationale asserting validation but omitting reviewer metadata.",
        "course_source_id": "SRC-MOSPI-ACBP-2026-27",
        "course_source_page": 2,
        "course_source_row": "17",
        "kcm_source_id": "SRC-CBC-KCM-2024",
        "kcm_source_page_def": 49,
        "kcm_source_page_sub": 50,
        "confidence_score": None,
        "confidence_metric": None,
        "validation_status": "validated",
        "reviewer_id": None,  # Missing
        "reviewer_role": None,  # Missing
        "reviewed_at": None,  # Missing
        "reviewer_notes": "",
        "creation_method": "automated_pipeline",
        "pipeline_version": "3.2.0",
        "created_at": "2026-10-18T14:40:00+00:00",
        "source_hash_course": EXPECTED_COURSE_HASH,
        "source_hash_kcm": EXPECTED_KCM_HASH,
    }

    errors = validate_single_record(bad_rec, courses_by_id, kcm_by_id, set(), set())
    assert any("reviewer_id" in e for e in errors)
    assert any("reviewer_role" in e for e in errors)
    assert any("reviewed_at" in e for e in errors)


def test_review_cli_dry_run_validate():
    """Verify review_mapping.py dry-run validation succeeds on valid mapping_id."""
    success, msg = execute_review(
        target_id="MAP-ACBP-KCM-017",
        action="validate",
        reviewer_id="nssta_reviewer_01",
        reviewer_role="NSSTA Faculty",
        rationale="Verified that course syllabus specifically covers inter-departmental trust and collaboration.",
        dry_run=True,
    )
    assert success
    assert "successfully evaluated for action 'validate' -> validated" in msg


def test_review_cli_dry_run_reject():
    """Verify review_mapping.py dry-run rejection succeeds and preserves audit critique."""
    success, msg = execute_review(
        target_id="MAP-ACBP-KCM-017",
        action="reject",
        reviewer_id="nssta_reviewer_01",
        reviewer_role="NSSTA Faculty",
        rationale="Course covers introductory departmental communication rather than full KCM collaboration sub-themes.",
        dry_run=True,
    )
    assert success
    assert "successfully evaluated for action 'reject' -> rejected" in msg


def test_review_cli_rejects_illegal_transition():
    """Verify review_mapping.py refuses to validate an unresolved domain course."""
    success, msg = execute_review(
        target_id="MAP-ACBP-KCM-001",
        action="validate",
        reviewer_id="nssta_reviewer_01",
        reviewer_role="NSSTA Faculty",
        rationale="Invalid attempt to validate an unresolved course directly.",
        dry_run=True,
    )
    assert not success
    assert "Illegal transition" in msg


def test_review_cli_rejects_course_id_as_ambiguous():
    """Verify review_mapping.py strictly rejects course_record_id with clear explanatory error (LIM-01)."""
    success, msg = execute_review(
        target_id="ACBP-CRS-017",
        action="validate",
        reviewer_id="nssta_reviewer_01",
        reviewer_role="NSSTA Faculty",
        rationale="Attempting to use course_record_id instead of mapping_id.",
        dry_run=True,
    )
    assert not success
    assert "Ambiguous identifier" in msg
    assert "course_record_id, not a mapping_id" in msg
    assert "MAP-ACBP-KCM-017" in msg


def test_review_cli_rejects_malformed_and_unknown_identifiers():
    """Verify review_mapping.py rejects empty, malformed, and non-existent mapping IDs."""
    # Empty
    success, msg = execute_review(target_id="", action="validate", rationale="Test", dry_run=True)
    assert not success
    assert "cannot be empty" in msg

    # Malformed format
    success, msg = execute_review(target_id="INVALID_ID_FORMAT", action="validate", rationale="Test", dry_run=True)
    assert not success
    assert "Invalid identifier format" in msg

    # Non-existent mapping ID
    success, msg = execute_review(target_id="MAP-ACBP-KCM-999", action="validate", rationale="Test", dry_run=True)
    assert not success
    assert "No mapping record exists with mapping_id 'MAP-ACBP-KCM-999'" in msg


def test_builder_refuses_overwrite_by_default(monkeypatch, capsys):
    """Verify build_mapping_registry.py refuses to overwrite existing files by default (LIM-02)."""
    import scripts.build_mapping_registry as bmr
    monkeypatch.setattr(sys, "argv", ["scripts/build_mapping_registry.py"])
    with pytest.raises(SystemExit) as excinfo:
        bmr.main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "[SAFETY HALT] Target mapping registry already exists" in captured.err
    assert "--merge-existing" in captured.err


def test_builder_merge_preserves_human_decisions(tmp_path):
    """Verify --merge-existing preserves human decisions (validated, rejected, curated) across rebuilds."""
    import scripts.build_mapping_registry as bmr

    # Load baseline
    courses, kcm_by_id, cand_by_course = bmr.load_input_datasets()
    source_hash_course = bmr.compute_sha256(bmr.ACBP_COURSES_PATH)
    source_hash_kcm = bmr.compute_sha256(bmr.KCM_COMPETENCIES_PATH)

    # Initial build in temp dir
    initial_mappings, initial_queue = bmr.build_mapping_records(
        courses, kcm_by_id, cand_by_course, source_hash_course, source_hash_kcm
    )

    # Simulate a human review: validate MAP-ACBP-KCM-040 and reject MAP-ACBP-KCM-036
    for m in initial_mappings:
        if m["mapping_id"] == "MAP-ACBP-KCM-040":
            m["mapping_type"] = "validated"
            m["validation_status"] = "validated"
            m["reviewer_id"] = "sme_faculty_01"
            m["reviewer_role"] = "NSSTA Faculty"
            m["reviewed_at"] = "2026-10-18T15:00:00+00:00"
            m["evidence_or_rationale"] = "Human verified: Indic leadership syllabus matches KCM-BEH-10 indicators."
            m["reviewer_notes"] = "Approved after module outline audit."
        elif m["mapping_id"] == "MAP-ACBP-KCM-036":
            m["validation_status"] = "rejected"
            m["reviewer_id"] = "sme_faculty_01"
            m["reviewer_role"] = "NSSTA Faculty"
            m["reviewed_at"] = "2026-10-18T15:05:00+00:00"
            m["evidence_or_rationale"] = "REJECTED: 36m lecture does not satisfy technical project management criteria."

    # Index simulated existing records
    existing_by_id = {m["mapping_id"]: m for m in initial_mappings}

    # Execute merge
    merged_mappings, merged_queue = bmr.build_mapping_records(
        courses, kcm_by_id, cand_by_course, source_hash_course, source_hash_kcm, existing_records=existing_by_id
    )

    # Verify that human decisions were preserved 100%
    merged_by_id = {m["mapping_id"]: m for m in merged_mappings}

    val_rec = merged_by_id["MAP-ACBP-KCM-040"]
    assert val_rec["validation_status"] == "validated"
    assert val_rec["reviewer_id"] == "sme_faculty_01"
    assert val_rec["reviewer_role"] == "NSSTA Faculty"
    assert val_rec["reviewed_at"] == "2026-10-18T15:00:00+00:00"
    assert "Indic leadership syllabus matches" in val_rec["evidence_or_rationale"]
    assert val_rec["reviewer_notes"] == "Approved after module outline audit."

    rej_rec = merged_by_id["MAP-ACBP-KCM-036"]
    assert rej_rec["validation_status"] == "rejected"
    assert rej_rec["reviewer_id"] == "sme_faculty_01"
    assert "does not satisfy technical project management criteria" in rej_rec["evidence_or_rationale"]


def test_builder_merge_detects_source_conflict_safely(tmp_path):
    """Verify --merge-existing detects source conflict and aborts safely without corrupting files."""
    import scripts.build_mapping_registry as bmr

    courses, kcm_by_id, cand_by_course = bmr.load_input_datasets()
    source_hash_course = bmr.compute_sha256(bmr.ACBP_COURSES_PATH)
    source_hash_kcm = bmr.compute_sha256(bmr.KCM_COMPETENCIES_PATH)

    # Initial build
    initial_mappings, _ = bmr.build_mapping_records(
        courses, kcm_by_id, cand_by_course, source_hash_course, source_hash_kcm
    )

    # Simulate validated record with old course title
    existing_by_id = {m["mapping_id"]: dict(m) for m in initial_mappings}
    existing_by_id["MAP-ACBP-KCM-040"]["validation_status"] = "validated"
    existing_by_id["MAP-ACBP-KCM-040"]["reviewer_id"] = "sme_faculty_01"
    existing_by_id["MAP-ACBP-KCM-040"]["course_name"] = "Different Old Title Before Update"

    # Running build should detect conflict and raise ValueError
    with pytest.raises(ValueError) as excinfo:
        bmr.build_mapping_records(
            courses, kcm_by_id, cand_by_course, source_hash_course, source_hash_kcm, existing_records=existing_by_id
        )
    assert "Conflict detected for course 'ACBP-CRS-040'" in str(excinfo.value)
    assert "Source course metadata in acbp_courses.json has changed" in str(excinfo.value)


def test_failed_review_operation_leaves_registry_unchanged():
    """Verify that a rejected or invalid review operation leaves persistent files byte-for-byte identical."""
    hash_json_before = compute_sha256(MAPPINGS_JSON_PATH)
    hash_csv_before = compute_sha256(MAPPINGS_CSV_PATH)

    # Attempt illegal transition
    success, _ = execute_review(
        target_id="MAP-ACBP-KCM-001",
        action="validate",
        reviewer_id="illegal_reviewer",
        reviewer_role="NSSTA Faculty",
        rationale="Illegal validation of unresolved course",
        dry_run=False,
    )
    assert not success

    hash_json_after = compute_sha256(MAPPINGS_JSON_PATH)
    hash_csv_after = compute_sha256(MAPPINGS_CSV_PATH)

    assert hash_json_before == hash_json_after, "Registry JSON modified during failed operation!"
    assert hash_csv_before == hash_csv_after, "Registry CSV modified during failed operation!"

