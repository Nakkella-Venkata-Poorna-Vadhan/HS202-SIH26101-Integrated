# Stage 3.5.1 — Expert Triage Packet Round-Trip and Decision Safeguards Audit

**Platform**: SIH26101 Official Statistics Competency Intelligence and Adaptive Learning Platform  
**Stage**: 3.5.1 — Expert Triage Packet Round-Trip and Decision Safeguards Audit  
**Evaluation Scope**: Stage 3.5 Expert Triage Packet (`expert_triage_packet.json` & `.csv`), Decision Safeguards, Evidence Immutability, and CSV-to-JSON Import Contract  
**Audit Date**: October 2026  
**Auditor**: Independent Pipeline Quality & Security Agent  
**Target Files Evaluated**:
- `data/interim/expert_triage_packet.json`
- `data/interim/expert_triage_packet.csv`
- `scripts/build_expert_triage_packet.py`
- `tests/test_expert_triage_packet.py`
- `tests/test_expert_triage_safeguards.py`
- `docs/expert_triage_guide.md`
- `docs/expert_triage_readiness_report.md`

---

## 1. Audit Verdict

### **Verdict: PASS WITH LIMITATIONS**

- **Round-Trip & Decision Safeguards**: **PASS**  
  All 13 safeguard test specifications pass cleanly. Case identification is strictly bound to `benchmark_case_id` (immune to row shuffling); RFC 4180 quoting protects commas, double quotes, and multiline rationales; decision labels and confidence ratings are strictly bounded; and reviewer slots remain separated.
- **Evidence Provenance & Metadata Protection**: **PASS**  
  A strict validation firewall prevents any CSV edit from escalating `external_reference_unverified` to `verified_local_source`, converting `is_exact_course_evidence` to `True`, or altering course metadata.
- **Core Dataset & Registry Immutability**: **PASS**  
  All baseline hashes (`acbp_courses.json`, `competencies_kcm.json`, `acbp_kcm_mappings.json`) match their exact frozen baselines. `data/raw/` and `data/processed/` have zero modifications.
- **Operational Limitation**: **DOCUMENTED LIMITATION**  
  The CSV packet is currently an **export for review**. No automated bulk ingestion script has been deployed to `scripts/` in order to prevent unauthorized automated overwrites prior to formal expert sign-off. The minimal safe import contract is formally defined and verified via test fixtures in `tests/test_expert_triage_safeguards.py`.

---

## 2. CSV Editing Support & Safe Import Contract

