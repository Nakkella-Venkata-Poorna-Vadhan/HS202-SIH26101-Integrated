# MoSPI ACBP to KCM Competency Mapping Benchmark: Design & Evaluation Architecture

> [!IMPORTANT]
> **Status**: APPROVED BENCHMARK DESIGN (Stage 3.3)  
> **Target Frameworks**: Mission Karmayogi (NPCSCB / CBC) & Ministry of Statistics and Programme Implementation (MoSPI / NSSTA)  
> **Associated Artifacts**:  
> - Manifest: [`data/interim/mapping_benchmark_manifest.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_manifest.json) & [`.csv`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_manifest.csv)  
> - Reviewer Template: [`data/interim/mapping_benchmark_template.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_template.json) & [`.csv`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_template.csv)  
> - Annotation Protocol: [`docs/mapping_benchmark_protocol.md`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/docs/mapping_benchmark_protocol.md)  
> - Automated Test Suite: [`tests/test_mapping_benchmark.py`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/tests/test_mapping_benchmark.py)

---

## 1. Executive Summary

Stage 3.3 establishes a scientifically defensible, human-in-the-loop evaluation benchmark for mapping courses from the MoSPI Annual Capacity Building Plan (ACBP 2026–27) to competencies in the Karmayogi Competency Model (KCM 2024).

The benchmark design rejects artificial optimization of mapping coverage at the expense of evidentiary validity. It introduces a **stratified 26-case pilot benchmark** that explicitly captures the full spectrum of mapping difficulty:
1. Lexical title matches requiring syllabus verification.
2. Unresolved behavioural courses with broad cultural titles.
3. Unresolved functional courses with statutory and procedural focus.
4. Domain courses representing India's official statistical system gap.
5. Cross-cadre course repetitions to evaluate cadre-level context influence.

---

## 2. Benchmark Case Stratification (The 26-Case Pilot)

The pilot benchmark consists of 26 carefully sampled cases distributed across 5 mutually exclusive strata:

```
Total Pilot Benchmark (N = 26 Cases)
├── Strata A: Title-Reference Candidates (n = 6) [100% of automated heuristic candidates]
├── Strata B: Unresolved Behavioural Courses (n = 6) [Cultural, Wellness, Indic Ethos, Self-Leadership]
├── Strata C: Unresolved Functional Courses (n = 7) [Parliamentary, GFR Procurement, Inquiry, FRSR, Policy]
├── Strata D: MoSPI Domain Official Statistics Gaps (n = 5) [HCES Microdata, ASI Microdata, Big Data, R/Python]
└── Strata E: Cross-Cadre Context Contrast Pair (n = 2) [Noting & Drafting: SSO vs Clerical Cadre]
```

### 2.1 Detailed Stratification Breakdown

