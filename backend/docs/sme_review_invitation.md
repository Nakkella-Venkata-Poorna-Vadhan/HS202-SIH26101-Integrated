# MoSPI ACBP Benchmark: Subject-Matter Expert (SME) Review Invitation & Evaluation Charter

> [!IMPORTANT]
> **Invitation Purpose**: Engagement protocol for qualified Indian Statistical Service (ISS) officers, Subordinate Statistical Service (SSS) officers, central civil servants, and public administration training faculty.  
> **Evaluation Scope**: 26-Case Competency Mapping Benchmark ([`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv)).  
> **Integrity Safeguard**: This invitation sets forth independent, blind dual-review evaluation rules. It establishes clear operational boundaries between preliminary triage and final authoritative adjudication.

---

## 1. Invitation Overview & Research Context

Dear Colleague / Subject-Matter Expert,

The Ministry of Statistics and Programme Implementation (MoSPI) has approved its **Annual Capacity Building Plan (ACBP) FY 2026–27**, comprising courses spanning official statistics, public administration, financial rules, and workplace behaviours.

Under India's **National Programme for Civil Services Capacity Building (Mission Karmayogi)**, capacity building must be anchored in empirical competency frameworks. However, automated systems and broad topical comparisons often produce deceptive mappings—such as equating a 15-minute introductory video on "Project Leadership" with an advanced functional competency in GFR capital appraisal.

The **SIH26101 Competency Intelligence Platform** has engineered a 26-case benchmark to validate course-to-competency mappings against the official **Karmayogi Competency Model (KCM 2024)**. 

We invite you to serve as an **Independent Subject-Matter Reviewer** to evaluate these candidate mappings using primary institutional evidence.

---

## 2. Expected Effort & Time Commitment

| Review Phase | Scope | Cases | Estimated Time per Case | Total Expected Commitment |
| :--- | :--- | :---: | :---: | :---: |
| **Phase 1: Pilot Review (Recommended)** | Representative sample across all 5 strata | **6 Cases** | 15–20 minutes | **~1.5 to 2.0 hours** |
| **Phase 2: Comprehensive Review** | Complete benchmark evaluation | **20 Cases** (Remaining) | 12–15 minutes | **~4.0 to 5.0 hours** |

Reviewers may choose to participate in the initial 6-case pilot only, or proceed to the full 26-case benchmark. Evaluations are performed asynchronously in a structured CSV review template.

---

## 3. Preliminary Triage vs. Final Adjudication

It is essential to understand the operational distinction between **Preliminary Triage** and **Final Adjudication**:

```
[REVIEW LIFECYCLE FLOW]
1. PRELIMINARY TRIAGE (Phase 1 / Individual Review)
   - Conducted by: Individual Reviewers (Reviewer 1 & Reviewer 2 independently)
   - Question: "Based on currently available evidence, is this candidate mapping supported, plausible, incorrect, or a domain gap?"
   - Output: Independent reviewer decision label, confidence rating (1–5), cited text, and rationale.
   ▼
2. AUTOMATED CONSENSUS IMPORT (CLI Tool)
   - Evaluates: Agreement between Reviewer 1 and Reviewer 2.
   - Classification: Consensus reached vs. Discordant / Conflicting.
   ▼
3. FINAL ADJUDICATION (Phase 2 / Consensus & Panel Resolution)
   - Conducted by: Adjudication Panel (Joint resolution of discordant cases or escalation).
   - Question: "What is the final, definitive ground-truth label and target competency for the benchmark dataset?"
   - Output: Authoritative ground-truth label locked into the benchmark registry.
```

Reviewers do **not** need to force a final consensus during triage. If evidence is ambiguous, incomplete, or absent, the correct professional judgment is to record `plausible_insufficient_evidence` or `unresolved_conflicting_evidence` and state the missing requirements.

---

## 4. Approved Decision Labels (Controlled Vocabulary)

To ensure machine validation and statistical agreement measurement (Cohen's Kappa), reviewers must select **strictly one** of the five approved labels:

```
[THE 5 APPROVED DECISION LABELS]
├── 1. supported_mapping
│      Syllabus/outcomes explicitly prove alignment with KCM competency & sub-theme.
├── 2. plausible_insufficient_evidence
│      Topic appears relevant, but available evidence lacks session detail or assessment rubrics.
├── 3. incorrect_mapping
│      Course content directly contradicts the proposed KCM competency.
├── 4. no_applicable_kcm_competency
│      Course covers specialized official statistics or technical domain outside civil service KCM.
└── 5. unresolved_conflicting_evidence
       Available evidence presents contradictory curricular objectives or multi-cadre divergence.
```

### Detailed Evaluation Criteria:

1. **`supported_mapping`**:
   - *Requirement*: Level 3 (granular session outline) or Level 4 (learning outcomes) evidence is available and directly demonstrates the knowledge, skills, or behaviours defined in KCM.
   - *Citing*: Must cite specific module numbers, session titles, or verbatim learning outcome sentences.
2. **`plausible_insufficient_evidence`**:
   - *Requirement*: The course title or broad topic is plausibly related, but available documentation is limited to Level 1 (title/metadata) or Level 2 (calendar summary).
   - *Standard*: A 15-minute video or high-level prospectus paragraph cannot be labeled `supported_mapping`.
3. **`incorrect_mapping`**:
   - *Requirement*: The course curriculum covers a distinct administrative subject that does not align with the asserted KCM competency (e.g., mapping statutory procurement of civil works to "Information Technology").
4. **`no_applicable_kcm_competency`**:
   - *Requirement*: The course covers technical domain subject matter unique to official statistics (e.g., NSS multi-stage sampling weights, HCES item aggregation, ASI factory schedules) for which no generic civil service KCM competency exists.
   - *Purpose*: Prevents forcing domain-specific official statistical functions into generic civil service buckets.
5. **`unresolved_conflicting_evidence`**:
   - *Requirement*: Primary evidence shows internal conflict, overlapping candidate competencies that cannot be disambiguated, or cross-cadre divergence requiring curriculum split.

---

## 5. Reviewer Evaluation Protocol: Step-by-Step

For each assigned benchmark case:

1. **Inspect Course Identity & Cadre**:
   - Examine the Course Name, listed Cadre / Target Role, nominal duration, and Listed Provider.
   - Note the administrative seniority (e.g., Joint Secretary vs. Assistant Director vs. Clerical Assistant).
2. **Review Candidate Competency & Definition**:
   - Read the candidate KCM Competency Name, Competency Type (Functional / Behavioural), and official CBC definition.
   - Inspect any alternative candidates or documented boundary overlaps.
3. **Examine Available Evidence**:
   - Review the verified excerpt, evidence institution, and current acquisition status.
   - Note whether the evidence is a local gazetted manual (`verified_local_source`) or an unverified portal summary (`external_reference_unverified`).
4. **Apply Conflation Safeguards**:
   - **Subject-Matter Relevance vs. Competency Alignment**: A course on "Data Analytics" does not automatically teach official statistics survey methodology.
   - **Nominal Title vs. Behavioral Depth**: A course titled "Leading with Collaboration" may only provide high-level conceptual awareness rather than verified collaborative mastery.
5. **Record Your Judgment**:
   - Enter your **Decision Label** (one of the 5 approved labels).
   - If suggesting an alternative competency, specify the valid `KCM-FUNC-##` or `KCM-BEH-##` identifier.
   - Enter your **Confidence Rating** on an integer scale from 1 (Speculative / Low) to 5 (Definitive / Level 4 Evidenced).
   - Write a concise **Expert Rationale** (2–4 sentences) citing specific evidence or explaining evidentiary gaps.
   - Enter any **Requisition Notes** identifying documents needed if evidence was insufficient.

---

## 6. Blind Dual-Review & Ethical Commitments

To preserve scientific validity and civil service governance standards:
- **Independent Evaluation**: Reviewers must evaluate cases independently without consulting other reviewers or inspecting prior reviewer labels.
- **No Hallucination**: Do not assume unstated course modules or unverified learning outcomes. If an item is not documented in the evidence packet, treat it as unverified.
- **Conflict of Interest**: Reviewers who designed, authored, or formally delivered any listed training course must declare an interest and recuse themselves from adjudicating that specific case.
- **Data Protection**: Unreleased course materials or learner data accessed under official auspices must be treated with appropriate confidentiality.

---

## 7. How to Submit Your Evaluation

1. You will receive a pre-populated CSV review packet named `expert_triage_packet_<your_reviewer_id>.csv`.
2. Open the file in your preferred spreadsheet editor (Microsoft Excel, LibreOffice Calc) or text editor with UTF-8 encoding.
3. Populate strictly the designated reviewer columns:
   - `r1_expert_decision_label` (or `r2_...`)
   - `r1_expert_target_kcm_id`
   - `r1_expert_target_kcm_name`
   - `r1_expert_subtheme`
   - `r1_evidence_sufficiency_verdict` (`sufficient` | `insufficient`)
   - `r1_depth_assessment` (`awareness` | `operational` | `mastery` | `insufficient_evidence`)
   - `r1_confidence_rating` (`1` to `5`)
   - `r1_expert_rationale` (text)
   - `r1_requisition_notes` (text)
4. Do not alter any existing case metadata, course IDs, or primary source citations.
5. Return the completed CSV via official government email to:  
   `[Insert Designated Platform Operator Email: e.g., capacitybuilding.mospi@gov.in]`

We express our sincere gratitude for your contribution to establishing rigorous, evidence-grounded competency standards for India's Official Statistical System.
