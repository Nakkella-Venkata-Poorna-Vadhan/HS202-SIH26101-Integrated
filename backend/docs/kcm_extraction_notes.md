# Karmayogi Competency Model (KCM) — Extraction Notes & Review Report

## 1. Executive Summary
- **Source Document:** `data/raw/KCM-Output_RestructuredOct17.pdf`
- **Stable Source ID:** `SRC-CBC-KCM-2024`
- **Total Competencies Extracted:** 34
  - **Behavioural Competencies:** 13 (8 Core + 5 Leadership)
  - **Functional Competencies:** 21
- **Total Sub-Themes / Behaviours Extracted:** 110
- **Explicit Competency Levels Defined in Source:** **None** (Explicitly confirmed)
- **Validation Status:** All records marked `pending_review`

---

## 2. Structure and Organization of the Source Document

The Karmayogi Competency Model (KCM) is structured as follows:
1. **Core Virtues (Guṇas):** The foundational philosophical framework defines four virtues:
   - *Svādhyāya* (Self)
   - *Sahakāryatā* (Team / Collaboration)
   - *Rājyakarma* (Workplace / Systems)
   - *Svadharma* (Citizen / Public Good)
2. **Three Spheres of Competency:**
   - **Behavioural Competencies:** Key traits expected across all civil service roles.
   - **Functional Competencies:** Cross-cutting knowledge and skills common across ministries.
   - **Domain Competencies:** Explicitly declared as **OUTSIDE THE SCOPE** of KCM (Page 4, Page 24). In accordance with data integrity rules, no domain competencies were fabricated.
3. **Two-Page Layout Convention in Annexures (Pages 38 to 107):**
   - **Odd Page (Definition):** Full competency title, official Definition paragraph, and category.
   - **Even Page (Sub-Themes):** Sub-theme titles and detailed behavioural indicator statements.

---

## 3. Explicit Competency Level Scale Findings

> [!IMPORTANT]
> **Finding on Competency Levels:**
> The KCM source PDF does **NOT** define graded proficiency levels (e.g., Level 1 to 5, Beginner, Intermediate, Advanced).
> While occasional descriptive phrases like 'highest level of proficiency' appear in descriptive text, there is no level hierarchy or scale.
> In strict compliance with extraction rules ('Do not invent descriptions, behaviours, competency levels or assessment criteria'), `level_information` is set to `null` across all records.

---

## 4. Source Layout Anomalies & Extraction Notes

| Competency ID | Competency Name | Source Pages | Anomaly / Layout Note |
| :--- | :--- | :--- | :--- |
| `KCM-FUNC-04` | Govt Program Formulation | 72, 73 | Definition heading reads `'Govt Program Formulation'`, while summary pages (p29, p34) read `'Government Program Formulation'`. The verbatim title from the definition page was retained. |
| `KCM-FUNC-05` | Project Management | 74, 75 | Summary page 30 lists 3 bullets (`Project Planning`, `Project Implementation`, `Project Evaluation & Monitoring`). Detailed Annexure page 75 presents 4 distinct panels (`Project Planning`, `Project Implementation`, `Project Evaluation`, `Project KPIs Monitoring`). All 4 distinct source panels were preserved. |
| `KCM-FUNC-13` | Office Management | 90, 91 | Definition text on page 90 is identical to pages 92 and 94 due to source document authoring reuse of Central Secretariat Manual of Office Procedures (CSMOP) text. Sub-themes on page 91 are distinct. |
| `KCM-FUNC-14` | Handling Parliamentary Matters | 92, 93 | Definition text on page 92 is identical to Office Management (page 90). The 2 sub-themes on page 93 are distinct. |
| `KCM-FUNC-15` | Handling RTI Matters | 94, 95 | Definition text on page 94 is identical to Office Management (page 90). The 2 sub-themes on page 95 are distinct. |
| `KCM-FUNC-21` | Administration Matters | 106, 107 | **Document Header Error:** Page 107 errantly carries the header title `'Change Management Sub-Themes'` copied from page 105. However, the sub-themes listed are Allowances & Reimbursements, Leave & Travel, Misc Matters, and Official Language, matching Administration Matters. |

---

## 5. Ingested Competencies Inventory

