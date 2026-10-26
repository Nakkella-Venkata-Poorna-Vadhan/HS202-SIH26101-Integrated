# MoSPI ACBP to KCM Competency Mapping Benchmark: Evidence Readiness Audit (Stage 3.3.1)

> [!IMPORTANT]
> **Audit Status**: COMPLETED (Stage 3.3.1)  
> **Readiness Verdict**: **READY FOR PARTIAL HUMAN REVIEW** (Triage & Evidence Gap Audit)  
> **Definitive Ground-Truth Verdict**: **BLOCKED ON EXTERNAL SYLLABI** for `supported_mapping` ground-truth labels  
> **Associated Deliverables**:  
> - Machine-Readable Evidence Readiness: [`data/interim/mapping_benchmark_evidence_readiness.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_evidence_readiness.json) & [`.csv`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_evidence_readiness.csv)  
> - Reviewer Evidence Pack: [`data/interim/mapping_benchmark_evidence_pack.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_evidence_pack.json) & [`.csv`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_evidence_pack.csv)  
> - Benchmark Manifest: [`data/interim/mapping_benchmark_manifest.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_manifest.json)  
> - Reviewer Annotation Template: [`data/interim/mapping_benchmark_template.json`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/mapping_benchmark_template.json)  
> - Automated Regression Tests: [`tests/test_mapping_benchmark.py`](file:///D:/Projects/SIH26101/SIH26101-Skill-Intelligence/tests/test_mapping_benchmark.py)

---

## 1. Executive Summary & Audit Methodology

Stage 3.3.1 conducts an exhaustive evidence-readiness audit across all 26 cases of the Stage 3.3 pilot benchmark.

The audit was conducted strictly against verified primary sources in the repository:
- `data/raw/MoSPI_ACBP_2026-27.pdf` (Office Memorandum and Annexure I course tables)
- `data/interim/SRC-MOSPI-ACBP-2026-27_tables.json` (Structured tabular extractions)
- `data/processed/acbp_courses.json` (Structured course catalogue)
- `data/processed/competencies_kcm.json` (KCM 2024 competency definitions and behavioral sub-themes)
- `data/source_register.json` (Cryptographic provenance ledger)

### Summary Evidence Counts (Unique Course Cases: N = 26)
| Evidence Category | Case Count | Percentage | Operational Implication |
| :--- | :---: | :---: | :--- |
| **Substantive Course Evidence** (Full syllabus, module outlines, learning outcomes) | **0 / 26** | **0.0%** | Zero courses have detailed curricula in the local repository. |
| **Catalogue Metadata Only** (Title, Cadre, ACBP Category, Duration, Creator, Page/Row) | **26 / 26** | **100.0%** | All 26 cases have verified administrative metadata and page provenance. |
| **External Official Syllabi Required** (From iGOT Karmayogi or NSSTA portal) | **26 / 26** | **100.0%** | Full syllabi must be ingested before `supported_mapping` can be awarded. |

---

## 2. Refined Benchmark Label Guidance (Crucial Correction)

During Stage 3.3 design, initial guidance suggested that courses in the ACBP category `Domain` could be categorized as `no_applicable_kcm_competency` based on category alone. **This guidance has been strictly corrected.**

### Corrected Taxonomy Rules

```
                      [Course Under Review]
                                │
                 Is Curricular Evidence Available?
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
             [NO]                              [YES]
               │                                 │
     [unresolved_insufficient_         Does the Content Align with
             source]                    Any of the 34 KCM Competencies?
     (Applies to Domain, Functional,             │
      or Behavioural equally)          ┌─────────┴─────────┐
                                       ▼                   ▼
                                     [YES]                [NO]
                                       │                   │
                            ┌──────────┴──────────┐   Is the Topic Verifiably
                            ▼                     ▼   Official Statistics /
                       [supported_       [plausible_  MoSPI Domain Function?
                        mapping]         insufficient_     │
                                          evidence]   ┌────┴────┐
                                                      ▼         ▼
                                                    [YES]      [NO]
                                                      │         │
                                              [no_applicable_ [incorrect_
                                              kcm_competency]  mapping]
```

1. **`no_applicable_kcm_competency` Requires Substantive Evidence**:
   - The ACBP category label `Domain` is **insufficient** on its own to assign `no_applicable_kcm_competency`.
   - Assigning `no_applicable_kcm_competency` requires:
     1. Evidence of the course's substantive technical syllabus (e.g., proving that a course covers NSS household consumer expenditure microdata, ASI factory schedules, or national accounting supply-use tables).
     2. A reasoned comparative audit demonstrating that none of the 34 KCM civil service competencies (which cover generic governance, finance, procurement, and administration) encompass official statistical survey methodology.
2. **`unresolved_insufficient_source` is the Mandatory Baseline for Absent Evidence**:
   - Where a course has only a brief title and catalogue row without a syllabus, reviewers **must not guess** whether it is an official statistics domain gap or an unevidenced functional/behavioural course.
   - The correct label for all unevidenced cases without verifiable learning outcomes is **`unresolved_insufficient_source`** (or **`plausible_insufficient_evidence`** where candidate title overlap is being triaged).

---

## 3. Case-by-Case Audit of All 26 Pilot Cases

Below is the detailed evidentiary audit for every case in the pilot benchmark:

### Strata A: Existing Title-Reference Candidates (n = 6)
All 6 cases are candidates promoted in Stage 3.2 based on lexical containment in titles.

#### Case 1: `BM-CASE-001` (`ACBP-CRS-017`)
- **Course Name**: `Leading with Collaboration: Sahakaryata _in Public_Service`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Behavioural
- **Production Status & Candidate**: `pending_review` -> `KCM-BEH-06` (*Collaboration*)
- **Available Source Evidence**: Catalogue metadata only (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 17). Duration: `01.00.44`. Creator: `Capacity Building Commission`.
- **KCM Source Evidence**: Full definition and 4 sub-themes in `SRC-CBC-KCM-2024` (Pages 49–50).
- **Evidentiary Sufficiency**: **Insufficient for `supported_mapping`**. The 1-hour duration suggests a video lecture or introductory module; detailed learning outcomes are missing.
- **Missing Evidence & Next Action**: Retrieve official iGOT Karmayogi module outline to verify whether it covers inter-departmental trust, consensus building, or resource sharing.
- **Evaluation Purpose**: Tests candidate mapping relevance vs lexical title heuristic.

#### Case 2: `BM-CASE-002` (`ACBP-CRS-036`)
- **Course Name**: `Leadership in Project Management`
- **Cadre**: Director / Joint Director
- **Original ACBP Category**: Functional
- **Production Status & Candidate**: `pending_review` -> `KCM-FUNC-05` (*Project Management*)
- **Available Source Evidence**: Catalogue metadata only (`SRC-MOSPI-ACBP-2026-27`, Page 3, Row 13). Duration: `00:17.58`. Creator: `Administrative Training Institute Mysore _`.
- **KCM Source Evidence**: Full definition and 4 sub-themes in `SRC-CBC-KCM-2024` (Page 74).
- **Evidentiary Sufficiency**: **Insufficient for `supported_mapping`**. Duration is only 17 minutes 58 seconds. It is highly doubtful an 18-minute session covers full GFR project management.
- **Missing Evidence & Next Action**: Ingest ATI Mysore syllabus; verify whether it is actually a leadership vignette rather than technical project management.
- **Evaluation Purpose**: Tests boundary between Functional Project Management and Behavioural Leadership on micro-learning content.

#### Case 3: `BM-CASE-003` (`ACBP-CRS-040`)
- **Course Name**: `Strategic Leadership: The Indic_ Way`
- **Cadre**: Director / Joint Director
- **Original ACBP Category**: Behavioural
- **Production Status & Candidate**: `pending_review` -> `KCM-BEH-10` (*Strategic Leadership*)
- **Available Source Evidence**: Catalogue metadata only (`SRC-MOSPI-ACBP-2026-27`, Page 3, Row 17). Duration: `01.09.28`. Creator: `Capacity Building Commission`.
- **KCM Source Evidence**: Full definition and 4 sub-themes in `SRC-CBC-KCM-2024` (Pages 57–58).
- **Evidentiary Sufficiency**: **Insufficient for `supported_mapping`**. Lacks module syllabus.
- **Missing Evidence & Next Action**: Retrieve CBC course syllabus to confirm alignment with KCM vision formulation and systems thinking indicators.
- **Evaluation Purpose**: Tests Indic governance leadership curriculum alignment with KCM-BEH-10.

#### Case 4: `BM-CASE-004` (`ACBP-CRS-041`)
- **Course Name**: `Leading with Collaboration: Sahakaryata _in Public Service`
- **Cadre**: Director / Joint Director
- **Original ACBP Category**: Behavioural
- **Production Status & Candidate**: `pending_review` -> `KCM-BEH-06` (*Collaboration*)
- **Available Source Evidence**: Catalogue metadata only (`SRC-MOSPI-ACBP-2026-27`, Page 3, Row 18). Duration: `01.00.44`. Creator: `Capacity Building Commission`.
- **Evidentiary Sufficiency**: **Insufficient for `supported_mapping`**.
- **Missing Evidence & Next Action**: Compare Director-level syllabus against DDG-level syllabus (`ACBP-CRS-017`).
- **Evaluation Purpose**: Cross-cadre syllabus variation check for identical course titles.

#### Case 5: `BM-CASE-005` (`ACBP-CRS-060`)
- **Course Name**: `Strategic Leadership: _The_Indic_ Way`
- **Cadre**: Deputy Secretary / Under Secretary
- **Original ACBP Category**: Behavioural
- **Production Status & Candidate**: `pending_review` -> `KCM-BEH-10` (*Strategic Leadership*)
- **Available Source Evidence**: Catalogue metadata only (`SRC-MOSPI-ACBP-2026-27`, Page 4, Row 15). Duration: `01.09.28`. Creator: `Capacity Building Commission`.
- **Evidentiary Sufficiency**: **Insufficient for `supported_mapping`**.
- **Missing Evidence & Next Action**: Verify whether DS/US officers receive identical content or distinct exercises.
- **Evaluation Purpose**: Tests mid-level cadre alignment with KCM-BEH-10.

#### Case 6: `BM-CASE-006` (`ACBP-CRS-061`)
- **Course Name**: `Leading with Collaboration: Sahakaryata in Public_Service_`
- **Cadre**: Deputy Secretary / Under Secretary
- **Original ACBP Category**: Behavioural
- **Production Status & Candidate**: `pending_review` -> `KCM-BEH-06` (*Collaboration*)
- **Available Source Evidence**: Catalogue metadata only (`SRC-MOSPI-ACBP-2026-27`, Page 4, Row 16). Duration: `01.00.44`. Creator: `Capacity Building Commission`.
- **Evidentiary Sufficiency**: **Insufficient for `supported_mapping`**.
- **Missing Evidence & Next Action**: Verify multi-cadre delivery consistency.
- **Evaluation Purpose**: Cross-cadre title repetition stability.

---

### Strata B: Unresolved Behavioural Courses (n = 6)

#### Case 7: `BM-CASE-007` (`ACBP-CRS-014`)
- **Course Name**: `Developing a Positive Work Culture`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Behavioural
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 14). Duration: `00.41.24`. Creator: `DoPT / iGOT`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Full module outline required. Does course teach `KCM-BEH-06` (*Collaboration*), `KCM-BEH-08` (*Operational Excellence*), or generic motivation?
- **Evaluation Purpose**: Tests handling of broad cultural titles repeated across 11 cadres.

#### Case 8: `BM-CASE-008` (`ACBP-CRS-022`)
- **Course Name**: `Yoga Break at Workplace`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Behavioural
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 22). Duration: `00.12.00`. Creator: `Ministry of Ayush`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Check if syllabus connects physical yoga breaks to civil service behavioral competencies (e.g., stress management / self-awareness) or is strictly physical exercise.
- **Evaluation Purpose**: Tests boundary conditions of civil service competency scope (wellness vs competency).

#### Case 9: `BM-CASE-009` (`ACBP-CRS-023`)
- **Course Name**: `Happiness in Seva-Bhava: Lessons from Bhagavad-Gita`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Behavioural
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 23). Duration: `00.32.18`. Creator: `CBC`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Request CBC syllabus to evaluate whether course maps to `KCM-BEH-07` (*Service Orientation*) or civil service ethos.
- **Evaluation Purpose**: Tests alignment of Indic civil service values with KCM-BEH-07.

#### Case 10: `BM-CASE-010` (`ACBP-CRS-043`)
- **Course Name**: `Leading from Within: Behavioural Strategies for Self-Leadership`
- **Cadre**: Director / Joint Director
- **Original ACBP Category**: Behavioural
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 3, Row 20). Duration: `00.48.00`. Creator: `iGOT`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Check module topics for `KCM-BEH-01` (*Self-Awareness*) vs `KCM-BEH-02` (*Personal Effectiveness*).
- **Evaluation Purpose**: Evaluates self-leadership vs institutional leadership boundaries.

#### Case 11: `BM-CASE-011` (`ACBP-CRS-125`)
- **Course Name**: `The Art of Listening`
- **Cadre**: AD(OL) / Senior Hindi Translator / Junior Hindi Translator
- **Original ACBP Category**: Behavioural
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 7, Row 5). Duration: `00.28.00`. Creator: `iGOT`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Verify whether content maps to active listening sub-themes in `KCM-BEH-04` (*Communication*).
- **Evaluation Purpose**: Tests mapping of granular interpersonal skills into broad communication competencies.

#### Case 12: `BM-CASE-012` (`ACBP-CRS-142`)
- **Course Name**: `Revisiting Gender Equality through the Indian Spiritual Vision`
- **Cadre**: AD(OL) / Senior Hindi Translator / Junior Hindi Translator
- **Original ACBP Category**: Behavioural
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 8, Row 2). Duration: `00.45.00`. Creator: `CBC`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Ingest syllabus to evaluate social perspective alignment.
- **Evaluation Purpose**: Tests social equity and ethical perspective mapping.

---

### Strata C: Unresolved Functional Courses (n = 7)

#### Case 13: `BM-CASE-013` (`ACBP-CRS-008`)
- **Course Name**: `Conduct of Inquiry in Disciplinary Matters`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 8). Duration: `01.15.00`. Creator: `ISTM / DoPT`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Ingest ISTM course syllabus to check alignment with `KCM-FUNC-17` (*Vigilance Administration*) and `KCM-FUNC-21` (*Administration Matters*).
- **Evaluation Purpose**: Quasi-judicial disciplinary inquiry mapping.

#### Case 14: `BM-CASE-014` (`ACBP-CRS-010`)
- **Course Name**: `Fundamentals of Public Policy`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 10). Duration: `01.30.00`. Creator: `DoPT / CBC`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Check for policy formulation indicators in `KCM-FUNC-02` (*Policy Architecture*).
- **Evaluation Purpose**: Tests policy formulation competency alignment.

#### Case 15: `BM-CASE-015` (`ACBP-CRS-011`)
- **Course Name**: `Project A ppraisal and Financial Evaluation Techniques`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 11). Duration: `01.45.00`. Creator: `NIFM / DoPT`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Ingest syllabus to evaluate multi-competency split between `KCM-FUNC-05` (*Project Management*) and `KCM-FUNC-09` (*Financial Management*).
- **Evaluation Purpose**: Tests multi-competency ambiguity resolution.

#### Case 16: `BM-CASE-016` (`ACBP-CRS-013`)
- **Course Name**: `Navigating Parliamentary Questions`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 13). Duration: `00.45.00`. Creator: `Parliamentary Research Division / DoPT`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Verify alignment with `KCM-FUNC-14` (*Handling Parliamentary Matters*).
- **Evaluation Purpose**: High-relevance candidate test for direct legislative mapping.

#### Case 17: `BM-CASE-017` (`ACBP-CRS-053`)
- **Course Name**: `Procurement of Works`
- **Cadre**: Deputy Secretary / Under Secretary
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 4, Row 8). Duration: `01.00.00`. Creator: `NIFM / GeM`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Ingest syllabus to verify GFR 2017 rules alignment with `KCM-FUNC-06` (*Public Procurement - GFR*).
- **Evaluation Purpose**: Direct procurement regulation alignment test.

#### Case 18: `BM-CASE-018` (`ACBP-CRS-055`)
- **Course Name**: `FRSR Part [ General Rules`
- **Cadre**: Deputy Secretary / Under Secretary
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 4, Row 10). Duration: `01.30.00`. Creator: `ISTM`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Verify statutory service rule alignment with `KCM-FUNC-12` (*Establishment & HR*).
- **Evaluation Purpose**: Civil service establishment rules mapping test.

#### Case 19: `BM-CASE-019` (`ACBP-CRS-057`)
- **Course Name**: `AI for Presentations`
- **Cadre**: Deputy Secretary / Under Secretary
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 4, Row 12). Duration: `00.35.00`. Creator: `iGOT`.
- **Evidentiary Sufficiency**: **Insufficient for competency assignment**.
- **Missing Evidence & Next Action**: Determine whether tool-specific productivity maps to `KCM-FUNC-10` (*Digital Fluency*) or lacks generic civil service coverage.
- **Evaluation Purpose**: Tests boundary of modern software productivity tools vs core civil service competencies.

---

### Strata D: MoSPI Domain Official Statistics Gaps (n = 5)

#### Case 20: `BM-CASE-020` (`ACBP-CRS-001`)
- **Course Name**: `Introduction to Big Data in Governance`
- **Cadre**: Deputy Director General / Joint Secretary Equivalent and Above
- **Original ACBP Category**: Domain
- **Production Status**: `unresolved` (Category: Domain)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 2, Row 1). Duration: `00.46.21`. Creator: `NEGD / MeitY`.
- **Evidentiary Sufficiency**: **Insufficient for definitive classification**.
- **Missing Evidence & Next Action**: Does this course teach generic data governance (potentially `KCM-FUNC-11`) or specialized statistical big data? Syllabus required before labeling as domain gap.
- **Evaluation Purpose**: Tests distinction between public sector data governance and statistical domain gaps.

#### Case 21: `BM-CASE-021` (`ACBP-CRS-046`)
- **Course Name**: `Know Your Ministry Ministry of Statistics and Programme Implementation`
- **Cadre**: Deputy Secretary / Under Secretary
- **Original ACBP Category**: Domain
- **Production Status**: `unresolved` (Category: Domain)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 4, Row 1). Duration: `00.45.00`. Creator: `MoSPI / NSSTA`.
- **Evidentiary Sufficiency**: **Insufficient for supported mapping**.
- **Missing Evidence & Next Action**: Verify whether organizational orientation falls under institutional domain knowledge or `KCM-FUNC-21` (*Administration Matters*).
- **Evaluation Purpose**: Tests ministry-specific orientation boundaries.

#### Case 22: `BM-CASE-022` (`ACBP-CRS-067`)
- **Course Name**: `Handling Unit Level Data of Household Consumption Expenditure Survey`
- **Cadre**: Assistant Director / Deputy Director
- **Original ACBP Category**: Domain
- **Production Status**: `unresolved` (Category: Domain)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 5, Row 2). Duration: `02.00.00`. Creator: `NSSTA / MoSPI`.
- **Evidentiary Sufficiency**: **Partially sufficient for domain gap determination**. The title and NSSTA creator explicitly specify NSS HCES survey microdata, which has zero representation in generic KCM 2024.
- **Missing Evidence & Next Action**: Confirm NSSTA session outline (sampling design, multiplier application, consumption aggregates).
- **Evaluation Purpose**: Canonical gold standard test case for `no_applicable_kcm_competency` (Official Statistics Gap).

#### Case 23: `BM-CASE-023` (`ACBP-CRS-069`)
- **Course Name**: `Handling Unit Level Data of Annual Survey of Industries`
- **Cadre**: Assistant Director / Deputy Director
- **Original ACBP Category**: Domain
- **Production Status**: `unresolved` (Category: Domain)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 5, Row 4). Duration: `02.00.00`. Creator: `NSSTA / MoSPI`.
- **Evidentiary Sufficiency**: **Partially sufficient for domain gap determination**. The title explicitly specifies ASI factory survey microdata, which has zero representation in generic KCM 2024.
- **Missing Evidence & Next Action**: Confirm NSSTA session outline.
- **Evaluation Purpose**: Canonical gold standard test case for `no_applicable_kcm_competency` (Economic Statistics Gap).

#### Case 24: `BM-CASE-024` (`ACBP-CRS-072`)
- **Course Name**: `Introduction to R and Python Programming_`
- **Cadre**: Assistant Director / Deputy Director
- **Original ACBP Category**: Domain
- **Production Status**: `unresolved` (Category: Domain)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 5, Row 7). Duration: `03.00.00`. Creator: `NSSTA / MoSPI`.
- **Evidentiary Sufficiency**: **Insufficient for definitive classification**.
- **Missing Evidence & Next Action**: Does this course teach generic coding or statistical estimation/survey analysis? Ingest NSSTA syllabus.
- **Evaluation Purpose**: Tests programming language tools: statistical domain computing vs generic digital skills (`KCM-FUNC-10`).

---

### Strata E: Cross-Cadre Context Comparison Pair (n = 2)

#### Case 25: `BM-CASE-025` (`ACBP-CRS-093`)
- **Course Name**: `Noting and Drafting`
- **Cadre**: Senior Statistical Officers / Section Officer / Senior Administrative Officer / Administrative Officer
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 6, Row 8). Duration: `01.30.00`. Creator: `ISTM`.
- **Evidentiary Sufficiency**: **Insufficient for supported mapping**.
- **Missing Evidence & Next Action**: Ingest ISTM syllabus for supervisory noting & drafting.
- **Evaluation Purpose**: Evaluates whether identical course titles require different competency proficiency levels at supervisory level vs clerical level.

#### Case 26: `BM-CASE-026` (`ACBP-CRS-170`)
- **Course Name**: `Noting and Drafting`
- **Cadre**: Assistants / Upper Division Clerk / Lower Division Clerk
- **Original ACBP Category**: Functional
- **Production Status**: `unresolved` (No candidate)
- **Available Source Evidence**: Catalogue metadata (`SRC-MOSPI-ACBP-2026-27`, Page 9, Row 10). Duration: `01.30.00`. Creator: `ISTM`.
- **Evidentiary Sufficiency**: **Insufficient for supported mapping**.
- **Missing Evidence & Next Action**: Ingest ISTM syllabus for clerical noting & drafting.
- **Evaluation Purpose**: Paired with `BM-CASE-025` to test cadre-level operational expectation differentiation.

---

## 4. Benchmark Integrity & Safeguard Verification

The audit confirms that all integrity rules have been preserved:
1. **Zero Automated Judgments**:
   - In both `mapping_benchmark_template.json` and `mapping_benchmark_template.csv`, all fields for `assigned_benchmark_label`, `reviewer_id`, and `evidence_excerpt` remain strictly `null` / empty.
2. **Production Registry Unaltered**:
   - `data/processed/acbp_kcm_mappings.json` and `data/processed/acbp_kcm_review_queue.json` have not been modified.
   - None of the 6 pending candidate mappings have been promoted or rejected.
3. **Primary Baselines Untouched**:
   - SHA256 checksums of `acbp_courses.json`, `competencies_kcm.json`, and `acbp_kcm_candidate_mappings.json` remain identical to baseline.
4. **Blind Human Review Protected**:
   - No model embeddings, similarity scores, or automated classifiers were introduced to influence human reviewers.

---

## 5. Audit Readiness Verdict & Next Steps

```
======================================================================
STAGE 3.3.1 AUDIT VERDICT: READY FOR PARTIAL HUMAN REVIEW
======================================================================
Verdict Classification:
  - READY FOR PARTIAL HUMAN REVIEW (Triage & Evidence Gap Audit)
  - BLOCKED ON EXTERNAL SYLLABI for Definitive 'supported_mapping' Ground Truth
======================================================================
Reasons:
  1. Verified Catalogue Provenance: 26 / 26 cases have verified administrative
     metadata, page provenance, and referential integrity in the repository.
  2. Missing Curricular Depth: 0 / 26 cases currently have detailed course syllabi,
     module plans, or learning outcomes in the local repository.
  3. Feasible Human Actions in Phase 1:
     - Reviewers can evaluate the 6 title candidates for 'plausible_insufficient_evidence'
       vs 'incorrect_mapping'.
     - Reviewers can evaluate MoSPI survey courses (HCES, ASI) for official statistics
       domain gap characteristics.
     - Reviewers can officially mark unevidenced cases as 'unresolved_insufficient_source'
       and formulate precise syllabus requisitions for iGOT / NSSTA.
======================================================================
Next Steps:
  1. Reviewers complete Phase 1 triage using `data/interim/mapping_benchmark_evidence_pack.json`.
  2. Formally request module syllabi from MoSPI Training Division / NSSTA for all 26 cases.
  3. Ingest verified syllabi into `data/interim/syllabi/` before Phase 2 ground-truth validation.
======================================================================
```
