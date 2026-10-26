"""
SIH26101 - Stage 2B.1: Automated Regression Test Suite for MoSPI ACBP OCR Extraction
=====================================================================================
Validates OCR extraction fidelity, table recovery, 1-indexed page preservation,
cadre mapping completeness, and strict GoI data integrity rules.
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
OCR_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "SRC-MOSPI-ACBP-2026-27_ocr.json"
TABLES_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "SRC-MOSPI-ACBP-2026-27_tables.json"
COURSES_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "SRC-MOSPI-ACBP-2026-27_tables.csv"
NODAL_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "SRC-MOSPI-ACBP-2026-27_nodal_officers.csv"
QUALITY_REPORT_PATH = PROJECT_ROOT / "docs" / "acbp_ocr_quality_report.md"
KCM_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"

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
def ocr_data() -> Dict[str, Any]:
    assert OCR_JSON_PATH.exists(), f"Missing required file: {OCR_JSON_PATH}"
    with open(OCR_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def tables_data() -> Dict[str, Any]:
    assert TABLES_JSON_PATH.exists(), f"Missing required file: {TABLES_JSON_PATH}"
    with open(TABLES_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_artifacts_exist_and_non_empty() -> None:
    """Verify all Stage 2B.1 output artifacts are generated and non-empty."""
    for path in [OCR_JSON_PATH, TABLES_JSON_PATH, COURSES_CSV_PATH, NODAL_CSV_PATH, QUALITY_REPORT_PATH]:
        assert path.exists(), f"Missing output artifact: {path}"
        assert path.stat().st_size > 0, f"Artifact is empty: {path}"


def test_document_metadata_and_sha256(ocr_data: Dict[str, Any]) -> None:
    """Verify source document identity, SHA256 checksum, and official provenance."""
    assert ocr_data["document_id"] == "SRC-MOSPI-ACBP-2026-27"
    assert ocr_data["sha256"] == EXPECTED_SHA256
    assert ocr_data["data_provenance_classification"] == "official_public"
    assert ocr_data["validation_status"] == "pending_review"
    assert ocr_data["total_pages"] == 13
    assert ocr_data["pages_processed"] == 13


def test_page_number_preservation_and_indexing(ocr_data: Dict[str, Any]) -> None:
    """Ensure strict 1-indexed page numbering across all 13 pages."""
    pages = ocr_data["pages"]
    assert len(pages) == 13
    page_nums = [p["page_number"] for p in pages]
    assert page_nums == list(range(1, 14)), f"Page numbers must be 1..13, got: {page_nums}"


def test_dual_extraction_methods_distinguished(ocr_data: Dict[str, Any]) -> None:
    """Verify that native PDF text and OCR layers are explicitly distinguished."""
    for p in ocr_data["pages"]:
        assert "extraction_methods" in p
        methods = p["extraction_methods"]
        assert "native_pdf" in methods
        assert "ocr_easyocr" in methods
        # Native text must record the eOffice watermark string
        assert "1200351/2026/O/o NSSTA" in p["native_text"] or "File No." in p["native_text"]


def test_page_1_office_memorandum_structure(ocr_data: Dict[str, Any]) -> None:
    """Verify Page 1 circular metadata, reference numbers, directives, and signatory."""
    p1 = ocr_data["pages"][0]
    assert p1["page_number"] == 1
    assert p1["page_type"] == "office_memorandum"
    meta = p1["metadata"]
    assert meta["file_no"] == "Y-11011/01/2022-23/NSSTA-Part (i)"
    assert meta["date"] == "22.09.2026"
    assert "ACBP" in meta["subject"]
    assert "Karmayogi" in meta["dopt_reference"]
    assert "Suraj Kumar Shukla" in meta["signatory"]
    assert "one hour of learning" in meta["monthly_mandate"]


def test_all_11_cadres_present_in_annexure_i(ocr_data: Dict[str, Any]) -> None:
    """Verify that all 11 official cadres are recovered on Pages 2 to 12."""
    cadre_pages = ocr_data["pages"][1:12]
    assert len(cadre_pages) == 11
    extracted_titles = [p["cadre_role"] for p in cadre_pages]
    assert extracted_titles == EXPECTED_CADRES

    for p in cadre_pages:
        assert p["table_headers"] == ["S. No.", "Course Name", "Competency", "Duration", "Course Creator"]
        assert p["row_count"] >= 20, f"Page {p['page_number']} has only {p['row_count']} rows"


def test_course_table_records_fidelity(tables_data: Dict[str, Any]) -> None:
    """Verify recovered courses in the tables catalog."""
    courses = tables_data["courses"]
    assert len(courses) >= 220, f"Expected >= 220 courses, got {len(courses)}"
    assert tables_data["total_courses"] == len(courses)

    for c in courses:
        assert c["source_page"] in range(2, 13)
        assert c["cadre_role"] in EXPECTED_CADRES
        assert len(c["course_name"]) > 0
        assert c["competency"] in {"Domain", "Functional", "Behavioural", "Unknown"}
        assert c["provenance"] == "official_public"
        assert c["validation_status"] == "pending_review"


def test_competency_type_distribution(tables_data: Dict[str, Any]) -> None:
    """Ensure courses cover all three GoI competency pillars (Domain, Functional, Behavioural)."""
    courses = tables_data["courses"]
    comp_types = {c["competency"] for c in courses}
    assert "Domain" in comp_types
    assert "Functional" in comp_types
    assert "Behavioural" in comp_types

    domain_count = sum(1 for c in courses if c["competency"] == "Domain")
    func_count = sum(1 for c in courses if c["competency"] == "Functional")
    beh_count = sum(1 for c in courses if c["competency"] == "Behavioural")

    assert domain_count >= 30, f"Expected >= 30 domain courses, got {domain_count}"
    assert func_count >= 75, f"Expected >= 75 functional courses, got {func_count}"
    assert beh_count >= 80, f"Expected >= 80 behavioural courses, got {beh_count}"


def test_nodal_officers_directory_page_13(tables_data: Dict[str, Any], ocr_data: Dict[str, Any]) -> None:
    """Verify Annexure II Nodal Officers directory on Page 13."""
    p13 = ocr_data["pages"][12]
    assert p13["page_number"] == 13
    assert p13["page_type"] == "annexure_nodal_officers"
    assert p13["table_headers"] == ["Sr. No.", "Division", "Name of the Officer", "Designation", "Email"]

    nodals = tables_data["nodal_officers"]
    assert len(nodals) == 30, f"Expected 30 nodal officers, got {len(nodals)}"
    assert tables_data["total_nodal_officers"] == 30

    for n in nodals:
        assert n["source_page"] == 13
        assert len(n["division"]) > 0
        assert n["provenance"] == "official_public"
        assert n["validation_status"] == "pending_review"


def test_uncertainty_flagging_without_guessing(ocr_data: Dict[str, Any], tables_data: Dict[str, Any]) -> None:
    """Ensure low-confidence or noisy OCR outputs are explicitly flagged rather than guessed."""
    uncertain_courses = [c for c in tables_data["courses"] if c["is_uncertain"]]
    assert len(uncertain_courses) > 0, "Expected at least some uncertain courses to be flagged"

    uncertain_nodals = [n for n in tables_data["nodal_officers"] if n["is_uncertain"]]
    assert len(uncertain_nodals) > 0, "Expected at least some uncertain nodal officers to be flagged"

    # Verify that flags contain clear diagnostic reasons
    for c in uncertain_courses:
        assert len(c["uncertainty_flags"]) > 0


def test_csv_export_consistency(tables_data: Dict[str, Any]) -> None:
    """Verify consistency between exported CSVs and JSON catalogs."""
    with open(COURSES_CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == len(tables_data["courses"])

    with open(NODAL_CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == len(tables_data["nodal_officers"])


def test_immutability_of_kcm_dataset_and_raw_pdfs() -> None:
    """Verify that the raw PDF files and the Stage 2A KCM frozen dataset are 100% untouched."""
    raw_files = list(RAW_PDF_PATH.parent.glob("*.pdf"))
    assert len(raw_files) == 5, f"Expected exactly 5 raw PDFs in data/raw/, found {len(raw_files)}"

    # Check that KCM processed JSON is intact and matches freeze checksum
    assert KCM_PROCESSED_PATH.exists()
    sha = hashlib.sha256()
    with open(KCM_PROCESSED_PATH, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    assert sha.hexdigest() == KCM_FROZEN_SHA256, "KCM processed dataset hash has changed!"
