# MoSPI ACBP to KCM Competency Mapping: Adjudication Readiness Report (Stage 3.4.2 / 3.4.3)

> [!IMPORTANT]
> **Readiness Status**: **READY FOR EXPERT TRIAGE — PENDING EXTERNAL EVIDENCE REQUISITION**  
> **Key Finding**: The 26-case pilot benchmark is fully packaged, structured, and auditable for expert human review. **No benchmark case has been marked as human-validated or assigned an automated ground truth label.**  
> **Primary Deliverables**:  
> - Machine-Readable Adjudication Packet (JSON): [`data/interim/mapping_adjudication_packet.json`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_adjudication_packet.json)  
> - Tabular Adjudication Packet (CSV): [`data/interim/mapping_adjudication_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_adjudication_packet.csv)  
> - Deterministic Packet Builder Script: [`scripts/build_adjudication_packet.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/scripts/build_adjudication_packet.py)  
> - Automated Test Suite: [`tests/test_adjudication_packet.py`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/tests/test_adjudication_packet.py)  
> - Reviewer Adjudication Guide: [`docs/mapping_adjudication_guide.md`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/mapping_adjudication_guide.md)

---

## 1. Executive Summary & Readiness Verdict

Stage 3.4.2 prepares the comprehensive human-adjudication package for the 26-case MoSPI ACBP to KCM competency-mapping benchmark. 

The primary goal of this stage is to make human expert review **transparent, reproducible, evidence-based, and operationally safe**. It enforces complete segregation between heuristic triage recommendations and binding human decisions.

```
======================================================================
STAGE 3.4.2 ADJUDICATION READINESS VERDICT: READY FOR EXPERT TRIAGE
======================================================================
Total Benchmark Cases: 26
  - Structured Adjudication Cards Built: 26 / 26 (100.0%)
  - Blank Human Review Fields Preserved: 26 / 26 (100.0%)
  - Human Review Status: 'pending_review' (26 / 26)
  - Evaluated Against 6-Question Framework: 26 / 26 (100.0%)
  - Exact-Course Verified Locally: 0 / 26 (0.0%)
  - Blocked for Ground Truth Certification Pending Syllabi: 26 / 26 (100.0%)
======================================================================
```

### Critical Declarations:
1. **Zero Human Decisions Fabricated**: All reviewer fields (`adjudicated_label`, `reviewer_id`, `adjudication_date`, `reviewer_rationale`, `confidence_rating`) remain strictly `null` across all 26 cases.
2. **Production Registry Untouched**: The 226-record production mapping registry ([`data/processed/acbp_kcm_mappings.json`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/processed/acbp_kcm_mappings.json)) remains completely unmodified. Zero candidates have been promoted to `validated`.
3. **No Private Portal Access Claimed**: The platform honestly documents that 9 courses are access-restricted behind civil service Parichay single sign-on (SSO) on iGOT Karmayogi.

---

## 2. Benchmark Case Categorization & Triage Readiness

To organize expert panel time efficiently, all 26 benchmark cases are categorized into three operational readiness tiers:

```mermaid
pie title Benchmark Case Operational Triage Breakdown (N = 26)
    "Ready for Standard Expert Triage (Strata A, B, C, E)" : 21
    "Requiring Specialist Official-Statistics SME Panel (Strata D)" : 5
```

### Category 1: Ready for Expert Human Triage (26 / 26 Cases)
- **Status**: Every case possesses a complete machine-readable adjudication card containing:
  - Exact ACBP course title, cadre, duration, and provider.
  - Verbatim excerpt from official institutional documentation.
  - Analysis under the 6-question adjudication process.
  - Candidate KCM definition and sub-theme behavioral indicators (where applicable).
  - Counter-evidence, known limitations, and alternative competency candidates.
  - Targeted questions requiring SME judgment.
- **Action**: Evaluators can immediately commence preliminary scoring, confidence rating, and identification of required evidence.

### Category 2: Blocked for Final Ground-Truth Certification (26 / 26 Cases)
- **Status**: While all 26 cases have authentic institutional or portal evidence, **zero cases** possess a downloaded, lesson-by-lesson syllabus for the exact micro-course locally.
  - 12 cases rely on related apex institutional curricula (ISTM, NSSTA, AJ-NIFM, MDNIY).
  - 9 cases are hosted on iGOT Karmayogi behind Parichay SSO.
  - 5 cases rely on high-level institutional frameworks or training calendar rows.