| ID | Competency Name | Type | Sub-Themes Count | Source Pages | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `KCM-BEH-01` | Self-Awareness | `behavioural` | 4 | `[39, 40]` | `pending_review` |
| `KCM-BEH-02` | Personal Effectiveness | `behavioural` | 3 | `[41, 42]` | `pending_review` |
| `KCM-BEH-03` | Solution Orientation | `behavioural` | 3 | `[43, 44]` | `pending_review` |
| `KCM-BEH-04` | Communication | `behavioural` | 4 | `[45, 46]` | `pending_review` |
| `KCM-BEH-05` | Outcome Orientation | `behavioural` | 4 | `[47, 48]` | `pending_review` |
| `KCM-BEH-06` | Collaboration | `behavioural` | 3 | `[49, 50]` | `pending_review` |
| `KCM-BEH-07` | Service Orientation | `behavioural` | 3 | `[51, 52]` | `pending_review` |
| `KCM-BEH-08` | Operational Excellence | `behavioural` | 4 | `[53, 54]` | `pending_review` |
| `KCM-BEH-09` | Creativity & Innovation | `behavioural` | 2 | `[55, 56]` | `pending_review` |
| `KCM-BEH-10` | Strategic Leadership | `behavioural` | 4 | `[57, 58]` | `pending_review` |
| `KCM-BEH-11` | Collaborative Leadership | `behavioural` | 2 | `[59, 60]` | `pending_review` |
| `KCM-BEH-12` | Team Leadership | `behavioural` | 3 | `[61, 62]` | `pending_review` |
| `KCM-BEH-13` | Decision Making | `behavioural` | 2 | `[63, 64]` | `pending_review` |
| `KCM-FUNC-01` | Citizen Centricity | `functional` | 3 | `[66, 67]` | `pending_review` |
| `KCM-FUNC-02` | Policy Architecture | `functional` | 4 | `[68, 69]` | `pending_review` |
| `KCM-FUNC-03` | Cabinet Note Preparation | `functional` | 2 | `[70, 71]` | `pending_review` |
| `KCM-FUNC-04` | Govt Program Formulation | `functional` | 4 | `[72, 73]` | `pending_review` |
| `KCM-FUNC-05` | Project Management | `functional` | 4 | `[74, 75]` | `pending_review` |
| `KCM-FUNC-06` | Public Procurement (GFR) | `functional` | 4 | `[76, 77]` | `pending_review` |
| `KCM-FUNC-07` | Material Management (GFR) | `functional` | 2 | `[78, 79]` | `pending_review` |
| `KCM-FUNC-08` | Monitoring & Evaluation | `functional` | 2 | `[80, 81]` | `pending_review` |
| `KCM-FUNC-09` | Financial Management | `functional` | 4 | `[82, 83]` | `pending_review` |
| `KCM-FUNC-10` | Digital Fluency | `functional` | 2 | `[84, 85]` | `pending_review` |
| `KCM-FUNC-11` | Data Analytics | `functional` | 4 | `[86, 87]` | `pending_review` |
| `KCM-FUNC-12` | Establishment & HR | `functional` | 5 | `[88, 89]` | `pending_review` |
| `KCM-FUNC-13` | Office Management | `functional` | 5 | `[90, 91]` | `pending_review` |
| `KCM-FUNC-14` | Handling Parliamentary Matters | `functional` | 2 | `[92, 93]` | `pending_review` |
| `KCM-FUNC-15` | Handling RTI Matters | `functional` | 2 | `[94, 95]` | `pending_review` |
| `KCM-FUNC-16` | Grievance Redressal | `functional` | 2 | `[96, 97]` | `pending_review` |
| `KCM-FUNC-17` | Vigilance Administration | `functional` | 5 | `[98, 99]` | `pending_review` |
| `KCM-FUNC-18` | Litigation Management | `functional` | 3 | `[100, 101]` | `pending_review` |
| `KCM-FUNC-19` | Information & Communication Management | `functional` | 3 | `[102, 103]` | `pending_review` |
| `KCM-FUNC-20` | Change Management | `functional` | 3 | `[104, 105]` | `pending_review` |
| `KCM-FUNC-21` | Administration Matters | `functional` | 4 | `[106, 107]` | `pending_review` |
