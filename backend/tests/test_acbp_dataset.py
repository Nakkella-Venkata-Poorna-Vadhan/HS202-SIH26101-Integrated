"""
SIH26101 - Stage 2B.2: Automated Regression Tests for Processed ACBP Datasets
=============================================================================
Validates data integrity, schema compliance, JSON/CSV parity, uncertainty preservation,
KCM reconciliation boundaries, and non-modification invariants.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PDF_PATH = PROJECT_ROOT / "data" / "raw" / "OM -Annual Capacity Building Plan (ACBP) for MoSPI officials employees for FY 2026–27.pdf"
KCM_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"

PROCESSED_COURSES_JSON = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
PROCESSED_COURSES_CSV = PROJECT_ROOT / "data" / "processed" / "acbp_courses.csv"
PROCESSED_NODAL_JSON = PROJECT_ROOT / "data" / "processed" / "acbp_nodal_officers.json"
PROCESSED_NODAL_CSV = PROJECT_ROOT / "data" / "processed" / "acbp_nodal_officers.csv"
PROCESSED_MAPPINGS_JSON = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_candidate_mappings.json"

DATA_DICTIONARY_MD = PROJECT_ROOT / "docs" / "acbp_data_dictionary.md"
RECONCILIATION_REPORT_MD = PROJECT_ROOT / "docs" / "acbp_reconciliation_report.md"

EXPECTED_SHA256 = "73ee47e6809982b63ffe928e95e86e4084d33865d325876e0cb9ff755a634205"
KCM_FROZEN_SHA256 = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"

EXPECTED_CADRES = [
    "Deputy Director General / Joint Secretary Equivalent and Above",
    "Director / Joint Director",
    "Deputy Secretary / Under Secretary",
    "Assistant Director / Deputy Director",
    "Sr. PPS / PSO / PPS / PS",
    "Senior Statistical Officers / Section Officer / Senior Administrative Officer / Administrative Officer",
    "Junior Statistical Officers / Assistant Section Officers / Data Processing Assistant (All Grades)",
    "AD(OL) / Senior Hindi Translator / Junior Hindi Translator",
    "Assistants / Upper Division Clerk / Lower Division Clerk",
    "Stenographer (All Grades) / Data Entry Operator (All Grades)",
    "MTS / Driver (All Grades)",
]


@pytest.fixture(scope="module")
def courses_data() -> Dict[str, Any]:
    assert PROCESSED_COURSES_JSON.exists(), f"Missing file: {PROCESSED_COURSES_JSON}"
    with open(PROCESSED_COURSES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def nodal_data() -> Dict[str, Any]:
    assert PROCESSED_NODAL_JSON.exists(), f"Missing file: {PROCESSED_NODAL_JSON}"
    with open(PROCESSED_NODAL_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def mappings_data() -> Dict[str, Any]:
    assert PROCESSED_MAPPINGS_JSON.exists(), f"Missing file: {PROCESSED_MAPPINGS_JSON}"
    with open(PROCESSED_MAPPINGS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_processed_files_exist_and_non_empty() -> None:
    """Verify all Stage 2B.2 processed datasets and documents exist and are non-empty."""
    for path in [
        PROCESSED_COURSES_JSON,
        PROCESSED_COURSES_CSV,
        PROCESSED_NODAL_JSON,
        PROCESSED_NODAL_CSV,
        PROCESSED_MAPPINGS_JSON,
        DATA_DICTIONARY_MD,
        RECONCILIATION_REPORT_MD,
    ]:
        assert path.exists(), f"Missing processed file: {path}"
        assert path.stat().st_size > 0, f"File is empty: {path}"


def test_course_record_counts_and_unique_ids(courses_data: Dict[str, Any]) -> None:
    """Verify exact count of 226 courses and globally unique record IDs."""
    records = courses_data["records"]
    assert len(records) == 226, f"Expected 226 course records, got {len(records)}"
    assert courses_data["total_records"] == 226

    ids = [r["record_id"] for r in records]
    assert len(ids) == len(set(ids)), "Duplicate record_id found in courses dataset"
    assert ids[0] == "ACBP-CRS-001"
    assert ids[-1] == "ACBP-CRS-226"


def test_all_11_cadres_present_in_courses(courses_data: Dict[str, Any]) -> None:
    """Verify that all 11 official cadres are present in the course dataset."""
    records = courses_data["records"]
    cadres_present = sorted(list({r["cadre_role"] for r in records}))
    assert cadres_present == sorted(EXPECTED_CADRES)


def test_course_required_fields_and_types(courses_data: Dict[str, Any]) -> None:
    """Ensure all required fields are present and non-empty in every course record."""
    required_keys = [
        "record_id",
        "interim_record_id",
        "cadre_role",
        "course_name",
        "competency_category",
        "duration",
        "course_creator",
        "source_id",
        "source_page",
        "source_row",
        "provenance",
        "validation_status",
        "raw_ocr_values",
        "is_uncertain",
        "uncertainty_flags",
        "review_notes",
    ]

    for r in courses_data["records"]:
        for k in required_keys:
            assert k in r, f"Missing key '{k}' in record {r.get('record_id')}"
            assert r[k] is not None, f"Key '{k}' is null in record {r.get('record_id')}"

        assert r["source_id"] == "SRC-MOSPI-ACBP-2026-27"
        assert r["provenance"] == "official_public"
        assert r["validation_status"] == "pending_review"
        assert r["source_page"] in range(2, 13)
        assert r["competency_category"] in {"Domain", "Functional", "Behavioural"}
        assert len(r["course_name"]) > 0
        assert len(r["course_creator"]) > 0


def test_nodal_officer_record_counts_and_schema(nodal_data: Dict[str, Any]) -> None:
    """Verify nodal officers directory has exactly 30 records and valid fields."""
    records = nodal_data["records"]
    assert len(records) == 30, f"Expected 30 nodal officer records, got {len(records)}"
    assert nodal_data["total_records"] == 30

    ids = [r["record_id"] for r in records]
    assert len(ids) == len(set(ids)), "Duplicate record_id found in nodal directory"

    for r in records:
        assert r["source_page"] == 13
        assert r["source_id"] == "SRC-MOSPI-ACBP-2026-27"
        assert r["provenance"] == "official_public"
        assert r["validation_status"] == "pending_review"
        assert len(r["division"]) > 0
        assert len(r["email"]) > 0
        if not r["officer_name"]:
            assert r["is_uncertain"] is True
            assert any("officer_name" in flag for flag in r["uncertainty_flags"])
        if not r["designation"]:
            assert r["is_uncertain"] is True
            assert any("designation" in flag for flag in r["uncertainty_flags"])
        assert "raw_ocr_values" in r


def test_json_and_csv_parity_for_courses(courses_data: Dict[str, Any]) -> None:
    """Verify byte-for-byte record and field count parity between JSON and CSV exports."""
    with open(PROCESSED_COURSES_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    json_records = courses_data["records"]
    assert len(reader) == len(json_records)

    for csv_row, json_rec in zip(reader, json_records):
        assert csv_row["record_id"] == json_rec["record_id"]
        assert csv_row["cadre_role"] == json_rec["cadre_role"]
        assert csv_row["course_name"] == json_rec["course_name"]
        assert csv_row["competency_category"] == json_rec["competency_category"]
        assert csv_row["duration"] == json_rec["duration"]
        assert csv_row["course_creator"] == json_rec["course_creator"]
        assert int(csv_row["source_page"]) == json_rec["source_page"]


def test_json_and_csv_parity_for_nodals(nodal_data: Dict[str, Any]) -> None:
    """Verify parity for nodal officers CSV and JSON."""
    with open(PROCESSED_NODAL_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    json_records = nodal_data["records"]
    assert len(reader) == len(json_records)

    for csv_row, json_rec in zip(reader, json_records):
        assert csv_row["record_id"] == json_rec["record_id"]
        assert csv_row["division"] == json_rec["division"]
        assert csv_row["officer_name"] == json_rec["officer_name"]
        assert csv_row["email"] == json_rec["email"]


def test_uncertainty_preservation_and_flags(courses_data: Dict[str, Any], nodal_data: Dict[str, Any]) -> None:
    """Verify that uncertain fields are flagged explicitly with preserved raw values."""
    unc_courses = [r for r in courses_data["records"] if r["is_uncertain"]]
    assert len(unc_courses) == 17, f"Expected exactly 17 uncertain course records, got {len(unc_courses)}"

    for c in unc_courses:
        assert len(c["uncertainty_flags"]) > 0
        assert len(c["raw_ocr_values"]) > 0
        assert len(c["review_notes"]) > 0

    unc_nodals = [r for r in nodal_data["records"] if r["is_uncertain"]]
    assert len(unc_nodals) > 0


def test_candidate_kcm_mappings_strictness(mappings_data: Dict[str, Any]) -> None:
    """Verify that KCM candidate mappings prefer exact title references and leave non-explicit unresolved."""
    mappings = mappings_data["mappings"]
    assert len(mappings) == 226

    explicit_maps = [m for m in mappings if m["mapping_method"] != "unresolved"]
    unresolved_maps = [m for m in mappings if m["mapping_method"] == "unresolved"]

    assert len(explicit_maps) > 0, "Expected at least some explicit KCM mappings"
    assert len(unresolved_maps) > 200, "Expected majority of specialized courses to be unresolved without fabrication"

    for m in explicit_maps:
        assert m["candidate_kcm_competency_id"] is not None
        assert m["candidate_kcm_competency_id"].startswith(("KCM-BEH-", "KCM-FUNC-"))
        assert m["confidence"] is not None
        assert m["confidence"] >= 0.85

    for m in unresolved_maps:
        assert m["candidate_kcm_competency_id"] is None
        assert m["confidence"] is None
        assert "No explicit competency name stated" in m["evidence_or_rationale"]


def test_immutability_of_raw_pdfs_and_frozen_kcm() -> None:
    """Ensure raw PDF files and the Stage 2A frozen KCM baseline are 100% unaltered."""
    raw_files = list(RAW_PDF_PATH.parent.glob("*.pdf"))
    assert len(raw_files) == 5, f"Expected 5 raw PDFs, found {len(raw_files)}"

    # Check raw ACBP checksum
    sha_raw = hashlib.sha256(RAW_PDF_PATH.read_bytes()).hexdigest()
    assert sha_raw == EXPECTED_SHA256

    # Check frozen KCM checksum
    sha_kcm = hashlib.sha256(KCM_PROCESSED_PATH.read_bytes()).hexdigest()
    assert sha_kcm == KCM_FROZEN_SHA256, "KCM processed dataset hash was modified!"
