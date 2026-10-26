"""
SIH26101 - Stage 1: Source Register Management & Schema Validation
==================================================================
Manages the authoritative registry of raw government publications and source documents.

Strict Governance Rules:
1. Never invent URLs, dates, or author organizations. Mark uncertain fields as 'unknown' or 'pending_review'.
2. Classify publications as 'official_public' only when provenance is substantiated by document text.
3. Stable source IDs follow the format: SRC-<ORG>-<CODE>-<YEAR/PERIOD>.
4. Synchronize with extraction pipeline results to track character counts, page counts, and OCR flags.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


REQUIRED_FIELDS = [
    "source_id",
    "original_filename",
    "document_title",
    "issuing_organization",
    "publication_or_reporting_period",
    "source_url",
    "local_relative_path",
    "document_type",
    "extraction_status",
    "data_provenance_classification",
    "notes_and_limitations",
]

ALLOWED_STATUSES = {
    "pending",
    "extracted",
    "partially_extracted",
    "failed",
    "needs_review",
}

ALLOWED_PROVENANCE = {
    "official_public",
    "official_internal_administrative",
    "pending_review",
}


@dataclass
class SourceRecord:
    source_id: str
    original_filename: str
    document_title: str
    issuing_organization: str
    publication_or_reporting_period: str
    source_url: str
    local_relative_path: str
    document_type: str
    extraction_status: str
    data_provenance_classification: str
    notes_and_limitations: str
    sha256: Optional[str] = None
    total_pages: Optional[int] = None
    extracted_characters: Optional[int] = None
    pages_needing_ocr: Optional[List[int]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceRecord":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# Initial registered raw publications provided in data/raw/
INITIAL_SOURCES: List[Dict[str, Any]] = [
    {
        "source_id": "SRC-CBC-KCM-2024",
        "original_filename": "KCM-Output_RestructuredOct17.pdf",
        "document_title": "Karmayogi Competency Model (KCM)",
        "issuing_organization": "Capacity Building Commission (CBC) / Mission Karmayogi, Department of Personnel and Training (DoPT), Government of India (pending_review for formal gazetted publisher)",
        "publication_or_reporting_period": "October 2024 (PDF generation timestamp: 2024-10-18; pending formal gazette/release confirmation)",
        "source_url": "unknown",
        "local_relative_path": "data/raw/KCM-Output_RestructuredOct17.pdf",
        "document_type": "competency_framework",
        "extraction_status": "pending",
        "data_provenance_classification": "official_public",
        "notes_and_limitations": "Outlines civil service competency pillars (Vikāsa, Garva, Kartavya), behavioral, and functional competency dictionaries. Contains Devanagari and IAST transliterated characters; requires strict UTF-8 processing. Page 1, 36, and 37 are title/divider pages.",
    },
    {
        "source_id": "SRC-MOSPI-ACBP-2026-27",
        "original_filename": "OM -Annual Capacity Building Plan (ACBP) for MoSPI officials employees for FY 2026–27.pdf",
        "document_title": "Office Memorandum — Annual Capacity Building Plan (ACBP) for MoSPI Officials and Employees for FY 2026–27",
        "issuing_organization": "National Statistical Systems Training Academy (NSSTA), Ministry of Statistics and Programme Implementation (MoSPI), Government of India",
        "publication_or_reporting_period": "FY 2026–27",
        "source_url": "unknown",
        "local_relative_path": "data/raw/OM -Annual Capacity Building Plan (ACBP) for MoSPI officials employees for FY 2026–27.pdf",
        "document_type": "annual_capacity_building_plan",
        "extraction_status": "pending",
        "data_provenance_classification": "official_public",
        "notes_and_limitations": "Internal eOffice exported PDF (File No. Y-11011/01/2022-23/NSSTA-Part(i) Computer No. 80529). All 13 pages contain eOffice header watermark text (~256 chars) wrapping full-page scanned bitmap images. Substantive training matrices require OCR for automated field parsing.",
    },
    {
        "source_id": "SRC-NSSTA-TRG-CAL-2025-26",
        "original_filename": "Circular_NSSTA_Advance_Training_Calander_FY(25-26).pdf",
        "document_title": "Circular & Advance Training Calendar for FY 2025–26",
        "issuing_organization": "National Statistical Systems Training Academy (NSSTA), Ministry of Statistics and Programme Implementation (MoSPI), Government of India",
        "publication_or_reporting_period": "FY 2025–26",
        "source_url": "unknown",
        "local_relative_path": "data/raw/Circular_NSSTA_Advance_Training_Calander_FY(25-26).pdf",
        "document_type": "training_calendar",
        "extraction_status": "pending",
        "data_provenance_classification": "official_public",
        "notes_and_limitations": "Page 1 is a scanned notification letter without extractable digital text (flagged for OCR). Pages 2–9 contain dense schedules covering ISS probationers, SSS officials, topic modules, durations, and partner institutes (ISI Kolkata, DSE Delhi, etc.).",
    },
    {
        "source_id": "SRC-MOSPI-AR-2023-24",
        "original_filename": "NSSTA AnnualReport_2023-24.pdf",
        "document_title": "Annual Report 2023–24, Ministry of Statistics and Programme Implementation",
        "issuing_organization": "Ministry of Statistics and Programme Implementation (MoSPI), Government of India",
        "publication_or_reporting_period": "2023–24",
        "source_url": "https://www.mospi.gov.in",
        "local_relative_path": "data/raw/NSSTA AnnualReport_2023-24.pdf",
        "document_type": "annual_report",
        "extraction_status": "pending",
        "data_provenance_classification": "official_public",
        "notes_and_limitations": "Supplied file is named 'NSSTA AnnualReport_2023-24.pdf', but internal table of contents and Chapter 1 verify this as the comprehensive MoSPI Annual Report 2023–24. Pages 1, 3, and 116 are cover artwork or blank separators with zero digital text.",
    },
    {
        "source_id": "SRC-CSO-NAS-SM-2012",
        "original_filename": "NAS - Sources and Methods.pdf",
        "document_title": "National Accounts Statistics — Sources and Methods 2012",
        "issuing_organization": "Central Statistics Office (CSO), Ministry of Statistics and Programme Implementation (MoSPI), Government of India",
        "publication_or_reporting_period": "2012",
        "source_url": "https://www.mospi.gov.in",
        "local_relative_path": "data/raw/NAS - Sources and Methods.pdf",
        "document_type": "statistical_methodology_guide",
        "extraction_status": "pending",
        "data_provenance_classification": "official_public",
        "notes_and_limitations": "Definitive 353-page methodological guide for National Accounts (base year 2004-05 series). Contains extensive statistical tables, estimation formulas, sector classifications, and data sources across agriculture, manufacturing, services, and public administration.",
    },
]


def validate_source_record(record: Dict[str, Any]) -> List[str]:
    """Validate a single source register record against mandatory fields and vocabularies."""
    errors: List[str] = []
    for f in REQUIRED_FIELDS:
        if f not in record or record[f] is None or str(record[f]).strip() == "":
            errors.append(f"Missing required field: '{f}'")

    status = record.get("extraction_status")
    if status and status not in ALLOWED_STATUSES:
        errors.append(f"Invalid extraction_status: '{status}'. Allowed: {sorted(ALLOWED_STATUSES)}")

    provenance = record.get("data_provenance_classification")
    if provenance and provenance not in ALLOWED_PROVENANCE:
        errors.append(
            f"Invalid data_provenance_classification: '{provenance}'. Allowed: {sorted(ALLOWED_PROVENANCE)}"
        )

    # Ensure source_id follows convention
    sid = record.get("source_id", "")
    if not sid.startswith("SRC-"):
        errors.append(f"Source ID must start with 'SRC-': '{sid}'")

    return errors


def validate_source_register(records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Validate an entire collection of source register entries."""
    all_errors: Dict[str, List[str]] = {}
    seen_ids = set()

    for idx, r in enumerate(records):
        sid = r.get("source_id", f"record_{idx}")
        rec_errors = validate_source_record(r)
        if sid in seen_ids:
            rec_errors.append(f"Duplicate source_id detected: '{sid}'")
        seen_ids.add(sid)

        if rec_errors:
            all_errors[sid] = rec_errors

    return all_errors


