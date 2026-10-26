# KCM Competency Extraction Quality Audit (Stage 2A.1)

> **Document Status:** Quality Audit Report  
> **Source PDF:** `data/raw/KCM-Output_RestructuredOct17.pdf`  
> **Evaluated Dataset:** `data/processed/competencies_kcm.json` and `data/processed/competencies_kcm.csv`  
> **Evaluated Pipeline:** `scripts/extract_kcm.py`  
> **Reference Ledger:** `data/source_register.json` (`SRC-CBC-KCM-2024`)

---

## 1. Executive Summary & Independent Count Reconciliation

An independent verification of `data/processed/competencies_kcm.json`, `data/processed/competencies_kcm.csv`, `docs/kcm_extraction_notes.md`, and the raw source PDF (`data/raw/KCM-Output_RestructuredOct17.pdf`) was performed to resolve the behaviour-count discrepancy and evaluate source fidelity.

### 1.1. Summary of Counts

| Metric | Stated in Previous Summary | Calculated from Current JSON/CSV | Official Stated in KCM PDF | Actual Verifiable in KCM PDF Annexures |
| :--- | :---: | :---: | :---: | :---: |
| **Total Competency Records** | 34 | 34 | 34 | 34 |
| **Behavioural Competencies** | 13 | 13 | 13 (8 Core + 5 Leadership) | 13 (8 Core + 5 Leadership) |
| **Functional Competencies** | 21 | 21 | 21 | 21 |
| **Domain Competencies** | 0 | 0 | 0 (Declared out of scope) | 0 (Declared out of scope) |
| **Core Behavioural Sub-Themes** | 28 | 28 | 28 (Page 25) | 28 (Pages 39–54) |
| **Leadership Behavioural Sub-Themes** | 13 | 15 (defective) | 13 (Page 27) | 13 (Pages 55–64) |
| **Total Behavioural Sub-Themes** | 41 | 43 (defective) | 41 (Page 25) | 41 (Pages 39–64) |
| **Functional Sub-Themes** | 68 | 75 (defective) | 68 (Page 29) | 69 (Pages 66–107)* |
| **Total Model Sub-Themes / Behaviours** | **110 / 118** | **118** | **109** | **110** |

*\* Note on Functional Sub-Themes:* Page 29 of KCM states: *"The Karmayogī Competency Model consists of 21 Functional Competencies and 68 associated sub-themes."* However, on Page 75, `Project Management` details 4 sub-themes (`Project Planning`, `Project Implementation`, `Project Evaluation`, `Project KPIs Monitoring`) instead of the 3 bulleted on Page 30 (`Project Planning`, `Project Implementation`, `Project Evaluation & Monitoring`). Counting the 4 distinct panels gives **69** functional sub-themes and **110** total model sub-themes.

---

## 2. Investigation of the 118-versus-110 Discrepancy

### 2.1. Root Cause Analysis

The discrepancy between the reported **118** entries in `competencies_kcm.json` and the **110** official sub-themes in the KCM source document was traced directly to the column-bucketing algorithm in `scripts/extract_kcm.py` (`parse_subthemes_for_page()`):

```python
# scripts/extract_kcm.py (Current Implementation)
columns = {}
for b in clean_blocks:
    x_center = (b[0] + b[2]) / 2.0
    matched_col = None
    for col_x in columns.keys():
        if abs(x_center - col_x) < 160:
            matched_col = col_x
            break
    if matched_col is None:
        columns[int(x_center)] = [b]
    else:
        columns[matched_col].append(b)
```

In Adobe InDesign exports, sub-theme pages (pages 40 to 107) exhibit three layout patterns:
1. **Wide Banner Header Frames:** On 18 out of 34 pages (e.g., Pages 40, 42, 44, 48, 56, 58, 60, 64, 71, 79, 87, 89, 95, 99, 105, 107), InDesign placed multiple column titles inside a **single wide text frame** stretching across the entire width of the page (e.g., `bbox=(63, 552)-(1760, 605)`).
2. **Column Misallocation:** Because the frame spans the entire width, its center coordinate (`x_center ≈ 911`) falls into the middle column bucket. The outer columns (e.g., Column 1 at `x=63` and Column 4 at `x=1464`) received *only* their descriptive body text blocks, with no separate title block.
3. **Pseudo-Title Generation:** For columns lacking a title block, the fallback logic:
   ```python
   text_lines = [l.strip() for l in col_blocks[0][4].splitlines() if l.strip()]
   title = text_lines[0]
   desc = " ".join(text_lines[1:])
   ```
   arbitrarily split the body text, taking the **first sentence fragment as a pseudo-title** (e.g., `'Exhibits a commitment to addressing the:'` or `'Demonstrates a high level of proficiency:'`).
