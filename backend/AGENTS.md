# AGENTS.md — Developer & AI Agent Guidelines

## Repository Overview
This repository contains the official codebase for **SIH26101: Official Statistics Competency Intelligence and Adaptive Learning Platform for India's Official Statistical System**.

The platform is designed to align with India's **Mission Karmayogi (National Programme for Civil Services Capacity Building - NPCSCB)** and the **Ministry of Statistics and Programme Implementation (MoSPI)** human resource and statistical training frameworks (NSSTA).

---

## Architecture & Directory Conventions

```text
SIH26101-Skill-Intelligence/
├── data/
│   ├── raw/           # IMMUTABLE: Original source PDFs (read-only; never edit/delete)
│   ├── interim/       # Structured page-by-page JSON extractions & extraction reports
│   ├── processed/     # Future stages: cleaned, validated competency dictionaries
│   ├── synthetic/     # Future stages: labeled evaluation benchmarks (clearly marked)
│   └── source_register.json # Machine-readable provenance ledger
├── docs/              # Architectural documentation and human-readable registers
├── scripts/           # Python pipeline utilities (CLI runners, extractors, validators)
├── tests/             # Automated test suite (pytest, fast fixtures)
├── requirements.txt   # Minimal, pinned dependencies
├── README.md          # Project overview & operator instructions
└── AGENTS.md          # AI agent constraints & operational rules
```

---

## Strict Data Integrity Constraints

Every AI agent and contributor operating in this repository must strictly adhere to the following rules:

1. **Immutability of `data/raw/`**:
   - Never edit, overwrite, rename, or delete any file in `data/raw/`.
   - Never write intermediate outputs into `data/raw/`.

2. **No Hallucination or Fabrication**:
   - Do **NOT** invent source URLs, publication dates, or ministerial departments. If a field cannot be verified directly from the document text or official metadata, mark it explicitly as `unknown` or `pending_review`.
   - Do **NOT** fabricate competencies, proficiency levels, training courses, or role mappings.
   - Do **NOT** represent synthetic evaluation data as real government administrative records.
   - Do **NOT** claim access to private iGOT Karmayogi APIs, learner records, or restricted government portals.

3. **Classification of Government Publications**:
   - Use `official_public` provenance only when the document's official origin is confirmed in the text (e.g., CSO, MoSPI, NSSTA, CBC).

4. **Unicode & Character Encoding**:
   - Always open and write files with explicit `encoding="utf-8"`.
   - The Karmayogi Competency Model contains Devanagari and IAST transliterated characters (e.g., *Ātmanirbhar*, *Vikāsa*, *Kartavya*, *Śhakti*). Never assume ASCII or Windows-1252.

5. **Graceful Fault Tolerance**:
   - PDF extraction code must handle missing, unreadable, or corrupted files gracefully. An extraction error in one document must never silently abort the batch.

---

## How to Run & Verify

### Environment Setup
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### Run Extraction Pipeline
```bash
python scripts/extract_text.py
```

### Run Automated Tests
```bash
python -m pytest -v
```

---

## Current Scope (Stage 1)
- **Deliberately Implemented**:
  - Raw PDF discovery and page-by-page text extraction (`PyMuPDF`).
  - Page-number preservation (1-indexed).
  - Empty page, low-text density, and scanned-page OCR flagging.
  - Source register management with SHA256 cryptographic provenance.
  - Consolidated machine-readable JSON extraction reports.
  - Resilient error handling and automated test coverage.

- **Deliberately NOT Implemented Yet**:
  - No OCR engines (Tesseract / EasyOCR / PaddleOCR) — flagged pages are logged for human review.
  - No frontend / UI components.
  - No backend REST API (FastAPI / Flask).
  - No databases (PostgreSQL, SQLite, Redis).
  - No vector stores or embeddings (Chroma, FAISS, pgvector).
  - No LLM API calls, prompting chains, or AI tutors.
