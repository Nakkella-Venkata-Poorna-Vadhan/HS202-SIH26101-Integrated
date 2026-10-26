"""
Document Ingestion, Extraction, and Provenance Service (Stage 4.7)
Handles trainer material uploads (PDF and TXT), enforces strict size/type boundaries,
extracts text preserving page numbers, and registers documents with cryptographic hashes.
Strictly isolates uploaded content in data/uploads/ away from official baseline catalogues.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pymupdf

from competency_engine.config import (
    UPLOADED_DOCS_DIR,
    UPLOADED_EXTRACTED_DIR,
    UPLOADED_REGISTRY_PATH,
    UPLOADS_DIR,
)
from competency_engine.models import DocumentPageChunk, UploadedDocumentMetadata

logger = logging.getLogger(__name__)

# Security and validation constraints
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MIN_EXTRACTABLE_TEXT_CHARS = 50

# Prompt injection defense patterns
PROMPT_INJECTION_PATTERN = re.compile(
    r"(ignore\s+(?:all\s+)?(?:previous\s+)?instructions|system\s*(?:prompt)?\s*:\s*|system\s+prompt\s+override|you\s+are\s+now|override\s+system\s+rules|<\|im_start\|>|<\|im_end\|>)",
    re.IGNORECASE,
)


class DocumentProcessingError(Exception):
    """Raised when an uploaded document fails validation, extraction, or security checks."""
    pass


class DocumentService:
    """Manages trainer document ingestion, extraction, and chunking with full provenance."""

    def __init__(
        self,
        uploads_dir: Path = UPLOADS_DIR,
        docs_dir: Path = UPLOADED_DOCS_DIR,
        extracted_dir: Path = UPLOADED_EXTRACTED_DIR,
        registry_path: Path = UPLOADED_REGISTRY_PATH,
    ):
        self.uploads_dir = uploads_dir
        self.docs_dir = docs_dir
        self.extracted_dir = extracted_dir
        self.registry_path = registry_path

        self._registry: Dict[str, Dict[str, Any]] = {}
        self._ensure_storage()
        self.load_registry()

    def _ensure_storage(self) -> None:
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self._write_json(self.registry_path, {"documents": []})

    def load_registry(self) -> None:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._registry = {doc["document_id"]: doc for doc in data.get("documents", [])}
            except Exception as e:
                logger.error("Failed to load upload registry: %s", e)
                self._registry = {}

    def _save_registry(self) -> None:
        data = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_documents": len(self._registry),
            "documents": list(self._registry.values()),
        }
        self._write_json(self.registry_path, data)

    def _write_json(self, path: Path, data: Any) -> None:
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(path)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Strip dangerous path traversal characters and directory delimiters."""
        clean = Path(filename).name
        clean = re.sub(r"[^\w.\- ]", "_", clean)
        return clean or "uploaded_document"

    @staticmethod
    def sanitize_untrusted_text(text: str) -> str:
        """Neutralize known prompt injection markers in untrusted user-uploaded text."""
        return PROMPT_INJECTION_PATTERN.sub("[FILTERED_INPUT]", text)

    def process_upload(
        self,
        file_bytes: bytes,
        original_filename: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UploadedDocumentMetadata:
        """
        Validate, extract, and register an uploaded training document.
        Enforces size limits, cryptographic hashing, and page provenance.
        """
        # 1. Check size limit
        file_size = len(file_bytes)
        if file_size == 0:
            raise DocumentProcessingError("Uploaded file is empty (0 bytes).")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise DocumentProcessingError(
                f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES / (1024 * 1024):.0f} MB."
            )

        # 2. Check file extension
        safe_filename = self.sanitize_filename(original_filename)
        ext = Path(safe_filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise DocumentProcessingError(
                f"Unsupported file type '{ext}'. Only {sorted(list(ALLOWED_EXTENSIONS))} files are supported."
            )

        # 3. Compute SHA-256 hash
        sha256 = hashlib.sha256(file_bytes).hexdigest()

        # 4. Generate unique document ID
        doc_uuid = uuid.uuid4().hex[:8].upper()
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        doc_id = f"SRC-UP-{timestamp_str}-{doc_uuid}"

        # 5. Save raw file
        stored_filename = f"{doc_id}_{safe_filename}"
        raw_storage_path = self.docs_dir / stored_filename
        with open(raw_storage_path, "wb") as f:
            f.write(file_bytes)

        # 6. Extract text page-by-page
        pages_text: List[Tuple[int, str]] = []
        extraction_status: str = "extracted"
        extraction_error: Optional[str] = None

        if ext == ".txt":
            try:
                content = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    content = file_bytes.decode("latin-1")
                except Exception as e:
                    raise DocumentProcessingError(f"Failed to decode text file: {e}")

            sanitized_content = self.sanitize_untrusted_text(content)
            pages_text.append((1, sanitized_content))

        elif ext == ".pdf":
            try:
                pdf_doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            except Exception as e:
                raise DocumentProcessingError(f"Corrupt or unreadable PDF document: {e}")

            if pdf_doc.is_encrypted:
                raise DocumentProcessingError("Encrypted or password-protected PDFs are not supported.")

            total_chars = 0
            has_images = False

            for page_idx in range(len(pdf_doc)):
                page = pdf_doc[page_idx]
                page_num = page_idx + 1
                text = page.get_text() or ""
                text = self.sanitize_untrusted_text(text)
                pages_text.append((page_num, text))
                total_chars += len(text.strip())
                if len(page.get_images()) > 0:
                    has_images = True

            pdf_doc.close()

            # If document has virtually no extractable text but has pages/images, flag for OCR
            if total_chars < MIN_EXTRACTABLE_TEXT_CHARS:
                extraction_status = "ocr_required"
                extraction_error = "Scanned PDF detected. Insufficient digital text for automated MCQ generation."

        # 7. Write extracted structured pages JSON
        extracted_doc_data = {
            "document_id": doc_id,
            "filename": safe_filename,
            "sha256": sha256,
            "page_count": len(pages_text),
            "pages": [
                {
                    "page_number": p_num,
                    "character_count": len(p_text),
                    "text": p_text,
                }
                for p_num, p_text in pages_text
            ],
        }
        extracted_file_path = self.extracted_dir / f"{doc_id}.json"
        self._write_json(extracted_file_path, extracted_doc_data)

        # 8. Create metadata record
        total_characters = sum(len(p[1]) for p in pages_text)
        doc_title = title or safe_filename.rsplit(".", 1)[0].replace("_", " ").title()

        metadata = UploadedDocumentMetadata(
            document_id=doc_id,
            filename=safe_filename,
            file_type="pdf" if ext == ".pdf" else "txt",
            file_size_bytes=file_size,
            sha256=sha256,
            uploaded_at=datetime.now(timezone.utc).isoformat(),
            extraction_status=extraction_status,
            page_count=len(pages_text),
            character_count=total_characters,
            provenance="trainer_uploaded_material",
            title=doc_title,
            description=description or f"Uploaded training resource ({safe_filename})",
            extraction_error=extraction_error,
        )

        self._registry[doc_id] = metadata.model_dump()
        self._save_registry()

        return metadata

    def list_documents(self) -> List[UploadedDocumentMetadata]:
        """Return all registered uploaded documents, sorted newest first."""
        docs = [UploadedDocumentMetadata(**item) for item in self._registry.values()]
        return sorted(docs, key=lambda d: d.uploaded_at, reverse=True)

    def get_document(self, document_id: str) -> Optional[UploadedDocumentMetadata]:
        """Fetch document metadata by its ID."""
        data = self._registry.get(document_id)
        return UploadedDocumentMetadata(**data) if data else None

    def get_document_pages(self, document_id: str) -> List[Tuple[int, str]]:
        """Retrieve page texts for a document."""
        extracted_file_path = self.extracted_dir / f"{document_id}.json"
        if not extracted_file_path.exists():
            return []
        try:
            with open(extracted_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [(p["page_number"], p["text"]) for p in data.get("pages", [])]
        except Exception as e:
            logger.error("Failed to read extracted pages for %s: %s", document_id, e)
            return []

    def get_document_chunks(
        self,
        document_id: str,
        target_chunk_size: int = 1000,
        min_chunk_size: int = 150,
    ) -> List[DocumentPageChunk]:
        """
        Segment document pages into semantic chunks with exact page provenance.
        Chunks do not span across page boundaries so page citations are strictly verifiable.
        """
        pages = self.get_document_pages(document_id)
        chunks: List[DocumentPageChunk] = []
        chunk_idx = 1

        for page_num, page_text in pages:
            # Clean and normalize paragraphs
            paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [p.strip() for p in page_text.split("\n") if p.strip()]

            current_chunk: List[str] = []
            current_len = 0

            for para in paragraphs:
                para_len = len(para)
                if current_len + para_len > target_chunk_size and current_len >= min_chunk_size:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(
                        DocumentPageChunk(
                            chunk_id=f"{document_id}-P{page_num}-C{chunk_idx}",
                            document_id=document_id,
                            page_number=page_num,
                            character_count=len(chunk_text),
                            text=chunk_text,
                        )
                    )
                    chunk_idx += 1
                    current_chunk = [para]
                    current_len = para_len
                else:
                    current_chunk.append(para)
                    current_len += para_len

            if current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                if len(chunk_text) >= min_chunk_size or len(chunks) == 0:
                    chunks.append(
                        DocumentPageChunk(
                            chunk_id=f"{document_id}-P{page_num}-C{chunk_idx}",
                            document_id=document_id,
                            page_number=page_num,
                            character_count=len(chunk_text),
                            text=chunk_text,
                        )
                    )
                    chunk_idx += 1

        return chunks
