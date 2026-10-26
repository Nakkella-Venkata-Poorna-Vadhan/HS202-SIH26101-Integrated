"""
SIH26101 - Stage 1: PDF Extraction CLI Pipeline
===============================================
Command-line runner for discovering, extracting, and reporting on raw government PDFs.

Usage:
    python scripts/extract_text.py [--raw-dir data/raw] [--interim-dir data/interim]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path for clean modular imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.pdf_extractor import PDFExtractor
from scripts.source_register import (
    export_markdown_source_register,
    load_source_register,
    save_source_register,
    update_register_with_extraction_results,
    validate_source_register,
)


def run_pipeline(
    raw_dir: Path,
    interim_dir: Path,
    source_register_path: Path,
    docs_register_path: Path,
    min_chars: int = 50,
) -> int:
    """Execute complete Stage 1 extraction pipeline."""
    print("=" * 80)
    print("SIH26101 — Stage 1: Official Statistics PDF Text Extraction Pipeline")
    print("=" * 80)
    print(f"Source Directory   : {raw_dir.resolve()}")
    print(f"Interim Output Dir : {interim_dir.resolve()}")
    print(f"Source Register    : {source_register_path.resolve()}")
    print(f"Min Text Threshold : {min_chars} characters/page")
    print("-" * 80)

    # 1. Load and validate source register
    print("[1/5] Loading source register...")
    register = load_source_register(source_register_path)
    val_errors = validate_source_register(register)
    if val_errors:
        print("ERROR: Source register schema validation failed:")
        for sid, errs in val_errors.items():
            print(f"  [{sid}] {', '.join(errs)}")
        return 1
    print(f"  Loaded {len(register)} registered source definitions.")

    # Build mapping from filename -> stable source_id
    id_mapping = {r["original_filename"]: r["source_id"] for r in register}

    # 2. Discover PDFs in raw directory
    print("[2/5] Discovering PDF documents in data/raw/...")
    discovered = PDFExtractor.discover_pdfs(raw_dir)
    print(f"  Discovered {len(discovered)} PDF file(s).")
    for idx, p in enumerate(discovered, 1):
        matched_id = id_mapping.get(p.name, "AUTO_GENERATED")
        print(f"    {idx}. {p.name} -> ID: [{matched_id}]")

    # Check for registered files that are missing from disk
    registered_files = {r["original_filename"] for r in register}
    found_filenames = {p.name for p in discovered}
    missing_from_disk = registered_files - found_filenames
    if missing_from_disk:
        print("\n  [WARNING] The following registered files were NOT found in data/raw/:")
        for m in sorted(missing_from_disk):
            print(f"    - {m}")
    else:
        print("  All registered source documents are present on disk.")

    # Check for un-registered PDFs in raw
    unregistered = found_filenames - registered_files
    if unregistered:
        print("\n  [NOTE] The following PDFs are present in data/raw/ but not pre-registered:")
        for u in sorted(unregistered):
            print(f"    + {u} (will be assigned auto-generated ID)")

    if not discovered:
        print("ERROR: No PDF files found in raw directory.")
        return 1

    # 3. Perform Extraction
    print(f"\n[3/5] Extracting text page-by-page using PyMuPDF...")
    extractor = PDFExtractor(min_text_chars=min_chars)
    results, report = extractor.extract_batch(
        pdf_paths=discovered,
        output_dir=interim_dir,
        id_mapping=id_mapping,
        base_dir=PROJECT_ROOT,
    )

    # 4. Update and Persist Source Register
    print("\n[4/5] Updating source register with live extraction metrics...")
    updated_register = update_register_with_extraction_results(register, results)
    save_source_register(updated_register, source_register_path)
    export_markdown_source_register(updated_register, docs_register_path)
    print(f"  Saved JSON register : {source_register_path}")
    print(f"  Exported Markdown   : {docs_register_path}")

    # 5. Output Summary & OCR Review Directives
    print("\n[5/5] Pipeline Summary & OCR Review Flags:")
    print("=" * 80)
    summary = report["summary"]
    print(f"Files Discovered       : {summary['total_files_discovered']}")
    print(f"Files Processed        : {summary['total_files_processed']}")
    print(f"Files Failed           : {summary['total_files_failed']}")
    print(f"Total Pages Extracted  : {summary['total_pages_extracted']}")
    print(f"Total Chars Extracted  : {summary['total_characters_extracted']:,}")
    print(f"Total Words Extracted  : {summary['total_words_extracted']:,}")
    print(f"Pages Needing OCR      : {summary['total_pages_flagged_for_ocr_review']}")
    print("-" * 80)

    print("Document-by-Document Breakdown:")
    for r in results:
        status_symbol = "[OK]" if r.status == "success" else "[FAILED]"
        print(f"\n  {status_symbol} {r.document_id} ({r.source_filename})")
        print(f"      Status: {r.status} | Size: {r.file_size_bytes:,} bytes | SHA256: {r.sha256[:16]}...")
        if r.status == "success":
            print(f"      Pages: {r.total_pages} | Chars: {r.total_characters:,} | Words: {r.total_words:,}")
            if r.pages_needing_ocr:
                print(f"      OCR / Visual Review Required on {len(r.pages_needing_ocr)} page(s): {r.pages_needing_ocr}")
            else:
                print("      OCR Review: Clean (all pages have high text density)")
        else:
            print(f"      Error: {r.error_message}")

    ocr_details = report.get("ocr_review_details", [])
    if ocr_details:
        print("\n" + "=" * 80)
        print("PAGES FLAGGED FOR OCR OR VISUAL REVIEW (WHY OCR IS NEEDED):")
        print("=" * 80)
        for idx, item in enumerate(ocr_details, 1):
            print(f"  {idx}. [{item['document_id']}] Page {item['page_number']}:")
            print(f"     Characters: {item['character_count']} | Images: {item['image_count']} | Flags: {item['flags']}")
            print(f"     Reason: {item['review_reason']}")

    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE. Artifacts available in data/interim/ and docs/")
    print("=" * 80)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SIH26101 Stage 1: Official Statistics PDF Text Extraction Pipeline",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Directory containing source PDFs (default: data/raw)",
    )
    parser.add_argument(
        "--interim-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "interim",
        help="Directory to store extracted text and reports (default: data/interim)",
    )
    parser.add_argument(
        "--source-register",
        type=Path,
        default=PROJECT_ROOT / "data" / "source_register.json",
        help="Path to source register JSON (default: data/source_register.json)",
    )
    parser.add_argument(
        "--docs-register",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_register.md",
        help="Path to export Markdown source register (default: docs/source_register.md)",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=50,
        help="Minimum character threshold below which a page is flagged for review (default: 50)",
    )

    args = parser.parse_args()
    exit_code = run_pipeline(
        raw_dir=args.raw_dir,
        interim_dir=args.interim_dir,
        source_register_path=args.source_register,
        docs_register_path=args.docs_register,
        min_chars=args.min_chars,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