def load_source_register(register_path: Path | str) -> List[Dict[str, Any]]:
    """Load the JSON source register from disk, or initialize with defaults if absent."""
    p = Path(register_path)
    if not p.exists():
        return INITIAL_SOURCES
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_source_register(records: List[Dict[str, Any]], register_path: Path | str) -> None:
    """Save the validated source register to disk as formatted JSON."""
    validation = validate_source_register(records)
    if validation:
        error_details = "; ".join(f"{k}: {', '.join(v)}" for k, v in validation.items())
        raise ValueError(f"Cannot save invalid source register: {error_details}")

    p = Path(register_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def update_register_with_extraction_results(
    register: List[Dict[str, Any]],
    extraction_results: List[Any],
) -> List[Dict[str, Any]]:
    """Update source register entries with live extraction statistics."""
    res_by_file = {r.source_filename: r for r in extraction_results}
    res_by_id = {r.document_id: r for r in extraction_results}

    updated = []
    for rec in register:
        item = dict(rec)
        fname = item.get("original_filename")
        sid = item.get("source_id")

        match = res_by_file.get(fname) or res_by_id.get(sid)
        if match:
            item["sha256"] = match.sha256
            item["total_pages"] = match.total_pages
            item["extracted_characters"] = match.total_characters
            item["pages_needing_ocr"] = match.pages_needing_ocr

            if match.status == "success":
                item["extraction_status"] = "extracted" if not match.pages_needing_ocr else "needs_review"
            elif match.status == "corrupted":
                item["extraction_status"] = "failed"
            else:
                item["extraction_status"] = "failed"
        updated.append(item)

    return updated


def export_markdown_source_register(records: List[Dict[str, Any]], output_path: Path | str) -> None:
    """Generate a clean GitHub Markdown documentation file of the source register."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Official Statistics Competency Intelligence Platform — Source Register",
        "",
        "## Overview",
        "The Source Register is the authoritative provenance ledger for all source documents ingested into SIH26101. "
        "Every document is assigned a permanent, stable ID, cryptographic checksum, and verified organizational metadata.",
        "",
        "### Provenance & Data Integrity Principles",
        "- **Zero Fabrication:** Source URLs, dates, and issuing bodies are never fabricated. Uncertain fields are marked `unknown` or `pending_review`.",
        "- **Official Public Status:** Documents are classified as `official_public` only when supported by verifiable government publication origin.",
        "- **Raw Immutability:** Files in `data/raw/` are strictly read-only and never modified or overwritten.",
        "",
        "## Ingested Documents Table",
        "",
        "| Source ID | Document Title | Issuing Org | Period | Type | Provenance | Pages | Extracted Chars | OCR Flags | Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for r in records:
        sid = r.get("source_id", "unknown")
        title = r.get("document_title", "unknown")
        org = r.get("issuing_organization", "unknown").split(",")[0]
        period = r.get("publication_or_reporting_period", "unknown")
        dtype = r.get("document_type", "unknown")
        prov = r.get("data_provenance_classification", "unknown")
        pages = r.get("total_pages", "-")
        chars = f"{r.get('extracted_characters', 0):,}" if r.get("extracted_characters") is not None else "-"
        ocr_cnt = len(r.get("pages_needing_ocr", [])) if r.get("pages_needing_ocr") is not None else "-"
        status = r.get("extraction_status", "pending")
        lines.append(f"| `{sid}` | {title} | {org} | {period} | `{dtype}` | `{prov}` | {pages} | {chars} | {ocr_cnt} | `{status}` |")

    lines.extend([
        "",
        "## Detailed Document Profiles",
        "",
    ])

    for r in records:
        lines.extend([
            f"### `{r.get('source_id')}`: {r.get('document_title')}",
            f"- **Original Filename:** `{r.get('original_filename')}`",
            f"- **Local Path:** `{r.get('local_relative_path')}`",
            f"- **Issuing Organization:** {r.get('issuing_organization')}",
            f"- **Reporting Period:** {r.get('publication_or_reporting_period')}",
            f"- **Source URL:** `{r.get('source_url')}`",
            f"- **Document Type:** `{r.get('document_type')}`",
            f"- **Data Provenance:** `{r.get('data_provenance_classification')}`",
            f"- **SHA-256 Checksum:** `{r.get('sha256', 'Pending extraction')}`",
            f"- **Extraction Status:** `{r.get('extraction_status')}`",
            f"- **Pages / Characters:** {r.get('total_pages', '-')} pages / {r.get('extracted_characters', '-')} chars",
            f"- **Pages Flagged for OCR / Visual Review:** `{r.get('pages_needing_ocr', [])}`",
            f"- **Notes and Limitations:** {r.get('notes_and_limitations')}",
            "",
        ])

    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
