"""
Synthetic Seed Data Generator for Prototype Demonstration.
Creates explicitly labelled synthetic role requirements and learner profiles in data/synthetic/.
Never modifies official datasets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from competency_engine.config import (
    DATA_SYNTHETIC_DIR,
    SYNTHETIC_LEARNERS_PATH,
    SYNTHETIC_ROLES_PATH,
)

# Explicit provenance banner
SYNTHETIC_METADATA = {
    "provenance": "synthetic",
    "is_synthetic": True,
    "warning": (
        "PROTOTYPE DEMONSTRATION DATA ONLY. "
        "These roles and learner assessments are synthetic fixtures generated for the "
        "SIH26101 prototype. They do not represent real civil servants, official personnel records, "
        "or authenticated iGOT Karmayogi learner data."
    ),
    "generated_for": "SIH26101 Stage 4.1 Prototype Slice",
}

SEED_ROLES: List[Dict[str, Any]] = [
    {
        "role_id": "ROLE-SSO-SO",
        "role_name": "Senior Statistical Officer / Section Officer",
        "cadre_role": "Senior Statistical Officers / Section Officer / Senior Administrative Officer / Administrative Officer",
        "description": "Supervises field survey operations, data scrutiny, statistical tabulations, and section administration.",
        "department": "Field Operations Division (FOD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "required_competencies": [
            {
                "competency_id": "KCM-FUNC-11",
                "competency_name": "Data Analytics",
                "required_level": 4,
                "priority": "critical",
                "rationale": "Supervises survey data validation, tabulation algorithms, outlier scrutiny, and official statistical estimation.",
            },
            {
                "competency_id": "KCM-FUNC-21",
                "competency_name": "Administration Matters",
                "required_level": 3,
                "priority": "high",
                "rationale": "Manages section workflows, file movement, staff duties, and official correspondence.",
            },
            {
                "competency_id": "KCM-BEH-04",
                "competency_name": "Communication",
                "required_level": 3,
                "priority": "high",
                "rationale": "Drafts analytical survey inspection reports, briefing notes, and coordinates field communications.",
            },
            {
                "competency_id": "KCM-BEH-02",
                "competency_name": "Personal Effectiveness",
                "required_level": 3,
                "priority": "medium",
                "rationale": "Handles field operational stress, unexpected survey sampling roadblocks, and strict survey timelines.",
            },
        ],
    },
    {
        "role_id": "ROLE-DIR-JD",
        "role_name": "Director / Joint Director",
        "cadre_role": "Director / Joint Director",
        "description": "Programme director leading national survey rounds, macro-statistical compilations, and inter-cadre supervision.",
        "department": "National Accounts Division (NAD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "required_competencies": [
            {
                "competency_id": "KCM-FUNC-05",
                "competency_name": "Project Management",
                "required_level": 4,
                "priority": "critical",
                "rationale": "Leads multi-year statistical census and survey programmes, milestone delivery, and resource planning.",
            },
            {
                "competency_id": "KCM-BEH-10",
                "competency_name": "Strategic Leadership",
                "required_level": 4,
                "priority": "high",
                "rationale": "Steers institutional statistical reforms, methodological modernization, and inter-agency coordination.",
            },
            {
                "competency_id": "KCM-BEH-06",
                "competency_name": "Collaboration",
                "required_level": 3,
                "priority": "high",
                "rationale": "Coordinates with Directorate of Economics and Statistics (DES), line ministries, and international bodies.",
            },
            {
                "competency_id": "KCM-FUNC-01",
                "competency_name": "Citizen Centricity",
                "required_level": 3,
                "priority": "medium",
                "rationale": "Ensures official statistical releases and microdata dissemination satisfy public and policy needs transparently.",
            },
        ],
    },
    {
        "role_id": "ROLE-DDG-JS",
        "role_name": "Deputy Director General / Joint Secretary",
        "cadre_role": "Deputy Director General / Joint Secretary Equivalent and Above",
        "description": "Apex executive leadership overseeing broad ministerial divisions, national statistical policy, and statutory compliance.",
        "department": "Economic Statistics Division (ESD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "required_competencies": [
            {
                "competency_id": "KCM-BEH-10",
                "competency_name": "Strategic Leadership",
                "required_level": 5,
                "priority": "critical",
                "rationale": "National statistical strategy, high-level policy advice, and inter-ministerial vision under Mission Karmayogi.",
            },
            {
                "competency_id": "KCM-BEH-06",
                "competency_name": "Collaboration",
                "required_level": 4,
                "priority": "high",
                "rationale": "Builds high-level partnerships across state statistical machineries and international agencies.",
            },
            {
                "competency_id": "KCM-FUNC-17",
                "competency_name": "Vigilance Administration",
                "required_level": 4,
                "priority": "high",
                "rationale": "Conducts disciplinary oversight, upholds administrative integrity, and enforces statutory rules.",
            },
            {
                "competency_id": "KCM-FUNC-09",
                "competency_name": "Financial Management",
                "required_level": 4,
                "priority": "medium",
                "rationale": "Oversees departmental scheme budget formulations, capital allocations, and public finance compliance.",
            },
        ],
    },
    {
        "role_id": "ROLE-DS-US",
        "role_name": "Deputy Secretary / Under Secretary",
        "cadre_role": "Deputy Secretary / Under Secretary",
        "description": "Mid-level executive handling procurement of works, establishment rules, and administrative scrutinies.",
        "department": "Administration & General Division, MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "required_competencies": [
            {
                "competency_id": "KCM-FUNC-06",
                "competency_name": "Public Procurement - GFR",
                "required_level": 4,
                "priority": "critical",
                "rationale": "Manages procurement tenders, EPC contracts, and ensures adherence to GFR 2017 rules.",
            },
            {
                "competency_id": "KCM-FUNC-12",
                "competency_name": "Establishment & HR",
                "required_level": 4,
                "priority": "high",
                "rationale": "Supervises service books, pay fixation under FRSR, deputations, and cadre welfare.",
            },
            {
                "competency_id": "KCM-BEH-06",
                "competency_name": "Collaboration",
                "required_level": 3,
                "priority": "high",
                "rationale": "Aligns operational workflows across administrative sections and technical divisions.",
            },
            {
                "competency_id": "KCM-BEH-03",
                "competency_name": "Problem Solving",
                "required_level": 3,
                "priority": "medium",
                "rationale": "Diagnoses bureaucratic bottlenecks and synthesizes administrative solutions.",
            },
        ],
    },
    {
        "role_id": "ROLE-JSO-ASO",
        "role_name": "Junior Statistical Officer / Assistant Section Officer",
        "cadre_role": "Junior Statistical Officers / Assistant Section Officers / Data Processing Assistant (All Grades)",
        "description": "Primary fieldwork inspection, primary data compilation, and procedural case file processing.",
        "department": "Survey Design & Research Division (SDRD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "required_competencies": [
            {
                "competency_id": "KCM-FUNC-11",
                "competency_name": "Data Analytics",
                "required_level": 3,
                "priority": "critical",
                "rationale": "Executes data cleaning, script verification, consistency checks, and basic descriptive statistics.",
            },
            {
                "competency_id": "KCM-BEH-01",
                "competency_name": "Self-Awareness",
                "required_level": 3,
                "priority": "medium",
                "rationale": "Commitment to ongoing statistical learning, self-reflection, and official statistical integrity.",
            },
            {
                "competency_id": "KCM-BEH-04",
                "competency_name": "Communication",
                "required_level": 2,
                "priority": "medium",
                "rationale": "Field survey respondent interaction, interview questioning, and daily reporting.",
            },
            {
                "competency_id": "KCM-FUNC-21",
                "competency_name": "Administration Matters",
                "required_level": 2,
                "priority": "medium",
                "rationale": "Adheres to office procedures, file indexing, and routine noting protocols.",
            },
        ],
    },
]

SEED_LEARNERS: List[Dict[str, Any]] = [
    {
        "learner_id": "LEARNER-001",
        "name": "Arun Kumar",
        "role_id": "ROLE-SSO-SO",
        "cadre_role": "Senior Statistical Officers / Section Officer / Senior Administrative Officer / Administrative Officer",
        "department": "Field Operations Division (FOD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "assessed_competencies": [
            {
                "competency_id": "KCM-FUNC-11",
                "estimated_level": 2,
                "assessment_status": "assessed",
                "confidence": 0.85,
                "evidence_sources": [
                    "synthetic_statistical_coding_quiz_score_68pct",
                    "synthetic_in_service_refresher_2025",
                ],
                "last_assessed_date": "2026-08-15T10:00:00Z",
            },
            {
                "competency_id": "KCM-FUNC-21",
                "estimated_level": 3,
                "assessment_status": "assessed",
                "confidence": 0.90,
                "evidence_sources": [
                    "synthetic_supervisor_annual_evaluation_satisfactory",
                ],
                "last_assessed_date": "2026-07-20T14:30:00Z",
            },
            {
                "competency_id": "KCM-BEH-04",
                "estimated_level": 2,
                "assessment_status": "assessed",
                "confidence": 0.70,
                "evidence_sources": [
                    "synthetic_peer_feedback_survey_communication_q2",
                ],
                "last_assessed_date": "2026-06-10T09:15:00Z",
            },
            {
                "competency_id": "KCM-BEH-02",
                "estimated_level": None,
                "assessment_status": "unassessed",
                "confidence": 0.0,
                "evidence_sources": [],
                "last_assessed_date": None,
            },
        ],
    },
    {
        "learner_id": "LEARNER-002",
        "name": "Dr. Meenakshi Sundaram",
        "role_id": "ROLE-DIR-JD",
        "cadre_role": "Director / Joint Director",
        "department": "National Accounts Division (NAD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "assessed_competencies": [
            {
                "competency_id": "KCM-FUNC-05",
                "estimated_level": 2,
                "assessment_status": "assessed",
                "confidence": 0.80,
                "evidence_sources": [
                    "synthetic_management_assessment_simulation_mid_score",
                ],
                "last_assessed_date": "2026-09-01T11:00:00Z",
            },
            {
                "competency_id": "KCM-BEH-10",
                "estimated_level": 3,
                "assessment_status": "assessed",
                "confidence": 0.85,
                "evidence_sources": [
                    "synthetic_executive_leadership_360_feedback",
                ],
                "last_assessed_date": "2026-08-25T16:00:00Z",
            },
            {
                "competency_id": "KCM-BEH-06",
                "estimated_level": 3,
                "assessment_status": "assessed",
                "confidence": 0.90,
                "evidence_sources": [
                    "synthetic_inter_ministerial_working_group_chair_appraisal",
                ],
                "last_assessed_date": "2026-07-30T10:00:00Z",
            },
            {
                "competency_id": "KCM-FUNC-01",
                "estimated_level": 3,
                "assessment_status": "assessed",
                "confidence": 0.85,
                "evidence_sources": [
                    "synthetic_public_data_portal_user_satisfaction_audit",
                ],
                "last_assessed_date": "2026-07-15T15:00:00Z",
            },
        ],
    },
    {
        "learner_id": "LEARNER-003",
        "name": "Pooja Verma",
        "role_id": "ROLE-JSO-ASO",
        "cadre_role": "Junior Statistical Officers / Assistant Section Officers / Data Processing Assistant (All Grades)",
        "department": "Survey Design & Research Division (SDRD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "assessed_competencies": [
            # Fresh recruit: all competencies unassessed or with zero recorded assessment evidence
            {
                "competency_id": "KCM-FUNC-11",
                "estimated_level": None,
                "assessment_status": "unassessed",
                "confidence": 0.0,
                "evidence_sources": [],
                "last_assessed_date": None,
            },
            {
                "competency_id": "KCM-BEH-01",
                "estimated_level": None,
                "assessment_status": "unassessed",
                "confidence": 0.0,
                "evidence_sources": [],
                "last_assessed_date": None,
            },
            {
                "competency_id": "KCM-BEH-04",
                "estimated_level": None,
                "assessment_status": "unassessed",
                "confidence": 0.0,
                "evidence_sources": [],
                "last_assessed_date": None,
            },
            {
                "competency_id": "KCM-FUNC-21",
                "estimated_level": None,
                "assessment_status": "unassessed",
                "confidence": 0.0,
                "evidence_sources": [],
                "last_assessed_date": None,
            },
        ],
    },
    {
        "learner_id": "LEARNER-004",
        "name": "Rajesh Sharma",
        "role_id": "ROLE-DDG-JS",
        "cadre_role": "Deputy Director General / Joint Secretary Equivalent and Above",
        "department": "Economic Statistics Division (ESD), MoSPI",
        "is_synthetic": True,
        "provenance": "synthetic",
        "assessed_competencies": [
            {
                "competency_id": "KCM-BEH-10",
                "estimated_level": 4,
                "assessment_status": "assessed",
                "confidence": 0.85,
                "evidence_sources": [
                    "synthetic_executive_mentorship_panel_review",
                ],
                "last_assessed_date": "2026-08-10T12:00:00Z",
            },
            {
                "competency_id": "KCM-BEH-06",
                "estimated_level": 2,
                "assessment_status": "assessed",
                "confidence": 0.75,
                "evidence_sources": [
                    "synthetic_inter_agency_stakeholder_survey_2026",
                ],
                "last_assessed_date": "2026-07-12T14:00:00Z",
            },
            {
                "competency_id": "KCM-FUNC-17",
                "estimated_level": 4,
                "assessment_status": "assessed",
                "confidence": 0.90,
                "evidence_sources": [
                    "synthetic_inquiry_officer_empanelment_certificate",
                ],
                "last_assessed_date": "2026-06-25T11:00:00Z",
            },
            {
                "competency_id": "KCM-FUNC-09",
                "estimated_level": 3,
                "assessment_status": "assessed",
                "confidence": 0.80,
                "evidence_sources": [
                    "synthetic_budget_standing_committee_appraisal",
                ],
                "last_assessed_date": "2026-05-18T16:30:00Z",
            },
        ],
    },
]


def seed_synthetic_data(force: bool = False) -> Dict[str, int]:
    """
    Ensure synthetic seed datasets exist in data/synthetic/.
    If force=True, overwrites synthetic files with seed baselines.
    Never alters data/raw/ or data/processed/.
    """
    DATA_SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

    seeded_counts = {"roles": 0, "learners": 0}

    # Seed roles
    if force or not SYNTHETIC_ROLES_PATH.exists():
        payload = {
            "metadata": SYNTHETIC_METADATA,
            "total_roles": len(SEED_ROLES),
            "roles": SEED_ROLES,
        }
        with open(SYNTHETIC_ROLES_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        seeded_counts["roles"] = len(SEED_ROLES)
    else:
        with open(SYNTHETIC_ROLES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            seeded_counts["roles"] = len(data.get("roles", []))

    # Seed learners
    if force or not SYNTHETIC_LEARNERS_PATH.exists():
        payload = {
            "metadata": SYNTHETIC_METADATA,
            "total_learners": len(SEED_LEARNERS),
            "learners": SEED_LEARNERS,
        }
        with open(SYNTHETIC_LEARNERS_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        seeded_counts["learners"] = len(SEED_LEARNERS)
    else:
        with open(SYNTHETIC_LEARNERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            seeded_counts["learners"] = len(data.get("learners", []))

    return seeded_counts


if __name__ == "__main__":
    counts = seed_synthetic_data(force=True)
    print(f"Seeded {counts['roles']} roles and {counts['learners']} learners to {DATA_SYNTHETIC_DIR}.")
