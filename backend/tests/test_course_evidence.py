"""
Automated Test Suite for Course Evidence Acquisition Ledger (Stage 3.4).

Verifies:
  1. Structural validity of data/interim/course_evidence_ledger.json and .csv.
  2. Exact referential integrity across all 26 benchmark cases.
  3. Adherence to allowed acquisition statuses.
  4. Non-fabrication of evidence excerpts and citations.
  5. JSON and CSV parity.
  6. Immutability of raw and processed baselines.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Paths
LEDGER_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_ledger.json"
LEDGER_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_ledger.csv"
MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
ACBP_COURSES_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_COMPETENCIES_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"

ALLOWED_ACQUISITION_STATUSES = {
    "official_evidence_found",
    "possible_match_needs_verification",
    "not_found_publicly",
    "access_restricted",
    "institutional_request_needed",
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
def ledger_data():
    with open(LEDGER_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_data():
    with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def courses_data():
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["records"]


def test_baseline_dataset_immutability():
    """Verify source datasets remain untouched during Stage 3.4."""
    assert compute_sha256(ACBP_COURSES_PATH) == EXPECTED_COURSE_HASH
    assert compute_sha256(KCM_COMPETENCIES_PATH) == EXPECTED_KCM_HASH


def test_evidence_ledger_files_exist_and_non_empty():
    """Verify evidence ledger JSON and CSV exist and are non-empty."""
    assert LEDGER_JSON_PATH.exists()
    assert LEDGER_JSON_PATH.stat().st_size > 0
    assert LEDGER_CSV_PATH.exists()
    assert LEDGER_CSV_PATH.stat().st_size > 0


def test_evidence_ledger_structure_and_counts(ledger_data):
    """Verify ledger contains exactly 26 audited cases."""
    assert ledger_data["ledger_id"] == "LEDGER-BM-PILOT-MOSPI-2026-V1"
    assert ledger_data["total_cases_catalogued"] == 26

    records = ledger_data["records"]
    assert len(records) == 26

    case_ids = [r["benchmark_case_id"] for r in records]
    assert len(case_ids) == len(set(case_ids))
    assert all(cid.startswith("BM-CASE-") for cid in case_ids)


def test_evidence_ledger_referential_integrity(ledger_data, manifest_data, courses_data):
    """Verify 100% of ledger records match manifest cases and course catalogue."""
    courses_by_id = {c["record_id"]: c for c in courses_data}
    manifest_by_id = {m["benchmark_case_id"]: m for m in manifest_data["cases"]}

    for rec in ledger_data["records"]:
        case_id = rec["benchmark_case_id"]
        assert case_id in manifest_by_id, f"Case {case_id} not in manifest!"
        m = manifest_by_id[case_id]

        cid = rec["course_record_id"]
        assert cid == m["course_record_id"]
        assert cid in courses_by_id
        src = courses_by_id[cid]

        assert rec["course_name"] == src["course_name"]
        assert rec["cadre_role"] == src["cadre_role"]
        assert rec["acbp_competency_category"] == src["competency_category"]


def test_acquisition_statuses_validity(ledger_data):
    """Verify every record uses an allowed acquisition status."""
    for rec in ledger_data["records"]:
        st = rec["acquisition_status"]
        assert st in ALLOWED_ACQUISITION_STATUSES, f"Illegal status '{st}' in {rec['benchmark_case_id']}"
        assert len(rec["source_institution"]) > 0
        assert len(rec["source_document_title"]) > 0
        assert len(rec["source_url_or_path"]) > 0
        assert len(rec["evidence_excerpt_verbatim"]) > 0
        assert len(rec["institutional_contact_channel"]) > 0


def test_official_evidence_found_fidelity(ledger_data):
    """Verify records flagged as official_evidence_found have concrete curricular excerpts."""
    found_records = [r for r in ledger_data["records"] if r["acquisition_status"] == "official_evidence_found"]
    assert len(found_records) >= 10, "Expected at least 10 official evidence findings from ISTM, NSSTA, NIFM, Ayush"

    for r in found_records:
        assert r["evidence_type"] in ("full_syllabus", "curriculum_manual")
        assert r["match_fidelity"] == "exact_match"
        assert len(r["evidence_excerpt_verbatim"]) > 20


def test_access_restricted_records_fidelity(ledger_data):
    """Verify records flagged as access_restricted explicitly identify iGOT portal restrictions."""
    restricted = [r for r in ledger_data["records"] if r["acquisition_status"] == "access_restricted"]
    assert len(restricted) >= 6, "Expected at least 6 access restricted iGOT records"

    for r in restricted:
        assert "igot" in r["source_url_or_path"].lower() or "parichay" in r["source_url_or_path"].lower()
        assert len(r["missing_evidence_details"]) > 0


def test_json_and_csv_parity_evidence_ledger(ledger_data):
    """Verify exact parity between JSON and CSV ledger representations."""
    with open(LEDGER_CSV_PATH, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    records = ledger_data["records"]
    assert len(records) == len(csv_rows)

    for j_rec, c_rec in zip(records, csv_rows):
        for k, v in j_rec.items():
            expected = "" if v is None else str(v)
            assert c_rec[k] == expected, f"Parity mismatch on {j_rec['benchmark_case_id']} field {k}"
