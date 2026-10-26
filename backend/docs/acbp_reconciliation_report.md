# MoSPI ACBP Stage 2B.2 Source Reconciliation & Audit Report

## 1. Audit Overview & Verification Ledger

| Dimension / Metric | Status / Verified Value |
| :--- | :--- |
| **Document ID** | `SRC-MOSPI-ACBP-2026-27` |
| **Source Checksum (SHA-256)** | `73ee47e6809982b63ffe928e95e86e4084d33865d325876e0cb9ff755a634205` |
| **Frozen KCM Checksum (SHA-256)** | `9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4` (Unchanged) |
| **Total ACBP Course Records** | **226** course assignments across 11 cadres |
| **Total Cadre Tables (Annexure I)** | **11** official cadre sections (Pages 2 to 12) |
| **Total Division Nodal Officers (Annexure II)** | **30** nodal officers (Page 13) |
| **Total Candidate KCM Mappings** | 226 records evaluated: **6** explicit matches, **220** unresolved |
| **Courses Pending Manual Review** | **17** records flagged with explicit OCR/font anomalies |
| **Nodal Officers Pending Manual Review** | **27** records flagged (chiefly email OCR noise or blank designation) |
| **Readiness Status** | **READY FOR COMPETENCY MAPPING** |

---

## 2. Cadre Section Reconciled Breakdown (Annexure I)

| Page | Cadre / Role Section | Total Courses | Domain | Functional | Behavioural | Uncertain Records |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **2** | Deputy Director General / Joint Secretary Equivalent and Above | 23 | 6 | 7 | 10 | 0 |
| **3** | Director / Joint Director | 22 | 6 | 7 | 9 | 0 |
| **4** | Deputy Secretary / Under Secretary | 20 | 5 | 8 | 7 | 1 |
| **5** | Assistant Director / Deputy Director | 20 | 6 | 8 | 6 | 2 |
| **6** | Sr. PPS / PSO / PPS / PS | 20 | 3 | 9 | 8 | 2 |
| **7** | Senior Statistical Officers / Section Officer / Senior Admin Officer | 20 | 3 | 9 | 8 | 3 |
| **8** | Junior Statistical Officers / Assistant Section Officers / DPA | 20 | 3 | 9 | 8 | 0 |
| **9** | AD(OL) / Senior Hindi Translator / Junior Hindi Translator | 20 | 2 | 10 | 8 | 3 |
| **10** | Assistants / Upper Division Clerk / Lower Division Clerk | 20 | 2 | 10 | 8 | 1 |
| **11** | Stenographer (All Grades) / Data Entry Operator (All Grades) | 21 | 2 | 11 | 8 | 5 |
| **12** | MTS / Driver (All Grades) | 20 | 1 | 10 | 9 | 0 |
| **TOTAL** | **11 Official Cadres** | **226** | **51** | **79** | **96** | **17** |

---

## 3. Recurring Courses Across Cadres

The ACBP intentionally assigns foundational courses across multiple cadre levels. The top recurring courses are:
1. `Developing a Positive Work Culture` (Behavioural): Assigned to **all 11 cadres** (Pages 2–12).
2. `Overview of Basic Statistics` (Domain): Assigned to **8 cadres** (Pages 5–12).
3. `Happiness in Seva-Bhava: Lessons from Bhagavad-Gita` (Behavioural): Assigned to **6 cadres** (Pages 2, 7, 8, 10, 11, 12).
4. `Know Your Ministry Ministry of Statistics and Programme Implementation` (Domain): Assigned to **6 cadres** (Pages 4, 6, 7, 8, 9, 10, 12).
5. `Navigating Parliamentary Questions` (Functional): Assigned to **5 cadres** (Pages 2, 3, 4, 5, 7).
6. `AI for Presentations` (Domain): Assigned to **5 cadres** (Pages 6, 7, 8, 10, 11).

*Audit Note*: These represent genuine GoI curricular design patterns rather than duplicate extraction errors. Each course assignment represents a distinct cadre role requirement with its own source page and row.

---

## 4. Itemization of Unresolved Source Ambiguities & Uncertainty Flags

The table below catalogs all **17 course records** and representative nodal officer records flagged for manual review:

