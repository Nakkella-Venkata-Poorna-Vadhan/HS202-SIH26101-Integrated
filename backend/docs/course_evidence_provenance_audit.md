# MoSPI ACBP to KCM Competency Mapping: Evidence Provenance & Claim Audit (Stage 3.4.1)

> [!IMPORTANT]
> **Audit Status**: COMPLETED (Stage 3.4.1)  
> **Audit Verdict**: **EVIDENCE AUDIT PASSED WITH LIMITATIONS**  
> **Primary Deliverables**:  
> - Machine-Readable Provenance Audit: [`data/interim/course_evidence_provenance_audit.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/course_evidence_provenance_audit.json)  
> - Automated Regression Test Suite: [`tests/test_evidence_provenance_audit.py`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/tests/test_evidence_provenance_audit.py)  
> **Audited Baseline Artifacts**:  
> - Stage 3.4 Report: [`docs/course_evidence_acquisition_report.md`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/course_evidence_acquisition_report.md)  
> - Stage 3.4 Ledger: [`data/interim/course_evidence_ledger.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/course_evidence_ledger.json) & [`.csv`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/course_evidence_ledger.csv)

---

## 1. Executive Summary & Audit Verdict

Stage 3.4.1 independently audits the evidence acquired and claims asserted in the Stage 3.4 Course Evidence Acquisition Report.

The audit evaluated all 26 pilot benchmark cases across four critical criteria:
1. **Physical Presence & Provenance**: Whether the cited source documents physically exist locally in the repository or are external references.
2. **Curricular Granularity**: Whether an excerpt represents an exact iGOT course syllabus, a multi-day classroom curriculum, or general statutory/administrative reference material.
3. **Competency Inference Rigor**: Whether evidence demonstrating that a course *touches a subject* proves that it *develops a specific KCM competency to the degree asserted*.
4. **Domain-Gap Validity**: Whether official statistics survey courses (HCES, ASI) can be definitively declared unmapped without considering conceptual overlap with generic data analytics (`KCM-FUNC-11`).

```
======================================================================
STAGE 3.4.1 AUDIT VERDICT: EVIDENCE AUDIT PASSED WITH LIMITATIONS
======================================================================
Audit Classification Breakdown (N = 26 Cases):
  1. exact_course_verified: 0 / 26 (0.0%)
     [No exact iGOT session plans are mirrored locally in the repository]
  2. official_related_material: 12 / 26 (46.2%)
     [Authentic apex institute curricula/manuals covering the topic]
  3. possible_match_needs_verification: 5 / 26 (19.2%)
     [Institutional frameworks or calendar topics requiring lesson plan check]
  4. access_restricted: 9 / 26 (34.6%)
     [Hosted on iGOT Karmayogi behind Parichay SSO]
  5. not_found_publicly: 0 / 26 (0.0%)
======================================================================
```

### Key Audit Findings & Necessary Limitations:
1. **Reclassification of "Official Evidence Found"**:
   - Stage 3.4 categorized 12 cases as `official_evidence_found`. The audit establishes that none of these 12 cases possess a downloaded, lesson-by-lesson syllabus for the *exact iGOT video course* locally.
   - Rather, they represent **`official_related_material`**—authoritative curricula from apex academies (ISTM, NSSTA, AJ-NIFM, MDNIY) covering the substantive domain.
   - **Crucial Limitation**: A 3-day ISTM classroom syllabus on disciplinary inquiry or GFR procurement proves subject matter relevance, but does not prove that a 45-minute or 75-minute iGOT video imparts full civil service competency.
2. **Refinement of the Domain-Gap Conclusion**:
   - Stage 3.4 asserted that the NSSTA survey manuals for HCES (`BM-CASE-022`) and ASI (`BM-CASE-023`) provided "irrefutable proof of no applicable KCM competency."
   - The audit finds this conclusion **overstated**. While official statistics sampling methodology is absent from KCM, microdata extraction, cleaning, and tabulation share conceptual overlap with `KCM-FUNC-11` (*Data Analytics*).
   - **Corrected Standard**: The domain gap must be classified as **`potential_domain_gap_requires_adjudication`**. It cannot be treated as an automated zero-match without human expert review from NSSTA.
3. **100% Referential Validity of KCM Competency IDs**:
   - All 18 KCM competency IDs and verbatim names cited across the reports were independently cross-referenced against `data/processed/competencies_kcm.json` and verified with 100% accuracy.

---

## 2. Reclassified Evidence Taxonomy

To ensure scientific integrity and eliminate ambiguity, evidence is classified using five mutually exclusive statuses:

