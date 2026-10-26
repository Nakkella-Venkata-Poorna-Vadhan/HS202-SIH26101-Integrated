"""
MoSPI ACBP to KCM Competency Mapping Human Adjudication Packet Builder (Stage 3.4.2 / 3.4.3).

Constructs the comprehensive human-adjudication package for the 26-case benchmark.
Adheres strictly to the 6-question adjudication decision process:
  1. Course identity: Exact course, related course, or general subject.
  2. Subject coverage: Specific topics supported by authentic evidence.
  3. Competency alignment: Precise KCM definition and behavioral sub-theme match.
  4. Evidence sufficiency: Evaluation of evidence completeness.
  5. Competency depth: Stated learning objectives, assessment, and mastery limitations.
  6. Final benchmark label: Justified benchmark label under the approved taxonomy.

Outputs:
  - data/interim/mapping_adjudication_packet.json
  - data/interim/mapping_adjudication_packet.csv
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input paths
MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
LEDGER_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_ledger.json"
AUDIT_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_provenance_audit.json"
COURSES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
EVIDENCE_PACK_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_evidence_pack.json"

# Output paths
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PACKET_JSON_PATH = INTERIM_DIR / "mapping_adjudication_packet.json"
PACKET_CSV_PATH = INTERIM_DIR / "mapping_adjudication_packet.csv"

# Immutable source hashes
EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"

# Traceable evidence source identifiers
CASE_SOURCE_IDS: Dict[str, str] = {
    "BM-CASE-001": "SRC-EXT-CBC-IGOT-2024",
    "BM-CASE-002": "SRC-EXT-ATI-MYSURU-2023",
    "BM-CASE-003": "SRC-EXT-CBC-INDIC-2024",
    "BM-CASE-004": "SRC-EXT-CBC-IGOT-2024",
    "BM-CASE-005": "SRC-EXT-CBC-INDIC-2024",
    "BM-CASE-006": "SRC-EXT-CBC-IGOT-2024",
    "BM-CASE-007": "SRC-EXT-DOPT-IGOT-2024",
    "BM-CASE-008": "SRC-EXT-AYUSH-YBREAK-2024",
    "BM-CASE-009": "SRC-EXT-CBC-SEVA-2024",
    "BM-CASE-010": "SRC-EXT-IGOT-LEADERSHIP-2024",
    "BM-CASE-011": "SRC-EXT-IGOT-LISTENING-2024",
    "BM-CASE-012": "SRC-EXT-CBC-GENDER-2024",
    "BM-CASE-013": "SRC-EXT-ISTM-CIDM-2024",
    "BM-CASE-014": "SRC-EXT-DOPT-POLICY-2024",
    "BM-CASE-015": "SRC-EXT-AJNIFM-APPRAISAL-2024",
    "BM-CASE-016": "SRC-EXT-LOKSABHA-PRIDE-2024",
    "BM-CASE-017": "SRC-EXT-GEM-WORKS-2024",
    "BM-CASE-018": "SRC-EXT-ISTM-FRSR-2024",
    "BM-CASE-019": "SRC-EXT-IGOT-AIPRES-2024",
    "BM-CASE-020": "SRC-EXT-NEGD-BIGDATA-2024",
    "BM-CASE-021": "SRC-MOSPI-AR-2023-24",
    "BM-CASE-022": "SRC-EXT-NSSTA-HCES-2024",
    "BM-CASE-023": "SRC-EXT-NSSTA-ASI-2024",
    "BM-CASE-024": "SRC-NSSTA-TRG-CAL-2025-26",
    "BM-CASE-025": "SRC-NSSTA-TRG-CAL-2025-26",
    "BM-CASE-026": "SRC-EXT-ISTM-CLERICAL-2024",
}

# Detailed case-by-case adjudication guidance specifications matching exact manifest courses
CASE_ADJUDICATION_SPECS: Dict[str, Dict[str, Any]] = {
    "BM-CASE-001": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. High-level CBC mandate covers collaborative governance, but local lesson plan is unmirrored and behind Parichay SSO.",
        "q2_subject_coverage": "Collaborative governance in public service; institutional partnership mechanisms.",
        "q3_competency_alignment": "Candidate KCM-BEH-06 (Collaboration) definition matches 'Working in tandem with others as an integral unit...', specifically Relationship Management and Knowledge Sharing sub-themes.",
        "q4_evidence_sufficiency": "Insufficient. Course metadata and title match verified, but lack of granular syllabus precludes behavioral verification.",
        "q5_competency_depth": "Duration is 1 hour 00 minutes 44 seconds. No evidence on interactive exercises, simulations, or behavioral assessment criteria.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Course title explicitly references 'Collaboration'; provider is CBC (author of KCM framework); targeted at apex executive leadership.",
        "counter_evidence_and_limitations": "Restricted behind civil service Parichay SSO; cannot prove whether course teaches deep behavioral indicators or merely conceptual awareness.",
        "alternative_kcm_candidates": "KCM-BEH-10 (Strategic Leadership), KCM-BEH-11 (Collaborative Leadership)",
        "sme_adjudication_questions": "Does a 1-hour online module impart observable behavioral collaboration for apex officers (DDG/JS+), or does it serve as an awareness briefing?",
    },
    "BM-CASE-002": {
        "q1_course_identity": "ATI Mysuru executive modules cover public project leadership, matching the general topic, but the exact 17m 58s iGOT module is unmirrored.",
        "q2_subject_coverage": "Project leadership, team steering, and outcome monitoring in development programmes.",
        "q3_competency_alignment": "Partial and ambiguous. 'Leadership' suggests KCM-BEH-10 (Strategic Leadership) or KCM-BEH-12 (Team Leadership), while 'Project Management' aligns with KCM-FUNC-05 (Project Management).",
        "q4_evidence_sufficiency": "Insufficient. 18-minute runtime is inadequate to prove functional competency development.",
        "q5_competency_depth": "Severe Limitation: An 18-minute micro-module cannot impart technical project management (PERT/CPM, GFR appraisal, risk register).",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Title contains 'Project Management' and provider is an official state Administrative Training Institute.",
        "counter_evidence_and_limitations": "Very brief runtime (17m 58s). Combines behavioral ('Leadership') and functional ('Project Management') domains.",
        "alternative_kcm_candidates": "KCM-BEH-10 (Strategic Leadership), KCM-BEH-12 (Team Leadership)",
        "sme_adjudication_questions": "Should an 18-minute module be mapped to a complex functional competency like KCM-FUNC-05, or should micro-modules below 30 minutes be classified under behavioral awareness or rejected as insufficient for competency acquisition?",
    },
    "BM-CASE-003": {
        "q1_course_identity": "CBC Indic Leadership framework verified via public executive collaborations (IIM Calcutta), but specific 1h 09m iGOT lesson plan is unverified and behind SSO.",
        "q2_subject_coverage": "Indic statecraft, ethical leadership, civilizational governance principles (Rajadharma, Arthashastra).",
        "q3_competency_alignment": "Aligns conceptually with KCM-BEH-10 (Strategic Leadership) sub-themes: Strategic Direction, Visioning, and Value-Driven Governance.",
        "q4_evidence_sufficiency": "Insufficient. High-level framework verified, but session outline unverified.",
        "q5_competency_depth": "Limitation: 1-hour conceptual module; lacks evidence on strategic execution or simulation-based assessment.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Developed under CBC Karmayogi leadership series; title explicitly targets Strategic Leadership.",
        "counter_evidence_and_limitations": "Traditional civilizational frameworks may not map cleanly onto modern public administration strategic planning indicators without lesson plan inspection.",
        "alternative_kcm_candidates": "KCM-BEH-02 (Personal Effectiveness), KCM-BEH-01 (Self-Awareness - Purposefulness)",
        "sme_adjudication_questions": "To what extent does 'Indic Way' statecraft satisfy the modern bureaucratic metrics of KCM-BEH-10 (e.g. multi-year departmental roadmapping, KPIs)?",
    },
    "BM-CASE-004": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. Cross-cadre delivery to Director / JD level. Same CBC course asset as BM-CASE-001.",
        "q2_subject_coverage": "Collaborative governance in public service; institutional partnership mechanisms.",
        "q3_competency_alignment": "Candidate KCM-BEH-06 (Collaboration) definition matches 'Working in tandem with others as an integral unit...', specifically Relationship Management and Knowledge Sharing sub-themes.",
        "q4_evidence_sufficiency": "Insufficient. Course metadata verified, but lack of granular syllabus precludes behavioral verification.",
        "q5_competency_depth": "Duration 01.00.44. No assessment criteria or learning outcomes verified locally.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Course title explicitly references 'Collaboration'; provider is CBC.",
        "counter_evidence_and_limitations": "Restricted behind Parichay SSO; cross-cadre differentiation unverified.",
        "alternative_kcm_candidates": "KCM-BEH-10 (Strategic Leadership), KCM-BEH-11 (Collaborative Leadership)",
        "sme_adjudication_questions": "Does the Director/JD cadre delivery differ in syllabus or proficiency expectation from the DDG/JS+ delivery, or is it an identical digital asset?",
    },
    "BM-CASE-005": {
        "q1_course_identity": "CBC Indic Leadership series delivered to DS / US middle management. High-level framework verified, but session plan is unverified and behind SSO.",
        "q2_subject_coverage": "Indic governance ethics, Rajadharma, administrative decision-making.",
        "q3_competency_alignment": "Candidate KCM-BEH-10 (Strategic Leadership) title matches, but applicability to middle management operational roles is debatable.",
        "q4_evidence_sufficiency": "Insufficient. Course syllabus unverified locally.",
        "q5_competency_depth": "Duration 01.09.28. No formative or summative assessment details available.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Part of CBC flagship leadership series; title contains 'Strategic Leadership'.",
        "counter_evidence_and_limitations": "Cadre DS/US rarely exercises ministry-wide strategic leadership; duties focus on branch administration and file movement.",
        "alternative_kcm_candidates": "KCM-BEH-05 (Outcome Orientation), KCM-BEH-13 (Decision Making)",
        "sme_adjudication_questions": "Is Strategic Leadership an appropriate competency target for DS/US officers whose duties are primarily operational/supervisory, or should this map to Decision Making or Team Leadership?",
    },
    "BM-CASE-006": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. Delivered to DS / US cadre. Same CBC course asset as BM-CASE-001 and BM-CASE-004.",
        "q2_subject_coverage": "Collaborative governance in public service; institutional partnership mechanisms.",
        "q3_competency_alignment": "Candidate KCM-BEH-06 (Collaboration) matches title and high-level CBC mandate.",
        "q4_evidence_sufficiency": "Insufficient. Granular syllabus restricted behind SSO.",
        "q5_competency_depth": "Duration 01.00.44. No practice exercises or workplace assessment verified.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Title contains 'Collaboration'; official CBC course asset.",
        "counter_evidence_and_limitations": "SSO access restriction prevents verification of learning depth.",
        "alternative_kcm_candidates": "KCM-BEH-11 (Collaborative Leadership), KCM-BEH-06 (Collaboration)",
        "sme_adjudication_questions": "Should identical course assets delivered across three distinct cadre tiers (DDG, Director, DS/US) receive the same competency mapping or differentiated proficiency levels?",
    },
    "BM-CASE-007": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. Highly repeated title across 11 cadres; exact lesson plan unmirrored and behind Parichay SSO.",
        "q2_subject_coverage": "Workplace culture, organizational climate, public service motivation, administrative ethics.",
        "q3_competency_alignment": "Broad organizational aspiration. Conceptually relates to KCM-BEH-06 (Collaboration) or KCM-BEH-08 (Operational Excellence) or KCM-BEH-01 (Self-Awareness), but lacks explicit sub-theme proof.",
        "q4_evidence_sufficiency": "Insufficient. Course metadata verified, but lack of granular syllabus precludes behavioral verification.",
        "q5_competency_depth": "Duration 41 minutes 24 seconds; lacks behavioral assessment criteria or observable indicators.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "Official DoPT/iGOT behavioral course prescribed in ACBP across multiple cadres.",
        "counter_evidence_and_limitations": "Broad organizational aspiration title that appears across all 11 cadres without differentiated syllabi.",
        "alternative_kcm_candidates": "KCM-BEH-06 (Collaboration), KCM-BEH-08 (Operational Excellence)",
        "sme_adjudication_questions": "Does 'Developing a Positive Work Culture' teach specific behavioral indicators under Collaboration, or is it an introductory organizational development overview?",
    },
    "BM-CASE-008": {
        "q1_course_identity": "Ministry of Ayush / MDNIY Y-Break protocol verified as official government protocol; exact 5-minute workplace module is unmirrored.",
        "q2_subject_coverage": "5-minute workplace physical stretching, mindful breathing (Pranayama), ergonomics, workplace stress alleviation.",
        "q3_competency_alignment": "Outside civil service competency model. Remotely touches KCM-BEH-01 (Self-Awareness: physical well-being), but physical wellness is not an official administrative competency in KCM 2024.",
        "q4_evidence_sufficiency": "Sufficient for physical protocol; absent for civil service competency.",
        "q5_competency_depth": "Duration 5 minutes; physical ergonomic exercise with zero administrative or behavioral learning outcomes.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "Official Ministry of Ayush / MDNIY protocol adopted by DoPT across central secretariats.",
        "counter_evidence_and_limitations": "5-minute physical protocol has no connection to civil service operational competencies.",
        "alternative_kcm_candidates": "no_applicable_kcm_competency (Wellness Gap), KCM-BEH-01 (Self-Awareness)",
        "sme_adjudication_questions": "Should 5-minute workplace physical health/wellness interventions be designated as no_applicable_kcm_competency (outside KCM scope) or retained as unresolved?",
    },
    "BM-CASE-009": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. CBC course on Seva-Bhava (32m 18s); lesson plan is unverified and behind Parichay SSO.",
        "q2_subject_coverage": "Seva-Bhava (service mindset), ethical civil service motivation, citizen-centric public service philosophy from Bhagavad-Gita.",
        "q3_competency_alignment": "Conceptually aligns with KCM-BEH-07 (Service Orientation: Citizen Focus, Empathy) or KCM-BEH-01 (Self-Awareness: Purposefulness) or KCM-FUNC-01 (Citizen Centricity).",
        "q4_evidence_sufficiency": "Insufficient. Course outline restricted behind SSO.",
        "q5_competency_depth": "Duration 32 minutes; philosophical and motivational orientation without workplace simulation.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "Official CBC Karmayogi course exploring civilizational administrative ethics.",
        "counter_evidence_and_limitations": "32-minute runtime; absence of session outline prevents verifying behavioral indicators.",
        "alternative_kcm_candidates": "KCM-BEH-07 (Service Orientation), KCM-BEH-01 (Self-Awareness), KCM-FUNC-01 (Citizen Centricity)",
        "sme_adjudication_questions": "Does philosophical Seva-Bhava map to behavioural Service Orientation (KCM-BEH-07) or functional Citizen Centricity (KCM-FUNC-01)?",
    },
    "BM-CASE-010": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. iGOT course (48m); restricted behind Parichay SSO.",
        "q2_subject_coverage": "Self-leadership, introspection, emotional regulation, proactive goal setting in administrative roles.",
        "q3_competency_alignment": "Conceptually matches KCM-BEH-01 (Self-Awareness: Self-Analysis, Self-Confidence, Purposefulness) and KCM-BEH-02 (Personal Effectiveness: Self-Management).",
        "q4_evidence_sufficiency": "Insufficient. Syllabus unmirrored locally.",
        "q5_competency_depth": "Duration 48 minutes; lacks verification of behavioral assessments or coaching frameworks.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "iGOT official behavioral curriculum addressing executive self-management.",
        "counter_evidence_and_limitations": "Restricted behind SSO; proxy mapping between Self-Awareness and Personal Effectiveness required.",
        "alternative_kcm_candidates": "KCM-BEH-01 (Self-Awareness), KCM-BEH-02 (Personal Effectiveness)",
        "sme_adjudication_questions": "Does 'Leading from Within' map primarily to Self-Awareness (KCM-BEH-01) or Personal Effectiveness (KCM-BEH-02)?",
    },
    "BM-CASE-011": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. iGOT course (28m); restricted behind Parichay SSO.",
        "q2_subject_coverage": "Active listening techniques, non-verbal listening cues, overcoming listening barriers in office communication.",
        "q3_competency_alignment": "Matches KCM-BEH-04 (Communication: Active Listening sub-theme) or KCM-BEH-06 (Collaboration: Knowledge Sharing).",
        "q4_evidence_sufficiency": "Insufficient. 28-minute module; lesson outline restricted behind SSO.",
        "q5_competency_depth": "Duration 28 minutes; introductory awareness of listening techniques.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "Official iGOT behavioral module targeting interpersonal workplace dynamics.",
        "counter_evidence_and_limitations": "Very brief runtime (28m); isolated listening skill vs comprehensive civil service communication.",
        "alternative_kcm_candidates": "KCM-BEH-04 (Communication), KCM-BEH-06 (Collaboration)",
        "sme_adjudication_questions": "Can a 28-minute module on listening be certified as developing full Communication (KCM-BEH-04) or only a foundational behavioral sub-indicator?",
    },
    "BM-CASE-012": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. CBC/iGOT course (45m); restricted behind Parichay SSO.",
        "q2_subject_coverage": "Gender equality, civilizational perspectives on gender harmony, workplace inclusivity and equity.",
        "q3_competency_alignment": "Aligns with KCM-BEH-06 (Collaboration: Diversity & Inclusion sub-theme) or KCM-BEH-02 (Personal Effectiveness: Social Awareness).",
        "q4_evidence_sufficiency": "Insufficient. Syllabus restricted behind SSO.",
        "q5_competency_depth": "Duration 45 minutes; philosophical and legal awareness.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "CBC official course addressing workplace diversity and inclusion.",
        "counter_evidence_and_limitations": "Absence of module outline; alignment to Diversity & Inclusion is conceptual.",
        "alternative_kcm_candidates": "KCM-BEH-06 (Collaboration - Diversity & Inclusion), KCM-FUNC-12 (Establishment & HR - Gender Sensitization)",
        "sme_adjudication_questions": "Does this course map to behavioural Collaboration (Diversity & Inclusion sub-theme) or functional Establishment & HR rules on gender parity?",
    },
    "BM-CASE-013": {
        "q1_course_identity": "ISTM CIDM multi-day classroom curriculum verified; exact 75-minute iGOT video is unmirrored locally.",
        "q2_subject_coverage": "CCS (CCA) Rules 1965, appointment of inquiry officer/presenting officer, framing of charges, examination/cross-examination, daily order sheets, inquiry report drafting.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-17 (Vigilance Administration) definition and disciplinary inquiry sub-themes.",
        "q4_evidence_sufficiency": "Insufficient for exact 75m course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 75 minutes; multi-day classroom material condensed into executive overview; cannot prove quasi-judicial inquiry mastery.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM official CIDM course circular verifies statutory disciplinary inquiry procedures.",
        "counter_evidence_and_limitations": "75m runtime cannot impart full inquiry officer competence.",
        "alternative_kcm_candidates": "KCM-FUNC-17 (Vigilance Administration), KCM-FUNC-18 (Litigation Management)",
        "sme_adjudication_questions": "Does a 75-minute module qualify an officer for Vigilance Administration (KCM-FUNC-17) or only foundational procedural awareness?",
    },
    "BM-CASE-014": {
        "q1_course_identity": "Public policy foundation framework exists on DoPT portal; exact 1h 30m module on iGOT is unverified and behind SSO.",
        "q2_subject_coverage": "Policy cycle, problem identification, policy instrument design, stakeholder consultation, outcome evaluation.",
        "q3_competency_alignment": "Matches KCM-FUNC-02 (Policy Architecture) and secondary KCM-FUNC-04 (Govt Program Formulation).",
        "q4_evidence_sufficiency": "Insufficient. Exact iGOT module unmirrored locally.",
        "q5_competency_depth": "Duration 1 hour 30 minutes; executive overview.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "DoPT induction and mid-career training module curriculum.",
        "counter_evidence_and_limitations": "Boundary between Policy Architecture (FUNC-02) and Govt Program Formulation (FUNC-04) requires granular module verification.",
        "alternative_kcm_candidates": "KCM-FUNC-02 (Policy Architecture), KCM-FUNC-04 (Govt Program Formulation)",
        "sme_adjudication_questions": "Does 'Fundamentals of Public Policy' develop legislative and strategic policy architecture (KCM-FUNC-02) or program scheme design (KCM-FUNC-04)?",
    },
    "BM-CASE-015": {
        "q1_course_identity": "AJ-NIFM executive MDP curriculum on project appraisal verified; specific 1h 45m iGOT module remains unmirrored locally.",
        "q2_subject_coverage": "Capital budgeting, discounted cash flow (NPV, IRR), financial feasibility, cost-benefit analysis, GFR appraisal guidelines.",
        "q3_competency_alignment": "Matches KCM-FUNC-09 (Financial Management) and secondary KCM-FUNC-05 (Project Management).",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour 45 minutes; covers financial evaluation principles.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "AJ-NIFM is the Ministry of Finance's premier financial management academy.",
        "counter_evidence_and_limitations": "Dual alignment: project appraisal bridges Financial Management (FUNC-09) and Project Management (FUNC-05).",
        "alternative_kcm_candidates": "KCM-FUNC-09 (Financial Management), KCM-FUNC-05 (Project Management)",
        "sme_adjudication_questions": "Is the primary competency Financial Management (KCM-FUNC-09) or Project Management (KCM-FUNC-05)?",
    },
    "BM-CASE-016": {
        "q1_course_identity": "Documented in local source SRC-NSSTA-TRG-CAL-2025-26 (Page 7) and Lok Sabha PRIDE manual; exact 45m iGOT module unmirrored.",
        "q2_subject_coverage": "Types of questions (Starred, Unstarred, Short Notice), question admission rules, drafting replies, pad preparation, handling assurances.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-14 (Handling Parliamentary Matters) definition and sub-themes.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject relevance.",
        "q5_competency_depth": "Duration 45 minutes; executive overview without drafting exercises.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Lok Sabha PRIDE manual and NSSTA training calendar confirm curriculum.",
        "counter_evidence_and_limitations": "45m runtime; lack of assessment criteria.",
        "alternative_kcm_candidates": "KCM-FUNC-14 (Handling Parliamentary Matters)",
        "sme_adjudication_questions": "Can a 45-minute orientation certify competency in handling high-stakes Parliamentary Questions under KCM-FUNC-14?",
    },
    "BM-CASE-017": {
        "q1_course_identity": "GFR 2017 Rules 130-141 and GeM/AJ-NIFM manual cover works procurement; 1-hour iGOT module unmirrored locally.",
        "q2_subject_coverage": "GFR 2017 works chapters, Standard Bidding Documents (SBD) for EPC and Item Rate works, bid evaluation, contract management.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-06 (Public Procurement (GFR)) sub-themes.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for statutory subject relevance.",
        "q5_competency_depth": "Duration 1 hour; statutory procurement rules.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "AJ-NIFM procurement manual and GFR statutory provisions.",
        "counter_evidence_and_limitations": "Distinction between procurement of goods/services vs civil works contracts.",
        "alternative_kcm_candidates": "KCM-FUNC-06 (Public Procurement (GFR)), KCM-FUNC-07 (Material Management (GFR))",
        "sme_adjudication_questions": "Does works procurement map cleanly to Public Procurement (GFR) or does EPC contract management require separate engineering competency?",
    },
    "BM-CASE-018": {
        "q1_course_identity": "ISTM FRSR Part I curriculum verified on portal; covers rules 1-130; 90m iGOT module unmirrored.",
        "q2_subject_coverage": "Fundamental Rules & Supplementary Rules, pay fixation (FR 22), increment rules, joining time, foreign service, lien.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-12 (Establishment & HR: Service Rules sub-theme) and secondary KCM-FUNC-21 (Administration Matters).",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour 30 minutes; statutory rules overview.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM official statutory curriculum for service rules.",
        "counter_evidence_and_limitations": "Full FRSR is a massive volume; 90m course covers foundational concepts only.",
        "alternative_kcm_candidates": "KCM-FUNC-12 (Establishment & HR), KCM-FUNC-21 (Administration Matters)",
        "sme_adjudication_questions": "Should FRSR general rules be mapped to Establishment & HR (KCM-FUNC-12) or Administration Matters (KCM-FUNC-21)?",
    },
    "BM-CASE-019": {
        "q1_course_identity": "Inaccessible online micro-course on iGOT Karmayogi. iGOT course on AI presentations (35m); restricted behind Parichay SSO.",
        "q2_subject_coverage": "Slide structuring, AI-assisted graphic generation, summary generation, digital presentation design tools.",
        "q3_competency_alignment": "Matches KCM-FUNC-10 (Digital Fluency: Digital Office Tools sub-theme).",
        "q4_evidence_sufficiency": "Insufficient. Syllabus restricted behind SSO.",
        "q5_competency_depth": "Duration 35 minutes; narrow productivity tool utility.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "Official iGOT emerging tech module.",
        "counter_evidence_and_limitations": "35-minute runtime; narrow software utility vs broad civil service digital fluency.",
        "alternative_kcm_candidates": "KCM-FUNC-10 (Digital Fluency), KCM-FUNC-19 (Information & Communication Management)",
        "sme_adjudication_questions": "Is an AI presentation tool course a legitimate civil service competency under Digital Fluency (KCM-FUNC-10) or a software micro-skill?",
    },
    "BM-CASE-020": {
        "q1_course_identity": "NeGD course (46m 21s); high-level framework verified; exact iGOT session plan is unverified and behind SSO.",
        "q2_subject_coverage": "Big data architectures, data lakes, public sector data governance, predictive analytics use cases.",
        "q3_competency_alignment": "Overlaps with KCM-FUNC-10 (Digital Fluency) and KCM-FUNC-11 (Data Analytics). ACBP categorized this as 'Domain', but NeGD created it for generic governance.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 46m 21s; high-level executive briefing.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "NeGD official digital governance training framework.",
        "counter_evidence_and_limitations": "ACBP classified under Domain; cannot be declared an official statistics domain gap without inspecting module outline.",
        "alternative_kcm_candidates": "KCM-FUNC-10 (Digital Fluency), KCM-FUNC-11 (Data Analytics)",
        "sme_adjudication_questions": "Why did MoSPI classify generic Big Data governance under 'Domain' instead of 'Functional'? Does it map to KCM-FUNC-10 or KCM-FUNC-11?",
    },
    "BM-CASE-021": {
        "q1_course_identity": "MoSPI mandate verified in local source SRC-MOSPI-AR-2023-24.json and NSSTA induction calendar; 45m iGOT module unmirrored.",
        "q2_subject_coverage": "Institutional structure of MoSPI, Allocation of Business Rules, National Statistical Commission (NSC), Central Statistics Office (CSO), National Sample Survey Office (NSSO), Twenty Point Programme.",
        "q3_competency_alignment": "Specific to MoSPI institutional machinery. KCM 2024 has no ministry-specific domain competency.",
        "q4_evidence_sufficiency": "Sufficient for institutional mandate; confirms absence from generic civil service KCM.",
        "q5_competency_depth": "Duration 45 minutes; institutional induction overview.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "Official MoSPI Annual Report and NSSTA induction materials.",
        "counter_evidence_and_limitations": "Represents organizational orientation rather than behavioral/functional competency.",
        "alternative_kcm_candidates": "no_applicable_kcm_competency (MoSPI Domain Gap), KCM-FUNC-21 (Administration Matters)",
        "sme_adjudication_questions": "Does ministry induction represent an official statistics Domain gap (no_applicable_kcm_competency) or generic Administration Matters (KCM-FUNC-21)?",
    },
    "BM-CASE-022": {
        "q1_course_identity": "NSSTA training manual and NSS Schedule 1.0 verify official survey methodology; exact 2-hour iGOT video unmirrored.",
        "q2_subject_coverage": "Household Consumption Expenditure Survey (HCES), microdata record layout, Monthly Per Capita Consumer Expenditure (MPCE), sampling multipliers, multi-stage stratified sampling.",
        "q3_competency_alignment": "Dual consideration: Microdata extraction and tabulation share conceptual overlap with KCM-FUNC-11 (Data Analytics). However, survey weighting, NSS sampling designs, and consumption concepts are specialist statistical domain knowledge.",
        "q4_evidence_sufficiency": "Sufficient for survey methodology; insufficient to resolve generic vs domain mapping without expert adjudication.",
        "q5_competency_depth": "Duration 2 hours; unit-level data extraction.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "NSSTA is the apex national training academy for NSS survey operations.",
        "counter_evidence_and_limitations": "Over-simplified claim of pure domain gap ignores Data Analytics (KCM-FUNC-11) overlap; requires expert adjudication.",
        "alternative_kcm_candidates": "KCM-FUNC-11 (Data Analytics) vs no_applicable_kcm_competency (HCES Survey Domain Gap)",
        "sme_adjudication_questions": "Should HCES microdata handling be mapped to generic Data Analytics (KCM-FUNC-11) or flagged as an official statistics Domain gap?",
    },
    "BM-CASE-023": {
        "q1_course_identity": "NSSTA ASI Survey Manual and microdata documentation verify industrial statistics curriculum; exact 2-hour iGOT course is unmirrored.",
        "q2_subject_coverage": "Annual Survey of Industries (ASI), factory sector frame, NIC-2008 classification, Gross Value Added (GVA), capital formation, multiplier application.",
        "q3_competency_alignment": "Dual consideration: Statistical data manipulation aligns with KCM-FUNC-11 (Data Analytics), but industrial economic accounting and sampling frame maintenance are specialist official statistics knowledge.",
        "q4_evidence_sufficiency": "Sufficient for industrial survey methodology; requires expert adjudication on domain gap vs analytics.",
        "q5_competency_depth": "Duration 2 hours; enterprise microdata extraction.",
        "triage_guidance_label": "unresolved_insufficient_source",
        "evidence_supporting_proposed": "NSSTA official industrial statistics curriculum and survey schedules.",
        "counter_evidence_and_limitations": "Potential overlap with Data Analytics (KCM-FUNC-11) must be evaluated alongside domain-specific economic concepts.",
        "alternative_kcm_candidates": "KCM-FUNC-11 (Data Analytics) vs no_applicable_kcm_competency (ASI Survey Domain Gap)",
        "sme_adjudication_questions": "Should ASI enterprise microdata analysis be mapped to Data Analytics (KCM-FUNC-11) or treated as an official statistics Domain gap?",
    },
    "BM-CASE-024": {
        "q1_course_identity": "Verified in local source SRC-NSSTA-TRG-CAL-2025-26.json (Pages 2, 9); foundation course on statistical computing using Python/R; exact session plan unmirrored.",
        "q2_subject_coverage": "Python and R programming foundations, statistical data structures, pandas, numpy, and R tidyverse; exploratory data analysis.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-11 (Data Analytics) or KCM-FUNC-10 (Digital Fluency). Categorized as 'Domain' in ACBP, but Python/R programming is a core data analytics skill.",
        "q4_evidence_sufficiency": "Insufficient for exact session outline; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 2 hours; statistical programming foundation.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "NSSTA training calendar confirms programming modules for official statistical staff.",
        "counter_evidence_and_limitations": "Categorized as Domain in ACBP; tests boundary between general programming (FUNC-10/FUNC-11) and statistical domain applications.",
        "alternative_kcm_candidates": "KCM-FUNC-11 (Data Analytics), KCM-FUNC-10 (Digital Fluency)",
        "sme_adjudication_questions": "Should Python and R statistical programming be mapped to Data Analytics (KCM-FUNC-11) despite being categorized under Domain in ACBP?",
    },
    "BM-CASE-025": {
        "q1_course_identity": "Documented in local source SRC-NSSTA-TRG-CAL-2025-26 (Page 3) and ISTM CSMOP manual for Section Officers; 90m iGOT module outline unmirrored.",
        "q2_subject_coverage": "CSMOP 16th Edition guidelines, types of notes (summary for cabinet, self-contained note), rule interpretation, statutory referencing, decision synthesis.",
        "q3_competency_alignment": "Direct match to KCM-FUNC-13 (Office Management: Noting and Drafting sub-theme) at supervisory level.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour 30 minutes; supervisory critical noting.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM is the statutory authority for Central Secretariat Office Procedure.",
        "counter_evidence_and_limitations": "Cadre-specific proficiency difference (SSO/SO vs clerical) must be evaluated.",
        "alternative_kcm_candidates": "KCM-FUNC-13 (Office Management)",
        "sme_adjudication_questions": "For Section Officers / SSOs, does the syllabus assess intermediate/advanced noting (statutory rule interpretation, synthesizing conflicting branch views), and how is this differentiated from clerical staff?",
    },
    "BM-CASE-026": {
        "q1_course_identity": "ISTM clerical induction modules verified; routine noting & drafting for clerical staff; 60m iGOT module unmirrored.",
        "q2_subject_coverage": "Routine noting and reference verification, docketing, file referencing, flagging annexures, drafting routine communications (acknowledgments, endorsements).",
        "q3_competency_alignment": "Direct match to KCM-FUNC-13 (Office Management: Noting and Drafting sub-theme) at foundational operational level.",
        "q4_evidence_sufficiency": "Insufficient for exact course; sufficient for subject matter relevance.",
        "q5_competency_depth": "Duration 1 hour; targets routine secretariat drafting tasks.",
        "triage_guidance_label": "plausible_insufficient_evidence",
        "evidence_supporting_proposed": "ISTM clerical training syllabus for UDC/LDC/Assistants cadres.",
        "counter_evidence_and_limitations": "Duration is 1 hour; represents foundational operational proficiency.",
        "alternative_kcm_candidates": "KCM-FUNC-13 (Office Management)",
        "sme_adjudication_questions": "For clerical cadre, does the 1-hour session target foundational operational proficiency (docketing, routine acknowledgments), justifying a Level 1 proficiency tag?",
    },
}

# CSV column headers in deterministic order
CSV_HEADERS = [
    "benchmark_case_id",
    "stratum",
    "course_record_id",
    "course_name",
    "cadre_role",
    "acbp_competency_category",
    "duration",
    "course_creator",
    "course_source_id",
    "course_source_citation",
    "current_evidence_status",
    "evidence_source_id",
    "evidence_source_title",
    "evidence_institution",
    "evidence_url_or_path",
    "evidence_publication_year",
    "evidence_type",
    "match_fidelity",
    "evidence_excerpt_verbatim",
    "is_exact_course_evidence",
    "missing_evidence_details",
    "candidate_kcm_id",
    "candidate_kcm_name",
    "candidate_kcm_type",
    "kcm_source_citation",
    "kcm_verbatim_definition",
    "kcm_verbatim_subthemes",
    "question_1_course_identity_finding",
    "question_2_subject_coverage_finding",
    "question_3_competency_alignment_finding",
    "question_4_evidence_sufficiency_finding",
    "question_5_competency_depth_limitation",
    "triage_guidance_label",
    "evidence_supporting_proposed",
    "counter_evidence_and_limitations",
    "alternative_kcm_candidates",
    "sme_adjudication_questions",
    "adjudication_status",
    "adjudicated_label",
    "adjudicated_target_kcm_id",
    "adjudicated_target_kcm_name",
    "adjudicated_subtheme",
    "evidence_sufficiency_verdict",
    "depth_assessment",
    "reviewer_id",
    "reviewer_role",
    "adjudication_date",
    "reviewer_rationale",
    "confidence_rating",
    "second_reviewer_required",
    "consensus_status",
]


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_input_datasets() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    # Verify immutable baselines
    course_hash = compute_sha256(COURSES_JSON_PATH)
    if course_hash != EXPECTED_COURSE_HASH:
        raise ValueError(f"acbp_courses.json hash mismatch: {course_hash}")

    kcm_hash = compute_sha256(KCM_JSON_PATH)
    if kcm_hash != EXPECTED_KCM_HASH:
        raise ValueError(f"competencies_kcm.json hash mismatch: {kcm_hash}")

    with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    with open(LEDGER_JSON_PATH, "r", encoding="utf-8") as f:
        ledger_data = json.load(f)

    with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
        audit_data = json.load(f)

    with open(COURSES_JSON_PATH, "r", encoding="utf-8") as f:
        courses_raw = json.load(f)["records"]
        courses_dict = {c["record_id"]: c for c in courses_raw}

    with open(KCM_JSON_PATH, "r", encoding="utf-8") as f:
        kcm_raw = json.load(f)
        kcm_dict = {k["competency_id"]: k for k in kcm_raw}

    with open(EVIDENCE_PACK_JSON_PATH, "r", encoding="utf-8") as f:
        pack_raw = json.load(f)["evidence_pack"]
        pack_dict = {p["benchmark_case_id"]: p for p in pack_raw}

    return manifest_data, ledger_data, audit_data, courses_dict, kcm_dict, pack_dict


def build_adjudication_cases() -> List[Dict[str, Any]]:
    manifest_data, ledger_data, audit_data, courses_dict, kcm_dict, pack_dict = load_input_datasets()

    ledger_by_id = {r["benchmark_case_id"]: r for r in ledger_data["records"]}
    audit_by_id = {c["benchmark_case_id"]: c for c in audit_data["cases"]}

    adjudication_cases: List[Dict[str, Any]] = []

    for manifest_case in manifest_data["cases"]:
        case_id = manifest_case["benchmark_case_id"]
        course_id = manifest_case["course_record_id"]
        course = courses_dict[course_id]
        ledger_rec = ledger_by_id[case_id]
        audit_rec = audit_by_id[case_id]
        pack_rec = pack_dict[case_id]
        spec = CASE_ADJUDICATION_SPECS[case_id]

        # Determine KCM candidate information
        candidate_kcm_id = manifest_case.get("candidate_kcm_competency_id")
        candidate_kcm_name = manifest_case.get("candidate_kcm_competency_name")
        candidate_kcm_type = manifest_case.get("candidate_kcm_competency_type")

        # If not in manifest, check if audit identified an institutional claimed candidate
        if candidate_kcm_id is None and audit_rec.get("claimed_kcm_id"):
            candidate_kcm_id = audit_rec["claimed_kcm_id"]
            candidate_kcm_name = audit_rec["claimed_kcm_name"]
            if candidate_kcm_id in kcm_dict:
                candidate_kcm_type = kcm_dict[candidate_kcm_id]["competency_type"]

        # Extract KCM definition and subthemes if candidate exists
        kcm_source_citation: Optional[str] = None
        kcm_definition: Optional[str] = None
        kcm_subthemes: Optional[str] = None

        if candidate_kcm_id and candidate_kcm_id in kcm_dict:
            kcm_entry = kcm_dict[candidate_kcm_id]
            kcm_source_citation = f"{kcm_entry['source_id']} (Page {kcm_entry['source_page']})"
            kcm_definition = kcm_entry["description"]
            behaviours = kcm_entry.get("behaviours", [])
            kcm_subthemes = " | ".join(behaviours) if behaviours else None

        # Build adjudication card
        case_record: Dict[str, Any] = {
            # 1. Identifiers & Course Metadata
            "benchmark_case_id": case_id,
            "stratum": manifest_case["stratum"],
            "course_record_id": course_id,
            "course_name": course["course_name"],
            "cadre_role": course["cadre_role"],
            "acbp_competency_category": course["competency_category"],
            "duration": course["duration"],
            "course_creator": course["course_creator"],
            "course_source_id": manifest_case["course_source_id"],
            "course_source_citation": f"{manifest_case['course_source_id']} (Annexure I, Page {manifest_case['course_source_page']}, Row {manifest_case['course_source_row']})",
            # 2. Evidence Provenance & Audit Classification
            "current_evidence_status": audit_rec["audit_classification"],
            "evidence_source_id": CASE_SOURCE_IDS[case_id],
            "evidence_source_title": ledger_rec["source_document_title"],
            "evidence_institution": ledger_rec["source_institution"],
            "evidence_url_or_path": ledger_rec["source_url_or_path"],
            "evidence_publication_year": ledger_rec["evidence_publication_year"],
            "evidence_type": ledger_rec["evidence_type"],
            "match_fidelity": ledger_rec["match_fidelity"],
            "evidence_excerpt_verbatim": ledger_rec["evidence_excerpt_verbatim"],
            "is_exact_course_evidence": False,  # Established in Stage 3.4.1: no local exact course session plans
            "missing_evidence_details": ledger_rec["missing_evidence_details"],
            # 3. KCM Candidate Reference
            "candidate_kcm_id": candidate_kcm_id,
            "candidate_kcm_name": candidate_kcm_name,
            "candidate_kcm_type": candidate_kcm_type,
            "kcm_source_citation": kcm_source_citation,
            "kcm_verbatim_definition": kcm_definition,
            "kcm_verbatim_subthemes": kcm_subthemes,
            # 4. Six-Question Adjudication Guidance
            "question_1_course_identity_finding": spec["q1_course_identity"],
            "question_2_subject_coverage_finding": spec["q2_subject_coverage"],
            "question_3_competency_alignment_finding": spec["q3_competency_alignment"],
            "question_4_evidence_sufficiency_finding": spec["q4_evidence_sufficiency"],
            "question_5_competency_depth_limitation": spec["q5_competency_depth"],
            "triage_guidance_label": spec["triage_guidance_label"],
            "evidence_supporting_proposed": spec["evidence_supporting_proposed"],
            "counter_evidence_and_limitations": spec["counter_evidence_and_limitations"],
            "alternative_kcm_candidates": spec["alternative_kcm_candidates"],
            "sme_adjudication_questions": spec["sme_adjudication_questions"],
            # 5. Blank Human Adjudication Fields (Strictly null for human review)
            "adjudication_status": "pending_review",
            "adjudicated_label": None,
            "adjudicated_target_kcm_id": None,
            "adjudicated_target_kcm_name": None,
            "adjudicated_subtheme": None,
            "evidence_sufficiency_verdict": None,
            "depth_assessment": None,
            "reviewer_id": None,
            "reviewer_role": None,
            "adjudication_date": None,
            "reviewer_rationale": None,
            "confidence_rating": None,
            "second_reviewer_required": None,
            "consensus_status": None,
        }

        adjudication_cases.append(case_record)

    return adjudication_cases


def export_adjudication_packet(cases: List[Dict[str, Any]]) -> None:
    # Summary calculations
    strata_counts: Dict[str, int] = {}
    evidence_status_counts: Dict[str, int] = {}

    for c in cases:
        st = c["stratum"]
        strata_counts[st] = strata_counts.get(st, 0) + 1

        ev = c["current_evidence_status"]
        evidence_status_counts[ev] = evidence_status_counts.get(ev, 0) + 1

    packet_json_content: Dict[str, Any] = {
        "packet_id": "ADJ-PACKET-BM-PILOT-MOSPI-2026-V1",
        "benchmark_id": "BM-PILOT-MOSPI-2026-V1",
        "version": "1.1.0",
        "stage": "3.4.2",
        "created_at": "2026-10-18T17:30:00Z",
        "total_cases": len(cases),
        "strata_summary": strata_counts,
        "evidence_status_summary": evidence_status_counts,
        "adjudication_status_summary": {
            "pending_review": len(cases),
            "review_in_progress": 0,
            "adjudicated": 0,
            "requires_more_evidence": 0,
        },
        "allowed_benchmark_labels": [
            "supported_mapping",
            "plausible_insufficient_evidence",
            "incorrect_mapping",
            "unresolved_insufficient_source",
            "no_applicable_kcm_competency",
        ],
        "allowed_evidence_sufficiency": [
            "sufficient",
            "insufficient",
            "absent",
        ],
        "allowed_adjudication_statuses": [
            "pending_review",
            "review_in_progress",
            "adjudicated",
            "requires_more_evidence",
        ],
        "confidence_rating_scale": {
            "1": "Very Low: Speculative or title-only evidence; no verifiable syllabus or session plan.",
            "2": "Low: Related subject material identified, but exact iGOT course module outline is unverified.",
            "3": "Moderate: Apex institutional curriculum verified, but course duration or delivery modality differs from online micro-course.",
            "4": "High: Granular course session outline verified with direct alignment to specific KCM sub-theme indicators.",
            "5": "Very High: Complete syllabus with observable behavioral learning outcomes and assessment criteria verified.",
        },
        "consensus_workflow_rules": {
            "single_reviewer_threshold": "Allowed only when confidence >= 4 and supported by Level 3/4 syllabus evidence.",
            "dual_reviewer_mandatory": "Mandatory for all cases with confidence <= 3, all Domain gap cases, and all title-reference candidates.",
            "disagreement_escalation": "When two independent reviewers assign different benchmark labels, case is escalated to an NSSTA / MoSPI subject-matter expert panel.",
        },
        "cases": cases,
    }

    # Write JSON
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    with open(PACKET_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(packet_json_content, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Exported JSON adjudication packet: {PACKET_JSON_PATH} ({len(cases)} cases)")

    # Write CSV
    with open(PACKET_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        for c in cases:
            row = []
            for h in CSV_HEADERS:
                val = c.get(h)
                if val is None:
                    row.append("")
                elif isinstance(val, bool):
                    row.append("true" if val else "false")
                else:
                    row.append(str(val))
            writer.writerow(row)
    print(f"[SUCCESS] Exported CSV adjudication packet: {PACKET_CSV_PATH} ({len(cases)} rows)")


def main() -> None:
    print("=" * 70)
    print("MoSPI SIH26101: Building Human Adjudication Packet (Stage 3.4.2 / 3.4.3)")
    print("=" * 70)
    cases = build_adjudication_cases()
    export_adjudication_packet(cases)
    print("=" * 70)
    print("Adjudication packet compilation completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