- **Action**: Final `supported_mapping` ground-truth certification must be withheld until formal data requisitions provide granular lesson plans.

### Category 3: Requiring Specialist Official-Statistics Domain Judgment (5 Cases)
Cases in Strata D require review by senior official statisticians and NSSTA faculty to resolve the boundary between generic central civil service competencies and specialist official statistical knowledge:

| Case ID | Course Record ID | Cadre | Exact Course Title | Current ACBP Category | Target Evaluation Issue |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BM-CASE-020** | `ACBP-CRS-001` | DDG / JS+ | Introduction to Big Data in Governance | Domain | Reconcile ACBP "Domain" category with provider NeGD (MeitY); evaluate alignment with `KCM-FUNC-10` (*Digital Fluency*) or `KCM-FUNC-11` (*Data Analytics*). |
| **BM-CASE-021** | `ACBP-CRS-046` | Director / JD | Know Your Ministry Ministry of Statistics and Programme Implementation | Domain | Confirm whether ministry institutional machinery represents an official statistics Domain gap vs `KCM-FUNC-21` (*Administration Matters*). |
| **BM-CASE-022** | `ACBP-CRS-067` | DS / US | Handling Unit Level Data of Household Consumption Expenditure Survey (HCES) | Domain | Evaluate whether microdata manipulation overlaps with `KCM-FUNC-11` (*Data Analytics*) vs specialist survey sampling weights constituting a pure Domain gap. |
| **BM-CASE-023** | `ACBP-CRS-069` | DS / US | Handling Unit Level Data of Annual Survey of Industries (ASI) | Domain | Evaluate economic data tabulation against `KCM-FUNC-11` (*Data Analytics*) vs enterprise sampling framework representing a Domain gap. |
| **BM-CASE-024** | `ACBP-CRS-072` | DS / US | Introduction to R and Python Programming_ | Domain | Reconcile ACBP "Domain" classification with generic data science programming competencies under `KCM-FUNC-11` (*Data Analytics*) and `KCM-FUNC-10` (*Digital Fluency*). |

---

## 3. Case-by-Case Triage Guidance & Evidence Breakdown

### Strata A: Title-Reference Candidates (n = 6)
*Existing candidate mappings in the production registry requiring verification against instructional reality.*

| Case ID | Course Name | Cadre | Duration | Provider | Current Evidence Status | Proposed KCM ID | Triage Guidance Label | Key SME Question |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BM-CASE-001** | Leading with Collaboration: Sahakaryata _in Public_Service | DDG / JS+ | 01.00.44 | CBC | `access_restricted` | `KCM-BEH-06` | `plausible_insufficient_evidence` | Does a 1-hour module develop observable behavioral collaboration for apex officers? |
| **BM-CASE-002** | Leadership in Project Management | Director / JD | 00.17.58 | ATI Mysuru | `possible_match_needs_verification` | `KCM-FUNC-05` | `plausible_insufficient_evidence` | Can an 18-minute micro-module impart technical project management competency? |
| **BM-CASE-003** | Strategic Leadership: The Indic_ Way | Director / JD | 01.09.28 | CBC | `possible_match_needs_verification` | `KCM-BEH-10` | `plausible_insufficient_evidence` | Does Indic statecraft satisfy modern bureaucratic metrics of strategic leadership? |
| **BM-CASE-004** | Leading with Collaboration: Sahakaryata _in Public Service | Director / JD | 01.00.44 | CBC | `access_restricted` | `KCM-BEH-06` | `plausible_insufficient_evidence` | Does Director-level delivery differ from apex delivery? |
| **BM-CASE-005** | Strategic Leadership: _The_Indic_ Way | DS / US | 01.09.28 | CBC | `possible_match_needs_verification` | `KCM-BEH-10` | `plausible_insufficient_evidence` | Is Strategic Leadership appropriate for middle management operational roles? |
| **BM-CASE-006** | Leading with Collaboration: Sahakaryata in Public_Service_ | DS / US | 01.00.44 | CBC | `access_restricted` | `KCM-BEH-06` | `plausible_insufficient_evidence` | Should identical digital assets across cadres receive differentiated proficiency ratings? |

---

### Strata B: Behavioural Unresolved (n = 6)
*ACBP Behavioural courses currently unmapped in the production registry.*

