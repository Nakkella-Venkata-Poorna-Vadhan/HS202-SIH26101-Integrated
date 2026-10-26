"""
SIH26101 - Stage 1: Automated Tests for Source Register Schema & Validation
===========================================================================
Ensures data governance rules: no invented URLs, mandatory fields, controlled vocabularies.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from scripts.source_register import (
    INITIAL_SOURCES,
    REQUIRED_FIELDS,
    export_markdown_source_register,
    load_source_register,
    save_source_register,
    validate_source_record,
    validate_source_register,
)


def test_initial_source_register_validity() -> None:
    """Verify that all pre-registered initial documents pass strict schema validation."""
    errors = validate_source_register(INITIAL_SOURCES)
    assert errors == {}, f"Initial sources have validation errors: {errors}"
    assert len(INITIAL_SOURCES) == 5


def test_missing_mandatory_field() -> None:
    """Verify that omitting any required field fails schema validation."""
    incomplete_record = {
        "source_id": "SRC-TEST-INCOMPLETE",
        "original_filename": "test.pdf",
        # missing document_title
        "issuing_organization": "Test Org",
        "publication_or_reporting_period": "2024",
        "source_url": "unknown",
        "local_relative_path": "data/raw/test.pdf",
        "document_type": "report",
        "extraction_status": "pending",
        "data_provenance_classification": "official_public",
        "notes_and_limitations": "Test notes",
    }
    errs = validate_source_record(incomplete_record)
    assert any("document_title" in e for e in errs)


def test_invalid_provenance_classification() -> None:
    """Verify that non-approved provenance values are rejected."""
    bad_prov_record = dict(INITIAL_SOURCES[0])
    bad_prov_record["data_provenance_classification"] = "unverified_internet_blog"

    errs = validate_source_record(bad_prov_record)
    assert any("data_provenance_classification" in e for e in errs)


def test_invalid_extraction_status() -> None:
    """Verify that unknown extraction statuses are rejected."""
    bad_status_record = dict(INITIAL_SOURCES[0])
    bad_status_record["extraction_status"] = "in_progress_maybe"

    errs = validate_source_record(bad_status_record)
    assert any("extraction_status" in e for e in errs)


def test_invalid_source_id_format() -> None:
    """Verify that source IDs must follow the 'SRC-' prefix convention."""
    bad_id_record = dict(INITIAL_SOURCES[0])
    bad_id_record["source_id"] = "DOC_123"

    errs = validate_source_record(bad_id_record)
    assert any("Source ID must start with 'SRC-'" in e for e in errs)


def test_duplicate_source_id_detection() -> None:
    """Verify that duplicate source IDs in the register are caught."""
    duplicate_records = [
        dict(INITIAL_SOURCES[0]),
        dict(INITIAL_SOURCES[0]),
    ]
    all_errors = validate_source_register(duplicate_records)
    assert "SRC-CBC-KCM-2024" in all_errors
    assert any("Duplicate source_id" in e for e in all_errors["SRC-CBC-KCM-2024"])


def test_save_and_load_roundtrip() -> None:
    """Verify saving to JSON and reloading preserves data accurately."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        reg_file = Path(tmp_dir) / "source_register.json"
        md_file = Path(tmp_dir) / "source_register.md"

        save_source_register(INITIAL_SOURCES, reg_file)
        loaded = load_source_register(reg_file)

        assert len(loaded) == len(INITIAL_SOURCES)
        assert loaded[0]["source_id"] == INITIAL_SOURCES[0]["source_id"]

        export_markdown_source_register(loaded, md_file)
        assert md_file.exists()
        md_text = md_file.read_text(encoding="utf-8")
        assert "SRC-CBC-KCM-2024" in md_text
        assert "SRC-CSO-NAS-SM-2012" in md_text


def test_live_source_register_file_if_present() -> None:
    """Verify that if data/source_register.json exists on disk, it is valid."""
    root_reg = Path(__file__).resolve().parent.parent / "data" / "source_register.json"
    if root_reg.exists():
        records = load_source_register(root_reg)
        errors = validate_source_register(records)
        assert errors == {}, f"Live source register has errors: {errors}"
        for r in records:
            assert r.get("sha256") is not None
            assert r.get("total_pages") is not None
            assert r.get("extracted_characters") is not None
