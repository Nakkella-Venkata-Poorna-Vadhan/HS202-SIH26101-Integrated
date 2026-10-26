# MoSPI ACBP Benchmark: SME Review Operator Checklist & Execution Standard (Stage 3.6)

> [!IMPORTANT]
> **Operational Scope**: Standard Operating Procedure (SOP) for platform operators to distribute review packets, collect blind SME judgments, execute CLI validation, and import expert reviews into the SIH26101 pipeline.  
> **Source Baseline**: Frozen Stage 3.5 Review Importer ([`scripts/import_expert_reviews.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/scripts/import_expert_reviews.py)) and Canonical Review Packet ([`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv)).  
> **Strict Immutability Rule**: The canonical CSV `data/interim/expert_triage_packet.csv` must NEVER be directly edited. Reviewers must receive independent copies.

---

## 1. Pre-Distribution Workflow (Packet Preparation)

```
[PACKET GENERATION & DISTRIBUTION ARCHITECTURE]
data/interim/expert_triage_packet.csv (FROZEN CANONICAL MASTER)
               │
               ├── Copy A ──► data/interim/expert_triage_packet_reviewer1.csv ──► [Reviewer 1: ISS Cadre Lead]
               │
               └── Copy B ──► data/interim/expert_triage_packet_reviewer2.csv ──► [Reviewer 2: Public Admin Faculty]
```

### Step 1.1: Verify Canonical Master Checksum
Before generating reviewer working copies, compute and verify the SHA256 checksum of the canonical packet:
```powershell
Get-FileHash -Algorithm SHA256 data/interim/expert_triage_packet.csv
```
*Ensure this matches the baseline record. Never allow write operations to this master file.*

### Step 1.2: Generate Independent Reviewer Working Copies
Create dedicated review copies for Reviewer 1 and Reviewer 2:
```powershell
Copy-Item data/interim/expert_triage_packet.csv data/interim/expert_triage_packet_reviewer1.csv
Copy-Item data/interim/expert_triage_packet.csv data/interim/expert_triage_packet_reviewer2.csv
```

### Step 1.3: Package Reviewer Kit
Assemble the distribution package for each SME:
1. Assigned working CSV: `expert_triage_packet_reviewer1.csv` (or `_reviewer2.csv`)
2. Review Invitation & Charter: [`docs/sme_review_invitation.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/sme_review_invitation.md)
3. Triage & Decision Guide: [`docs/expert_triage_guide.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/expert_triage_guide.md)
4. Evidence Acquisition Report: [`docs/course_evidence_acquisition_report.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/course_evidence_acquisition_report.md)

---

## 2. Review Collection & Blind Custody Standard

### Step 2.1: Enforce Blind Dual Review
- Reviewer 1 and Reviewer 2 must not be informed of each other's identity or intermediate entries.
- If a reviewer requests clarification on a case, provide factual document citations only; never share how another reviewer scored that case.

### Step 2.2: Check Column Integrity Upon Receipt
When an SME returns their completed CSV, verify that:
- Rows have **not** been added, deleted, or reordered (must remain exactly 26 cases, `BM-CASE-001` through `BM-CASE-026`).
- Benchmark case IDs, course names, and primary source citations are unaltered.
- Reviewer populated their designated columns (`r1_...` for Reviewer 1; `r2_...` for Reviewer 2).

---

## 3. CLI Validation & Quality Assurance (Pre-Import)

The frozen importer provides a dedicated validation command (`--validate`). Run this immediately upon receiving any returned CSV to detect syntax errors, invalid labels, or missing rationales.

### Step 3.1: Execute Dry-Run Validation
Run the validator from repository root:
```powershell
python scripts/import_expert_reviews.py --validate data/interim/expert_triage_packet_reviewer1.csv
```

### Step 3.2: Interpret Validator Feedback
The validator performs the following automated checks:

| Validation Rule | Target Requirement | Remediation if Failed |
| :--- | :--- | :--- |
| **Row Count** | Exactly 26 benchmark cases | Check if SME deleted or added rows. Re-align with canonical master. |
| **Case ID Match** | `BM-CASE-001` through `BM-CASE-026` in order | Restore corrupted Case IDs. |
| **Decision Label** | Exactly one of the 5 controlled vocabulary labels | Check for typos (e.g., `supported` instead of `supported_mapping`). |
| **Confidence Score** | Integer between `1` and `5` | Request reviewer to assign valid integer rating. |
| **Rationale Field** | Minimum 10 characters explaining decision | Prompt reviewer for substantive textual justification. |
| **Target KCM ID** | Valid `KCM-FUNC-##` or `KCM-BEH-##` if label is `supported_mapping` | Ensure referenced competency exists in KCM 2024 catalogue. |

*If validation fails, return the specific line and error description to the reviewer for prompt correction.*

---

## 4. Merging Independent Reviews into Master Review Packet

Once both Reviewer 1 and Reviewer 2 CSVs have passed individual validation:

### Step 4.1: Merge Reviewer Columns
Merge Reviewer 1's fields (`r1_*`) and Reviewer 2's fields (`r2_*`) into a consolidated review file:  
`data/interim/expert_triage_packet_completed.csv`.

*Ensure Reviewer 1 columns occupy `r1_*` and Reviewer 2 columns occupy `r2_*` without overwriting benchmark case metadata.*

### Step 4.2: Validate Consolidated Master Review Packet
```powershell
python scripts/import_expert_reviews.py --validate data/interim/expert_triage_packet_completed.csv
```
*Both `reviewer_1_complete` and `reviewer_2_complete` should report 26/26 valid cases.*

---

## 5. Executing Production Import & Generating Adjudication Review

Once validated, execute the authoritative import using the frozen CLI runner:

### Step 5.1: Run Importer
```powershell
python scripts/import_expert_reviews.py --import data/interim/expert_triage_packet_completed.csv --output data/interim/adjudicated_benchmark_review.json
```

### Step 5.2: Verify Import Output Metrics
The importer will generate a structured summary report in `data/interim/adjudicated_benchmark_review.json` containing:
1. **Total Cases Processed**: 26
2. **Reviewer 1 Completion**: 26 / 26
3. **Reviewer 2 Completion**: 26 / 26
4. **Consensus Agreement Rate**: Percentage of exact label matches
5. **Discordant / Escalated Cases**: Detailed breakdown of cases where Reviewer 1 and Reviewer 2 differed (e.g., `supported_mapping` vs `plausible_insufficient_evidence`)

---

## 6. Post-Import Verification & Safety Protocol

Immediately following import, execute the standard safety verification checks:

```powershell
# 1. Ensure test suite remains 100% green
python -m pytest tests/test_import_expert_reviews.py tests/test_expert_triage_packet.py tests/test_expert_triage_safeguards.py

# 2. Confirm no protected directories or files were modified
git status
```

### Safety Rules:
1. **Zero Overwrites to `data/raw/`**: Confirm no raw PDF has been touched or modified.
2. **Zero Overwrites to `data/processed/`**: Confirm production dictionaries (`competencies_kcm.json`, `acbp_courses.json`, `acbp_kcm_mappings.json`) remain identical to baseline SHA256 hashes.
3. **No Unilateral Ground-Truth Injection**: In discordant cases, the adjudication status must remain `pending_review` or `panel_review_required` until the official Adjudication Panel conducts formal joint reconciliation.
