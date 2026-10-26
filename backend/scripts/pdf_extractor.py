"""
SIH26101 - Stage 1: PDF Text Extraction Engine
=============================================
Modular, reproducible PDF text-extraction pipeline built with PyMuPDF (pymupdf).

Key Responsibilities:
1. Discover PDF documents in input directories.
2. Extract text page by page while preserving 1-based page numbers and document identity.
3. Compute SHA256 cryptographic checksums for source traceability.
4. Detect empty, text-poor, or scanned pages that require OCR or visual inspection.
5. Provide resilient error handling so one corrupt file never halts batch extraction.
6. Export structured JSON per document and an overarching machine-readable extraction report.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pymupdf


# Thresholds and heuristics
DEFAULT_MIN_TEXT_CHARS = 50
EOFFICE_HEADER_PATTERN = re.compile(
    r"(File\s*No\.?\s*[A-Z0-9\-/()]+|Generated\s*from\s*eOffice|Computer\s*No\.?\s*\d+)",
    re.IGNORECASE,
)


@dataclass
class PageExtraction:
    """Represents extraction results and quality flags for a single PDF page."""
    page_number: int  # 1-indexed
    character_count: int
    word_count: int
    image_count: int
    needs_ocr_review: bool
    flags: List[str]
    review_reason: Optional[str]
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentExtractionResult:
    """Represents the complete extraction outcome for a single document."""
    document_id: str
    source_filename: str
    relative_path: str
    file_size_bytes: int
    sha256: str
    extraction_timestamp: str
    status: str  # "success", "failed", "corrupted"
    total_pages: int = 0
    total_characters: int = 0
    total_words: int = 0
    flagged_pages_count: int = 0
    pages_needing_ocr: List[int] = field(default_factory=list)
    pages: List[PageExtraction] = field(default_factory=list)
    error_message: Optional[str] = None

    def to_dict(self, include_pages: bool = True) -> Dict[str, Any]:
        d = {
            "document_id": self.document_id,
            "source_filename": self.source_filename,
            "relative_path": self.relative_path,
            "file_size_bytes": self.file_size_bytes,
            "sha256": self.sha256,
            "extraction_timestamp": self.extraction_timestamp,
            "status": self.status,
            "total_pages": self.total_pages,
            "total_characters": self.total_characters,
            "total_words": self.total_words,
            "flagged_pages_count": self.flagged_pages_count,
            "pages_needing_ocr": self.pages_needing_ocr,
            "error_message": self.error_message,
        }
        if include_pages:
            d["pages"] = [p.to_dict() for p in self.pages]
        return d


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA256 digest of a file in streaming chunks."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def sanitize_filename_to_id(filename: str) -> str:
    """Generate a clean, filesystem-safe document identifier from a filename."""
    base = Path(filename).stem
    # Replace non-alphanumeric chars with hyphen, collapse multiples
    clean = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-")
    return clean[:60] if clean else "doc"


def analyze_page(
    page: pymupdf.Page,
    page_number: int,
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
) -> PageExtraction:
    """
    Extract text and detect whether the page requires visual review or OCR.

    Heuristics applied:
    - EMPTY_PAGE: 0 extractable characters.
    - LOW_TEXT_DENSITY: 0 < chars < min_text_chars (e.g. logos, signatures, cover graphics).
    - CONTAINS_IMAGES: Page contains 1 or more embedded raster images.
    - EOFFICE_WATERMARK_ONLY: Page text consists predominantly of an eOffice system watermark
      (e.g., File No., Computer No., generated from eOffice) while substantive content is an embedded image.
    """
    text = page.get_text("text") or ""
    stripped = text.strip()
    char_count = len(stripped)
    word_count = len(stripped.split())

    # Count images embedded on page
    images = page.get_images(full=True)
    image_count = len(images)

    flags: List[str] = []
    needs_ocr = False
    review_reasons: List[str] = []

    is_eoffice_banner = bool(EOFFICE_HEADER_PATTERN.search(stripped))

    if char_count == 0:
        flags.append("EMPTY_PAGE")
        needs_ocr = True
        if image_count > 0:
            flags.append("CONTAINS_IMAGES")
            review_reasons.append(
                f"Page has 0 extractable characters but contains {image_count} embedded image(s); "
                "likely a scanned letter, circular, or graphic cover page requiring OCR."
            )
        else:
            review_reasons.append(
                "Page has 0 extractable characters and no images; blank divider or layout spacer page."
            )
    elif char_count < min_text_chars:
        flags.append("LOW_TEXT_DENSITY")
        needs_ocr = True
        if image_count > 0:
            flags.append("CONTAINS_IMAGES")
            review_reasons.append(
                f"Very low text density ({char_count} chars < threshold {min_text_chars}) with {image_count} "
                "embedded image(s); likely a cover header, divider graphic, or stamp requiring inspection."
            )
        else:
            review_reasons.append(
                f"Low text density ({char_count} chars < threshold {min_text_chars}) without images."
            )
    elif is_eoffice_banner and image_count > 0 and char_count < 350:
        # Detected eOffice watermark wrapper around scanned documents
        flags.append("EOFFICE_WATERMARK_SCAN")
        flags.append("CONTAINS_IMAGES")
        needs_ocr = True
        review_reasons.append(
            f"Extracted text ({char_count} chars) matches eOffice metadata/watermark header, while the body "
            f"contains {image_count} image(s); substantive document content is scanned and requires OCR."
        )

    if image_count > 0 and "CONTAINS_IMAGES" not in flags:
        flags.append("CONTAINS_IMAGES")

    return PageExtraction(
        page_number=page_number,
        character_count=char_count,
        word_count=word_count,
        image_count=image_count,
        needs_ocr_review=needs_ocr,
        flags=flags,
        review_reason=" ".join(review_reasons) if review_reasons else None,
        text=text,
    )


class PDFExtractor:
    """Core PDF extraction engine handling file discovery, extraction, and reporting."""

    def __init__(
        self,
        min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
    ):
        self.min_text_chars = min_text_chars

    @staticmethod
    def discover_pdfs(directory: Path | str) -> List[Path]:
        """Discover all PDF files within the specified directory (non-recursive)."""
        target_dir = Path(directory)
        if not target_dir.exists() or not target_dir.is_dir():
            return []
        # Sorted for determinism
        return sorted([p for p in target_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"])

    def extract_document(
        self,
        pdf_path: Path | str,
        document_id: Optional[str] = None,
        base_dir: Optional[Path | str] = None,
    ) -> DocumentExtractionResult:
        """
        Extract text page-by-page from a PDF file.

        Handles corrupted, unreadable, and missing files without crashing.
        """
        path = Path(pdf_path)
        timestamp = datetime.now(timezone.utc).isoformat()
        doc_id = document_id or sanitize_filename_to_id(path.name)
        rel_path = str(path.relative_to(base_dir)) if base_dir and path.is_relative_to(base_dir) else str(path)

        if not path.exists():
            return DocumentExtractionResult(
                document_id=doc_id,
                source_filename=path.name,
                relative_path=rel_path,
                file_size_bytes=0,
                sha256="",
                extraction_timestamp=timestamp,
                status="failed",
                error_message=f"File not found: {path}",
            )

        try:
            file_size = path.stat().st_size
            file_hash = compute_sha256(path)
        except Exception as e:
            return DocumentExtractionResult(
                document_id=doc_id,
                source_filename=path.name,
                relative_path=rel_path,
                file_size_bytes=0,
                sha256="",
                extraction_timestamp=timestamp,
                status="failed",
                error_message=f"Cannot read file metadata or compute hash: {e}",
            )

        try:
            doc = pymupdf.open(str(path))
        except Exception as e:
            return DocumentExtractionResult(
                document_id=doc_id,
                source_filename=path.name,
                relative_path=rel_path,
                file_size_bytes=file_size,
                sha256=file_hash,
                extraction_timestamp=timestamp,
                status="corrupted",
                error_message=f"PyMuPDF failed to open PDF document: {e}",
            )

        pages: List[PageExtraction] = []
        total_chars = 0
        total_words = 0
        pages_needing_ocr: List[int] = []

        try:
            total_pages = len(doc)
            for page_idx in range(total_pages):
                page_obj = doc[page_idx]
                page_result = analyze_page(
                    page=page_obj,
                    page_number=page_idx + 1,  # 1-indexed
                    min_text_chars=self.min_text_chars,
                )
                pages.append(page_result)
                total_chars += page_result.character_count
                total_words += page_result.word_count
                if page_result.needs_ocr_review:
                    pages_needing_ocr.append(page_result.page_number)
        except Exception as e:
            doc.close()
            return DocumentExtractionResult(
                document_id=doc_id,
                source_filename=path.name,
                relative_path=rel_path,
                file_size_bytes=file_size,
                sha256=file_hash,
                extraction_timestamp=timestamp,
                status="corrupted",
                error_message=f"Error reading pages from PDF: {e}",
            )
        finally:
            doc.close()

        return DocumentExtractionResult(
            document_id=doc_id,
            source_filename=path.name,
            relative_path=rel_path,
            file_size_bytes=file_size,
            sha256=file_hash,
            extraction_timestamp=timestamp,
            status="success",
            total_pages=len(pages),
            total_characters=total_chars,
            total_words=total_words,
            flagged_pages_count=len(pages_needing_ocr),
            pages_needing_ocr=pages_needing_ocr,
            pages=pages,
        )

    def extract_batch(
        self,
        pdf_paths: List[Path],
        output_dir: Path | str,
        id_mapping: Optional[Dict[str, str]] = None,
        base_dir: Optional[Path | str] = None,
    ) -> Tuple[List[DocumentExtractionResult], Dict[str, Any]]:
        """
        Execute batch extraction over a collection of PDF files.

        Writes individual extracted documents to <output_dir>/<doc_id>.json
        and creates a consolidated extraction report.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        id_map = id_mapping or {}

        results: List[DocumentExtractionResult] = []

        for p in pdf_paths:
            doc_id = id_map.get(p.name, sanitize_filename_to_id(p.name))
            res = self.extract_document(p, document_id=doc_id, base_dir=base_dir)
            results.append(res)

            # Persist individual document json
            doc_json_path = out_dir / f"{doc_id}.json"
            with open(doc_json_path, "w", encoding="utf-8") as f:
                json.dump(res.to_dict(include_pages=True), f, indent=2, ensure_ascii=False)

        # Build consolidated machine-readable report
        successful = [r for r in results if r.status == "success"]
        failed = [r for r in results if r.status != "success"]

        total_pages = sum(r.total_pages for r in successful)
        total_chars = sum(r.total_characters for r in successful)
        total_words = sum(r.total_words for r in successful)
        total_ocr_flagged = sum(r.flagged_pages_count for r in successful)

        ocr_review_details = []
        for r in successful:
            for p in r.pages:
                if p.needs_ocr_review:
                    ocr_review_details.append({
                        "document_id": r.document_id,
                        "source_filename": r.source_filename,
                        "page_number": p.page_number,
                        "character_count": p.character_count,
                        "image_count": p.image_count,
                        "flags": p.flags,
                        "review_reason": p.review_reason,
                    })

        report = {
            "report_metadata": {
                "generator": "SIH26101 PDF Extraction Pipeline Stage 1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "output_directory": str(out_dir),
                "min_text_chars_threshold": self.min_text_chars,
            },
            "summary": {
                "total_files_discovered": len(pdf_paths),
                "total_files_processed": len(successful),
                "total_files_failed": len(failed),
                "total_pages_extracted": total_pages,
                "total_characters_extracted": total_chars,
                "total_words_extracted": total_words,
                "total_pages_flagged_for_ocr_review": total_ocr_flagged,
            },
            "files": [r.to_dict(include_pages=False) for r in results],
            "ocr_review_details": ocr_review_details,
        }

        report_path = out_dir / "extraction_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return results, report
