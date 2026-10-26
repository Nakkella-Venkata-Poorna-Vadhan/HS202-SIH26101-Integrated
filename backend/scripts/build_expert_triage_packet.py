"""
build_expert_triage_packet.py
Stage 3.5 — Expert Triage Preparation for the 26-Case Competency Mapping Benchmark.

Constructs the standardized expert-triage package (JSON and CSV) for the 26-case benchmark.
Enables authorized Subject Matter Experts (SMEs) to inspect verified vs unverified evidence,
review potential competency overlaps, examine candidate options, and record independent decisions.

Strict Safeguards:
- 0 automated decisions or generated ground-truth labels.
- Dual reviewer slots (Reviewer 1 and Reviewer 2) initialized to blank / null.
- Clear separation between verified local evidence and unverified external references.
- Domain category never treated as an automatic domain gap.
- Explicit documentation of conceptual overlap with KCM-FUNC-11 (Data Analytics) for statistical courses.
- Deterministic, repeatable generation.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input paths
MANIFEST_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json"
LEDGER_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_ledger.json"
AUDIT_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "course_evidence_provenance_audit.json"
ADJUDICATION_PACKET_PATH = PROJECT_ROOT / "data" / "interim" / "mapping_adjudication_packet.json"
CITATION_VERIF_PATH = PROJECT_ROOT / "data" / "interim" / "source_citation_verification.json"
COURSES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
SOURCE_REGISTER_PATH = PROJECT_ROOT / "data" / "source_register.json"

# Output paths
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_JSON_PATH = INTERIM_DIR / "expert_triage_packet.json"
OUTPUT_CSV_PATH = INTERIM_DIR / "expert_triage_packet.csv"

# Immutable source hashes
EXPECTED_COURSE_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
EXPECTED_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"

# Detailed potential competency overlaps and evidentiary summaries per case
CASE_SPECIFICS: Dict[str, Dict[str, str]] = {
    "BM-CASE-001": {
        "potential_competency_overlaps": "Candidate KCM-BEH-06 (Collaboration) vs KCM-BEH-10 (Strategic Leadership) or KCM-BEH-11 (Collaborative Leadership). Focuses on inter-ministerial collaborative governance for apex leadership.",
        "verified_evidence_summary": "Course existence, duration (01:00:44), JS+ cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 2, Row 17). KCM-BEH-06 definition verified in CBC KCM 2024.",
        "unverified_evidence_summary": "Granular session plan, video transcripts, and assessment rubrics are unmirrored locally and secured behind Parichay SSO on iGOT Karmayogi.",
        "missing_evidence_details": "Granular session outline and learning assessment criteria from iGOT Karmayogi (Parichay SSO requisition required).",
    },
    "BM-CASE-002": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-05 (Project Management) vs KCM-BEH-10 (Strategic Leadership). Tests boundary between general executive project leadership and technical functional project management.",
        "verified_evidence_summary": "Course existence, duration (17m 58s), Director cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 13). KCM-FUNC-05 definition verified in KCM 2024.",
        "unverified_evidence_summary": "ATI Mysuru general executive leadership modules catalogued from public metadata; specific 18-minute iGOT micro-course video content unacquired locally.",
        "missing_evidence_details": "Exact 18-minute micro-course module transcript and learning objectives from ATI Mysuru / iGOT.",
    },
    "BM-CASE-003": {
        "potential_competency_overlaps": "Candidate KCM-BEH-10 (Strategic Leadership) vs KCM-BEH-01 (Self-Awareness: Purposefulness). Tests alignment of philosophical Indic leadership principles to executive behavioral competencies.",
        "verified_evidence_summary": "Course existence, duration (01:21:00), Director cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 17). KCM-BEH-10 definition verified in KCM 2024.",
        "unverified_evidence_summary": "CBC Indic Leadership publication series catalogued; exact 81-minute iGOT course module outline and assessment rubrics unacquired locally.",
        "missing_evidence_details": "Granular lecture outline and behavioral assessment rubrics from CBC Indic Leadership curriculum on iGOT.",
    },
    "BM-CASE-004": {
        "potential_competency_overlaps": "Candidate KCM-BEH-06 (Collaboration) vs KCM-BEH-02 (Personal Effectiveness). Cross-cadre contrast with BM-CASE-001 (DDG) and BM-CASE-006 (US) testing mid-level Director collaboration.",
        "verified_evidence_summary": "Course existence, duration (01:00:44), Director cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 18). KCM-BEH-06 definition verified in KCM 2024.",
        "unverified_evidence_summary": "Exact iGOT module content restricted behind Parichay SSO; identical title to Case 001/006 but assigned to distinct administrative cadre.",
        "missing_evidence_details": "iGOT micro-course lesson plan to evaluate whether cadre-specific exercises or case studies exist for Directors.",
    },
    "BM-CASE-005": {
        "potential_competency_overlaps": "Candidate KCM-BEH-10 (Strategic Leadership) vs KCM-BEH-03 (Problem Solving). Parallel Indic leadership module for Director cadre testing strategic decision synthesis.",
        "verified_evidence_summary": "Course existence, duration (01:21:00), Director cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 4, Row 17). KCM-BEH-10 definition verified in KCM 2024.",
        "unverified_evidence_summary": "Exact iGOT session outline and video content unacquired locally; secondary CBC Indic series catalogued.",
        "missing_evidence_details": "Exact module structure and learning objectives from CBC Indic Leadership course on iGOT.",
    },
    "BM-CASE-006": {
        "potential_competency_overlaps": "Candidate KCM-BEH-06 (Collaboration) vs KCM-BEH-04 (Communication). Cross-cadre contrast with Case 001/004 evaluating operational coordination for Under Secretary / Section Officer level.",
        "verified_evidence_summary": "Course existence, duration (01:00:44), DS/US cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 4, Row 18). KCM-BEH-06 definition verified in KCM 2024.",
        "unverified_evidence_summary": "Course content restricted behind civil service Parichay SSO on iGOT Karmayogi.",
        "missing_evidence_details": "Course lesson plan and practice assignments from iGOT Karmayogi.",
    },
    "BM-CASE-007": {
        "potential_competency_overlaps": "Potential false domain gap. Overlaps conceptually with KCM-BEH-06 (Collaboration: Culture) and KCM-BEH-08 (Operational Excellence: Workplace Standards). Categorized as Behavioural in ACBP without candidate KCM.",
        "verified_evidence_summary": "Course existence, duration (00:30:00), DS/US cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 4, Row 20).",
        "unverified_evidence_summary": "DoPT/iGOT course content restricted behind civil service Parichay SSO.",
        "missing_evidence_details": "30-minute course module outline to determine whether specific behavioral indicators are taught or merely general organizational advice.",
    },
    "BM-CASE-008": {
        "potential_competency_overlaps": "Workplace physical health intervention. Potential domain gap (no_applicable_kcm_competency - wellness outside civil service competency scope) vs remote overlap with KCM-BEH-01 (Self-Awareness: physical well-being).",
        "verified_evidence_summary": "Course existence, duration (00:05:00), DS/US cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 5, Row 1). MDNIY / Ministry of Ayush Y-Break guidelines catalogued.",
        "unverified_evidence_summary": "Exact 5-minute video exercise content unacquired locally.",
        "missing_evidence_details": "SME decision on whether workplace physical health routines constitute a competency within KCM scope or should be confirmed as no_applicable_kcm_competency.",
    },
    "BM-CASE-009": {
        "potential_competency_overlaps": "Overlap between KCM-BEH-07 (Service Orientation: Citizen Focus, Empathy) and KCM-FUNC-01 (Citizen Centricity) or KCM-BEH-01 (Self-Awareness: Purposefulness). Categorized as Behavioural in ACBP without candidate KCM.",
        "verified_evidence_summary": "Course existence, duration (00:30:00), DS/US cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 5, Row 2).",
        "unverified_evidence_summary": "Course content restricted behind civil service Parichay SSO on iGOT Karmayogi.",
        "missing_evidence_details": "Granular session plan from iGOT to establish whether philosophical Seva-Bhava aligns to behavioral Service Orientation or functional Citizen Centricity.",
    },
    "BM-CASE-010": {
        "potential_competency_overlaps": "Overlap between KCM-BEH-01 (Self-Awareness: Self-Analysis, Purposefulness) and KCM-BEH-02 (Personal Effectiveness: Emotional Stability). Categorized as Behavioural in ACBP without candidate KCM.",
        "verified_evidence_summary": "Course existence, duration (00:30:00), SSO cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 5, Row 22).",
        "unverified_evidence_summary": "Course content restricted behind civil service Parichay SSO on iGOT Karmayogi.",
        "missing_evidence_details": "Course syllabus from iGOT to evaluate whether self-leadership maps to Self-Awareness or Personal Effectiveness.",
    },
    "BM-CASE-011": {
        "potential_competency_overlaps": "Overlap between KCM-BEH-04 (Communication: Active Listening sub-theme) and KCM-BEH-06 (Collaboration: Knowledge Sharing). Categorized as Behavioural in ACBP without candidate KCM.",
        "verified_evidence_summary": "Course existence, duration (00:28:10), JSO cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 9, Row 19).",
        "unverified_evidence_summary": "Course content restricted behind civil service Parichay SSO on iGOT Karmayogi.",
        "missing_evidence_details": "Course outline from iGOT to determine whether 28-minute module justifies full Communication mapping or represents a sub-indicator.",
    },
    "BM-CASE-012": {
        "potential_competency_overlaps": "Overlap between KCM-BEH-06 (Collaboration: Diversity & Inclusion sub-theme) and KCM-FUNC-12 (Establishment & HR: Gender Sensitization rules). Categorized as Behavioural in ACBP without candidate KCM.",
        "verified_evidence_summary": "Course existence, duration (00:30:00), Non-Gazetted cadre, and Behavioural category verified in ACBP FY 2026-27 (Annexure I, Page 10, Row 16).",
        "unverified_evidence_summary": "Course content restricted behind civil service Parichay SSO on iGOT Karmayogi.",
        "missing_evidence_details": "Module outline from iGOT to evaluate behavioral diversity alignment vs statutory administrative rules.",
    },
    "BM-CASE-013": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-17 (Legal Framework: Inquiry Procedures) vs KCM-FUNC-12 (Establishment & HR: CCS CCA Rules). Tests technical quasi-judicial inquiry procedure mapping.",
        "verified_evidence_summary": "Course existence, duration (02:00:00), DDG cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 2, Row 8). ISTM CIDM syllabus catalogued.",
        "unverified_evidence_summary": "ISTM classroom handbook catalogued; specific 2-hour iGOT micro-course module breakdown unacquired locally.",
        "missing_evidence_details": "Granular iGOT lesson plan and case studies to confirm whether course focuses on statutory legal framework or general HR administration.",
    },
    "BM-CASE-014": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-02 (Policy Formulation) vs KCM-FUNC-03 (Policy Implementation). Evaluates whether introductory policy course targets conceptual formulation or field execution.",
        "verified_evidence_summary": "Course existence, duration (00:30:00), DDG cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 2, Row 10). KCM-FUNC-02 definition verified in KCM 2024.",
        "unverified_evidence_summary": "DoPT/iGOT course content restricted behind civil service Parichay SSO.",
        "missing_evidence_details": "Granular session plan from iGOT to verify if a 30-minute overview satisfies Policy Formulation competency requirements.",
    },
    "BM-CASE-015": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-09 (Financial Management) vs KCM-FUNC-05 (Project Management: Financial Appraisal). Evaluates capital budgeting and cost-benefit analysis alignment.",
        "verified_evidence_summary": "Course existence, duration (02:00:00), DDG cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 2, Row 11). AJ-NIFM executive training materials catalogued.",
        "unverified_evidence_summary": "AJ-NIFM classroom manual catalogued; specific 2-hour iGOT micro-course module plan unacquired locally.",
        "missing_evidence_details": "Course syllabus and practical financial appraisal exercise outlines from AJ-NIFM / iGOT.",
    },
    "BM-CASE-016": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-14 (Government Procedure: Parliamentary Questions) vs KCM-FUNC-13 (Office Management). Tests specific legislative procedural workflow alignment.",
        "verified_evidence_summary": "Course existence, duration (00:45:00), DDG cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 2, Row 13). Lok Sabha PRIDE manual catalogued.",
        "unverified_evidence_summary": "PRIDE legislative drafting handbook catalogued; specific 45-minute iGOT micro-course video breakdown unacquired locally.",
        "missing_evidence_details": "Specific session outline and drafting templates from Lok Sabha Secretariat / iGOT.",
    },
    "BM-CASE-017": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-06 (Procurement: Works) vs KCM-FUNC-04 (Budget Management: Works Expenditure). Focuses on GFR 2017 Chapter 5 and GeM procurement rules.",
        "verified_evidence_summary": "Course existence, duration (02:00:00), Director cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 5). GeM / AJ-NIFM procurement guidelines catalogued.",
        "unverified_evidence_summary": "AJ-NIFM procurement handbook catalogued; specific 2-hour iGOT course session plan unacquired locally.",
        "missing_evidence_details": "Detailed module syllabus from AJ-NIFM / GeM covering Works contract management on iGOT.",
    },
    "BM-CASE-018": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-12 (Establishment & HR: FRSR Rules) vs KCM-FUNC-13 (Office Management). Evaluates statutory service conditions and fundamental rules alignment.",
        "verified_evidence_summary": "Course existence, duration (01:00:00), Director cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 7). ISTM FRSR training handbook catalogued.",
        "unverified_evidence_summary": "ISTM service rules curriculum catalogued; specific 1-hour iGOT micro-course breakdown unacquired locally.",
        "missing_evidence_details": "iGOT course syllabus to verify whether 1-hour module covers operational rule application or executive awareness.",
    },
    "BM-CASE-019": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-10 (Digital Fluency: AI Productivity Tools) vs KCM-BEH-04 (Communication: Presentation Design). Tests generative AI presentation tooling alignment.",
        "verified_evidence_summary": "Course existence, duration (00:30:00), Director cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 9). KCM-FUNC-10 definition verified in KCM 2024.",
        "unverified_evidence_summary": "Course content restricted behind civil service Parichay SSO on iGOT Karmayogi.",
        "missing_evidence_details": "30-minute course outline and tool demonstration syllabus from iGOT Karmayogi.",
    },
    "BM-CASE-020": {
        "potential_competency_overlaps": "CRITICAL DOMAIN GAP OVERLAP: Categorized as 'Domain' in ACBP, but created by NeGD/MeitY for general civil servants. Direct conceptual overlap with KCM-FUNC-10 (Digital Fluency) and KCM-FUNC-11 (Data Analytics). Must NOT be auto-classified as domain gap without expert review.",
        "verified_evidence_summary": "Course existence, duration (02:00:00), Director cadre, and Domain category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 10). NeGD Big Data in Governance framework catalogued.",
        "unverified_evidence_summary": "NeGD training overview catalogued; exact 2-hour iGOT micro-course module plan unacquired locally.",
        "missing_evidence_details": "NeGD course module breakdown on iGOT to resolve whether Big Data governance maps to Digital Fluency or Data Analytics.",
    },
    "BM-CASE-021": {
        "potential_competency_overlaps": "Ministry induction course. Potential domain gap (no_applicable_kcm_competency - official statistics institutional machinery) vs KCM-FUNC-21 (Administration Matters: MoSPI Machinery).",
        "verified_evidence_summary": "Course existence, duration (01:00:00), Director cadre, and Domain category verified in ACBP FY 2026-27 (Annexure I, Page 3, Row 19). Official mandate of MoSPI, NSC, and CSO VERIFIED in local physical document SRC-MOSPI-AR-2023-24 (Page 35).",
        "unverified_evidence_summary": "Exact 1-hour iGOT micro-course lesson plan and module structure unacquired locally.",
        "missing_evidence_details": "Exact iGOT course syllabus from MoSPI CBU to verify whether induction maps to Administration Matters or constitutes a domain gap.",
    },
    "BM-CASE-022": {
        "potential_competency_overlaps": "CRITICAL STATISTICAL DOMAIN DUAL OVERLAP: Categorized as 'Domain' in ACBP. Microdata extraction, data cleaning, and tabulation share direct conceptual overlap with KCM-FUNC-11 (Data Analytics). However, NSS sampling multipliers, survey weighting, and household consumption expenditure aggregation represent official statistics domain knowledge (potential domain gap). Must be adjudicated by NSSTA expert.",
        "verified_evidence_summary": "Course existence, duration (03:00:00), Director cadre, and Domain category verified in ACBP FY 2026-27 (Annexure I, Page 4, Row 2). NSSTA HCES workshop documentation catalogued.",
        "unverified_evidence_summary": "NSSTA in-service workshop curriculum catalogued; exact 3-hour micro-course session outline unacquired locally.",
        "missing_evidence_details": "NSSTA syllabus detailing practical microdata exercises in Python/R/Stata vs survey methodology theory.",
    },
    "BM-CASE-023": {
        "potential_competency_overlaps": "CRITICAL STATISTICAL DOMAIN DUAL OVERLAP: Categorized as 'Domain' in ACBP. Enterprise microdata processing and industrial metric tabulation overlap with KCM-FUNC-11 (Data Analytics). However, NIC classification, factory accounting schedules, and sampling multiplier estimation represent official statistics domain knowledge (potential domain gap). Must be adjudicated by NSSTA expert.",
        "verified_evidence_summary": "Course existence, duration (03:00:00), Director cadre, and Domain category verified in ACBP FY 2026-27 (Annexure I, Page 4, Row 4). NSSTA ASI workshop documentation catalogued.",
        "unverified_evidence_summary": "NSSTA ASI training manual catalogued; exact 3-hour micro-course session outline unacquired locally.",
        "missing_evidence_details": "NSSTA syllabus detailing ASI unit-level data manipulation practicals vs industrial statistics concepts.",
    },
    "BM-CASE-024": {
        "potential_competency_overlaps": "CRITICAL STATISTICAL PROGRAMMING OVERLAP: Categorized as 'Domain' in ACBP, but Python and R programming are core data analytics foundational competencies. Candidate KCM-FUNC-10 (Digital Fluency) and KCM-FUNC-11 (Data Analytics). Local physical document confirms statistical computing topic.",
        "verified_evidence_summary": "Course existence, duration (02:00:00), Director cadre, and Domain category verified in ACBP FY 2026-27 (Annexure I, Page 4, Row 7). In-service training topic 'Machine Learning using Python' VERIFIED in local physical document SRC-NSSTA-TRG-CAL-2025-26 (Page 2).",
        "unverified_evidence_summary": "Exact 2-hour iGOT online micro-course module outline and coding exercises unacquired locally.",
        "missing_evidence_details": "Exact iGOT course syllabus from NSSTA to confirm whether programming modules map to Data Analytics or Digital Fluency.",
    },
    "BM-CASE-025": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-13 (Office Management: Noting and Drafting sub-theme). Supervisory level cross-cadre contrast with BM-CASE-026 testing statutory rule interpretation, synthesizing branch views, and cabinet notes (Level 2/3).",
        "verified_evidence_summary": "Course existence, duration (01:30:00), Section Officer cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 7, Row 15). In-service course 'Effective Noting and Drafting for Section Officers' VERIFIED in local physical document SRC-NSSTA-TRG-CAL-2025-26 (Page 3).",
        "unverified_evidence_summary": "Exact 90-minute iGOT online course module transcript unacquired locally.",
        "missing_evidence_details": "Exact iGOT module syllabus to confirm whether supervisory critical noting and decision synthesis are assessed.",
    },
    "BM-CASE-026": {
        "potential_competency_overlaps": "Candidate KCM-FUNC-13 (Office Management: Noting and Drafting sub-theme). Operational clerical level cross-cadre contrast with BM-CASE-025 testing routine docketing, file referencing, and routine acknowledgments (Level 1).",
        "verified_evidence_summary": "Course existence, duration (01:00:00), Clerical / Non-Gazetted cadre, and Functional category verified in ACBP FY 2026-27 (Annexure I, Page 12, Row 4). ISTM clerical training handbook catalogued.",
        "unverified_evidence_summary": "ISTM clerical induction manual catalogued; exact 1-hour iGOT micro-course breakdown unacquired locally.",
        "missing_evidence_details": "Exact 1-hour iGOT module outline to confirm foundational Level 1 operational drafting scope.",
    },
}

CSV_FIELDNAMES = [
    "benchmark_case_id",
    "stratum",
    "course_record_id",
    "course_name",
    "cadre_role",
    "acbp_competency_category",
    "duration",
    "course_creator",
    "primary_source_id",
    "primary_source_citation",
    "primary_source_provenance",
    "primary_source_verification_status",
    "candidate_kcm_id",
    "candidate_kcm_name",
    "candidate_kcm_type",
    "kcm_source_citation",
    "alternative_kcm_candidates",
    "potential_competency_overlaps",
    "evidence_source_id",
    "evidence_source_title",
    "evidence_institution",
    "evidence_url_or_path",
    "evidence_verification_status",
    "is_exact_course_evidence",
    "verified_evidence_summary",
    "unverified_evidence_summary",
    "missing_evidence_details",
    "question_1_course_identity",
    "question_2_subject_coverage",
    "question_3_competency_alignment",
    "question_4_evidence_sufficiency",
    "question_5_competency_depth",
    "curator_triage_guidance_label",
    "sme_adjudication_questions",
    "triage_readiness_status",
    "definitive_adjudication_status",
    "blocking_reason",
    "adjudication_status",
    "final_adjudicated_label",
    "final_adjudicated_kcm_id",
    "final_adjudicated_kcm_name",
    "final_adjudicated_subtheme",
    "consensus_status",
    "panel_escalation_notes",
    # Reviewer 1 slots (blank initially)
    "r1_reviewer_id",
    "r1_reviewer_role",
    "r1_reviewer_affiliation",
    "r1_review_date",
    "r1_expert_decision_label",
    "r1_expert_target_kcm_id",
    "r1_expert_target_kcm_name",
    "r1_expert_subtheme",
    "r1_evidence_sufficiency_verdict",
    "r1_depth_assessment",
    "r1_confidence_rating",
    "r1_expert_rationale",
    "r1_requisition_notes",
    # Reviewer 2 slots (blank initially)
    "r2_reviewer_id",
    "r2_reviewer_role",
    "r2_reviewer_affiliation",
    "r2_review_date",
    "r2_expert_decision_label",
    "r2_expert_target_kcm_id",
    "r2_expert_target_kcm_name",
    "r2_expert_subtheme",
    "r2_evidence_sufficiency_verdict",
    "r2_depth_assessment",
    "r2_confidence_rating",
    "r2_expert_rationale",
    "r2_requisition_notes",
]


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_json(filepath: Path) -> Any:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def build_expert_triage_cases() -> List[Dict[str, Any]]:
    # Verify baseline immutability
    assert compute_sha256(COURSES_JSON_PATH) == EXPECTED_COURSE_HASH, "acbp_courses.json hash mismatch"
    assert compute_sha256(KCM_JSON_PATH) == EXPECTED_KCM_HASH, "competencies_kcm.json hash mismatch"

    manifest = load_json(MANIFEST_JSON_PATH)
    adjudication_packet = load_json(ADJUDICATION_PACKET_PATH)
    adj_cases_map = {c["benchmark_case_id"]: c for c in adjudication_packet["cases"]}

    triage_cases = []

    for manifest_case in manifest["cases"]:
        cid = manifest_case["benchmark_case_id"]
        adj_case = adj_cases_map[cid]
        specifics = CASE_SPECIFICS.get(cid, {})

        # Primary source verification: local ACBP PDF is verified local source
        primary_source_id = manifest_case["course_source_id"]
        primary_source_cit = f"{primary_source_id} (Annexure I, Page {manifest_case['course_source_page']}, Row {manifest_case['course_source_row']})"
        primary_source_status = "verified_local_source"

        # Evidence verification status: 3 are local, 23 are external unverified
        if cid in ["BM-CASE-021", "BM-CASE-024", "BM-CASE-025"]:
            ev_status = "verified_local_source"
            blocking_reason = "Definitive adjudication requires exact iGOT online micro-course lesson plan and assessment criteria (in-service classroom calendar verifies subject relevance only)."
        else:
            ev_status = "external_reference_unverified"
            if adj_case.get("current_evidence_status") == "access_restricted":
                blocking_reason = "Definitive adjudication blocked on civil service Parichay SSO authentication to inspect exact iGOT micro-course lesson plan."
            else:
                blocking_reason = "Definitive adjudication blocked on physical curriculum requisition from apex training institute."

        case_obj = {
            "benchmark_case_id": cid,
            "stratum": manifest_case["stratum"],
            "course_record_id": manifest_case["course_record_id"],
            "course_name": manifest_case["course_name"],
            "cadre_role": manifest_case["cadre_role"],
            "acbp_competency_category": manifest_case["acbp_competency_category"],
            "duration": adj_case["duration"],
            "course_creator": adj_case["course_creator"],
            # Primary Source Reference
            "primary_source_id": primary_source_id,
            "primary_source_citation": primary_source_cit,
            "primary_source_provenance": "official_public",
            "primary_source_verification_status": primary_source_status,
            # Candidate Competency Options
            "candidate_kcm_id": adj_case.get("candidate_kcm_id"),
            "candidate_kcm_name": adj_case.get("candidate_kcm_name"),
            "candidate_kcm_type": adj_case.get("candidate_kcm_type"),
            "kcm_source_citation": adj_case.get("kcm_source_citation"),
            "kcm_verbatim_definition": adj_case.get("kcm_verbatim_definition"),
            "kcm_verbatim_subthemes": adj_case.get("kcm_verbatim_subthemes"),
            "alternative_kcm_candidates": adj_case.get("alternative_kcm_candidates", ""),
            "potential_competency_overlaps": specifics.get("potential_competency_overlaps", ""),
            # Evidence Traceability & Verification
            "evidence_source_id": adj_case.get("evidence_source_id", ""),
            "evidence_source_title": adj_case.get("evidence_source_title", ""),
            "evidence_institution": adj_case.get("evidence_institution", ""),
            "evidence_url_or_path": adj_case.get("evidence_url_or_path", ""),
            "evidence_verification_status": ev_status,
            "is_exact_course_evidence": False,
            "verified_evidence_summary": specifics.get("verified_evidence_summary", ""),
            "unverified_evidence_summary": specifics.get("unverified_evidence_summary", ""),
            "missing_evidence_details": specifics.get("missing_evidence_details", ""),
            # Structured 5-Question Review Findings
            "question_1_course_identity": adj_case.get("question_1_course_identity_finding", ""),
            "question_2_subject_coverage": adj_case.get("question_2_subject_coverage_finding", ""),
            "question_3_competency_alignment": adj_case.get("question_3_competency_alignment_finding", ""),
            "question_4_evidence_sufficiency": adj_case.get("question_4_evidence_sufficiency_finding", ""),
            "question_5_competency_depth": adj_case.get("question_5_competency_depth_limitation", ""),
            # Triage Guidance & Questions for the Expert
            "curator_triage_guidance_label": adj_case.get("triage_guidance_label", "unresolved_insufficient_source"),
            "sme_adjudication_questions": adj_case.get("sme_adjudication_questions", ""),
            "triage_readiness": "ready_for_expert_triage",
            "triage_readiness_status": True,
            "definitive_adjudication_readiness": "blocked_pending_additional_evidence",
            "definitive_adjudication_status": False,
            "blocking_reason": blocking_reason,
            # Blank Human Review & Adjudication Slots
            "adjudication_status": "pending_review",
            "final_adjudicated_label": None,
            "final_adjudicated_kcm_id": None,
            "final_adjudicated_kcm_name": None,
            "final_adjudicated_subtheme": None,
            "consensus_status": None,
            "panel_escalation_notes": None,
            "independent_reviews": [
                {
                    "reviewer_slot": 1,
                    "reviewer_id": None,
                    "reviewer_role": None,
                    "reviewer_affiliation": None,
                    "review_date": None,
                    "expert_decision_label": None,
                    "expert_target_kcm_id": None,
                    "expert_target_kcm_name": None,
                    "expert_subtheme": None,
                    "evidence_sufficiency_verdict": None,
                    "depth_assessment": None,
                    "confidence_rating": None,
                    "expert_rationale": None,
                    "missing_evidence_requisition_notes": None,
                },
                {
                    "reviewer_slot": 2,
                    "reviewer_id": None,
                    "reviewer_role": None,
                    "reviewer_affiliation": None,
                    "review_date": None,
                    "expert_decision_label": None,
                    "expert_target_kcm_id": None,
                    "expert_target_kcm_name": None,
                    "expert_subtheme": None,
                    "evidence_sufficiency_verdict": None,
                    "depth_assessment": None,
                    "confidence_rating": None,
                    "expert_rationale": None,
                    "missing_evidence_requisition_notes": None,
                },
            ],
        }
        triage_cases.append(case_obj)

    return triage_cases


def export_expert_triage_packet(cases: List[Dict[str, Any]]) -> None:
    strata_counts: Dict[str, int] = {}
    for c in cases:
        s = c["stratum"]
        strata_counts[s] = strata_counts.get(s, 0) + 1

    ev_counts: Dict[str, int] = {}
    for c in cases:
        ev = c["evidence_verification_status"]
        ev_counts[ev] = ev_counts.get(ev, 0) + 1

    packet_json_content: Dict[str, Any] = {
        "packet_id": "EXPERT-TRIAGE-PACKET-MOSPI-2026-V1",
        "benchmark_id": "BM-PILOT-MOSPI-2026-V1",
        "version": "1.0.0",
        "stage": "3.5",
        "created_at": "2026-10-18T20:00:00Z",
        "total_cases": len(cases),
        "triage_summary": {
            "ready_for_expert_triage": len(cases),
            "ready_for_definitive_adjudication": 0,
            "blocked_pending_additional_evidence": len(cases),
            "strata_breakdown": strata_counts,
            "evidence_verification_breakdown": ev_counts,
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
            "2": "Low: Related subject material identified from apex institutions, but exact iGOT course module outline is unverified.",
            "3": "Moderate: Apex institutional curriculum verified (e.g. ISTM classroom syllabus), but course duration, delivery modality, or audience differs from the online micro-course.",
            "4": "High: Granular course session outline verified with direct alignment to specific KCM sub-theme indicators, but lacking assessment data.",
            "5": "Very High: Complete syllabus with observable behavioral learning outcomes, practice exercises, and formative/summative assessment criteria verified.",
        },
        "consensus_workflow_rules": {
            "single_reviewer_threshold": "Allowed only when confidence >= 4 and supported by Level 3/4 syllabus evidence.",
            "dual_reviewer_mandatory": "Mandatory for all cases with confidence <= 3, all Domain gap cases, and all title-reference candidates.",
            "disagreement_escalation": "When two independent reviewers assign different benchmark labels, case is escalated to an NSSTA / MoSPI subject-matter expert panel.",
        },
        "cases": cases,
    }

    # Write JSON
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(packet_json_content, f, indent=2, ensure_ascii=False)
    print(f"Exported JSON: {OUTPUT_JSON_PATH} ({len(cases)} cases)")

    # Write CSV
    with open(OUTPUT_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for case in cases:
            r1 = case["independent_reviews"][0]
            r2 = case["independent_reviews"][1]
            row = {
                "benchmark_case_id": case["benchmark_case_id"],
                "stratum": case["stratum"],
                "course_record_id": case["course_record_id"],
                "course_name": case["course_name"],
                "cadre_role": case["cadre_role"],
                "acbp_competency_category": case["acbp_competency_category"],
                "duration": case["duration"],
                "course_creator": case["course_creator"],
                "primary_source_id": case["primary_source_id"],
                "primary_source_citation": case["primary_source_citation"],
                "primary_source_provenance": case["primary_source_provenance"],
                "primary_source_verification_status": case["primary_source_verification_status"],
                "candidate_kcm_id": case["candidate_kcm_id"] or "",
                "candidate_kcm_name": case["candidate_kcm_name"] or "",
                "candidate_kcm_type": case["candidate_kcm_type"] or "",
                "kcm_source_citation": case["kcm_source_citation"] or "",
                "alternative_kcm_candidates": case["alternative_kcm_candidates"],
                "potential_competency_overlaps": case["potential_competency_overlaps"],
                "evidence_source_id": case["evidence_source_id"],
                "evidence_source_title": case["evidence_source_title"],
                "evidence_institution": case["evidence_institution"],
                "evidence_url_or_path": case["evidence_url_or_path"],
                "evidence_verification_status": case["evidence_verification_status"],
                "is_exact_course_evidence": str(case["is_exact_course_evidence"]),
                "verified_evidence_summary": case["verified_evidence_summary"],
                "unverified_evidence_summary": case["unverified_evidence_summary"],
                "missing_evidence_details": case["missing_evidence_details"],
                "question_1_course_identity": case["question_1_course_identity"],
                "question_2_subject_coverage": case["question_2_subject_coverage"],
                "question_3_competency_alignment": case["question_3_competency_alignment"],
                "question_4_evidence_sufficiency": case["question_4_evidence_sufficiency"],
                "question_5_competency_depth": case["question_5_competency_depth"],
                "curator_triage_guidance_label": case["curator_triage_guidance_label"],
                "sme_adjudication_questions": case["sme_adjudication_questions"],
                "triage_readiness_status": str(case["triage_readiness_status"]),
                "definitive_adjudication_status": str(case["definitive_adjudication_status"]),
                "blocking_reason": case["blocking_reason"],
                "adjudication_status": case["adjudication_status"],
                "final_adjudicated_label": case["final_adjudicated_label"] or "",
                "final_adjudicated_kcm_id": case["final_adjudicated_kcm_id"] or "",
                "final_adjudicated_kcm_name": case["final_adjudicated_kcm_name"] or "",
                "final_adjudicated_subtheme": case["final_adjudicated_subtheme"] or "",
                "consensus_status": case["consensus_status"] or "",
                "panel_escalation_notes": case["panel_escalation_notes"] or "",
                # Reviewer 1 slots
                "r1_reviewer_id": r1["reviewer_id"] or "",
                "r1_reviewer_role": r1["reviewer_role"] or "",
                "r1_reviewer_affiliation": r1["reviewer_affiliation"] or "",
                "r1_review_date": r1["review_date"] or "",
                "r1_expert_decision_label": r1["expert_decision_label"] or "",
                "r1_expert_target_kcm_id": r1["expert_target_kcm_id"] or "",
                "r1_expert_target_kcm_name": r1["expert_target_kcm_name"] or "",
                "r1_expert_subtheme": r1["expert_subtheme"] or "",
                "r1_evidence_sufficiency_verdict": r1["evidence_sufficiency_verdict"] or "",
                "r1_depth_assessment": r1["depth_assessment"] or "",
                "r1_confidence_rating": r1["confidence_rating"] or "",
                "r1_expert_rationale": r1["expert_rationale"] or "",
                "r1_requisition_notes": r1["missing_evidence_requisition_notes"] or "",
                # Reviewer 2 slots
                "r2_reviewer_id": r2["reviewer_id"] or "",
                "r2_reviewer_role": r2["reviewer_role"] or "",
                "r2_reviewer_affiliation": r2["reviewer_affiliation"] or "",
                "r2_review_date": r2["review_date"] or "",
                "r2_expert_decision_label": r2["expert_decision_label"] or "",
                "r2_expert_target_kcm_id": r2["expert_target_kcm_id"] or "",
                "r2_expert_target_kcm_name": r2["expert_target_kcm_name"] or "",
                "r2_expert_subtheme": r2["expert_subtheme"] or "",
                "r2_evidence_sufficiency_verdict": r2["evidence_sufficiency_verdict"] or "",
                "r2_depth_assessment": r2["depth_assessment"] or "",
                "r2_confidence_rating": r2["confidence_rating"] or "",
                "r2_expert_rationale": r2["expert_rationale"] or "",
                "r2_requisition_notes": r2["missing_evidence_requisition_notes"] or "",
            }
            writer.writerow(row)
    print(f"Exported CSV: {OUTPUT_CSV_PATH} ({len(cases)} cases)")


def main() -> None:
    print("=" * 70)
    print("MoSPI SIH26101: Building Expert Triage Packet (Stage 3.5)")
    print("=" * 70)
    cases = build_expert_triage_cases()
    export_expert_triage_packet(cases)
    print("=" * 70)
    print("Expert Triage Packet successfully created.")


if __name__ == "__main__":
    main()
