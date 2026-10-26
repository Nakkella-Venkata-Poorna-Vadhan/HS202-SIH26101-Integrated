"""
Automated Test Suite for Evidence Provenance and Claim Audit (Stage 3.4.1).

Verifies:
  1. Structural integrity of data/interim/course_evidence_provenance_audit.json.
  2. 100% referential integrity across all 26 benchmark cases.
  3. Adherence to allowed audit statuses and non-upgrading rule (exact_course_verified == 0).
  4. 100% validity of claimed KCM competency IDs and verbatim names.
  5. Rigorous domain-gap audit standards for HCES and ASI.
  6. Immutability of baseline source datasets.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Paths
AUDIT_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_provenance_audit.json"
MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
ACBP_COURSES_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_COMPETENCIES_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"

ALLOWED_AUDIT_STATUSES = {
    "exact_course_verified",
    "official_related_material",
    "possible_match_needs_verification",
    "access_restricted",
    "not_found_publicly",
}

EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def audit_data():
    with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_data():
    with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def courses_data():
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["records"]


@pytest.fixture(scope="module")
def kcm_data():
    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        return {k["competency_id"]: k for k in json.load(f)}


def test_baseline_dataset_immutability():
    """Verify source datasets remain untouched during Stage 3.4.1."""
    assert compute_sha256(ACBP_COURSES_PATH) == EXPECTED_COURSE_HASH
    assert compute_sha256(KCM_COMPETENCIES_PATH) == EXPECTED_KCM_HASH


def test_provenance_audit_file_exists_and_valid(audit_data):
    """Verify audit JSON exists, is valid, and contains 26 audited cases."""
    assert audit_data["audit_id"] == "AUDIT-PROVENANCE-BM-PILOT-MOSPI-2026-V1"
    assert audit_data["benchmark_id"] == "BM-PILOT-MOSPI-2026-V1"
    assert audit_data["total_cases_audited"] == 26
    assert audit_data["audit_verdict"] == "EVIDENCE AUDIT PASSED WITH LIMITATIONS"

    cases = audit_data["cases"]
    assert len(cases) == 26
    case_ids = [c["benchmark_case_id"] for c in cases]
    assert len(case_ids) == len(set(case_ids))
    assert all(cid.startswith("BM-CASE-") for cid in case_ids)


def test_provenance_audit_referential_integrity(audit_data, manifest_data, courses_data):
    """Verify all audited records match manifest cases and course catalogue."""
    courses_by_id = {c["record_id"]: c for c in courses_data}
    manifest_by_id = {m["benchmark_case_id"]: m for m in manifest_data["cases"]}

    for rec in audit_data["cases"]:
        case_id = rec["benchmark_case_id"]
        assert case_id in manifest_by_id
        m = manifest_by_id[case_id]

        cid = rec["course_record_id"]
        assert cid == m["course_record_id"]
        assert cid in courses_by_id
        src = courses_by_id[cid]

        assert rec["course_name"] == src["course_name"]
        assert rec["cadre_role"] == src["cadre_role"]
        assert rec["acbp_competency_category"] == src["competency_category"]


def test_no_unverified_source_upgraded_to_exact_course(audit_data):
    """Verify strict audit rule: exact_course_verified must be 0 without local primary syllabi."""
    summary = audit_data["audit_classification_summary"]
    assert summary["exact_course_verified"] == 0, (
        "Violation: exact_course_verified cannot be assigned when exact iGOT course lesson plans are unmirrored locally."
    )
    assert summary["official_related_material"] == 12
    assert summary["possible_match_needs_verification"] == 5
    assert summary["access_restricted"] == 9
    assert summary["not_found_publicly"] == 0

    for rec in audit_data["cases"]:
        assert rec["audit_classification"] in ALLOWED_AUDIT_STATUSES
        # Verify that any official_related_material is flagged with realistic limitations
        if rec["audit_classification"] == "official_related_material":
            assert len(rec["limitations"]) > 0


def test_claimed_kcm_competencies_referential_validity(audit_data, kcm_data):
    """Verify that 100% of claimed KCM competencies match valid IDs and verbatim names in KCM 2024."""
    for rec in audit_data["cases"]:
        kid = rec["claimed_kcm_id"]
        if kid is not None:
            assert rec["kcm_id_valid"] is True
            assert rec["kcm_name_valid"] is True
            assert kid in kcm_data, f"Invalid KCM competency ID {kid}"
            expected_name = kcm_data[kid]["competency_name"]
            assert rec["claimed_kcm_name"] == expected_name


def test_hces_and_asi_domain_gap_audit_rigor(audit_data):
    """Verify that HCES and ASI cases are not treated as automatic zero-matches without noting analytical overlap."""
    cases_by_id = {c["benchmark_case_id"]: c for c in audit_data["cases"]}

    hces_case = cases_by_id["BM-CASE-022"]
    assert hces_case["course_record_id"] == "ACBP-CRS-067"
    assert hces_case["competency_relationship_tier"] == "potential_domain_gap_requires_adjudication"
    assert hces_case["domain_gap_finding"] == "strong_domain_gap_candidate_with_generic_analytics_overlap"

    asi_case = cases_by_id["BM-CASE-023"]
    assert asi_case["course_record_id"] == "ACBP-CRS-069"
    assert asi_case["competency_relationship_tier"] == "potential_domain_gap_requires_adjudication"
    assert asi_case["domain_gap_finding"] == "strong_domain_gap_candidate_with_generic_analytics_overlap"