4. **Phantom Split Entries:** On pages where a title block was split across lines or multi-column spans (e.g., `KCM-FUNC-05` Project Management on Page 75, `KCM-FUNC-07` Material Management on Page 79, `KCM-FUNC-10` Digital Fluency on Page 85, `KCM-FUNC-21` Administration Matters on Page 107), the title was isolated from its body paragraph, creating an empty title entry and an orphan body entry.

### 2.2. Mathematical Breakdown of the Inflation

| Competency ID | Competency Name | Official Sub-Themes | Extracted Entries | Net Inflation | Specific Defect |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `KCM-BEH-09` | Creativity & Innovation | 2 | 3 | +1 | Title banner `'Lateral Thinking: Transformation Orientation'` created as standalone entry; 2 descriptions extracted with sentence-fragment titles. |
| `KCM-BEH-10` | Strategic Leadership | 4 | 5 | +1 | Title banner for 4 sub-themes merged into Column 3; Columns 1, 2, 4, 5 extracted with sentence-fragment titles. |
| `KCM-BEH-11` | Collaborative Leadership | 2 | 3 | +1 | Title banner `'Influencing & Negotiation: Conflict Management'` isolated; 2 descriptions extracted with sentence-fragment titles. |
| `KCM-BEH-12` | Team Leadership | 3 | 2 | -1 | 3 titles merged into Paragraph 1; Paragraph 3 extracted as orphan. |
| `KCM-BEH-13` | Decision Making | 2 | 3 | +1 | Title banner `'Logical Reasoning: Sound Judgement'` isolated; 2 descriptions extracted with sentence-fragment titles. |
| `KCM-FUNC-01` | Citizen Centricity | 3 | 4 | +1 | Column 2 description split into 2 fragments. |
| `KCM-FUNC-03` | Cabinet Note Preparation | 2 | 3 | +1 | Title banner `'Rules of Business: Cabinet Note Writing'` isolated; 2 descriptions extracted with sentence-fragment titles. |
| `KCM-FUNC-05` | Project Management | 4 | 5 | +1 | `Project Evaluation` header box separated from body text box. |
| `KCM-FUNC-07` | Material Management (GFR) | 2 | 3 | +1 | Title banner `'Inventory Management: Maintenance and Disposal of materials'` isolated; 2 descriptions extracted with sentence-fragment titles. |
| `KCM-FUNC-10` | Digital Fluency | 2 | 3 | +1 | Title `'Digital: Service Design'` split across lines into separate entry. |
| `KCM-FUNC-21` | Administration Matters | 4 | 5 | +1 | Column 3 (`Leave and Travel`) split from description, creating 5 entries instead of 4. |
| **Total Impact** | | **110** | **118** | **+8** | **Net +8 phantom entries across 11 competencies** |

---

## 3. Findings Grouped by Severity

### Severity 1: High (Data Corruption & Text Fragmentation)

1. **21 out of 34 Competencies Contain Malformed Behaviour Strings:**
   - **Concatenated Sub-Theme Titles:** 16 competencies have entries where 2 to 4 sub-theme titles are glued together without proper separation (e.g., `'Self-Learning Self-Analysis Self Confidence Purposefulness'`, `'Attention to Detail Systems Thinking Analytical Thinking'`).
   - **Sentence-Fragment Pseudo-Titles:** At least 28 behaviour entries have invalid titles formed from the first 5–8 words of a descriptive sentence followed by a colon (e.g., `'Exhibits a commitment to addressing the:'`, `'Displays the quality of:'`, `'Demonstrates a high level of proficiency in conducting the official business:'`).
   - **Orphan Description Blocks:** Descriptions missing their official title because the title was captured in a different column bucket.

### Severity 2: Medium (Document Anomalies from Government Source)