| Status | Rigorous Definition | Current Case Count |
| :--- | :--- | :---: |
| **`exact_course_verified`** | The complete syllabus, lesson plan, and stated learning competencies for the *exact course title and duration* are physically mirrored in the local repository. | **0 / 26** |
| **`official_related_material`** | Authoritative publication, training manual, or classroom curriculum from the listed apex institute covering the course topic, but not the specific iGOT micro-course. | **12 / 26** |
| **`possible_match_needs_verification`** | High-level institutional framework, executive module mention, or training calendar row that matches the topic but lacks granular session outlines. | **5 / 26** |
| **`access_restricted`** | Course is hosted on `portal.igotkarmayogi.gov.in` behind civil service Parichay single sign-on (SSO) and lacks public unauthenticated access. | **9 / 26** |
| **`not_found_publicly`** | No authentic government documentation or provider reference could be identified. | **0 / 26** |

---

## 3. Case-by-Case Provenance & Claim Audit (All 26 Cases)

### Strata A: The Six Title-Reference Candidates (n = 6)

| Case ID | Course Record ID | Cadre | Course Name | Ledger Status | Audit Status | Local Presence | Verified Finding & Claim Reconciliation |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **BM-CASE-001** | `ACBP-CRS-017` | DDG / JS+ | Leading with Collaboration: Sahakaryata in Public Service | `access_restricted` | `access_restricted` | No | Inaccessible behind Parichay SSO. High-level CBC collaborative governance mandate is verified, but exact 1h 00m session plan is unverified locally. Claim of relevance to `KCM-BEH-06` remains plausible but unproven. |
| **BM-CASE-002** | `ACBP-CRS-036` | Director / JD | Leadership in Project Management | `possible_match_needs_verification` | `possible_match_needs_verification` | No | ATI Mysuru leadership materials cover general project leadership. However, the 17m 58s iGOT module is unmirrored. An 18-minute module cannot be inferred to impart technical `KCM-FUNC-05` (Project Management) without inspecting the video outline. |
| **BM-CASE-003** | `ACBP-CRS-040` | Director / JD | Strategic Leadership: The Indic Way | `possible_match_needs_verification` | `possible_match_needs_verification` | No | CBC Indic Leadership framework verified via IIM Calcutta public collaboration. However, specific session outline (01.09.28) is behind SSO. Relevance to `KCM-BEH-10` is plausible, but lesson plan is required. |
| **BM-CASE-004** | `ACBP-CRS-041` | Director / JD | Leading with Collaboration: Sahakaryata in Public Service | `access_restricted` | `access_restricted` | No | Same CBC course as Case 001. Cadre-specific variations unverified. |
| **BM-CASE-005** | `ACBP-CRS-060` | DS / US | Strategic Leadership: The Indic Way | `possible_match_needs_verification` | `possible_match_needs_verification` | No | Middle-management cadre delivery of the Indic Way series. Lesson plan restricted. |
| **BM-CASE-006** | `ACBP-CRS-061` | DS / US | Leading with Collaboration: Sahakaryata in Public Service | `access_restricted` | `access_restricted` | No | Same CBC course for Deputy Secretary cadre. Inaccessible behind SSO. |

---

### Strata B: Unresolved Behavioural Courses (n = 6)

- **`BM-CASE-007` (`ACBP-CRS-014`) — Developing a Positive Work Culture (DoPT/iGOT)**:
  - **Audit Status**: `access_restricted`.
  - **Audit Finding**: Inaccessible behind Parichay SSO. Highly repeated title (11 cadres). Stage 3.4 correctly retained conservative stance.
- **`BM-CASE-008` (`ACBP-CRS-022`) — Yoga Break at Workplace (Ministry of Ayush / MDNIY)**:
  - **Audit Status**: **`official_related_material`** *(Reclassified from official_evidence_found)*.
  - **Audit Finding**: The Ayush Y-Break protocol is an authentic government public health guideline (5–12 minute desk exercise routine comprising Tadasana, Pranayama, and Dhyana). However, it is an ergonomics/wellness physical intervention, not a competency curriculum. It does not map to any of the 34 KCM civil service competencies.
- **`BM-CASE-009` (`ACBP-CRS-023`) — Happiness in Seva-Bhava (CBC)**:
  - **Audit Status**: `access_restricted`. Conceptually relates to `KCM-BEH-07` (*Service Orientation*), but 32m lesson plan is unmirrored.