### Current Architecture
1. **Export for Review**: The CSV [`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv) is designed as a human-friendly export for Subject Matter Experts (SMEs) to inspect course dossiers in standard spreadsheet tools (Excel, LibreOffice).
2. **Independent Review Slots**: Flattened columns `r1_*` (Reviewer 1) and `r2_*` (Reviewer 2) provide isolated slots for blind evaluations without inter-reviewer contamination.
3. **Absence of Production Batch Importer**: The repository does not currently deploy an automatic CSV import runner. This is an intentional safety architecture to ensure that arbitrary CSV edits cannot corrupt the canonical JSON benchmark without passing through explicit validation gates.

### Minimal Future Import Contract
Any future CSV-to-JSON import utility must adhere to the following 8 immutable contract rules (verified in `tests/test_expert_triage_safeguards.py`):
1. **Case Key Identity**: Rows must be matched strictly by `benchmark_case_id`. Row position alone must never be trusted. Exactly 26 unique IDs matching `BM-CASE-001` through `BM-CASE-026` must be present.
2. **Immutable Metadata Firewall**: All 13 core course/manifest fields (`course_record_id`, `course_name`, `cadre_role`, `acbp_competency_category`, `duration`, `course_creator`, `primary_source_id`, `primary_source_citation`, `primary_source_provenance`, `primary_source_verification_status`, `evidence_source_id`, `evidence_verification_status`, `is_exact_course_evidence`) must be validated against the frozen manifest. Any edit to these fields must abort import with a `Tampering detected` error.
3. **Evidence Status Immutability**: Any attempt to modify `evidence_verification_status` or set `is_exact_course_evidence = True` via CSV must be rejected.
4. **Decision Label Taxonomy**: Reviewer decision labels must be empty string `""` or strictly one of the 5 allowed labels (`supported_mapping`, `plausible_insufficient_evidence`, `incorrect_mapping`, `unresolved_insufficient_source`, `no_applicable_kcm_competency`).
5. **Confidence Rating Scale**: Confidence ratings must be empty string `""` or an integer between `1` and `5` inclusive. Non-numeric strings or out-of-bounds numbers must be rejected.
6. **Review Completeness**: A decision label cannot be submitted without `reviewer_id`, `confidence_rating`, and `expert_rationale`. Incomplete submissions must be rejected.
7. **Consensus Isolation**: A single reviewer completing Slot 1 or 2 cannot set `final_adjudicated_label` or change `adjudication_status` to `adjudicated`. Status becomes `review_in_progress` pending the second reviewer.
8. **Disagreement Escalation**: When Reviewer 1 and Reviewer 2 submit conflicting decision labels, the importer must set `adjudication_status = "requires_more_evidence"` and `consensus_status = "reviewer_disagreement_escalated"`. The system must never silently average or overwrite conflicting decisions.

---

## 3. Actual Round-Trip Tests Performed

All round-trip tests were executed against temporary in-memory fixtures without modifying the underlying canonical datasets:

| Test Case | Description & Failure Mode Tested | Result |
| :--- | :--- | :---: |
| `test_case_lookup_resilience_to_row_reordering` | Shuffled all 26 CSV rows in random order; verified case matching occurs strictly by `benchmark_case_id`. | **PASSED** |
| `test_detect_duplicate_or_missing_case_ids` | Injected duplicate row for `BM-CASE-001` and deleted a row (25 rows); verified rejection. | **PASSED** |
| `test_detect_missing_or_extra_csv_columns` | Removed `duration` column; verified rejection on header mismatch. | **PASSED** |
| `test_quoting_multiline_commas_and_quotes` | Injected complex rationale with quotation marks, commas, and internal line breaks; verified RFC 4180 parsing fidelity. | **PASSED** |
| `test_reject_invalid_expert_decision_labels` | Injected illegal label `'approved_mapping'`; verified validation rejection. | **PASSED** |
| `test_reject_malformed_confidence_ratings` | Tested out-of-range rating `6` and non-numeric string `'high'`; verified validation rejection. | **PASSED** |
| `test_detect_incomplete_review_submissions` | Submitted decision label with empty rationale; verified validation rejection. | **PASSED** |
| `test_protect_immutable_course_and_case_metadata` | Tampered with `course_name` in CSV; verified tamper-detection rejection. | **PASSED** |
| `test_protect_evidence_provenance_against_escalation` | Attempted to escalate `evidence_verification_status` to `'verified_local_source'` and set `is_exact_course_evidence = True`; verified rejection. | **PASSED** |
| `test_single_reviewer_cannot_finalize_ground_truth` | Submitted valid Reviewer 1 decision; verified `adjudication_status` is `review_in_progress`, final label is `null`. | **PASSED** |
| `test_dual_reviewer_conflict_surfacing` | Reviewer 1 submitted `supported_mapping`, Reviewer 2 submitted `incorrect_mapping`; verified escalation to `requires_more_evidence`. | **PASSED** |
| `test_dual_reviewer_consensus_achievement` | Both reviewers submitted matching decisions with confidence $\ge 3$; verified consensus achievement. | **PASSED** |
| `test_production_mapping_registry_and_baseline_immutability` | Verified baseline hashes and 226-record count remain invariant. | **PASSED** |

---

## 4. Decision & Evidence-Provenance Safeguards Verified

1. **Reviewer Separation**: Reviewer 1 and Reviewer 2 entries reside in independent, non-overlapping columns and JSON structures. Reviewer 1 cannot overwrite Reviewer 2.
2. **Anti-Hallucination & Provenance Firewall**:
   - `verified_local_source` is strictly restricted to the 3 verified local documents (`BM-CASE-021`, `BM-CASE-024`, `BM-CASE-025`).
   - The remaining 23 cases remain strictly classified as `external_reference_unverified`.
   - Free-text reviewer comments cannot alter machine-readable provenance fields.
3. **Domain Gap Integrity**:
   - Administrative category `Domain` in ACBP is not treated as proof of zero KCM match.
   - Conceptual overlap with `KCM-FUNC-11` (*Data Analytics*) is explicitly preserved for `BM-CASE-022` (*HCES*), `BM-CASE-023` (*ASI*), `BM-CASE-020` (*Big Data*), and `BM-CASE-024` (*Python/R*).
4. **Non-Authentication of Self-Entered Roles**:
   - Reviewer role and affiliation fields are recorded as declarative reviewer metadata; they are never represented as formal institutional cryptographic signatures or official approvals.

---

## 5. Defects Found & Minimal Corrections Applied

- **Defect Identified**: In `tests/test_expert_triage_safeguards.py`, the initial test regex expected `Illegal evidence escalation in BM-CASE-001`, but the validator's immutable metadata check caught the unauthorized field modification first with `field 'evidence_verification_status' was modified`.
- **Minimal Correction**: Updated the test assertion in `tests/test_expert_triage_safeguards.py` to assert `field 'evidence_verification_status' was modified` and `field 'is_exact_course_evidence' was modified`.
- **Scope of Fix**: Zero changes to production or interim data files; limited strictly to test regex calibration.

---

## 6. Live Command Verification & Exit Codes

| Command Line | Purpose | Exit Code | Verified Output |
| :--- | :--- | :---: | :--- |
| `python -m pytest tests/test_expert_triage_safeguards.py -v` | Safeguards Test Suite | **`0`** | **13 passed in 0.10s** |
| `python -m pytest -v` | Full Repository Test Suite | **`0`** | **159 passed in 0.55s** across 12 test files |
| `python scripts/validate_competency_mappings.py` | Production Registry Validator | **`0`** | **All 226 records strictly satisfy schema & integrity rules** |
| `git diff --check` | Whitespace & Formatting Check | **`0`** | Clean (zero syntax or merge defects) |
| `git diff -- data/raw/ data/processed/` | Core Dataset Protection Check | **`0`** | **0 lines modified (Completely Empty)** |

---

## 7. Baseline Cryptographic Hash Comparison

| Target File | Baseline Expected Hash | Audited Live Hash | Verification Status |
| :--- | :--- | :--- | :---: |
| `data/processed/acbp_courses.json` | `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` | `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` | **MATCH (Frozen)** |
| `data/processed/competencies_kcm.json` | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` | **MATCH (Frozen)** |
| `data/processed/acbp_kcm_mappings.json` | `606926ad073e0e2a5682697f60c66c1867da908d57f5d2c53b1c2e596b5360f2` | `606926ad073e0e2a5682697f60c66c1867da908d57f5d2c53b1c2e596b5360f2` | **MATCH (Frozen)** |

---

## 8. Remaining Limitations

1. **Absence of Local Micro-Course Lesson Plans**: 23 course evidence references rely on secondary institutional publications or portal titles rather than verbatim micro-course module transcripts.
2. **Parichay SSO Barrier**: 11 iGOT Karmayogi micro-courses are secured behind civil service authentication and cannot be inspected without authorized government credentials.
3. **Automated Testing Boundary**: Passing 159 automated unit tests confirms structural integrity, schema compliance, and safeguard enforcement. It does **not** validate the substantive correctness of subjective human decisions or pedagogical alignment.

---

## 9. Safest Next Action for Authorized Human Reviewers

1. **Reviewer Evaluation**: Authorized SMEs should open [`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv) and independently complete their respective review columns (`r1_*` for Reviewer 1, `r2_*` for Reviewer 2).
2. **Respect Immutable Fields**: Reviewers must only edit columns designated for human evaluation (`r1_*`, `r2_*`). Do not modify case IDs, course names, or evidence verification statuses.
3. **Submit for Validation**: Once completed, the edited CSV should be validated against the 8 contract rules in `tests/test_expert_triage_safeguards.py` before any consensus synthesis occurs.
4. **Issue Evidence Requisitions**: Use the `r1_requisition_notes` and `r2_requisition_notes` columns to formally specify curriculum documents required from MoSPI CBU and apex training academies.