| Case ID | Course Name | Cadre | Duration | Provider | Current Evidence Status | Candidate KCM Options | Triage Guidance Label | Key SME Question |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BM-CASE-007** | Developing a Positive Work Culture | DDG / JS+ | 00.41.24 | DoPT / iGOT | `access_restricted` | `KCM-BEH-06` / `08` | `unresolved_insufficient_source` | Does this course teach specific behavioral indicators under Collaboration or broad OD concepts? |
| **BM-CASE-008** | Yoga Break at Workplace | Director / JD | 00.05.00 | Ministry of Ayush / MDNIY | `official_related_material` | `no_applicable_kcm_competency` vs `KCM-BEH-01` | `unresolved_insufficient_source` | Should 5-minute workplace physical health/wellness interventions be designated outside KCM scope? |
| **BM-CASE-009** | Happiness in Seva-Bhava: Lessons from Bhagavad-Gita | Director / JD | 00.32.18 | CBC / iGOT | `access_restricted` | `KCM-BEH-07` / `KCM-BEH-01` | `unresolved_insufficient_source` | Does philosophical Seva-Bhava map to behavioural Service Orientation or functional Citizen Centricity? |
| **BM-CASE-010** | Leading from Within: Behavioural Strategies for Self-Leadership | Director / JD | 00.48.00 | iGOT | `access_restricted` | `KCM-BEH-01` / `02` | `unresolved_insufficient_source` | Does 'Leading from Within' map primarily to Self-Awareness or Personal Effectiveness? |
| **BM-CASE-011** | The Art of Listening | SSO / SO | 00.28.00 | iGOT | `access_restricted` | `KCM-BEH-04` / `06` | `unresolved_insufficient_source` | Can a 28-minute module on listening be certified as developing full Communication competency? |
| **BM-CASE-012** | Revisiting Gender Equality through the Indian Spiritual Vision | JSO / ASO | 00.45.00 | CBC / iGOT | `access_restricted` | `KCM-BEH-06` (Diversity & Inclusion) | `unresolved_insufficient_source` | Does this course map to behavioural Collaboration (Diversity & Inclusion) or functional HR rules? |

---

### Strata C: Functional Unresolved (n = 7)
*ACBP Functional courses with strong topical matches to core central civil service competencies.*

