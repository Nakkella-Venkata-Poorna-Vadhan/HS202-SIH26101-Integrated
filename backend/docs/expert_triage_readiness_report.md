# Stage 3.5 — Expert Triage Readiness Report for the 26-Case Benchmark

**Platform**: SIH26101 Official Statistics Competency Intelligence and Adaptive Learning Platform  
**Stage**: 3.5 — Expert Triage Preparation for the 26-Case Competency Mapping Benchmark  
**Evaluation Scope**: 26-Case Human-Reviewed Competency Mapping Benchmark (`BM-PILOT-MOSPI-2026-V1`)  
**Date**: October 2026  
**Status**: Ready for Authorized Human Expert Triage  
**Authoritative Hash Baselines**:
- `data/processed/acbp_courses.json`: `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` (IMMUTABLE)
- `data/processed/competencies_kcm.json`: `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` (IMMUTABLE)
- `data/processed/acbp_kcm_mappings.json`: 226 records (IMMUTABLE)

---

## 1. Executive Summary

Stage 3.5 establishes the complete, production-grade **Expert Triage Package** for the 26-case pilot benchmark. The package empowers authorized Subject Matter Experts (SMEs) from NSSTA, MoSPI, and the Capacity Building Commission (CBC) to review candidate competency mappings, evaluate verified vs. unverified evidence, analyze potential competency overlaps, and record reasoned evaluations.

### Critical Operational Distinctions:
1. **Ready for Expert Triage: 26 / 26 (100.0%)**  
   All 26 cases possess verified course identities, traceable Annexure I source citations, authentic KCM definitions, structured 5-part review findings, alternative candidate competency options, explicit SME review questions, and dual independent review slots.
2. **Ready for Definitive Adjudication: 0 / 26 (0.0% — Strictly Denied)**  
   Definitive competency certification cannot be performed because 23 of the 26 cases lack locally verified exact lesson plans, video transcripts, or assessment rubrics, and 11 reside behind civil service Parichay Single Sign-On (SSO).
3. **Cases Needing More Evidence Before Definitive Adjudication: 26 / 26 (100.0%)**  
   All 26 cases require physical curriculum requisition from apex training institutes (ISTM, AJ-NIFM, ATI Mysuru) or authenticated civil service access to iGOT micro-courses to transition from triage to legally defensible ground truth.

---

## 2. Artifacts Created & Modified

