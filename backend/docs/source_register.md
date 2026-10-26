# Official Statistics Competency Intelligence Platform — Source Register

## Overview
The Source Register is the authoritative provenance ledger for all source documents ingested into SIH26101. Every document is assigned a permanent, stable ID, cryptographic checksum, and verified organizational metadata.

### Provenance & Data Integrity Principles
- **Zero Fabrication:** Source URLs, dates, and issuing bodies are never fabricated. Uncertain fields are marked `unknown` or `pending_review`.
- **Official Public Status:** Documents are classified as `official_public` only when supported by verifiable government publication origin.
- **Raw Immutability:** Files in `data/raw/` are strictly read-only and never modified or overwritten.

## Ingested Documents Table

| Source ID | Document Title | Issuing Org | Period | Type | Provenance | Pages | Extracted Chars | OCR Flags | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SRC-CBC-KCM-2024` | Karmayogi Competency Model (KCM) | Capacity Building Commission (CBC) / Mission Karmayogi | October 2024 (PDF generation timestamp: 2024-10-18; pending formal gazette/release confirmation) | `competency_framework` | `official_public` | 107 | 85,103 | 3 | `needs_review` |
| `SRC-MOSPI-ACBP-2026-27` | Office Memorandum — Annual Capacity Building Plan (ACBP) for MoSPI Officials and Employees for FY 2026–27 | National Statistical Systems Training Academy (NSSTA) | FY 2026–27 | `annual_capacity_building_plan` | `official_public` | 13 | 3,332 | 13 | `needs_review` |
| `SRC-NSSTA-TRG-CAL-2025-26` | Circular & Advance Training Calendar for FY 2025–26 | National Statistical Systems Training Academy (NSSTA) | FY 2025–26 | `training_calendar` | `official_public` | 9 | 26,375 | 1 | `needs_review` |
| `SRC-MOSPI-AR-2023-24` | Annual Report 2023–24, Ministry of Statistics and Programme Implementation | Ministry of Statistics and Programme Implementation (MoSPI) | 2023–24 | `annual_report` | `official_public` | 116 | 235,652 | 3 | `needs_review` |
| `SRC-CSO-NAS-SM-2012` | National Accounts Statistics — Sources and Methods 2012 | Central Statistics Office (CSO) | 2012 | `statistical_methodology_guide` | `official_public` | 353 | 1,354,844 | 0 | `extracted` |

## Detailed Document Profiles

### `SRC-CBC-KCM-2024`: Karmayogi Competency Model (KCM)
- **Original Filename:** `KCM-Output_RestructuredOct17.pdf`
- **Local Path:** `data/raw/KCM-Output_RestructuredOct17.pdf`
- **Issuing Organization:** Capacity Building Commission (CBC) / Mission Karmayogi, Department of Personnel and Training (DoPT), Government of India (pending_review for formal gazetted publisher)
- **Reporting Period:** October 2024 (PDF generation timestamp: 2024-10-18; pending formal gazette/release confirmation)
- **Source URL:** `unknown`
- **Document Type:** `competency_framework`
- **Data Provenance:** `official_public`
- **SHA-256 Checksum:** `4af22b02eb10cba483844e47b9ad08b5eb48f97b63375868576846c95a0a7ec7`
- **Extraction Status:** `needs_review`
- **Pages / Characters:** 107 pages / 85103 chars
- **Pages Flagged for OCR / Visual Review:** `[1, 36, 37]`
- **Notes and Limitations:** Outlines civil service competency pillars (Vikāsa, Garva, Kartavya), behavioral, and functional competency dictionaries. Contains Devanagari and IAST transliterated characters; requires strict UTF-8 processing. Page 1, 36, and 37 are title/divider pages.

### `SRC-MOSPI-ACBP-2026-27`: Office Memorandum — Annual Capacity Building Plan (ACBP) for MoSPI Officials and Employees for FY 2026–27
- **Original Filename:** `OM -Annual Capacity Building Plan (ACBP) for MoSPI officials employees for FY 2026–27.pdf`
- **Local Path:** `data/raw/OM -Annual Capacity Building Plan (ACBP) for MoSPI officials employees for FY 2026–27.pdf`
- **Issuing Organization:** National Statistical Systems Training Academy (NSSTA), Ministry of Statistics and Programme Implementation (MoSPI), Government of India
- **Reporting Period:** FY 2026–27
- **Source URL:** `unknown`
- **Document Type:** `annual_capacity_building_plan`
- **Data Provenance:** `official_public`
- **SHA-256 Checksum:** `73ee47e6809982b63ffe928e95e86e4084d33865d325876e0cb9ff755a634205`
- **Extraction Status:** `needs_review`
- **Pages / Characters:** 13 pages / 3332 chars
- **Pages Flagged for OCR / Visual Review:** `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]`
- **Notes and Limitations:** Internal eOffice exported PDF (File No. Y-11011/01/2022-23/NSSTA-Part(i) Computer No. 80529). All 13 pages contain eOffice header watermark text (~256 chars) wrapping full-page scanned bitmap images. Substantive training matrices require OCR for automated field parsing.

### `SRC-NSSTA-TRG-CAL-2025-26`: Circular & Advance Training Calendar for FY 2025–26
- **Original Filename:** `Circular_NSSTA_Advance_Training_Calander_FY(25-26).pdf`
- **Local Path:** `data/raw/Circular_NSSTA_Advance_Training_Calander_FY(25-26).pdf`
- **Issuing Organization:** National Statistical Systems Training Academy (NSSTA), Ministry of Statistics and Programme Implementation (MoSPI), Government of India
- **Reporting Period:** FY 2025–26
- **Source URL:** `unknown`
- **Document Type:** `training_calendar`
- **Data Provenance:** `official_public`
- **SHA-256 Checksum:** `e13589f4442a1d947f6599623c7a5354251e67dfe3c2ea5bee925e16f3ed99e6`
- **Extraction Status:** `needs_review`
- **Pages / Characters:** 9 pages / 26375 chars
- **Pages Flagged for OCR / Visual Review:** `[1]`
- **Notes and Limitations:** Page 1 is a scanned notification letter without extractable digital text (flagged for OCR). Pages 2–9 contain dense schedules covering ISS probationers, SSS officials, topic modules, durations, and partner institutes (ISI Kolkata, DSE Delhi, etc.).

### `SRC-MOSPI-AR-2023-24`: Annual Report 2023–24, Ministry of Statistics and Programme Implementation
- **Original Filename:** `NSSTA AnnualReport_2023-24.pdf`
- **Local Path:** `data/raw/NSSTA AnnualReport_2023-24.pdf`
- **Issuing Organization:** Ministry of Statistics and Programme Implementation (MoSPI), Government of India
- **Reporting Period:** 2023–24
- **Source URL:** `https://www.mospi.gov.in`
- **Document Type:** `annual_report`
- **Data Provenance:** `official_public`
- **SHA-256 Checksum:** `ac7532cfe6c42183fd9295e891db0b09bb76a1ef0263b29056216fdf6d706219`
- **Extraction Status:** `needs_review`
- **Pages / Characters:** 116 pages / 235652 chars
- **Pages Flagged for OCR / Visual Review:** `[1, 3, 116]`
- **Notes and Limitations:** Supplied file is named 'NSSTA AnnualReport_2023-24.pdf', but internal table of contents and Chapter 1 verify this as the comprehensive MoSPI Annual Report 2023–24. Pages 1, 3, and 116 are cover artwork or blank separators with zero digital text.

### `SRC-CSO-NAS-SM-2012`: National Accounts Statistics — Sources and Methods 2012
- **Original Filename:** `NAS - Sources and Methods.pdf`
- **Local Path:** `data/raw/NAS - Sources and Methods.pdf`
- **Issuing Organization:** Central Statistics Office (CSO), Ministry of Statistics and Programme Implementation (MoSPI), Government of India
- **Reporting Period:** 2012
- **Source URL:** `https://www.mospi.gov.in`
- **Document Type:** `statistical_methodology_guide`
- **Data Provenance:** `official_public`
- **SHA-256 Checksum:** `ebbadd5c0e5cc9e23a6d825b2704d341bff5b2cf2727cabcce29633acfe885b3`
- **Extraction Status:** `extracted`
- **Pages / Characters:** 353 pages / 1354844 chars
- **Pages Flagged for OCR / Visual Review:** `[]`
- **Notes and Limitations:** Definitive 353-page methodological guide for National Accounts (base year 2004-05 series). Contains extensive statistical tables, estimation formulas, sector classifications, and data sources across agriculture, manufacturing, services, and public administration.

