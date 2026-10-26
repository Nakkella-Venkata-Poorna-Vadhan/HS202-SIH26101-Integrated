# MoSPI ACBP Benchmark: Case-by-Case Evidence Acquisition Tracker (Stage 3.6)

> [!IMPORTANT]
> **Operational Purpose**: Dynamic administrative ledger for tracking institutional evidence requests, receipt milestones, verification states, and responsible contact channels across the 26 benchmark cases.  
> **Source Baseline**: [`data/interim/expert_triage_packet.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/expert_triage_packet.csv) and [`data/interim/course_evidence_ledger.csv`](file:///d:/Projects/SIH26101/SIH26101-Skill-Intelligence/data/interim/course_evidence_ledger.csv).  
> **Integrity Constraint**: Placeholders (`[Insert ...]`) are designated for administrative signatories, request dispatches, and follow-up target dates. No contact or receipt status is assumed without verified primary custody.

---

## 1. Tracker Overview & Status Definitions

```
[EVIDENCE ACQUISITION WORKFLOW STATES]
1. REQUEST DISPATCH:  [Pending] ➔ [Dispatched] ➔ [Follow-up Required]
2. RECEIPT STATUS:    [Awaiting Submission] ➔ [Received - Unverified] ➔ [Verified & Ingested]
3. EVIDENCE TIER:     Level 1 (Metadata) | Level 2 (Summary) | Level 3 (Session Syllabus) | Level 4 (Outcomes/Rubrics)
```

- **Current Status**:
  - `verified_local_source`: Physical document exists in repository `data/raw/` with verified page-level citation (Cases 021, 024, 025).
  - `external_reference_unverified`: Secondary circular or manual catalogued in metadata, but physical document not mirrored in `data/raw/` (14 cases).
  - `access_restricted`: Hosted on `portal.igotkarmayogi.gov.in` behind civil service Parichay Single Sign-On (9 cases).
- **Target Evidence Level**: The minimum evidentiary tier necessary to support definitive expert adjudication.

---

## 2. Master Evidence Acquisition Ledger (26 Benchmark Cases)

| Case ID | Course Record ID & Course Name | Target Cadre | Listed Provider / Institution | Current Evidence Status | Target Evidence Level | Specific Requested Evidence Item | Responsible Contact Channel Placeholder | Request Dispatch Date | Target Follow-Up Date | Receipt / Verification Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :---: | :---: | :--- |
| **BM-CASE-001** | `ACBP-CRS-017`<br>Leading with Collaboration: Sahakaryata in Public Service | DDG / JS+ | Capacity Building Commission (CBC) | `access_restricted` | **Level 3** | Full iGOT session plan, video transcripts, and collaborative governance indicators | `[Insert CBC Nodal Officer: info-cbc@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-002** | `ACBP-CRS-036`<br>Leadership in Project Management | Director / JD | ATI Mysuru | `external_reference_unverified` | **Level 3** | Exact 18-minute iGOT module syllabus and executive project governance topics | `[Insert ATI Director: director.ati@karnataka.gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Secondary Prospectus Verified) |
| **BM-CASE-003** | `ACBP-CRS-040`<br>Strategic Leadership: The Indic Way | Director / JD | CBC / IIM Calcutta | `external_reference_unverified` | **Level 3** | 81-minute iGOT lesson plan, case study readings, and Rajadharma ethics outlines | `[Insert CBC Nodal Officer: info-cbc@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (High-level framework verified) |
| **BM-CASE-004** | `ACBP-CRS-041`<br>Leading with Collaboration: Sahakaryata in Public Service | Director / JD | Capacity Building Commission (CBC) | `access_restricted` | **Level 3** | Director-level session outline and practice assignments from iGOT | `[Insert CBC Nodal Officer: info-cbc@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-005** | `ACBP-CRS-060`<br>Strategic Leadership: The Indic Way | DS / US | CBC / iGOT Karmayogi | `external_reference_unverified` | **Level 3** | Middle-management session outline and administrative decision-making topics | `[Insert CBC Nodal Officer: info-cbc@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (High-level framework verified) |
| **BM-CASE-006** | `ACBP-CRS-061`<br>Leading with Collaboration: Sahakaryata in Public Service | DS / US | Capacity Building Commission (CBC) | `access_restricted` | **Level 3** | Deputy Secretary-level session outline and collaborative exercise rubrics | `[Insert CBC Nodal Officer: info-cbc@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-007** | `ACBP-CRS-014`<br>Developing a Positive Work Culture | DDG / JS+ | DoPT / iGOT Karmayogi | `access_restricted` | **Level 3** | 35-minute module outline to test behavioural indicators vs. general advice | `[Insert DoPT Training Division: dopt-training@nic.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-008** | `ACBP-CRS-022`<br>Yoga Break at Workplace | DDG / JS+ | Morarji Desai National Institute of Yoga (MDNIY) | `external_reference_unverified` | **Level 2** | Y-Break training manual and official confirmation of civil service competency scope | `[Insert MDNIY Director: mdniy@yahoo.com]` | `[Insert Date]` | `[Insert Date]` | Level 2 Manual Catalogued (Physical copy pending) |
| **BM-CASE-009** | `ACBP-CRS-023`<br>Happiness in Seva-Bhava: Lessons from Bhagavad-Gita | DDG / JS+ | Capacity Building Commission (CBC) | `access_restricted` | **Level 3** | 32-minute course lesson plan to test Service Orientation (KCM-BEH-07) alignment | `[Insert CBC Nodal Officer: info-cbc@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-010** | `ACBP-CRS-043`<br>Leading from Within: Behavioural Strategies for Self-Leadership | Director / JD | iGOT Karmayogi / Karmayogi Bharat | `access_restricted` | **Level 3** | 48-minute session plan and self-regulation exercises | `[Insert Karmayogi Bharat: support.karmayogi@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-011** | `ACBP-CRS-125`<br>The Art of Listening | SSO / SO / AO | iGOT Karmayogi / Karmayogi Bharat | `access_restricted` | **Level 3** | 28-minute module outline covering active listening exercises | `[Insert Karmayogi Bharat: support.karmayogi@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-012** | `ACBP-CRS-142`<br>Revisiting Gender Equality through the Indian Spiritual Vision | JSO / ASO | Capacity Building Commission (CBC) | `access_restricted` | **Level 3** | 45-minute course syllabus and workplace diversity discussion prompts | `[Insert CBC Nodal Officer: info-cbc@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-013** | `ACBP-CRS-008`<br>Conduct of Inquiry in Disciplinary Matters | DDG / JS+ | Institute of Secretariat Training & Management (ISTM) | `external_reference_unverified` | **Level 4** | Complete ISTM CIDM training circular, CCS (CCA) 1965 case studies, and inquiry report rubrics | `[Insert Director ISTM: training-istm@gov.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Syllabus Catalogued (Full manual pending) |
| **BM-CASE-014** | `ACBP-CRS-010`<br>Fundamentals of Public Policy | DDG / JS+ | DoPT / CBC | `external_reference_unverified` | **Level 3** | 90-minute course module outline to determine Policy Architecture vs. Formulation | `[Insert DoPT Training Division: dopt-training@nic.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (High-level match catalogued) |
| **BM-CASE-015** | `ACBP-CRS-011`<br>Project Appraisal and Financial Evaluation Techniques | DDG / JS+ | AJ-NIFM | `external_reference_unverified` | **Level 4** | AJ-NIFM MDP syllabus covering NPV, IRR, risk models, and Central Sector scheme guidelines | `[Insert Director AJ-NIFM: mdp@nifm.ac.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Syllabus Catalogued (Full manual pending) |
| **BM-CASE-016** | `ACBP-CRS-013`<br>Navigating Parliamentary Questions | DDG / JS+ | Lok Sabha / PRIDE | `external_reference_unverified` | **Level 3** | PRIDE training manual on Starred/Unstarred question processing and assurance tracking | `[Insert Head PRIDE: pride@sansad.nic.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Manual Catalogued (Physical copy pending) |
| **BM-CASE-017** | `ACBP-CRS-053`<br>Procurement of Works | DS / US | GeM / AJ-NIFM | `external_reference_unverified` | **Level 4** | GFR 2017 Works manual, EPC contract standard bidding documents, and evaluation rubrics | `[Insert GeM Helpdesk: helpdesk-gem@gov.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Syllabus Catalogued (Full manual pending) |
| **BM-CASE-018** | `ACBP-CRS-055`<br>FRSR Part I General Rules | DS / US | Institute of Secretariat Training & Management (ISTM) | `external_reference_unverified` | **Level 3** | ISTM modular circular on FR 1–130, pay fixation (FR 22), lien, and deputation rules | `[Insert Director ISTM: training-istm@gov.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Syllabus Catalogued (Full manual pending) |
| **BM-CASE-019** | `ACBP-CRS-057`<br>AI for Presentations | DS / US | iGOT Karmayogi / Karmayogi Bharat | `access_restricted` | **Level 3** | 35-minute module outline covering presentation structuring and digital tools | `[Insert Karmayogi Bharat: support.karmayogi@gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (Behind Parichay SSO) |
| **BM-CASE-020** | `ACBP-CRS-001`<br>Introduction to Big Data in Governance | DDG / JS+ | NeGD / MeitY | `external_reference_unverified` | **Level 3** | NeGD course summary covering data lakes, analytics architectures, and governance | `[Insert NeGD Division: negd@digitalindia.gov.in]` | `[Insert Date]` | `[Insert Date]` | Awaiting Submission (High-level summary catalogued) |
| **BM-CASE-021** | `ACBP-CRS-046`<br>Know Your Ministry MoSPI | DS / US | MoSPI / NSSTA | `verified_local_source` | **Level 2** | MoSPI Annual Report 2023–24 Ch. 1 & 7 verified in local repo (`SRC-MOSPI-AR-2023-24`) | `[Verified Local Archive: data/raw/NSSTA AnnualReport...]` | 2026-10-25 | 2026-10-25 | **Verified & Ingested Locally** |
| **BM-CASE-022** | `ACBP-CRS-067`<br>Handling Unit Level Data of HCES | AD / DD | NSSTA / NSSO | `external_reference_unverified` | **Level 4** | NSSTA Schedule 1.0 extraction manual, sampling weight formulas, and STATA/R scripts | `[Insert Head NSSTA: nssta-mospi@gov.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Manual Catalogued (Official physical guide pending) |
| **BM-CASE-023** | `ACBP-CRS-069`<br>Handling Unit Level Data of ASI | AD / DD | NSSTA / IS Wing | `external_reference_unverified` | **Level 4** | NSSTA ASI schedule manual, NIC-2008 block linkage, and Value Added computation scripts | `[Insert Head NSSTA: nssta-mospi@gov.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Manual Catalogued (Official physical guide pending) |
| **BM-CASE-024** | `ACBP-CRS-072`<br>Introduction to R and Python Programming_ | AD / DD | NSSTA | `verified_local_source` | **Level 3** | NSSTA Advance Training Calendar Page 2 verified in local repo (`SRC-NSSTA-TRG-CAL-2025-26`) | `[Verified Local Archive: data/raw/Circular_NSSTA...]` | 2026-10-25 | 2026-10-25 | **Verified & Ingested Locally** |
| **BM-CASE-025** | `ACBP-CRS-093`<br>Noting and Drafting [Supervisory Staff] | Sr. PPS / SO / AO | ISTM / NSSTA | `verified_local_source` | **Level 4** | NSSTA Advance Calendar Page 3 verified locally; ISTM CSMOP 16th Ed. supervisory syllabus catalogued | `[Verified Local Archive: data/raw/Circular_NSSTA...]` | 2026-10-25 | 2026-10-25 | **Verified & Ingested Locally** |
| **BM-CASE-026** | `ACBP-CRS-170`<br>Noting and Drafting [Clerical Staff] | UDC / LDC / Assistants | ISTM | `external_reference_unverified` | **Level 3** | ISTM clerical foundation syllabus on routine docketing, referencing, and e-Office filing | `[Insert Director ISTM: training-istm@gov.in]` | `[Insert Date]` | `[Insert Date]` | Level 3 Syllabus Catalogued (Full manual pending) |

---

## 3. Weekly Operator Follow-Up Checklist

The platform operator must review this tracker weekly:
1. **Check Aging Requests**: Flag any request dispatched > 10 working days without response for formal administrative follow-up.
2. **Examine Received Artifacts**: Verify if received documents satisfy the minimum required evidence level (Tier 3 or 4) before marking as `Verified & Ingested`.
3. **Log Checksums**: When a physical PDF or document is received, immediately compute SHA256 checksum, place under `data/interim/evidence_docs/`, and register in `data/interim/course_evidence_ledger.csv`.
4. **Trigger Reviewer Dispatch**: When evidence for a case is elevated from `access_restricted` or `external_reference_unverified` to `Verified & Ingested`, notify assigned SMEs.