| Artifact Path | Format | Role & Purpose |
| :--- | :---: | :--- |
| [`data/interim/expert_triage_packet.json`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.json) | JSON | Machine-readable expert triage packet containing 26 structured case dossiers with dual independent review slots (`Reviewer 1` and `Reviewer 2`) initialized to null. |
| [`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv) | CSV | Spreadsheet export for SME reviewers with flattened columns for Reviewer 1, Reviewer 2, consensus fields, and evidence summaries. |
| [`scripts/build_expert_triage_packet.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/scripts/build_expert_triage_packet.py) | Python | Deterministic packet builder enforcing cryptographic hash checks, dual referential integrity, and unverified source safeguards. |
| [`docs/expert_triage_guide.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/expert_triage_guide.md) | Markdown | Operational triage manual explaining the 5-label taxonomy, the 4-part conflation safeguard, domain-gap guidelines, and the dual blind review workflow. |
| [`tests/test_expert_triage_packet.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/tests/test_expert_triage_packet.py) | Python | Automated regression test suite (9 tests) verifying case coverage, referential validity, blank review fields, domain safeguards, and JSON/CSV parity. |
| [`docs/expert_triage_readiness_report.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/expert_triage_readiness_report.md) | Markdown | This readiness report summarizing triage readiness, evidence limitations, test results, and reviewer instructions. |

---

## 3. Inventory Breakdown & Stratum Readiness

All 26 benchmark cases are uniquely indexed and resolve 1-to-1 to the authoritative ACBP course catalogue and CBC KCM framework:

| Stratum | Cases | Description | Verified Local Evidence | External Unverified References | Triage Readiness | Definitive Adjudication Status |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **Strata A: Title-Reference Candidates** | 6 | High-visibility executive courses (`BM-CASE-001` to `006`) testing whether titles reflect instructional content. | 0 | 6 (iGOT SSO / ATI / CBC) | **Ready (6/6)** | **Blocked (0/6)** |
| **Strata B: Behavioural Unresolved** | 6 | Civil service behavioural courses (`BM-CASE-007` to `012`) with conceptual ambiguity. | 0 | 6 (iGOT SSO / Ayush) | **Ready (6/6)** | **Blocked (0/6)** |
| **Strata C: Functional Unresolved** | 7 | Core government operational courses (`BM-CASE-013` to `019`) on finance, procurement, and policy. | 0 | 7 (ISTM / AJ-NIFM / GeM / PRIDE) | **Ready (7/7)** | **Blocked (0/7)** |
| **Strata D: Domain & Statistical Gaps** | 5 | Official statistics & specialist technical courses (`BM-CASE-020` to `024`). | 2 (`CASE-021`, `024`) | 3 (NeGD / NSSTA HCES & ASI) | **Ready (5/5)** | **Blocked (0/5)** |
| **Strata E: Cross-Cadre Contrasts** | 2 | Noting and Drafting courses (`BM-CASE-025`, `026`) contrasting supervisory vs. clerical proficiency. | 1 (`CASE-025`) | 1 (ISTM Clerical) | **Ready (2/2)** | **Blocked (0/2)** |
| **Total** | **26** | **Full Benchmark Cohort** | **3** | **23** | **Ready (26/26)** | **Blocked (0/26)** |

---

## 4. Potential Competency Overlaps Requiring Expert Review

The expert packet explicitly documents critical conceptual overlaps to prevent premature or erroneous classification:

### A. Official Statistics & Data Analytics (Strata D)
- **`BM-CASE-022` (*HCES Unit Level Data*) & `BM-CASE-023` (*ASI Unit Level Data*)**:
  - **Data Analytics Overlap**: Reading unit-level data files, variable filtering, merging schedule blocks, and calculating weighted aggregates overlap directly with `KCM-FUNC-11` (*Data Analytics*).
  - **Specialist Domain Knowledge**: NSS sampling design (strata, sub-strata, FSU/SSU), sampling weights / multipliers, multiplier adjustment formulas, item-level consumption aggregation, and Annual Survey of Industries (ASI) factory accounting schedules represent specialist official statistics domain knowledge.
  - **Expert Triage Task**: Determine whether the course is a practical computing course mapping to `KCM-FUNC-11` or a specialized survey methodology course representing an official statistics domain gap (`no_applicable_kcm_competency`).
- **`BM-CASE-020` (*Introduction to Big Data in Governance*)**:
  - Categorized as "Domain" in MoSPI's ACBP schedule, but authored by NeGD/MeitY for general civil servants.
  - Overlaps with `KCM-FUNC-10` (*Digital Fluency*) and `KCM-FUNC-11` (*Data Analytics*).
  - **Expert Triage Task**: Reconcile whether this is a false domain gap that should be mapped to Functional Digital Fluency / Data Analytics.
- **`BM-CASE-024` (*Introduction to R and Python Programming*)**:
  - Categorized as "Domain" in ACBP, but teaches foundational statistical programming in Python and R.
  - Local physical document ([`Circular_NSSTA_Advance_Training_Calander_FY(25-26).pdf`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/raw/Circular_NSSTA_Advance_Training_Calander_FY%2825-26%29.pdf), Page 2) confirms "Machine Learning using Python".
  - **Expert Triage Task**: Determine whether statistical computing tools map to `KCM-FUNC-11` (*Data Analytics*) or `KCM-FUNC-10` (*Digital Fluency*).

### B. Behavioural & Functional Governance Overlaps (Strata B & C)
- **`BM-CASE-002` (*Leadership in Project Management*)**: Candidate `KCM-FUNC-05` (*Project Management*) vs `KCM-BEH-10` (*Strategic Leadership*). Evaluates whether an 18-minute module teaches functional project tools or executive leadership concepts.
- **`BM-CASE-008` (*Yoga Break at Workplace*)**: Ministry of Ayush 5-minute workplace physical health intervention. Evaluates whether physical wellness lies outside the civil service competency model (`no_applicable_kcm_competency`) or maps remotely to `KCM-BEH-01` (*Self-Awareness: physical well-being*).
- **`BM-CASE-009` (*Happiness in Seva-Bhava*)**: Evaluates whether philosophical service orientation maps to behavioural `KCM-BEH-07` (*Service Orientation*) or functional `KCM-FUNC-01` (*Citizen Centricity*).
- **`BM-CASE-012` (*Gender Equality through Indian Spiritual Vision*)**: Evaluates whether gender equality maps to behavioural `KCM-BEH-06` (*Collaboration: Diversity & Inclusion*) or statutory administrative rules under `KCM-FUNC-12` (*Establishment & HR*).

### C. Cross-Cadre Pedagogical Contrast (Strata E)
- **`BM-CASE-025` vs `BM-CASE-026` (*Noting and Drafting*)**:
  - `BM-CASE-025` (Section Officers / SSOs, 90m): Evaluates intermediate/advanced supervisory noting, statutory rule interpretation, and decision synthesis (Level 2/3).
  - `BM-CASE-026` (Clerical / Assistants, 60m): Evaluates routine docketing, file referencing, and routine acknowledgments (Level 1).
  - Both map to `KCM-FUNC-13` (*Office Management: Noting and Drafting sub-theme*), testing the platform's ability to differentiate proficiency tiers.

---

## 5. Live Command Verification & Test Results

The entire platform test suite and mapping registry validator were executed cleanly:

### A. Full Automated Test Suite (`pytest`)
- **Command**: `python -m pytest -v`
- **Exit Code**: `0` (Success)
- **Duration**: `0.63s`
- **Results**: **146 passed** (including 9 new Stage 3.5 regression tests in `tests/test_expert_triage_packet.py`):
  - `tests/test_expert_triage_packet.py`: 9 passed
  - `tests/test_source_citation_verification.py`: 13 passed
  - `tests/test_adjudication_packet.py`: 12 passed
  - `tests/test_adjudication_packet_audit.py`: 9 passed
  - `tests/test_competency_mapping.py`: 24 passed
  - `tests/test_acbp_extraction.py`: 18 passed
  - `tests/test_kcm_extraction.py`: 19 passed
  - `tests/test_mapping_benchmark.py`: 8 passed
  - `tests/test_course_evidence.py`: 8 passed
  - `tests/test_evidence_provenance_audit.py`: 6 passed
  - `tests/test_pdf_extractor.py`: 10 passed
  - `tests/test_source_register.py`: 8 passed

### B. Production Competency Mapping Validation
- **Command**: `python scripts/validate_competency_mappings.py`
- **Exit Code**: `0` (Success)
- **Result**: All 226 records in `data/processed/acbp_kcm_mappings.json` strictly satisfy Draft 2020-12 schema rules, dual referential integrity, and domain category segregation.

---

## 6. Baseline Cryptographic Hash Comparison

| Target File | Baseline Expected Hash | Audited Live Hash | Immutability Status |
| :--- | :--- | :--- | :---: |
| `data/processed/acbp_courses.json` | `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` | `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` | **MATCH (Frozen)** |
| `data/processed/competencies_kcm.json` | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` | **MATCH (Frozen)** |
| `data/processed/acbp_kcm_mappings.json` | `606926ad073e0e2a5682697f60c66c1867da908d57f5d2c53b1c2e596b5360f2` | `606926ad073e0e2a5682697f60c66c1867da908d57f5d2c53b1c2e596b5360f2` | **MATCH (Frozen)** |

---

## 7. Working Tree and Git Status Summary

- **Tracked Modifications**:
  - `data/interim/mapping_adjudication_packet.csv`
  - `data/interim/mapping_adjudication_packet.json`
  - `docs/mapping_adjudication_readiness_report.md`
  - `scripts/build_adjudication_packet.py`
- **New Stage 3.5 Artifacts**:
  - `data/interim/expert_triage_packet.json`
  - `data/interim/expert_triage_packet.csv`
  - `docs/expert_triage_guide.md`
  - `docs/expert_triage_readiness_report.md`
  - `scripts/build_expert_triage_packet.py`
  - `tests/test_expert_triage_packet.py`
- **Untracked Audit Artifacts from Prior Stages (Preserved)**:
  - `data/interim/adjudication_packet_quality_audit.json`
  - `data/interim/source_citation_verification.json`
  - `docs/adjudication_packet_quality_audit.md`
  - `docs/source_citation_verification_report.md`
  - `docs/stage_3_4_3_4_final_audit_report.md`
  - `scripts/verify_source_citations.py`
  - `tests/test_adjudication_packet_audit.py`
  - `tests/test_source_citation_verification.py`
- **Protected Directories**: `data/raw/` and `data/processed/` have 0 lines modified. No git commit or push has been performed.

---

## 8. Remaining Limitations & Risk Governance

1. **Absence of Local Micro-Course Lesson Plans**: 23 course evidence references rely on secondary institutional publications or portal titles rather than verbatim micro-course module transcripts.
2. **Civil Service SSO Authentication Barrier**: 11 iGOT Karmayogi micro-courses are secured behind Parichay SSO and cannot be scraped or accessed by automated scripts.
3. **Automated Testing vs. Pedagogical Truth**: Passing 146 unit tests proves referential integrity, hash invariance, and code correctness. It does **not** prove that an unacquired syllabus matches an iGOT course.

---

## 9. Next Concrete Action Required from Authorized Human Reviewers

Authorized Subject Matter Experts from NSSTA, MoSPI, or CBC should execute the following steps:

1. **Open the Expert Triage Dossier**:
   - For spreadsheet-based review: Open [`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv) in Excel or LibreOffice.
   - For programmatic review: Inspect [`data/interim/expert_triage_packet.json`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.json).
2. **Follow the Operational Manual**: Read [`docs/expert_triage_guide.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/expert_triage_guide.md) before evaluating cases.
3. **Record Blind Independent Reviews**:
   - Reviewer 1 completes columns `r1_*` (or `independent_reviews[0]`).
   - Reviewer 2 completes columns `r2_*` (or `independent_reviews[1]`).
   - Reviewers select an approved benchmark label (`supported_mapping`, `plausible_insufficient_evidence`, `incorrect_mapping`, `unresolved_insufficient_source`, `no_applicable_kcm_competency`), record an anchored confidence rating (1–5), provide technical rationale, and note missing curriculum items.
4. **Initiate Official Evidence Requisitions**:
   - For the 11 iGOT courses: Request authenticated module transcripts from MoSPI Capacity Building Unit (CBU).
   - For the 12 apex academy courses: Request detailed session syllabi from ISTM, AJ-NIFM, and ATI Mysuru.