- **`BM-CASE-010` (`ACBP-CRS-043`) — Leading from Within (iGOT)**:
  - **Audit Status**: `access_restricted`. Lesson plan on self-awareness (`KCM-BEH-01`) is unmirrored.
- **`BM-CASE-011` (`ACBP-CRS-125`) — The Art of Listening (iGOT)**:
  - **Audit Status**: `access_restricted`. 28-minute module on communication (`KCM-BEH-04`) unmirrored.
- **`BM-CASE-012` (`ACBP-CRS-142`) — Revisiting Gender Equality (CBC)**:
  - **Audit Status**: `access_restricted`. Lesson plan unmirrored.

---

### Strata C: Unresolved Functional Courses (n = 7)

- **`BM-CASE-013` (`ACBP-CRS-008`) — Conduct of Inquiry in Disciplinary Matters (ISTM)**:
  - **Audit Status**: **`official_related_material`** *(Reclassified from official_evidence_found)*.
  - **Competency Claim Audited**: `KCM-FUNC-17` (*Vigilance Administration*) & `KCM-FUNC-21` (*Administration Matters*).
  - **Audit Finding**: ISTM course circular CIDM covers CCS (CCA) Rules 1965, examination of witnesses, and inquiry reports. This establishes that the *subject matter* relates to `KCM-FUNC-17`. However, ISTM CIDM is a 3-to-5 day classroom programme, whereas ACBP course is a 1h 15m video lecture. The evidence proves subject alignment, but does not prove the 75m video develops the full competency.
- **`BM-CASE-014` (`ACBP-CRS-010`) — Fundamentals of Public Policy (DoPT/CBC)**:
  - **Audit Status**: `possible_match_needs_verification`. High-level policy cycle materials exist, but 90m iGOT module outline is unmirrored.
- **`BM-CASE-015` (`ACBP-CRS-011`) — Project Appraisal & Financial Evaluation (AJ-NIFM)**:
  - **Audit Status**: **`official_related_material`** *(Reclassified from official_evidence_found)*.
  - **Competency Claim Audited**: `KCM-FUNC-09` (*Financial Management*) & `KCM-FUNC-05` (*Project Management*).
  - **Audit Finding**: AJ-NIFM MDP curriculum on project appraisal (NPV, IRR, GFR guidelines) verified. Proves subject matter relevance, but 105m iGOT module remains unmirrored locally.
- **`BM-CASE-016` (`ACBP-CRS-013`) — Navigating Parliamentary Questions (PRIDE / Lok Sabha)**:
  - **Audit Status**: **`official_related_material`** *(Reclassified from official_evidence_found)*.
  - **Competency Claim Audited**: `KCM-FUNC-14` (*Handling Parliamentary Matters*).
  - **Local Presence**: Documented in local primary file `SRC-NSSTA-TRG-CAL-2025-26.json` (Page 7) and Lok Sabha PRIDE manual. High confidence of subject alignment; 45m iGOT module is an executive briefing.
- **`BM-CASE-017` (`ACBP-CRS-053`) — Procurement of Works (GeM / AJ-NIFM)**:
  - **Audit Status**: **`official_related_material`** *(Reclassified from official_evidence_found)*.
  - **Competency Claim Audited**: `KCM-FUNC-06` (*Public Procurement - GFR*).
  - **Audit Finding**: GFR 2017 Rules 130-141 and AJ-NIFM procurement manuals cover EPC works. Proves subject matter is public procurement, but 1h iGOT module outline is unmirrored.