| Case ID | Course Record ID | Cadre Role | Course Name | ACBP Category | Candidate KCM Competency | Sampling Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BM-CASE-001** | `ACBP-CRS-017` | DDG / JS+ | Leading with Collaboration: Sahakaryata _in Public_Service | Behavioural | `KCM-BEH-06` (Collaboration) | Existing heuristic candidate; tests whether *"Sahakaryata in Public Service"* maps to Collaboration or requires deeper syllabus proof. |
| **BM-CASE-002** | `ACBP-CRS-036` | Director / JD | Leadership in Project Management | Functional | `KCM-FUNC-05` (Project Management) | Existing heuristic candidate; tests whether *"Leadership in Project Management"* maps to Project Management or Behavioural Leadership. |
| **BM-CASE-003** | `ACBP-CRS-040` | Director / JD | Strategic Leadership: The Indic_ Way | Behavioural | `KCM-BEH-10` (Strategic Leadership) | Existing heuristic candidate; tests whether *"Strategic Leadership: The Indic Way"* maps to Strategic Leadership. |
| **BM-CASE-004** | `ACBP-CRS-041` | Director / JD | Leading with Collaboration: Sahakaryata _in Public Service | Behavioural | `KCM-BEH-06` (Collaboration) | Existing candidate at Director level; tests cadre-specific syllabus variation against `KCM-BEH-06`. |
| **BM-CASE-005** | `ACBP-CRS-060` | DS / US | Strategic Leadership: _The_Indic_ Way | Behavioural | `KCM-BEH-10` (Strategic Leadership) | Existing candidate at Deputy Secretary level; tests cadre consistency against `KCM-BEH-10`. |
| **BM-CASE-006** | `ACBP-CRS-061` | DS / US | Leading with Collaboration: Sahakaryata in Public_Service_ | Behavioural | `KCM-BEH-06` (Collaboration) | Existing candidate at Deputy Secretary level; tests cadre consistency against `KCM-BEH-06`. |
| **BM-CASE-007** | `ACBP-CRS-014` | DDG / JS+ | Developing a Positive Work Culture | Behavioural | *None (Unresolved)* | Broad cultural title repeated across 11 cadres; tests whether broad culture maps to specific KCM competencies. |
| **BM-CASE-008** | `ACBP-CRS-022` | DDG / JS+ | Yoga Break at Workplace | Behavioural | *None (Unresolved)* | Workplace wellness title; tests boundary condition of whether physical wellness is out-of-scope or maps to self-regulation. |
| **BM-CASE-009** | `ACBP-CRS-023` | DDG / JS+ | Happiness in Seva-Bhava: Lessons from Bhagavad-Gita | Behavioural | *None (Unresolved)* | Indic civil service ethos title; tests alignment with `KCM-BEH-07` (*Service Orientation*) and ethical conduct. |
| **BM-CASE-010** | `ACBP-CRS-043` | Director / JD | Leading from Within: Behavioural Strategies for Self-Leadership | Behavioural | *None (Unresolved)* | Self-leadership title; tests potential mapping to `KCM-BEH-01` (*Self-Awareness*) or Team Leadership. |
| **BM-CASE-011** | `ACBP-CRS-125` | AD(OL) / Translator | The Art of Listening | Behavioural | *None (Unresolved)* | Granular interpersonal skill; tests whether focused interpersonal training maps to `KCM-BEH-04` (*Communication*). |
| **BM-CASE-012** | `ACBP-CRS-142` | AD(OL) / Translator | Revisiting Gender Equality through the Indian Spiritual Vision | Behavioural | *None (Unresolved)* | Social perspective title; tests potential alignment with Citizen Centricity / Service Orientation. |
| **BM-CASE-013** | `ACBP-CRS-008` | DDG / JS+ | Conduct of Inquiry in Disciplinary Matters | Functional | *None (Unresolved)* | Quasi-judicial disciplinary inquiry; tests potential mapping to `KCM-FUNC-17` (*Vigilance Administration*). |
| **BM-CASE-014** | `ACBP-CRS-010` | DDG / JS+ | Fundamentals of Public Policy | Functional | *None (Unresolved)* | Policy analysis title; tests potential mapping to `KCM-FUNC-02` (*Policy Architecture*) or Govt Program Formulation. |
| **BM-CASE-015** | `ACBP-CRS-011` | DDG / JS+ | Project A ppraisal and Financial Evaluation Techniques | Functional | *None (Unresolved)* | Financial appraisal title; tests multi-competency ambiguity between `KCM-FUNC-09` (*Financial Management*) and `KCM-FUNC-05` (*Project Management*). |
| **BM-CASE-016** | `ACBP-CRS-013` | DDG / JS+ | Navigating Parliamentary Questions | Functional | *None (Unresolved)* | Legislative process title; tests direct semantic mapping to `KCM-FUNC-14` (*Handling Parliamentary Matters*). |
| **BM-CASE-017** | `ACBP-CRS-053` | DS / US | Procurement of Works | Functional | *None (Unresolved)* | Public procurement title; tests mapping to `KCM-FUNC-06` (*Public Procurement - GFR*). |
| **BM-CASE-018** | `ACBP-CRS-055` | DS / US | FRSR Part [ General Rules | Functional | *None (Unresolved)* | Civil service statutory rules; tests mapping to `KCM-FUNC-12` (*Establishment & HR*) and `KCM-FUNC-21` (*Administration Matters*). |
| **BM-CASE-019** | `ACBP-CRS-057` | DS / US | AI for Presentations | Functional | *None (Unresolved)* | Technology productivity tool; tests whether modern software tools map to `KCM-FUNC-10` (*Digital Fluency*) or lack KCM coverage. |
| **BM-CASE-020** | `ACBP-CRS-001` | DDG / JS+ | Introduction to Big Data in Governance | Domain | *None (Unresolved)* | Domain data governance title; tests separation of Domain category from Functional data analytics. |
| **BM-CASE-021** | `ACBP-CRS-046` | DS / US | Know Your Ministry Ministry of Statistics and Programme Implementation | Domain | *None (Unresolved)* | Ministry orientation title; tests ministry-specific domain knowledge gap. |
| **BM-CASE-022** | `ACBP-CRS-067` | AD / DD | Handling Unit Level Data of Household Consumption Expenditure Survey | Domain | *None (Unresolved)* | Core official statistics survey microdata (HCES); canonical gold standard test case for `no_applicable_kcm_competency`. |
| **BM-CASE-023** | `ACBP-CRS-069` | AD / DD | Handling Unit Level Data of Annual Survey of Industries | Domain | *None (Unresolved)* | Core official statistics economic survey (ASI); canonical gold standard test case for `no_applicable_kcm_competency`. |
| **BM-CASE-024** | `ACBP-CRS-072` | AD / DD | Introduction to R and Python Programming_ | Domain | *None (Unresolved)* | Statistical computing tool; tests distinction between statistical domain computing and generic digital fluency. |
| **BM-CASE-025** | `ACBP-CRS-093` | SSO / SO / AO | Noting and Drafting | Functional | *None (Unresolved)* | Identical title at Supervisory Cadre; paired with `BM-CASE-026` to evaluate cadre-level context influence. |
| **BM-CASE-026** | `ACBP-CRS-170` | Assistants / UDC / LDC | Noting and Drafting | Functional | *None (Unresolved)* | Identical title at Clerical Cadre; paired with `BM-CASE-025` to evaluate operational expectation differences. |

---

## 3. Label Taxonomy and Adjudication Semantics

The benchmark separates semantic relevance from evidentiary sufficiency:

```
                                  [Course Case]
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
          [Domain Topic?]                               [Non-Domain Topic]
                 │                                             │
      ┌──────────┴──────────┐                        ┌─────────┴─────────┐
      ▼                     ▼                        ▼                   ▼
(MoSPI Official       (Generic Civil           (Syllabus /        (Syllabus /
  Statistics)           Service Domain)         Evidence           Evidence
      │                     │                   Present)            Absent)
      ▼                     ▼                        │                   │
[no_applicable_       [unresolved_                   │                   ▼
 kcm_competency]     insufficient_source]            │              [unresolved_
                                                     │             insufficient_source]
                        ┌────────────────────────────┼────────────────────────────┐
                        ▼                            ▼                            ▼
              (Contradicts / Flawed)        (Plausible / Brief)          (Sub-theme Verified)
                        │                            │                            │
                        ▼                            ▼                            ▼
               [incorrect_mapping]        [plausible_insufficient_       [supported_mapping]
                                                 evidence]
```

### Label Specifications
1. **`supported_mapping`**:
   - Curricular evidence proves alignment with specific KCM competency and sub-theme.
   - Permitted target KCM ID: Required (`KCM-BEH-*` or `KCM-FUNC-*`).
   - Evidentiary requirement: Verbatim syllabus quote + sub-theme indicator match.
2. **`plausible_insufficient_evidence`**:
   - Course title or high-level outline plausibly aligns, but full syllabus is unavailable or too brief to prove competency acquisition.
   - Permitted target KCM ID: Required (candidate ID under review).
3. **`incorrect_mapping`**:
   - Proposed candidate mapping is factually incorrect, misclassified, or contradicted by syllabus content.
   - Permitted target KCM ID: `null` or rejected candidate ID with documented contradiction.
4. **`unresolved_insufficient_source`**:
   - Course represents general administrative or behavioural training, but zero course documentation exists in the source repository to evaluate it.
   - Permitted target KCM ID: Must be `null`.
5. **`no_applicable_kcm_competency`**:
   - Course covers official statistics, statistical survey methodology, or MoSPI administrative functions not present in generic central civil services KCM 2024.
   - Permitted target KCM ID: Must be `null`.

---

## 4. Evaluation Leakage Prevention Plan

To ensure the benchmark remains an untainted gold standard, strict protocols are enforced:

### 4.1 Strict Partitioning of Data Layers
- The benchmark manifest and reviewer template are stored strictly under `data/interim/` (`mapping_benchmark_manifest.json` and `mapping_benchmark_template.json`).
- Benchmark files are physically separate from production registry files (`data/processed/acbp_kcm_mappings.json`).
- **No Overwrite Rule**: Running candidate generation scripts or registry builders cannot read from or overwrite the human benchmark artifacts.

### 4.2 Prohibition on Evaluation Tuning
- **Evaluation Contamination**: Machine learning models, prompt templates, or embedding retrievers must **never** be trained or fine-tuned on benchmark cases.
- **Future Dev/Test Split**: When the benchmark expands beyond the 26-case pilot, cases will be deterministically partitioned into:
  - **Development Set (40%)**: For error analysis, threshold tuning, and prompt refinement.
  - **Held-Out Evaluation Set (60%)**: Sealed and evaluated only once per release candidate.

### 4.3 Provenance & Versioning
- Every benchmark release is cryptographically locked with SHA256 source hashes of `acbp_courses.json` and `competencies_kcm.json`.
- All annotations will maintain full git commit history and tamper-evident audit trails.

---

## 5. Evaluation Metrics Formulation

When human annotations are completed, mapping pipelines will be evaluated using the following formal metrics:

### 5.1 Precision Among Reviewed Candidates ($P_{cand}$)
Measures how many retrieved or proposed candidate mappings are actually supported by curricular evidence:

$$P_{cand} = \frac{|\{c \in \text{Reviewed Candidates} : \text{Label}(c) = \text{supported\_mapping}\}|}{|\text{Reviewed Candidates}|}$$

### 5.2 Unsupported Candidate Rate ($UCR$)
Measures the proportion of candidates that were promoted based on lexical overlap but collapsed under human curricular review:

$$UCR = \frac{|\{c \in \text{Candidates} : \text{Label}(c) \in \{\text{plausible\_insufficient\_evidence}, \text{incorrect\_mapping}\}\}|}{|\text{Candidates}|}$$

### 5.3 Official Statistics Domain Gap Sensitivity ($OSGS$)
Measures whether the system correctly flags MoSPI domain courses as unrepresented in KCM rather than hallucinating generic civil service mappings:

$$OSGS = \frac{|\{c \in \text{MoSPI Domain Courses} : \text{System Decision}(c) = \text{unresolved\_domain\_gap}\}|}{|\text{MoSPI Domain Courses}|}$$

### 5.4 Inter-Reviewer Agreement (Cohen's $\kappa$ / Fleiss' $\kappa$)
Calculated across dual-annotated cases to evaluate review reliability before adjudication:

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

*Where $p_o$ is the observed proportion of agreement across the 5 benchmark labels, and $p_e$ is the expected agreement by chance.*

> [!CAUTION]
> **Reporting Constraint**: No numerical benchmark performance scores may be reported until human annotations have been independently conducted and adjudicated under the protocol.

---

## 6. Pilot Sample Limitations

The 26-case pilot benchmark is designed to validate evaluation methodology and test protocol feasibility. The following conclusions **cannot** be drawn from the pilot alone:
1. **Global Registry Accuracy**: A 26-case sample (11.5% of the 226 courses) is insufficient to calculate global precision or recall across the entire MoSPI training catalogue with narrow statistical confidence intervals.
2. **Exhaustive Domain Coverage**: While 5 domain courses are included, MoSPI administers dozens of specialised surveys (e.g., PLFS, Index of Industrial Production, CPI, National Accounts Statistics) that require domain-specific evaluation.
3. **Automated Model Acceptance**: Passing the pilot benchmark does not grant automated production deployment approval without stakeholder sign-off from NSSTA and CBC.
