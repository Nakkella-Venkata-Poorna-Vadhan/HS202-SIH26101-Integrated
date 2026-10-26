# Stage 3.5.2 — Safe Expert Review Import and Validation CLI Report

**Platform**: SIH26101 Official Statistics Competency Intelligence and Adaptive Learning Platform  
**Stage**: 3.5.2 — Implement a Safe Expert Review Import and Validation CLI  
**Evaluation Scope**: Expert Review Import Runner (`scripts/import_expert_reviews.py`), Review Contract Validation, Safety Regression Tests, and Import Artifact  
**Audit Date**: October 2026  
**Auditor**: Independent Pipeline Quality & Security Agent  
**Key Deliverables**:
- CLI Tool: [`scripts/import_expert_reviews.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/scripts/import_expert_reviews.py)
- Test Suite: [`tests/test_import_expert_reviews.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/tests/test_import_expert_reviews.py)
- Operational Guide: [`docs/expert_review_import_workflow.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/expert_review_import_workflow.md)

---

## 1. Audit Verdict

### **Verdict: PASS WITH LIMITATIONS**

- **CLI Architecture & Review Contract**: **PASS**  
  `scripts/import_expert_reviews.py` successfully implements `--validate` and `--import` modes. It strictly validates case identity (all 26 cases matching `BM-CASE-001` through `BM-CASE-026` resolved by ID), rejects modified immutable course/evidence metadata, enforces the 5-term benchmark label taxonomy, validates 1–5 integer confidence ratings, requires substantive rationales, and keeps Reviewer 1 and Reviewer 2 records strictly separated.
- **Data Protection & Overwrite Prevention**: **PASS**  
  The CLI strictly refuses to overwrite existing output files, canonical triage packet files (`expert_triage_packet.json`, `expert_triage_packet.csv`), or any file inside protected directories (`data/raw/` and `data/processed/`).
- **Core Dataset & Registry Immutability**: **PASS**  
  All frozen SHA256 hashes (`acbp_courses.json`, `competencies_kcm.json`, `acbp_kcm_mappings.json`) match their authoritative baselines. Zero modifications were introduced into `data/raw/` or `data/processed/`.
- **Operational Limitation**: **DOCUMENTED LIMITATION**  
  Reviewer names, roles, and affiliations entered in the CSV are declarative reviewer metadata and do **not** constitute cryptographically authenticated institutional approval. Furthermore, provisional consensus between Reviewer 1 and Reviewer 2 does **not** automatically finalize benchmark ground truth or alter the production mapping registry.

---

## 2. CLI Usage Examples

The CLI supports two primary operational modes plus comprehensive help:

### A. Validation-Only Mode
Validates a human-edited CSV against the canonical packet and review contract without creating or modifying any files:
```powershell
python scripts/import_expert_reviews.py --validate data/interim/expert_triage_packet.csv
```

### B. Import to New Review-Results Artifact Mode
Validates the CSV and imports the reviews into a separate, new JSON artifact:
```powershell
python scripts/import_expert_reviews.py --import data/interim/expert_triage_packet.csv --output data/interim/expert_reviews_round1.json
```

### C. Help and Safety Restrictions Mode
```powershell
python scripts/import_expert_reviews.py --help
```

---

## 3. Validation and Import Behavior

### A. Immutability Firewall
The tool compares all 26 cases against `data/interim/expert_triage_packet.json`. Any attempt to alter:
- Course name, duration, category, cadre, or provider;
- Primary source citation or source ID;
- Evidence verification status (e.g. promoting `external_reference_unverified` to `verified_local_source`);
- Setting `is_exact_course_evidence = True`;
results in immediate rejection with a clear error identifying the case ID and modified field.

### B. Incomplete Review Detection
Review submissions are validated for completeness:
- If a decision label is selected, `reviewer_id`, `confidence_rating` (1–5), and `expert_rationale` (minimum 5 chars) must all be provided.
- If any of these fields are missing or malformed, the review is rejected.
- If a review slot is completely blank, it is safely accepted as an unreviewed case.

### C. Consensus Evaluation Logic
- **Single Reviewer**: If only Reviewer 1 (or Reviewer 2) has evaluated a case, consensus status is set to `single_review_in_progress`. A single reviewer cannot establish consensus or benchmark ground truth.
- **Reviewer Agreement**: If both reviewers agree on the decision label and target KCM ID, the case is marked `provisional_consensus_achieved`. This is explicitly distinguished from final ground truth.
- **Reviewer Conflict**: If Reviewers 1 and 2 submit conflicting decision labels (e.g. `supported_mapping` vs `incorrect_mapping`), the case is marked `conflict_escalated` and flagged for panel review. Decisions are never silently averaged or merged.

### D. Separate Output JSON Artifact Schema
The imported JSON file contains:
- `artifact_type`: `"expert_review_results"`
- `disclaimer`: Explicit declaration that output is a review evaluation artifact and not production mappings.
- `packet_id` and `benchmark_id`.
- `imported_at`: ISO 8601 UTC timestamp.
- `source_csv_filename` and `source_csv_sha256`.
- `canonical_packet_sha256`: Hash of reference canonical packet.
- `summary`: Counts of unreviewed, completed, provisional consensus, and conflict cases.
- `cases`: Deterministically sorted list (`BM-CASE-001` through `026`) containing isolated Reviewer 1 and Reviewer 2 objects and consensus evaluation.

---

## 4. Actual Test Results & Verification

All 18 regression test specifications in `tests/test_import_expert_reviews.py` passed cleanly:

| Test Name | Verification Focus | Exit Code / Result |
| :--- | :--- | :---: |
| `test_cli_help` | Documents CLI usage and safety restrictions | **PASSED** |
| `test_validate_mode_on_canonical_csv` | Runs `--validate` on canonical CSV with zero file writes | **PASSED** |
| `test_import_mode_valid_canonical_csv` | Imports canonical CSV to temporary artifact | **PASSED** |
| `test_refuse_overwrite_existing_output` | Refuses to overwrite existing output file | **PASSED** |
| `test_refuse_overwrite_protected_canonical_files` | Refuses to write over canonical JSON or processed datasets | **PASSED** |
| `test_refuse_write_inside_protected_directories` | Refuses output paths inside `data/raw/` or `data/processed/` | **PASSED** |
| `test_row_reordering_resilience_and_deterministic_output` | Row-shuffled CSV imports properly; output sorted `BM-CASE-001` to `026` | **PASSED** |
| `test_reject_duplicate_and_missing_case_ids` | Rejects duplicate rows and missing cases | **PASSED** |
| `test_reject_header_mismatch` | Rejects CSV with missing or unauthorized columns | **PASSED** |
| `test_multiline_rationale_and_quoted_commas` | Preserves RFC 4180 complex multiline quotes and commas | **PASSED** |
| `test_reject_tampering_with_immutable_metadata` | Rejects CSV with modified `course_name` | **PASSED** |
| `test_reject_evidence_status_escalation` | Rejects attempt to escalate evidence status or exact evidence flag | **PASSED** |
| `test_reject_invalid_label_and_confidence` | Rejects invalid label `'definitely_true'` and confidence `'7'` | **PASSED** |
| `test_reject_incomplete_reviews` | Rejects decision submitted without rationale or reviewer ID | **PASSED** |
| `test_one_reviewer_only_does_not_finalize_ground_truth` | Reviewer 1 submission sets `single_review_in_progress`, final label `null` | **PASSED** |
| `test_dual_reviewer_conflict_surfacing` | Reviewer conflict sets `conflict_escalated`, requires panel | **PASSED** |
| `test_dual_reviewer_agreement_provisional_consensus` | Reviewer agreement sets `provisional_consensus_achieved` | **PASSED** |
| `test_zero_modifications_to_protected_baselines` | Frozen baseline files and 226 mappings remain immutable | **PASSED** |

### Complete Repository Test Suite:
- **Command**: `python -m pytest -v`
- **Result**: **177 passed in 3.01s** (0 failures across all 13 test files).
- **Mapping Registry Validator**: `python scripts/validate_competency_mappings.py` exited `0` (all 226 records strictly valid).

---

## 5. Baseline Cryptographic Hash Comparison

| Target File | Baseline Expected SHA256 Hash | Audited Live SHA256 Hash | Verification Status |
| :--- | :--- | :--- | :---: |
| `data/processed/acbp_courses.json` | `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` | `ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7` | **MATCH (Frozen)** |
| `data/processed/competencies_kcm.json` | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` | **MATCH (Frozen)** |
| `data/processed/acbp_kcm_mappings.json` | `606926ad073e0e2a5682697f60c66c1867da908d57f5d2c53b1c2e596b5360f2` | `606926ad073e0e2a5682697f60c66c1867da908d57f5d2c53b1c2e596b5360f2` | **MATCH (Frozen)** |

---

## 6. Working Tree and Git Status Summary

- **Tracked Modifications**:
  - `data/interim/mapping_adjudication_packet.csv`
  - `data/interim/mapping_adjudication_packet.json`
  - `docs/mapping_adjudication_readiness_report.md`
  - `scripts/build_adjudication_packet.py`
- **New Stage 3.5.2 Artifacts**:
  - `scripts/import_expert_reviews.py`
  - `tests/test_import_expert_reviews.py`
  - `docs/expert_review_import_workflow.md`
  - `docs/stage_3_5_2_review_import_report.md`
- **Protected Core Directories**: `data/raw/` and `data/processed/` have 0 lines modified. No git commit or push has been performed.

---

## 7. Remaining Limitations & Boundaries

1. **Declarative Reviewer Credentials**: Reviewer identifiers and affiliations are captured as declarative metadata from the CSV. They are not cryptographically signed certificates.
2. **Definitive Adjudication Blocks**: 23 of 26 benchmark cases remain blocked pending acquisition of physical course syllabi from apex training academies (ISTM, AJ-NIFM, ATI Mysuru) and authenticated civil service access to the 11 iGOT micro-courses behind Parichay SSO.
3. **Automated Testing Boundary**: 177 passing unit tests prove pipeline referential integrity, schema compliance, and safeguard enforcement. They do not substantiate the human subjective correctness of reviewer decisions.

---

## 8. Exact Next Action for Authorized Human Reviewers

1. **Execute Review**: Authorized experts from NSSTA, MoSPI, or CBC should open [`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv) and independently complete their respective review columns (`r1_*` for Reviewer 1, `r2_*` for Reviewer 2).
2. **Validate Submission**: Run the CLI in validation-only mode:
   ```powershell
   python scripts/import_expert_reviews.py --validate data/interim/expert_triage_packet.csv
   ```
3. **Import Results**: If validation passes with 0 errors, import to a new review artifact:
   ```powershell
   python scripts/import_expert_reviews.py --import data/interim/expert_triage_packet.csv --output data/interim/expert_reviews_round1.json
   ```
4. **Convene SME Panel for Conflicts**: Inspect cases marked `conflict_escalated` in the generated JSON summary and convene a joint NSSTA / MoSPI expert panel for binding consensus.
