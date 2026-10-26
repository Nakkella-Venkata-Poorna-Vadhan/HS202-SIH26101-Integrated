"""
Automated Test Suite for MoSPI ACBP to KCM Competency Mapping Benchmark (Stage 3.3).

Verifies:
  1. Structural validity of the 26-case benchmark manifest and reviewer template.
  2. Parity between JSON and CSV representations.
  3. 100% referential integrity with baseline acbp_courses.json and competencies_kcm.json.
  4. Strict safeguards against fabricated ground-truth labels and imaginary syllabi.
  5. Immutability of source datasets and production registry files.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Paths
ACBP_COURSES_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_COMPETENCIES_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
CANDIDATES_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_candidate_mappings.json"
MAPPINGS_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.json"
MAPPINGS_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.csv"
REVIEW_QUEUE_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_review_queue.json"

MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
MANIFEST_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.csv"
TEMPLATE_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_template.json"
TEMPLATE_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_template.csv"
READINESS_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_evidence_readiness.json"
READINESS_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_evidence_readiness.csv"
PACK_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_evidence_pack.json"
PACK_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_evidence_pack.csv"

# Immutable baselines
EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"
EXPECTED_CANDIDATE_HASH = "966cabebbcc02f5cc96f5879fdbe3c7af126adfdf57ad5c5219aae580656b801"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def manifest_data():
    with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def template_data():
    with open(TEMPLATE_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def courses_data():
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["records"]


@pytest.fixture(scope="module")
def kcm_data():
    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_baseline_dataset_immutability():
    """Verify that source datasets and production registry remain strictly untouched."""
    assert compute_sha256(ACBP_COURSES_PATH) == EXPECTED_COURSE_HASH
    assert compute_sha256(KCM_COMPETENCIES_PATH) == EXPECTED_KCM_HASH
    assert compute_sha256(CANDIDATES_PATH) == EXPECTED_CANDIDATE_HASH


def test_benchmark_artifacts_exist_and_non_empty():
    """Verify manifest and template artifacts exist and have non-zero size."""
    for p in [MANIFEST_JSON_PATH, MANIFEST_CSV_PATH, TEMPLATE_JSON_PATH, TEMPLATE_CSV_PATH]:
        assert p.exists(), f"Benchmark file {p} does not exist!"
        assert p.stat().st_size > 0, f"Benchmark file {p} is empty!"


def test_manifest_structure_and_strata(manifest_data):
    """Verify benchmark manifest contains exactly 26 stratified cases."""
    assert manifest_data["benchmark_id"] == "BM-PILOT-MOSPI-2026-V1"
    assert manifest_data["version"] == "1.0.0"
    assert manifest_data["total_cases"] == 26

    strata = manifest_data["strata_summary"]
    assert strata["strata_a_title_candidate"] == 6
    assert strata["strata_b_behavioural_unresolved"] == 6
    assert strata["strata_c_functional_unresolved"] == 7
    assert strata["strata_d_domain_statistical_gap"] == 5
    assert strata["strata_e_cross_cadre_contrast"] == 2

    cases = manifest_data["cases"]
    assert len(cases) == 26

    # Verify unique case IDs
    case_ids = [c["benchmark_case_id"] for c in cases]
    assert len(case_ids) == len(set(case_ids))
    assert all(cid.startswith("BM-CASE-") for cid in case_ids)


def test_manifest_referential_integrity(manifest_data, courses_data, kcm_data):
    """Verify that 100% of benchmark cases reference real courses and valid KCM competencies."""
    courses_by_id = {c["record_id"]: c for c in courses_data}
    kcm_by_id = {k["competency_id"]: k for k in kcm_data}

    for case in manifest_data["cases"]:
        cid = case["course_record_id"]
        assert cid in courses_by_id, f"Foreign key violation: course {cid} not in acbp_courses.json!"
        src = courses_by_id[cid]

        assert case["course_name"] == src["course_name"]
        assert case["cadre_role"] == src["cadre_role"]
        assert case["acbp_competency_category"] == src["competency_category"]
        assert case["course_source_page"] == src["source_page"]
        assert case["course_source_row"] == src["source_row"]
        assert case["course_source_id"] == src["source_id"]

        kid = case["candidate_kcm_competency_id"]
        if kid is not None:
            assert kid in kcm_by_id, f"Foreign key violation: competency {kid} not in competencies_kcm.json!"
            ksrc = kcm_by_id[kid]
            assert case["candidate_kcm_competency_name"] == ksrc["competency_name"]
            assert case["candidate_kcm_competency_type"] == ksrc["competency_type"]


def test_template_strictly_safeguards_against_fabricated_labels(template_data):
    """Verify that 100% of cases in template have unassigned ground truth and blank review fields."""
    assert template_data["template_id"] == "TPL-BM-PILOT-MOSPI-2026-V1"
    assert template_data["total_cases"] == 26

    annotations = template_data["annotations"]
    assert len(annotations) == 26

    for ann in annotations:
        # Crucial safeguard: no fabricated labels or imaginary syllabi
        assert ann["assigned_benchmark_label"] is None, (
            f"Violation: Case {ann['benchmark_case_id']} has premature label '{ann['assigned_benchmark_label']}'!"
        )
        assert ann["reviewer_id"] is None
        assert ann["reviewer_role"] is None
        assert ann["annotation_date"] is None
        assert ann["target_kcm_competency_id"] is None
        assert ann["target_kcm_subtheme"] is None
        assert ann["evidence_sufficiency"] is None
        assert ann["evidence_source_citation"] is None
        assert ann["evidence_excerpt"] is None
        assert ann["reviewer_rationale"] is None
        assert ann["counter_evidence_notes"] is None
        assert ann["adjudication_status"] == "pending_annotation"
        assert ann["adjudicator_id"] is None
        assert ann["adjudicator_notes"] is None


def test_json_and_csv_parity_manifest(manifest_data):
    """Verify exact parity between JSON and CSV manifest representations."""
    with open(MANIFEST_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    cases = manifest_data["cases"]
    assert len(cases) == len(csv_rows)

    for j_rec, c_rec in zip(cases, csv_rows):
        for k, v in j_rec.items():
            expected = "" if v is None else str(v)
            assert c_rec[k] == expected, f"Parity mismatch on {j_rec['benchmark_case_id']} field {k}"


def test_json_and_csv_parity_template(template_data):
    """Verify exact parity between JSON and CSV template representations."""
    with open(TEMPLATE_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    annotations = template_data["annotations"]
    assert len(annotations) == len(csv_rows)

    for j_rec, c_rec in zip(annotations, csv_rows):
        for k, v in j_rec.items():
            expected = "" if v is None else str(v)
            assert c_rec[k] == expected, f"Parity mismatch on template case {j_rec['benchmark_case_id']} field {k}"
            # Ensure label column is empty in CSV as well
            if k == "assigned_benchmark_label":
                assert c_rec[k] == "", f"Fabricated label in CSV for {j_rec['benchmark_case_id']}"


@pytest.fixture(scope="module")
def readiness_data():
    with open(READINESS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def pack_data():
    with open(PACK_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_evidence_readiness_report_integrity(readiness_data, courses_data):
    """Verify evidence readiness audit correctly documents missing syllabi across all 26 cases."""
    assert readiness_data["report_id"] == "AUDIT-BM-PILOT-MOSPI-2026-V1"
    assert readiness_data["total_cases_audited"] == 26
    assert readiness_data["readiness_verdict"] == "READY FOR PARTIAL HUMAN REVIEW"

    summary = readiness_data["evidence_tier_summary"]
    assert summary["substantive_course_evidence_count"] == 0
    assert summary["catalogue_metadata_only_count"] == 26
    assert summary["external_syllabus_required_count"] == 26

    courses_by_id = {c["record_id"]: c for c in courses_data}
    cases = readiness_data["cases"]
    assert len(cases) == 26

    for c in cases:
        cid = c["course_record_id"]
        assert cid in courses_by_id
        assert c["course_evidence_tier"] == "catalogue_metadata_only"
        assert c["has_substantive_syllabus"] is False
        assert c["evidence_sufficient_for_supported_mapping"] is False
        assert c["evidence_sufficient_for_triage_or_gap_flag"] is True
        assert len(c["missing_evidence"]) > 0
        assert len(c["next_action_required"]) > 0

    # CSV Parity check
    with open(READINESS_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(cases) == len(csv_rows)
    for j_rec, c_rec in zip(cases, csv_rows):
        for k, v in j_rec.items():
            expected = "" if v is None else str(v)
            assert c_rec[k] == expected


def test_evidence_pack_safeguards_and_parity(pack_data):
    """Verify evidence pack explicitly keeps syllabi missing and matches CSV parity."""
    assert pack_data["pack_id"] == "PACK-BM-PILOT-MOSPI-2026-V1"
    assert pack_data["total_cases"] == 26

    evidence_pack = pack_data["evidence_pack"]
    assert len(evidence_pack) == 26

    for item in evidence_pack:
        assert item["course_syllabus_excerpt"] == "[OFFICIAL SYLLABUS NOT PRESENT IN SOURCE DOCUMENT]"
        assert item["acbp_source_citation"].startswith("SRC-MOSPI-ACBP-2026-27")
        assert len(item["course_verbatim_metadata"]) > 0
        assert item["recommended_triage_label"] in ("plausible_insufficient_evidence", "unresolved_insufficient_source")

    # CSV Parity check
    with open(PACK_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(evidence_pack) == len(csv_rows)
    for j_rec, c_rec in zip(evidence_pack, csv_rows):
        for k, v in j_rec.items():
            expected = "" if v is None else str(v)
            assert c_rec[k] == expected