1. **Page 107 Heading Anomaly (`KCM-FUNC-21` Administration Matters):**
   - *Source text:* Page 107 bears the header title `"Change Management Sub-Themes"` (errantly repeated from Page 105).
   - *Actual content:* Details sub-themes for `Administration Matters` (*Allowances & Reimbursements*, *Leave and Travel*, *Miscellaneous matters*, *Implementing Official Language*).
   - *Status:* Confirmed source document publishing error. Must be documented in metadata.
2. **Repeated CSMOP Definition Text (`KCM-FUNC-13`, `14`, `15`):**
   - *Source text:* Page 90 (`Office Management`), Page 92 (`Handling Parliamentary Matters`), and Page 94 (`Handling RTI Matters`) contain the identical 815-character paragraph citing the Central Secretariat Manual of Office Procedures (CSMOP).
   - *Actual content:* Sub-themes on their respective facing pages (Pages 91, 93, 95) are completely distinct and role-specific.
   - *Status:* Confirmed source authoring artifact.
3. **Title Variant on Page 72 (`KCM-FUNC-04`):**
   - Heading on Page 72 reads `"Govt Program Formulation"`, while summary pages 29 and 34 read `"Government Program Formulation"`.
4. **Project Management Sub-Theme Count (Page 30 vs Page 75):**
   - Page 30 lists 3 bullets (`Project Planning`, `Project Implementation`, `Project Evaluation & Monitoring`).
   - Page 75 details 4 distinct columns (`Project Planning`, `Project Implementation`, `Project Evaluation`, `Project KPIs Monitoring`).
5. **Digital Fluency Scope (Page 31 vs Page 85):**
   - Page 31 summary lists 4 items (`Digital Tools & Platforms`, `Digital Service Design`, `AI/ML tools`, `Emerging technology`).
   - Page 85 details 2 multi-paragraph panels (`Digital Tools & Platforms` and `Digital Service Design`).

### Severity 3: Low (Whitespace & Transliteration Typography)

1. **Hyphenated Line-Breaks:** Occasional irregular spacing in extracted text (e.g., `high- quality`, `one- on-one`).
2. **IAST Transliteration Encoding:** All Devanagari and Romanized diacritics (*Svādhyāya*, *Sahakāryatā*, *Rājyakarma*, *Svadharma*, *Guṇas*, *Ātmanirbhar*) are correctly preserved via UTF-8.

---

## 4. Confirmed Issues vs. Unresolved Questions

### Confirmed Issues
1. The 118-count is an artifact of the column-bucketing algorithm in `scripts/extract_kcm.py`, not authentic source data.
2. The verifiable number of sub-themes in the KCM source document is **110** (41 Behavioural + 69 Functional).
3. The KCM does **not** define competency proficiency levels (Level 1–5). `level_information = null` is factually correct.
4. Domain competencies are explicitly outside KCM scope (Pages 4 and 24).
5. All 34 competency names, definitions, and page numbers are accurately paired.

### Unresolved Questions for User Review
1. **Sub-Theme Serialization Format:** Should `behaviours` remain a list of strings (`["Title: Description", ...]`), or should it be structured as an array of objects (`[{"sub_theme": "...", "description": "..."}, ...]`) in JSON while serializing cleanly to CSV?
2. **Project Management Sub-Themes Count:** Should `Project Management` be recorded as 4 sub-themes (as detailed on Page 75) or 3 sub-themes (as summarized on Page 30)? *Recommendation: Use the 4 detailed sub-themes from Page 75.*
3. **Digital Fluency Sub-Themes Count:** Should `Digital Fluency` be recorded as 2 sub-themes (the 2 detailed panels on Page 85) or 4 sub-themes (including AI/ML tools and Emerging Technology from Page 31)? *Recommendation: Use the 2 detailed panels from Page 85, noting the summary items in `extraction_notes`.*

---

## 5. Recommended Corrections (To Be Applied Upon User Approval)

1. **Replace Heuristic Bucketing with Canonical Anchor Matching:**
   Instead of guessing column boundaries with geometric coordinates, `scripts/extract_kcm.py` should match the verified sub-theme titles from the official KCM catalog against the text blocks on each sub-theme page, associating each title with its corresponding body paragraph.
2. **Eliminate All 8 Phantom Entries:**
   Cleanly output the true **110 sub-themes**, ensuring every single behaviour entry starts with its authentic official title.