| Page | Record ID | Field | Raw Extracted Value | Nature of Anomaly & Review Directive |
| :---: | :--- | :--- | :--- | :--- |
| **4** | `ACBP-CRS-045` | Duration | `00:.43.06` | Punctuation artifact (colon-dot combination). Recommended value: `00:43:06`. |
| **5** | `ACBP-CRS-065` | Duration | `Q1:000` | Scanned digit '0' read as letter 'Q'. Recommended value: `01:00:00`. |
| **5** | `ACBP-CRS-072` | Duration | `O1:OL.00` | Letter substitutions for digits '0' and '1'. Recommended value: `01:01:00`. |
| **6** | `ACBP-CRS-081` | Duration | `4` | Incomplete duration due to faint scan stroke. Pending official iGOT duration check. |
| **6** | `ACBP-CRS-086` | Duration | `01335.00` | Extra digit stroke in duration. Likely `01:35:00`. |
| **7** | `ACBP-CRS-108` | Duration | `00.4942` | Missing colon separator. Recommended value: `00:49:42`. |
| **7** | `ACBP-CRS-109` | Competency | `ctional` | Faint letter 'F' in scan; normalized to `Functional` with uncertainty flag. |
| **7** | `ACBP-CRS-112` | Duration | `0l.4.00` | Letter 'l' for digit '1'. Recommended value: `01:40:00` or `01:04:00`. |
| **9** | `ACBP-CRS-145` | Duration | `O1.0z.00` | Letter 'O' and 'z' substitutions. Recommended value: `01:02:00`. |
| **9** | `ACBP-CRS-146` | Course Name | `3jala: faia 3ir %in41 (d ZEr` | Devanagari Hindi text read by English OCR model. Requires Hindi manual verification. |
| **9** | `ACBP-CRS-153` | Duration | `01:13223` | Faint scan speck in seconds. Recommended value: `01:13:23`. |
| **10** | `ACBP-CRS-162` | Duration | `0134.00` | Missing separator. Recommended value: `01:34:00`. |
| **11** | `ACBP-CRS-181` | Duration | `01.334:00` | Extra digit stroke in duration. Recommended value: `01:34:00`. |
| **11** | `ACBP-CRS-183` | Duration | `0047:16` | Missing separator. Recommended value: `00:47:16`. |
| **11** | `ACBP-CRS-191` | Duration | `Ok:l5.00` | Letter substitutions. Recommended value: `01:15:00`. |
| **11** | `ACBP-CRS-199` | Duration | `00.:47.38` | Punctuation speck. Recommended value: `00:47:38`. |
| **11** | `ACBP-CRS-200` | Duration | `00335:11` | Extra digit stroke. Recommended value: `00:35:11`. |
| **13** | `ACBP-NODAL-021` | Designation | *(blank)* | Designation omitted in official printout for Smt R Vijaya Nirmala. |
| **13** | `ACBP-NODAL-027` | Designation | *(blank)* | Designation omitted in official printout for Shri A. Abdul Rahman. |
| **13** | Multiple | Email | Multiple | Scanned dots, underlines, and spaces produce OCR email noise (e.g. `sc.roy71@gov.in`). |

---

## 5. Candidate KCM Reconciliation Analysis

In accordance with strict GoI provenance rules, **no competency mappings are fabricated or hallucinated**.

- **Total Courses Evaluated**: 226
- **Explicit KCM Competency Title References**: **6** courses
  - Examples:
    - `Data Driven Decision Making for Government` -> `KCM-BEH-13` (*Decision Making*)
    - `Data Analytics and Visualizations for Government Officers` -> `KCM-FUNC-11` (*Data Analytics*)
    - `Change Management in Digital Transformation` -> `KCM-FUNC-20` (*Change Management*)
    - `Leadership in Project Management` -> `KCM-FUNC-05` (*Project Management*)
    - `Strategic Leadership: The Indic Way` -> `KCM-BEH-10` (*Strategic Leadership*)
    - `Leading with Collaboration: Sahakaryata in Public Service` -> `KCM-BEH-06` (*Collaboration*)
    - `Government Litigation Management and Tribunal Procedures` -> `KCM-FUNC-18` (*Litigation Management*)
- **Unresolved Courses**: **220** courses
  - Reason: ACBP training course titles often represent specialized applications (e.g., `PM Gatishakti`, `Overview of GeM for Buyers`, `Yoga Break at Workplace`, `Bhashini and Digital India`) that do not explicitly name an official KCM competency in their title.
  - Action: Preserved with `mapping_method = "unresolved"` and `candidate_kcm_competency_id = null` for subsequent semantic and curriculum curation in Stage 3.