- **`BM-CASE-018` (`ACBP-CRS-055`) — FRSR Part [ General Rules (ISTM)**:
  - **Audit Status**: **`official_related_material`** *(Reclassified from official_evidence_found)*.
  - **Competency Claim Audited**: `KCM-FUNC-12` (*Establishment & HR*) & `KCM-FUNC-21` (*Administration Matters*).
  - **Audit Finding**: ISTM statutory curriculum covers Fundamental Rules 1-130. Proves subject relevance, but 90m module outline is unmirrored.
- **`BM-CASE-019` (`ACBP-CRS-057`) — AI for Presentations (iGOT)**:
  - **Audit Status**: `access_restricted`. 35m module restricted behind SSO.

---

### Strata D: MoSPI Domain Official Statistics Gaps (n = 5)

- **`BM-CASE-020` (`ACBP-CRS-001`) — Introduction to Big Data in Governance (NeGD/MeitY)**:
  - **Audit Status**: `possible_match_needs_verification`. NeGD data governance materials exist. Cannot be declared a domain gap without inspecting lesson plan to see if it teaches generic data analytics (`KCM-FUNC-11`).
- **`BM-CASE-021` (`ACBP-CRS-046`) — Know Your Ministry MoSPI**:
  - **Audit Status**: **`official_related_material`**. Local primary source `SRC-MOSPI-AR-2023-24.json` verifies ministry mandate. Represents administrative domain orientation.
- **`BM-CASE-022` (`ACBP-CRS-067`) — Handling Unit Level Data of HCES (NSSTA/MoSPI)**:
  - **Audit Status**: **`official_related_material`**.
  - **Audit of Domain-Gap Claim**:
    - **Stage 3.4 Claim**: *"Irrefutable proof of no_applicable_kcm_competency."*
    - **Stage 3.4.1 Audit Evaluation**: NSSTA training manuals and MoSPI factsheets confirm that the course covers NSS Schedule 1.0, multi-stage stratified sampling multipliers, and MPCE calculation.
    - **Overlapping Competency Identified**: `KCM-FUNC-11` (**Data Analytics**): *"Ability to collect, clean, integrate, analyze, and visualize data to generate actionable insights."* Handling unit-level microdata requires data extraction, variable transformations, and analytical tabulation using tools like STATA/R/Python.
    - **Audit Finding**: While the *survey framework* (sampling design, consumer expenditure schedules) is an official statistics domain subject, the *technical skill* overlaps with applied data analytics.
    - **Verdict on Claim**: The claim of "irrefutable zero-match" is **unsupported**. The case must be classified as **`potential_domain_gap_requires_adjudication`**. It requires expert curriculum review at NSSTA to decide whether domain specificity overrides applied analytical overlap.
- **`BM-CASE-023` (`ACBP-CRS-069`) — Handling Unit Level Data of ASI (NSSTA/MoSPI)**:
  - **Audit Status**: **`official_related_material`**.
  - **Audit Finding**: ASI Schedule manuals confirm industrial statistics methodology (NIC-2008, Net Value Added). Overlaps conceptually with `KCM-FUNC-11` in microdata manipulation. Reclassified as **`potential_domain_gap_requires_adjudication`**.
- **`BM-CASE-024` (`ACBP-CRS-072`) — Introduction to R and Python Programming_ (NSSTA)**:
  - **Audit Status**: **`official_related_material`**. Local primary source `SRC-NSSTA-TRG-CAL-2025-26.json` (Pages 2, 9) documents Python/R programming for statistical personnel. Tests functional digital tool vs domain computing.

---

### Strata E: Cross-Cadre Context Comparison Pair (n = 2)

- **`BM-CASE-025` (`ACBP-CRS-093`) — Noting and Drafting [Supervisory Staff (SO)] (ISTM)**:
  - **Audit Status**: **`official_related_material`**. Documented in local source `SRC-NSSTA-TRG-CAL-2025-26.json` (Page 3) and ISTM CSMOP manual. Confirms supervisory noting emphasizes precedent evaluation and cabinet note synthesis.
- **`BM-CASE-026` (`ACBP-CRS-170`) — Noting and Drafting [Clerical Staff (UDC/LDC)] (ISTM)**:
  - **Audit Status**: **`official_related_material`**. ISTM clerical induction modules confirm operational focus on routine docketing, file indexing, and reminders. Confirms operational contrast with Case 025.

---

## 4. Verification of Competency IDs and Names

The audit conducted an independent verification of every KCM competency ID and name cited in Stage 3.4 against `data/processed/competencies_kcm.json`:

| Cited Competency ID | Cited Competency Name | Actual Name in `competencies_kcm.json` | Referential Validity | Sub-Theme Verification in KCM 2024 |
| :--- | :--- | :--- | :---: | :--- |
| `KCM-BEH-01` | Self-Awareness | Self-Awareness | **PASSED** | Verified (Pages 38–39): Self-learning, introspection, emotional regulation. |
| `KCM-BEH-02` | Personal Effectiveness | Personal Effectiveness | **PASSED** | Verified (Pages 40–42): Time management, resilience, adaptability. |
| `KCM-BEH-04` | Communication | Communication | **PASSED** | Verified (Pages 45–46): Active listening, clear articulation, stakeholder dialogue. |
| `KCM-BEH-06` | Collaboration | Collaboration | **PASSED** | Verified (Pages 49–50): Building trust, breaking silos, mutual support. |
| `KCM-BEH-07` | Service Orientation | Service Orientation | **PASSED** | Verified (Pages 51–52): Empathy, citizen focus, public value creation. |
| `KCM-BEH-08` | Operational Excellence | Operational Excellence | **PASSED** | Verified (Pages 53–54): Process optimization, quality focus, timeliness. |
| `KCM-BEH-10` | Strategic Leadership | Strategic Leadership | **PASSED** | Verified (Pages 57–58): Long-term vision, systems thinking, institutional stewardship. |
| `KCM-FUNC-02` | Policy Architecture | Policy Architecture | **PASSED** | Verified (Pages 68–69): Policy design, regulatory impact, stakeholder consultation. |
| `KCM-FUNC-04` | Govt Program Formulation | Govt Program Formulation | **PASSED** | Verified (Pages 72–73): Scheme formulation, target setting, budget alignment. |
| `KCM-FUNC-05` | Project Management | Project Management | **PASSED** | Verified (Pages 74–75): Project planning, milestones, PERT/CPM, risk tracking. |
| `KCM-FUNC-06` | Public Procurement (GFR) | Public Procurement (GFR) | **PASSED** | Verified (Pages 76–77): GFR 2017 rules, GeM procurement, bid evaluation, contract terms. |
| `KCM-FUNC-09` | Financial Management | Financial Management | **PASSED** | Verified (Pages 82–83): Budget preparation, financial appraisal, expenditure control. |
| `KCM-FUNC-10` | Digital Fluency | Digital Fluency | **PASSED** | Verified (Pages 84–85): Digital tools, e-Office adoption, cybersecurity awareness. |
| `KCM-FUNC-11` | Data Analytics | Data Analytics | **PASSED** | Verified (Pages 86–87): Data collection, cleaning, visualization, evidence-based insights. |
| `KCM-FUNC-12` | Establishment & HR | Establishment & HR | **PASSED** | Verified (Pages 88–89): Service rules (FRSR), recruitment, career progression, disciplinary matters. |
| `KCM-FUNC-13` | Office Management | Office Management | **PASSED** | Verified (Pages 90–91): CSMOP compliance, file lifecycle, records management. |
| `KCM-FUNC-14` | Handling Parliamentary Matters | Handling Parliamentary Matters | **PASSED** | Verified (Pages 92–93): Parliamentary questions, legislative briefs, assurances. |
| `KCM-FUNC-17` | Vigilance Administration | Vigilance Administration | **PASSED** | Verified (Pages 98–99): Preventive vigilance, disciplinary inquiry, CVC guidelines. |
| `KCM-FUNC-21` | Administration Matters | Administration Matters | **PASSED** | Verified (Pages 106–107): General office administration, logistics, protocol. |

**Audit Result**: Zero invalid competency IDs, zero misspelled names, and zero invented sub-themes. 100% referential integrity confirmed.

---

## 5. Separation of Evidentiary Claims

To prevent over-claiming, the audit strictly separates three levels of evidentiary proof:

```
[Claim Level 1: Subject Matter Relevance]
"Does the course touch on this subject?"
├── PROVEN for 12 cases via official training circulars and apex institute manuals.
│
[Claim Level 2: Competency Alignment]
"Does this subject matter align with a KCM competency definition?"
├── PROVEN conceptually (e.g. GFR 2017 aligns with KCM-FUNC-06).
│
[Claim Level 3: Competency Depth & Mastery]
"Does the specific ACBP course develop the competency to the degree asserted?"
└── UNPROVEN for all 26 cases: A 17-minute video on project leadership or a 75-minute
    video on inquiry cannot be proven to achieve competency mastery without inspecting
    the actual video transcripts, exercises, and evaluation rubrics.
```

---

## 6. Audit Verdict & Recommendations

### Final Verdict: **EVIDENCE AUDIT PASSED WITH LIMITATIONS**

#### Approved Findings:
1. **Source Authenticity**: 100% of cited institutions (ISTM, NSSTA, AJ-NIFM, CBC, Ayush) are authentic apex government academies.
2. **Referential Integrity**: 100% of cited KCM competency IDs and names match primary sources.
3. **No Fabricated Labels**: Production registries, review queues, and benchmark ground-truth labels remain strictly unaltered.

#### Required Limitations to Uphold in Future Stages:
1. **Do Not Treat Related Manuals as Exact Syllabi**: Retain `official_related_material` status until exact iGOT session transcripts are downloaded and mirrored.
2. **Do Not Declare Domain Gaps Automatically**: Retain `potential_domain_gap_requires_adjudication` for HCES and ASI to acknowledge analytical overlap with `KCM-FUNC-11`.
3. **Formal Institutional Requisition**: Disseminate the formal request list to the MoSPI Capacity Building Unit for authenticated iGOT course syllabus retrieval.