| Case ID | Course Name | Cadre | Duration | Provider | Current Evidence Status | Primary Target KCM ID | Triage Guidance Label | Key SME Question |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BM-CASE-013** | Conduct of Inquiry in Disciplinary Matters | DDG / JS+ | 01.15.00 | ISTM | `official_related_material` | `KCM-FUNC-17` | `plausible_insufficient_evidence` | Does a 75-minute module qualify an officer for Vigilance Administration (KCM-FUNC-17)? |
| **BM-CASE-014** | Fundamentals of Public Policy | DDG / JS+ | 01.30.00 | DoPT / CBC | `possible_match_needs_verification` | `KCM-FUNC-02` | `plausible_insufficient_evidence` | Does this course develop strategic Policy Architecture (FUNC-02) or Govt Program Formulation (FUNC-04)? |
| **BM-CASE-015** | Project A ppraisal and Financial Evaluation Techniques | DDG / JS+ | 01.45.00 | AJ-NIFM | `official_related_material` | `KCM-FUNC-09` / `05` | `plausible_insufficient_evidence` | Is the primary competency Financial Management (FUNC-09) or Project Management (FUNC-05)? |
| **BM-CASE-016** | Navigating Parliamentary Questions | DDG / JS+ | 00.45.00 | Lok Sabha / NSSTA | `official_related_material` | `KCM-FUNC-14` | `plausible_insufficient_evidence` | Can a 45-minute orientation certify competency in handling high-stakes Parliamentary Questions? |
| **BM-CASE-017** | Procurement of Works | DS / US | 01.00.00 | GeM / AJ-NIFM | `official_related_material` | `KCM-FUNC-06` | `plausible_insufficient_evidence` | Does works procurement map cleanly to Public Procurement (GFR) or require civil works competency? |
| **BM-CASE-018** | FRSR Part [ General Rules | DS / US | 01.30.00 | ISTM | `official_related_material` | `KCM-FUNC-12` / `21` | `plausible_insufficient_evidence` | Should FRSR general rules be mapped to Establishment & HR (FUNC-12) or Administration Matters (FUNC-21)? |
| **BM-CASE-019** | AI for Presentations | DS / US | 00.35.00 | iGOT | `access_restricted` | `KCM-FUNC-10` | `plausible_insufficient_evidence` | Is an AI presentation tool course a legitimate civil service competency under Digital Fluency? |

---

### Strata D: Domain Statistical Gap (n = 5)
*Specialist statistical and e-governance courses requiring domain gap resolution.*

| Case ID | Course Name | Cadre | Duration | Provider | Current Evidence Status | Target Evaluation Options | Triage Guidance Label | Key SME Question |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BM-CASE-020** | Introduction to Big Data in Governance | DDG / JS+ | 00.46.21 | NeGD | `possible_match_needs_verification` | `KCM-FUNC-10` / `11` | `plausible_insufficient_evidence` | Why was generic Big Data classified as Domain in ACBP? Does it map to KCM-FUNC-10 or FUNC-11? |
| **BM-CASE-021** | Know Your Ministry Ministry of Statistics and Programme Implementation | Director / JD | 00.45.00 | MoSPI / NSSTA | `official_related_material` | Domain Gap vs `KCM-FUNC-21` | `unresolved_insufficient_source` | Does ministry induction represent an official statistics Domain gap or generic Administration Matters? |
| **BM-CASE-022** | Handling Unit Level Data of HCES | DS / US | 02.00.00 | NSSTA | `official_related_material` | `KCM-FUNC-11` vs Gap | `unresolved_insufficient_source` | Map HCES microdata handling to Data Analytics (`KCM-FUNC-11`) or Domain gap? |
| **BM-CASE-023** | Handling Unit Level Data of ASI | DS / US | 02.00.00 | NSSTA | `official_related_material` | `KCM-FUNC-11` vs Gap | `unresolved_insufficient_source` | Map ASI enterprise analysis to Data Analytics or Domain gap? |
| **BM-CASE-024** | Introduction to R and Python Programming_ | DS / US | 02.00.00 | NSSTA | `official_related_material` | `KCM-FUNC-11` / `10` | `plausible_insufficient_evidence` | Should Python/R statistical programming be mapped to Data Analytics despite Domain classification? |

---

### Strata E: Cross-Cadre Contrast (n = 2)
*Contrasting supervisory vs clerical delivery of the identical course title.*

| Case ID | Course Name | Cadre | Duration | Provider | Current Evidence Status | Target KCM ID | Triage Guidance Label | Key SME Question |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BM-CASE-025** | Noting and Drafting | SSO / SO | 01.30.00 | ISTM | `official_related_material` | `KCM-FUNC-13` | `plausible_insufficient_evidence` | Does syllabus assess intermediate/advanced noting for Section Officers? |
| **BM-CASE-026** | Noting and Drafting | UDC / LDC / Assistants | 01.00.00 | ISTM | `official_related_material` | `KCM-FUNC-13` | `plausible_insufficient_evidence` | Does 1-hour session target foundational operational proficiency (Level 1)? |

---

## 4. Formal Data Requisition Roadmap

To enable final human adjudication and move from preliminary triage to ground-truth certification, three formal data requisitions are required:

1. **Requisition 1: Capacity Building Commission (CBC) & iGOT Portal Team**:
   - Request: Lesson-level session outlines, video transcripts, and formative assessment rubrics for the 9 access-restricted courses (`BM-CASE-001`, `004`, `006`, `007`, `009`, `010`, `011`, `012`, `019`).
2. **Requisition 2: National Statistical Systems Training Academy (NSSTA)**:
   - Request: Official module outlines for HCES (`BM-CASE-022`), ASI (`BM-CASE-023`), Know Your Ministry (`BM-CASE-021`), and Python/R (`BM-CASE-024`), with specific faculty guidance on whether microdata extraction maps to `KCM-FUNC-11` (*Data Analytics*).
3. **Requisition 3: Institute of Secretariat Training and Management (ISTM)**:
   - Request: Differentiated syllabus documents for Noting & Drafting across Supervisory (`BM-CASE-025`) and Clerical (`BM-CASE-026`) cadres.

---

## 5. Conclusion & Operational Status

The Human Adjudication Pack for Stage 3.4.2 is complete, verified, and ready for deployment. The evaluation platform guarantees that no automated label will overwrite human review, ensuring total fidelity to Mission Karmayogi's competency standards.
