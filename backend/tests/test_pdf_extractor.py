"""
SIH26101 - Stage 1: Automated Unit & Integration Tests for PDF Extraction
========================================================================
Tests are completely self-contained and run against programmatically generated
minimal PDF fixtures, ensuring fast, deterministic, repeatable test runs.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import pymupdf
import pytest

from scripts.pdf_extractor import (
    PDFExtractor,
    compute_sha256,
    sanitize_filename_to_id,
)
from scripts.source_register import (
    INITIAL_SOURCES,
    REQUIRED_FIELDS,
    validate_source_record,
    validate_source_register,
)


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Provide an isolated temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_pdf(temp_workspace: Path) -> Path:
    """
    Generate a 3-page synthetic PDF fixture:
    - Page 1: Normal dense official statistics text
    - Page 2: Completely empty page (0 characters)
    - Page 3: Text-poor page (<50 characters)
    """
    pdf_path = temp_workspace / "sample_official_document.pdf"
    doc = pymupdf.open()

    # Page 1: Dense text
    p1 = doc.new_page()
    text_content = (
        "National Statistical Systems Training Academy (NSSTA)\n"
        "Ministry of Statistics and Programme Implementation\n"
        "Annual Capacity Building Plan and Competency Framework.\n"
        "Official Statistics requires specialized domain knowledge in National Accounts,\n"
        "Price Statistics, Sample Surveys, and Data Governance."
    )
    p1.insert_text((50, 72), text_content, fontsize=12)

    # Page 2: Blank / Empty Page
    doc.new_page()

    # Page 3: Text-poor (< 50 chars)
    p3 = doc.new_page()
    p3.insert_text((50, 72), "Draft Notes Only", fontsize=10)

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_pdf_discovery(temp_workspace: Path, sample_pdf: Path) -> None:
    """Verify that discover_pdfs finds all PDFs and ignores non-PDF files."""
    # Create non-pdf files
    (temp_workspace / "readme.txt").write_text("Hello", encoding="utf-8")
    (temp_workspace / "data.csv").write_text("a,b,c", encoding="utf-8")

    discovered = PDFExtractor.discover_pdfs(temp_workspace)
    assert len(discovered) == 1
    assert discovered[0].name == sample_pdf.name


def test_page_number_preservation(sample_pdf: Path) -> None:
    """Verify that page numbers are 1-indexed and strictly preserved."""
    extractor = PDFExtractor(min_text_chars=50)
    result = extractor.extract_document(sample_pdf, document_id="TEST-DOC-001")

    assert result.status == "success"
    assert result.total_pages == 3
    assert len(result.pages) == 3

    page_numbers = [p.page_number for p in result.pages]
    assert page_numbers == [1, 2, 3]


def test_text_extraction_fidelity(sample_pdf: Path) -> None:
    """Verify that text is correctly extracted from non-empty pages."""
    extractor = PDFExtractor(min_text_chars=50)
    result = extractor.extract_document(sample_pdf, document_id="TEST-DOC-001")

    assert "National Statistical Systems Training Academy" in result.pages[0].text
    assert "National Accounts" in result.pages[0].text
    assert result.pages[0].character_count > 100
    assert result.pages[0].needs_ocr_review is False
    assert "EMPTY_PAGE" not in result.pages[0].flags


def test_empty_page_detection(sample_pdf: Path) -> None:
    """Verify that 0-character pages are flagged as EMPTY_PAGE and require review."""
    extractor = PDFExtractor(min_text_chars=50)
    result = extractor.extract_document(sample_pdf, document_id="TEST-DOC-001")

    page_2 = result.pages[1]
    assert page_2.page_number == 2
    assert page_2.character_count == 0
    assert page_2.word_count == 0
    assert "EMPTY_PAGE" in page_2.flags
    assert page_2.needs_ocr_review is True
    assert page_2.review_reason is not None
    assert "blank divider" in page_2.review_reason or "0 extractable" in page_2.review_reason


def test_low_text_density_detection(sample_pdf: Path) -> None:
    """Verify that pages with <50 characters are flagged as LOW_TEXT_DENSITY."""
    extractor = PDFExtractor(min_text_chars=50)
    result = extractor.extract_document(sample_pdf, document_id="TEST-DOC-001")

    page_3 = result.pages[2]
    assert page_3.page_number == 3
    assert 0 < page_3.character_count < 50
    assert "LOW_TEXT_DENSITY" in page_3.flags
    assert page_3.needs_ocr_review is True
    assert 3 in result.pages_needing_ocr


def test_missing_file_handling(temp_workspace: Path) -> None:
    """Verify that missing files do not crash the pipeline and return a failed status."""
    non_existent = temp_workspace / "ghost_file.pdf"
    extractor = PDFExtractor()
    result = extractor.extract_document(non_existent, document_id="TEST-MISSING")

    assert result.status == "failed"
    assert result.total_pages == 0
    assert result.error_message is not None
    assert "File not found" in result.error_message


def test_corrupted_file_handling(temp_workspace: Path) -> None:
    """Verify that invalid/corrupt PDF binaries return corrupted status without crashing."""
    corrupt_file = temp_workspace / "corrupted_archive.pdf"
    corrupt_file.write_bytes(b"%PDF-1.4\nGARBAGE_PAYLOAD_NOT_A_VALID_STRUCTURE_FFFFFFFF")

    extractor = PDFExtractor()
    result = extractor.extract_document(corrupt_file, document_id="TEST-CORRUPT")

    assert result.status == "corrupted"
    assert result.total_pages == 0
    assert result.error_message is not None
    assert "PyMuPDF failed to open" in result.error_message


def test_batch_extraction_and_reporting(temp_workspace: Path, sample_pdf: Path) -> None:
    """Verify batch extraction generates both document json and consolidation report."""
    # Add a second corrupt file to verify resilience during batch execution
    corrupt_file = temp_workspace / "broken.pdf"
    corrupt_file.write_bytes(b"INVALID_DATA")

    out_dir = temp_workspace / "interim_output"
    extractor = PDFExtractor(min_text_chars=50)

    results, report = extractor.extract_batch(
        pdf_paths=[sample_pdf, corrupt_file],
        output_dir=out_dir,
        id_mapping={sample_pdf.name: "SRC-TEST-SAMPLE"},
    )

    assert len(results) == 2
    assert report["summary"]["total_files_discovered"] == 2
    assert report["summary"]["total_files_processed"] == 1
    assert report["summary"]["total_files_failed"] == 1

    # Check exported artifacts
    assert (out_dir / "SRC-TEST-SAMPLE.json").exists()
    assert (out_dir / "extraction_report.json").exists()


def test_repeatable_output(sample_pdf: Path) -> None:
    """Verify that running extraction twice produces deterministic, identical outputs."""
    extractor = PDFExtractor(min_text_chars=50)
    run1 = extractor.extract_document(sample_pdf, document_id="TEST-DOC")
    run2 = extractor.extract_document(sample_pdf, document_id="TEST-DOC")

    assert run1.sha256 == run2.sha256
    assert run1.total_characters == run2.total_characters
    assert run1.total_words == run2.total_words
    assert run1.total_pages == run2.total_pages
    assert run1.pages_needing_ocr == run2.pages_needing_ocr
    assert [p.text for p in run1.pages] == [p.text for p in run2.pages]


def test_sanitize_filename_to_id() -> None:
    """Verify filename sanitization produces clean, safe identifiers."""
    assert sanitize_filename_to_id("Circular_NSSTA_Advance_Training_Calander_FY(25-26).pdf") == (
        "Circular-NSSTA-Advance-Training-Calander-FY-25-26"
    )
    assert sanitize_filename_to_id("NAS - Sources and Methods.pdf") == "NAS-Sources-and-Methods"
