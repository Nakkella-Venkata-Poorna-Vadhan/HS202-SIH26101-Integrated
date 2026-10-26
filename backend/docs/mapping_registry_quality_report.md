# Competency Mapping Registry: Quality & Validation Report

> **Document Status:** Release Quality Sign-Off  
> **Milestone:** SIH26101 — Stage 3.2: Implement the Competency Mapping Registry  
> **Evaluated Artifacts:**  
> - `data/processed/acbp_kcm_mappings.json` & [`.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_kcm_mappings.csv)  
> - `data/processed/acbp_kcm_review_queue.json` & [`.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_kcm_review_queue.csv)  
> **Verification Date:** 2026-10-18  
> **Quality Verdict:** **READY FOR MAPPING EVALUATION**  

---

## 1. Executive Quality Ledger

| Dimension / Metric | Target Requirement | Measured Value | Compliance Status |
| :--- | :--- | :--- | :---: |
| **Total ACBP Courses Evaluated** | Exactly 226 course allocations | **226 records** | **100% PASS** |
| **Cadres Covered** | All 11 cadre levels (Annexure I) | **11 cadres** | **100% PASS** |
| **Duplicate Course IDs** | 0 duplicate courses | **0 duplicates** | **100% PASS** |
| **Duplicate Mapping IDs** | 0 duplicate mapping IDs | **0 duplicates** | **100% PASS** |
| **Referential Integrity (Courses)** | 100% resolve to `acbp_courses.json` | **226 / 226 (100%)** | **100% PASS** |
| **Referential Integrity (KCM)** | 100% non-null IDs resolve to KCM | **6 / 6 (100%)** | **100% PASS** |
| **Domain Course Contamination** | 0 Domain courses mapped to KCM | **0 / 51 mapped (0.0%)** | **100% PASS** |
| **Fabricated Competency Levels** | 0 level inferences | **0 invented levels** | **100% PASS** |
| **Uncalibrated Heuristic Scores** | 0 arbitrary float probabilities | **0 float scores (`null`)** | **100% PASS** |
| **Unapproved Validations** | 0 unreviewed validations | **0 validated (`pending_review`)** | **100% PASS** |
| **JSON / CSV Serialization Parity** | 100% field value match | **100% parity (Registry & Queue)** | **100% PASS** |
| **Input Baseline Immutability** | Cryptographic hash match | **All 3 input hashes identical** | **100% PASS** |
| **Automated Test Suite** | 100% passing tests | **76 / 76 passed (0 failures)** | **100% PASS** |

---

## 2. Decoupled Metrics: Coverage vs. Validation Quality

In adherence to Mission Karmayogi principles, **coverage is reported strictly independently from validation quality**. Reporting inflated coverage achieved by forcing weak or dubious mappings compromises system integrity.

### 2.1 Catalogue Coverage Analysis

```text
Total ACBP Course Allocations:      226
Total Explicit Candidate Mappings:  6   (2.65% Catalogue Reach)
Total Unresolved Allocations:       220 (97.35% Documented Gaps)
```

#### Category-Granular Coverage Breakdown:
| Curricular Category | Total Courses in ACBP | Candidate Mappings | Unresolved Gaps | Coverage Percentage | Primary Reason for Unresolved State |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Domain** | 51 | 0 | 51 | **0.00%** | **MoSPI Domain Gap:** KCM defines zero Domain competencies. Segregated by design. |
| **Functional** | 79 | 1 | 78 | **1.27%** | **Curricular Gap:** Course titles do not explicitly cite KCM names; requires modular syllabus audit. |
| **Behavioural** | 96 | 5 | 91 | **5.21%** | **Curricular Gap:** Exact title references identified for *Collaboration* and *Strategic Leadership*; remaining require syllabus audit. |
| **TOTAL** | **226** | **6** | **220** | **2.65%** | **Catalogue Baseline** |

> [!NOTE]
> **Why 2.65% Initial Coverage is Methodologically Sound:**  
> The 2.65% coverage reflects exact, defensible title references without guessing. In Stage 3.3+, lexical BM25 and dense semantic retrieval will expand the candidate pool for human review across the 169 unresolved Functional and Behavioural courses, while preserving the 51 Domain courses as official gaps pending the MoSPI Domain Dictionary.

### 2.2 Validation Quality Analysis
- **Formally Validated Mappings:** **0**
- **Formally Rejected Mappings:** **0**
- **Pending Human Review:** **6** (Carried forward as candidate hypotheses)
- **Unresolved:** **220**