3. **Update Automated Tests:**
   Add regression assertions verifying that no behaviour entry contains pseudo-titles (e.g., fragments starting with `"Exhibits a"`, `"Demonstrates"`, `"Displays the"`), and that every competency has its exact official sub-theme count.

---

## 6. Regression Test Additions & Test Results

Targeted quality regression tests were added to [`tests/test_kcm_extraction.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/tests/test_kcm_extraction.py) to catch:
- Merged multi-title strings.
- Sentence-fragment pseudo-titles.
- Inaccurate behaviour counts.

Using `@pytest.mark.xfail`, these tests explicitly document and catch the 21 known defects on the current dataset without masking them.

### Test Execution Command
```powershell
python -m pytest -v
```

### Initial Audit Test Output (Pre-Remediation)
```text
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\Projects\SIH26101\SIH26101-Skill-Intelligence
collected 33 items

======================== 30 passed, 3 xfailed in 0.42s ========================
```

---

## 7. Stage 2A.2 Remediation Outcome & Verification

### 7.1. Ground Truth Reconciliation Table

The complete ground truth for all 34 competencies was reconciled across summary pages 25–35 and detailed annexure pages 39–107.

| ID | Competency Name | Type | Source Pages | Sub-Themes Count | Verified Sub-Theme Titles |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `KCM-BEH-01` | Self-Awareness | `behavioural` | [39, 40] | 4 | Self-Learning, Self-Analysis, Self Confidence, Purposefulness |
| `KCM-BEH-02` | Personal Effectiveness | `behavioural` | [41, 42] | 3 | Stress Management, Navigating Ambiguity, Resilience |
| `KCM-BEH-03` | Solution Orientation | `behavioural` | [43, 44] | 3 | Attention to Detail, Systems Thinking, Analytical Thinking |
| `KCM-BEH-04` | Communication | `behavioural` | [45, 46] | 4 | Reading & Comprehension, Active Listening, Verbal & Non-verbal communication, Presentation skills |
| `KCM-BEH-05` | Outcome Orientation | `behavioural` | [47, 48] | 4 | Initiative & Drive, Goal Setting, Accountability, Commitment to Quality |
| `KCM-BEH-06` | Collaboration | `behavioural` | [49, 50] | 3 | Relationship Management, Knowledge Sharing, Diversity & Inclusion |
| `KCM-BEH-07` | Service Orientation | `behavioural` | [51, 52] | 3 | Empathy, Responsiveness, Service Excellence |
| `KCM-BEH-08` | Operational Excellence | `behavioural` | [53, 54] | 4 | Process Excellence, Resource Management, Continuous Improvement, Planning & Prioritization |
| `KCM-BEH-09` | Creativity & Innovation | `behavioural` | [55, 56] | 2 | Lateral Thinking, Transformation Orientation |
| `KCM-BEH-10` | Strategic Leadership | `behavioural` | [57, 58] | 4 | Global Mindset, Forward Thinking, Executive Presence, Sustainable Mindset |
| `KCM-BEH-11` | Collaborative Leadership | `behavioural` | [59, 60] | 2 | Influencing & Negotiation, Conflict Management |
| `KCM-BEH-12` | Team Leadership | `behavioural` | [61, 62] | 3 | Mentoring, Inspiring Others, Sharing Constructive Feedback |
| `KCM-BEH-13` | Decision Making | `behavioural` | [63, 64] | 2 | Logical Reasoning, Sound Judgement |
| `KCM-FUNC-01` | Citizen Centricity | `functional` | [66, 67] | 3 | Design Thinking, Citizen Partnering & Collaboration, Political, Economic, Social, Technological Consciousness |
| `KCM-FUNC-02` | Policy Architecture | `functional` | [68, 69] | 4 | Research & Needs Analysis, Policy Design /Amendment, Policy Implementation, Policy Monitoring & Impact Assessment |
| `KCM-FUNC-03` | Cabinet Note Preparation | `functional` | [70, 71] | 2 | Rules of Business, Cabinet Note Writing |
| `KCM-FUNC-04` | Govt Program Formulation | `functional` | [72, 73] | 4 | Research & Needs Analysis, Scheme / Program Design, Feasibility and Risk Assessment, Implementation & Outreach |
| `KCM-FUNC-05` | Project Management | `functional` | [74, 75] | 4 | Project Planning, Project Implementation, Project Evaluation, Project KPIs Monitoring |
| `KCM-FUNC-06` | Public Procurement (GFR) | `functional` | [76, 77] | 4 | Procurement management through GeM, Procurement of Goods / Services / Works, Contract Management, Vendor / Consultant Management |
| `KCM-FUNC-07` | Material Management (GFR) | `functional` | [78, 79] | 2 | Inventory Management, Maintenance and Disposal of materials |
| `KCM-FUNC-08` | Monitoring & Evaluation | `functional` | [80, 81] | 2 | Creation of M&E Framework, Evaluation and output / outcome |
| `KCM-FUNC-09` | Financial Management | `functional` | [82, 83] | 4 | Budget Formulation & Implementation, PFMS Portal Management, Expenditure Management, Government Accounts |
| `KCM-FUNC-10` | Digital Fluency | `functional` | [84, 85] | 2 | Digital Tools (MS office, Excel & PPT) and Platforms, Digital Service Design |
| `KCM-FUNC-11` | Data Analytics | `functional` | [86, 87] | 4 | Data Management (Clean-up, segregation, processing), Data Analysis & Visualization, Data-led Decision Making, Data Use & Governance |
| `KCM-FUNC-12` | Establishment & HR | `functional` | [88, 89] | 5 | Establishment Matters, Fundamental Rules / Supplementary Rules (FRSR), Reservations, Prevention of Sexual Harassment Policy, Performance Appraisal |
| `KCM-FUNC-13` | Office Management | `functional` | [90, 91] | 5 | E-Office, File/DAK Management, Office Procedures, Noting & Drafting of official Communications, Technical Proposal / Report writing |
| `KCM-FUNC-14` | Handling Parliamentary Matters | `functional` | [92, 93] | 2 | Submission of briefs, supply of information, Maintaining records of parliamentary matters |
| `KCM-FUNC-15` | Handling RTI Matters | `functional` | [94, 95] | 2 | RTI Responsiveness, RTI Records and Report management |
| `KCM-FUNC-16` | Grievance Redressal | `functional` | [96, 97] | 2 | Manage cases on CPGRAMS, Public Grievance Handling |
| `KCM-FUNC-17` | Vigilance Administration | `functional` | [98, 99] | 5 | Conduct Rules, Provisions on Suspension, Proposal preparation for disciplinary proceedings, Handling prosecution cases; supporting investigations, Preventive Vigilance |
| `KCM-FUNC-18` | Litigation Management | `functional` | [100, 101] | 3 | Legal Know-how: Basic Knowledge of Legal drafting, Court Cases Management, LIMBS Portal Management |
| `KCM-FUNC-19` | Information & Communication Management | `functional` | [102, 103] | 3 | Dissemination of Information, Handling social media (engagement), Management of information on official websites |
| `KCM-FUNC-20` | Change Management | `functional` | [104, 105] | 3 | Change Readiness, Accepting Change, Implementing Change |
| `KCM-FUNC-21` | Administration Matters | `functional` | [106, 107] | 4 | Allowances & Reimbursements, Leave and Travel, Miscellaneous matters (Telephone, Car, Residence, Personal Staff etc.), Implementing Official Language |
| **Total** | **34 Competencies** | | | **110** | **41 Behavioural + 69 Functional Sub-Themes** |

### 7.2. Algorithm Remediation Details

In `scripts/extract_kcm.py`, `parse_subthemes_for_page()` was redesigned around the typographic and structural reality of the source PDF:
1. **Typography-Driven Text Classification:**
   - InDesign renders sub-theme titles in `SamsungSharpSans-Bold` with font sizes $\ge 30\,\text{pt}$ (typically $35.2$ to $49.9\,\text{pt}$).
   - Indicator prose is rendered in `SamsungSharpSans-Medium` with font sizes $\le 32\,\text{pt}$ (typically $18.5$ to $28.9\,\text{pt}$).
   - Running headers and page counters ($y < 300\,\text{pt}$) are excluded.
2. **Left-Margin Column Grouping ($x_0$):**
   - Title lines sharing the same left margin within $35\,\text{pt}$ are merged top-to-bottom into complete multi-line titles, resolving split titles (e.g., `'Reading &'` + `'Comprehension'` $\rightarrow$ `'Reading & Comprehension'`).
   - Title columns are ordered left-to-right.
3. **Horizontal Center Association:**
   - Each descriptive body line is assigned to its nearest title column based on horizontal centroid distance.
   - Zero sentences are chopped into pseudo-titles. Zero descriptions are lost.

### 7.3. Verified Post-Remediation Counts & Test Execution

Following pipeline execution (`python scripts/extract_kcm.py`), all 37 automated tests passed cleanly without any expected failures (`xfail`):

```powershell
python -m pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\Projects\SIH26101\SIH26101-Skill-Intelligence
plugins: anyio-4.13.0
collected 37 items

tests/test_kcm_extraction.py::test_processed_files_exist PASSED          [  2%]
tests/test_kcm_extraction.py::test_record_counts_consistency PASSED      [  5%]
tests/test_kcm_extraction.py::test_unique_competency_ids PASSED          [  8%]
tests/test_kcm_extraction.py::test_required_fields_present_in_all_records PASSED [ 10%]
tests/test_kcm_extraction.py::test_allowed_competency_types PASSED       [ 13%]
tests/test_kcm_extraction.py::test_non_empty_names_and_definitions PASSED [ 16%]
tests/test_kcm_extraction.py::test_valid_source_id_and_provenance PASSED [ 18%]
tests/test_kcm_extraction.py::test_valid_page_numbers PASSED             [ 21%]
tests/test_kcm_extraction.py::test_no_fabricated_competency_levels PASSED [ 24%]
tests/test_kcm_extraction.py::test_behaviours_structure_and_non_empty PASSED [ 27%]
tests/test_kcm_extraction.py::test_json_and_csv_field_value_consistency PASSED [ 29%]
tests/test_kcm_extraction.py::test_notes_documentation_contents PASSED   [ 32%]
tests/test_kcm_extraction.py::test_no_sentence_fragment_pseudo_titles PASSED [ 35%]
tests/test_kcm_extraction.py::test_no_concatenated_multi_titles PASSED   [ 37%]
tests/test_kcm_extraction.py::test_exact_official_subtheme_counts PASSED [ 40%]
tests/test_kcm_extraction.py::test_subtheme_titles_and_descriptions_against_reconciliation_fixture PASSED [ 43%]
tests/test_kcm_extraction.py::test_project_management_subtheme_fidelity PASSED [ 45%]
tests/test_kcm_extraction.py::test_page_107_administration_matters_fidelity PASSED [ 48%]
tests/test_kcm_extraction.py::test_csmop_repeated_definition_fidelity PASSED [ 51%]
tests/test_pdf_extractor.py::test_pdf_discovery PASSED                   [ 54%]
tests/test_pdf_extractor.py::test_page_number_preservation PASSED        [ 56%]
tests/test_pdf_extractor.py::test_text_extraction_fidelity PASSED        [ 59%]
tests/test_pdf_extractor.py::test_empty_page_detection PASSED            [ 62%]
tests/test_pdf_extractor.py::test_low_text_density_detection PASSED      [ 64%]
tests/test_pdf_extractor.py::test_missing_file_handling PASSED           [ 67%]
tests/test_pdf_extractor.py::test_corrupted_file_handling PASSED         [ 70%]
tests/test_pdf_extractor.py::test_batch_extraction_and_reporting PASSED  [ 72%]
tests/test_pdf_extractor.py::test_repeatable_output PASSED               [ 75%]
tests/test_pdf_extractor.py::test_sanitize_filename_to_id PASSED         [ 78%]
tests/test_source_register.py::test_initial_source_register_validity PASSED [ 81%]
tests/test_source_register.py::test_missing_mandatory_field PASSED       [ 83%]
tests/test_source_register.py::test_invalid_provenance_classification PASSED [ 86%]
tests/test_source_register.py::test_invalid_extraction_status PASSED     [ 89%]
tests/test_source_register.py::test_invalid_source_id_format PASSED      [ 91%]
tests/test_source_register.py::test_duplicate_source_id_detection PASSED [ 94%]
tests/test_source_register.py::test_save_and_load_roundtrip PASSED       [ 97%]
tests/test_source_register.py::test_live_source_register_file_if_present PASSED [100%]

============================= 37 passed in 0.34s ==============================
```