> [!IMPORTANT]
> **No Ground-Truth Claims Without Authoritative Labels:**  
> In accordance with repository constraints, **precision, recall, F1, and accuracy are not reported** because ground-truth validation labels have not yet been rendered by authorized MoSPI/NSSTA faculty.

---

## 3. Cryptographic Baseline & Hash Ledger

All source and processed artifacts were verified for cryptographic stability:

| Artifact Path | Stage Role | SHA-256 Hash | Integrity Status |
| :--- | :--- | :--- | :---: |
| `data/processed/competencies_kcm.json` | Frozen KCM Baseline | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` | **Verified Immutable** |
| `data/processed/acbp_courses.json` | ACBP Course Dataset | `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` | **Verified Immutable** |
| `data/processed/acbp_kcm_candidate_mappings.json` | Interim Baseline | `966cabebbcc02f5cc96f5879fdbe3c7af126adfdf57ad5c5219aae580656b801` | **Verified Immutable** |
| `data/processed/acbp_kcm_mappings.json` | Stage 3.2 Registry JSON | `9ea63a033f6b9aa08da797966f39ddc18684bb5f2ee374a49c693a027fc64a50` | Generated & Audited |
| `data/processed/acbp_kcm_review_queue.json` | Stage 3.2 Review Queue | `5cae0d2dc60e06806ea9c2ea5b2d9ec76ce5b4484b8061eb002dc0227976e578` | Generated & Audited |

---

## 4. Verification Check Ledger (The 10 Required Checks)

1. **JSON Schema Conformance:** Verified via [`scripts/validate_competency_mappings.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/scripts/validate_competency_mappings.py) against Draft 2020-12 constraints.
2. **Referential Integrity:** 100% of course IDs resolve to `acbp_courses.json`; 100% of non-null competency IDs resolve to `competencies_kcm.json`.
3. **Source References & Page Numbers:** All records maintain verified, 1-indexed document page references (`[2, 12]` for courses; `[39, 107]` for competencies).
4. **Required Evidence Presence:** Every record contains non-empty, audited rationale (minimum length $\ge 20$ characters).
5. **No Fabricated Confidence:** All uncalibrated heuristic scores (`0.85`, `0.90`) from Stage 2B.2 were replaced with `null`.
6. **Validated Approval Metadata Check:** Validator strictly rejects any record marked `validated` that lacks `reviewer_id`, `reviewer_role`, or `reviewed_at`.
7. **Unresolved State Integrity:** All 220 unresolved records strictly contain `candidate_kcm_competency_id = null` and `validation_status = "unresolved"`.
8. **Duplicate Detection:** Zero duplicate course representations; zero duplicate mapping IDs.
9. **JSON / CSV Value Parity:** Exact 1-to-1 parity confirmed across all 30 fields in the registry and all 16 fields in the review queue.
10. **Audit Trail Preservation:** Rejection operations update status to `rejected` with critique text; no record is deleted.

---

## 5. Known Limitations & Technical Debt

1. **Absence of Modular Syllabi in Source PDF:** The MoSPI ACBP document provides course titles, duration, category, and provider, but omits modular lecture outlines. Substantive sub-theme mapping for the 169 unresolved courses requires external syllabus acquisition.
2. **Command-Line Reviewer Authentication:** The CLI review tool (`review_mapping.py`) simulates reviewer identity. Production deployment requires integration with authenticated institutional identity providers (e.g. Parichay / MeriPehchaan or iGOT SSO).
3. **MoSPI Domain Dictionary Gap:** Until MoSPI and NSSTA formally publish an Official Statistics Competency Dictionary, the 51 Domain courses cannot be mapped to any national competency model without hallucination.

---

## 6. Release Verdict

### Verdict: **READY FOR MAPPING EVALUATION**

**Supporting Evidence:**
- **Full Catalogue Reach:** 226 / 226 courses represented in both JSON and CSV formats.
- **Flawless Validation:** `validate_competency_mappings.py` confirms 100% compliance across all 10 schema rules.
- **Comprehensive Test Coverage:** Full test suite passes 76 / 76 tests in 0.39 seconds.
- **Input Immutability:** Baseline KCM and ACBP hashes are 100% preserved.
- **Audit Preparedness:** Actionable human-review queue is partitioned by triage priority and ready for subject matter expert curation.
