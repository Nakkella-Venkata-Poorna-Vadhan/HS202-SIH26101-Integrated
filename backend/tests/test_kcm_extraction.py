"""
SIH26101 - Stage 2A: Automated Tests for KCM Competency Extraction & Validation
==============================================================================
Validates schema compliance, data integrity, format consistency, and zero-fabrication constraints.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.csv"
NOTES_PATH = PROJECT_ROOT / "docs" / "kcm_extraction_notes.md"

REQUIRED_FIELDS = [
    "competency_id",
    "competency_name",
    "competency_type",
    "description",
    "behaviours",
    "level_information",
    "source_id",
    "source_page",
    "provenance",
    "validation_status",
    "extraction_notes",
]

ALLOWED_TYPES = {"behavioural", "functional"}
EXPECTED_SOURCE_ID = "SRC-CBC-KCM-2024"
EXPECTED_TOTAL_COMPETENCIES = 34
EXPECTED_BEHAVIOURAL_COUNT = 13
EXPECTED_FUNCTIONAL_COUNT = 21


@pytest.fixture(scope="module")
def json_data():
    """Load processed JSON competency records."""
    assert JSON_PATH.exists(), f"Processed JSON file not found: {JSON_PATH}"
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def csv_data():
    """Load processed CSV competency records."""
    assert CSV_PATH.exists(), f"Processed CSV file not found: {CSV_PATH}"
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_processed_files_exist():
    """Verify that both output files and review notes exist."""
    assert JSON_PATH.exists(), "competencies_kcm.json does not exist."
    assert CSV_PATH.exists(), "competencies_kcm.csv does not exist."
    assert NOTES_PATH.exists(), "docs/kcm_extraction_notes.md does not exist."


def test_record_counts_consistency(json_data, csv_data):
    """Verify JSON and CSV have identical, expected record counts."""
    assert len(json_data) == EXPECTED_TOTAL_COMPETENCIES, (
        f"Expected {EXPECTED_TOTAL_COMPETENCIES} records in JSON, found {len(json_data)}"
    )
    assert len(csv_data) == EXPECTED_TOTAL_COMPETENCIES, (
        f"Expected {EXPECTED_TOTAL_COMPETENCIES} records in CSV, found {len(csv_data)}"
    )


def test_unique_competency_ids(json_data):
    """Verify all competency IDs are unique and properly formatted."""
    ids = [r["competency_id"] for r in json_data]
    assert len(ids) == len(set(ids)), f"Duplicate competency IDs detected: {ids}"
    for cid in ids:
        assert cid.startswith("KCM-BEH-") or cid.startswith("KCM-FUNC-"), (
            f"Invalid ID prefix: {cid}"
        )


def test_required_fields_present_in_all_records(json_data):
    """Verify every JSON record contains all required fields."""
    for r in json_data:
        for f in REQUIRED_FIELDS:
            assert f in r, f"Record {r.get('competency_id')} missing field: {f}"
            if f != "level_information":
                val = r[f]
                assert val is not None, f"Field {f} is None in {r.get('competency_id')}"
                if isinstance(val, (str, list)):
                    assert len(val) > 0, f"Field {f} is empty in {r.get('competency_id')}"


def test_allowed_competency_types(json_data):
    """Verify competency types and correct classification breakdown."""
    beh_count = 0
    func_count = 0

    for r in json_data:
        ctype = r["competency_type"]
        assert ctype in ALLOWED_TYPES, f"Invalid competency type '{ctype}' in {r['competency_id']}"
        if ctype == "behavioural":
            beh_count += 1
            assert r["competency_id"].startswith("KCM-BEH-")
        elif ctype == "functional":
            func_count += 1
            assert r["competency_id"].startswith("KCM-FUNC-")

    assert beh_count == EXPECTED_BEHAVIOURAL_COUNT, (
        f"Expected {EXPECTED_BEHAVIOURAL_COUNT} behavioural competencies, found {beh_count}"
    )
    assert func_count == EXPECTED_FUNCTIONAL_COUNT, (
        f"Expected {EXPECTED_FUNCTIONAL_COUNT} functional competencies, found {func_count}"
    )


def test_non_empty_names_and_definitions(json_data):
    """Verify that all names and descriptions are rich, authentic text."""
    for r in json_data:
        name = r["competency_name"]
        desc = r["description"]
        assert len(name.strip()) > 3, f"Competency name too short in {r['competency_id']}"
        assert len(desc.strip()) > 50, f"Competency description too short in {r['competency_id']}"


def test_valid_source_id_and_provenance(json_data):
    """Verify compliance with source register ID and official public provenance."""
    for r in json_data:
        assert r["source_id"] == EXPECTED_SOURCE_ID
        assert r["provenance"] == "official_public"
        assert r["validation_status"] == "pending_review"


def test_valid_page_numbers(json_data):
    """Verify that page numbers are valid within the 107-page KCM document."""
    for r in json_data:
        pages = r["source_page"]
        assert isinstance(pages, list), f"source_page must be a list in {r['competency_id']}"
        assert len(pages) == 2, f"source_page must contain [p_def, p_sub] in {r['competency_id']}"
        for p in pages:
            assert isinstance(p, int)
            assert 1 <= p <= 107, f"Invalid page number {p} in {r['competency_id']}"
        # Subtheme page follows definition page
        assert pages[1] == pages[0] + 1


def test_no_fabricated_competency_levels(json_data, csv_data):
    """Verify that no level scales were fabricated (level_information is null / empty)."""
    for r in json_data:
        assert r["level_information"] is None, (
            f"Expected level_information to be None, got: {r['level_information']} in {r['competency_id']}"
        )
    for row in csv_data:
        assert row["level_information"] == "", (
            f"Expected empty string for level_information in CSV, got: {row['level_information']}"
        )


def test_behaviours_structure_and_non_empty(json_data):
    """Verify that behaviours list is populated with sub-themes and indicator texts."""
    for r in json_data:
        behaviours = r["behaviours"]
        assert isinstance(behaviours, list), f"behaviours must be a list in {r['competency_id']}"
        assert len(behaviours) >= 2, f"Expected at least 2 behaviours/sub-themes in {r['competency_id']}"
        for b in behaviours:
            assert isinstance(b, str)
            assert len(b.strip()) > 10


def test_json_and_csv_field_value_consistency(json_data, csv_data):
    """Verify 1-to-1 fidelity between JSON and CSV output files."""
    assert len(json_data) == len(csv_data)

    csv_by_id = {row["competency_id"]: row for row in csv_data}

    for j_rec in json_data:
        cid = j_rec["competency_id"]
        assert cid in csv_by_id, f"ID {cid} not found in CSV"
        c_rec = csv_by_id[cid]

        assert j_rec["competency_name"] == c_rec["competency_name"]
        assert j_rec["competency_type"] == c_rec["competency_type"]
        assert j_rec["description"] == c_rec["description"]
        assert j_rec["source_id"] == c_rec["source_id"]
        assert j_rec["provenance"] == c_rec["provenance"]
        assert j_rec["validation_status"] == c_rec["validation_status"]
        assert j_rec["extraction_notes"] == c_rec["extraction_notes"]

        # Parse CSV serialized JSON strings
        parsed_behaviours = json.loads(c_rec["behaviours"])
        assert j_rec["behaviours"] == parsed_behaviours

        parsed_pages = json.loads(c_rec["source_page"])
        assert j_rec["source_page"] == parsed_pages


def test_notes_documentation_contents():
    """Verify that review notes documentation contains required analytical sections."""
    text = NOTES_PATH.read_text(encoding="utf-8")
    assert "Executive Summary" in text
    assert "Structure and Organization" in text
    assert "Explicit Competency Level Scale Findings" in text
    assert "Source Layout Anomalies" in text
    assert "Ingested Competencies Inventory" in text
    assert "KCM-FUNC-21" in text
    assert "Change Management Sub-Themes" in text


# =============================================================================
# STAGE 2A.2 REMEDIATED REGRESSION TESTS & RECONCILIATION FIXTURES
# =============================================================================

EXPECTED_KCM_RECONCILIATION = {
    "KCM-BEH-01": [
        "Self-Learning",
        "Self-Analysis",
        "Self Confidence",
        "Purposefulness",
    ],
    "KCM-BEH-02": [
        "Stress Management",
        "Navigating Ambiguity",
        "Resilience",
    ],
    "KCM-BEH-03": [
        "Attention to Detail",
        "Systems Thinking",
        "Analytical Thinking",
    ],
    "KCM-BEH-04": [
        "Reading & Comprehension",
        "Active Listening",
        "Verbal & Non-verbal communication",
        "Presentation skills",
    ],
    "KCM-BEH-05": [
        "Initiative & Drive",
        "Goal Setting",
        "Accountability",
        "Commitment to Quality",
    ],
    "KCM-BEH-06": [
        "Relationship Management",
        "Knowledge Sharing",
        "Diversity & Inclusion",
    ],
    "KCM-BEH-07": [
        "Empathy",
        "Responsiveness",
        "Service Excellence",
    ],
    "KCM-BEH-08": [
        "Process Excellence",
        "Resource Management",
        "Continuous Improvement",
        "Planning & Prioritization",
    ],
    "KCM-BEH-09": [
        "Lateral Thinking",
        "Transformation Orientation",
    ],
    "KCM-BEH-10": [
        "Global Mindset",
        "Forward Thinking",
        "Executive Presence",
        "Sustainable Mindset",
    ],
    "KCM-BEH-11": [
        "Influencing & Negotiation",
        "Conflict Management",
    ],
    "KCM-BEH-12": [
        "Mentoring",
        "Inspiring Others",
        "Sharing Constructive Feedback",
    ],
    "KCM-BEH-13": [
        "Logical Reasoning",
        "Sound Judgement",
    ],
    "KCM-FUNC-01": [
        "Design Thinking",
        "Citizen Partnering & Collaboration",
        "Political, Economic, Social, Technological Consciousness",
    ],
    "KCM-FUNC-02": [
        "Research & Needs Analysis",
        "Policy Design /Amendment",
        "Policy Implementation",
        "Policy Monitoring & Impact Assessment",
    ],
    "KCM-FUNC-03": [
        "Rules of Business",
        "Cabinet Note Writing",
    ],
    "KCM-FUNC-04": [
        "Research & Needs Analysis",
        "Scheme / Program Design",
        "Feasibility and Risk Assessment",
        "Implementation & Outreach",
    ],
    "KCM-FUNC-05": [
        "Project Planning",
        "Project Implementation",
        "Project Evaluation",
        "Project KPIs Monitoring",
    ],
    "KCM-FUNC-06": [
        "Procurement management through GeM",
        "Procurement of Goods / Services / Works",
        "Contract Management",
        "Vendor / Consultant Management",
    ],
    "KCM-FUNC-07": [
        "Inventory Management",
        "Maintenance and Disposal of materials",
    ],
    "KCM-FUNC-08": [
        "Creation of M&E Framework",
        "Evaluation and output / outcome",
    ],
    "KCM-FUNC-09": [
        "Budget Formulation & Implementation",
        "PFMS Portal Management",
        "Expenditure Management",
        "Government Accounts",
    ],
    "KCM-FUNC-10": [
        "Digital Tools (MS office, Excel & PPT) and Platforms",
        "Digital Service Design",
    ],
    "KCM-FUNC-11": [
        "Data Management (Clean-up, segregation, processing)",
        "Data Analysis & Visualization",
        "Data-led Decision Making",
        "Data Use & Governance",
    ],
    "KCM-FUNC-12": [
        "Establishment Matters",
        "Fundamental Rules / Supplementary Rules (FRSR)",
        "Reservations",
        "Prevention of Sexual Harassment Policy",
        "Performance Appraisal",
    ],
    "KCM-FUNC-13": [
        "E-Office",
        "File/DAK Management",
        "Office Procedures",
        "Noting & Drafting of official Communications",
        "Technical Proposal / Report writing",
    ],
    "KCM-FUNC-14": [
        "Submission of briefs, supply of information",
        "Maintaining records of parliamentary matters",
    ],
    "KCM-FUNC-15": [
        "RTI Responsiveness",
        "RTI Records and Report management",
    ],
    "KCM-FUNC-16": [
        "Manage cases on CPGRAMS",
        "Public Grievance Handling",
    ],
    "KCM-FUNC-17": [
        "Conduct Rules",
        "Provisions on Suspension",
        "Proposal preparation for disciplinary proceedings",
        "Handling prosecution cases; supporting investigations",
        "Preventive Vigilance",
    ],
    "KCM-FUNC-18": [
        "Legal Know-how: Basic Knowledge of Legal drafting",
        "Court Cases Management",
        "LIMBS Portal Management",
    ],
    "KCM-FUNC-19": [
        "Dissemination of Information",
        "Handling social media (engagement)",
        "Management of information on official websites",
    ],
    "KCM-FUNC-20": [
        "Change Readiness",
        "Accepting Change",
        "Implementing Change",
    ],
    "KCM-FUNC-21": [
        "Allowances & Reimbursements",
        "Leave and Travel",
        "Miscellaneous matters (Telephone, Car, Residence, Personal Staff etc.)",
        "Implementing Official Language",
    ],
}


def test_no_sentence_fragment_pseudo_titles(json_data):
    """Verify that behaviour strings start with authentic sub-theme titles, not body sentence fragments."""
    fragment_markers = [
        "Exhibits a commitment",
        "Displays the quality",
        "Demonstrates ability",
        "Demonstrates proficiency",
        "Ability to believe",
        "Ability to align",
        "Identifies one’s",
        "Objectively analyse",
    ]
    violations = []
    for r in json_data:
        for b in r["behaviours"]:
            title = b.split(":")[0].strip()
            for marker in fragment_markers:
                if title.startswith(marker):
                    violations.append(f"[{r['competency_id']}] Pseudo-title: '{title}'")
    assert violations == [], f"Found sentence-fragment pseudo-titles:\n" + "\n".join(violations)


def test_no_concatenated_multi_titles(json_data):
    """Verify that behaviour strings do not contain multiple concatenated sub-theme titles."""
    concatenated_markers = [
        "Self-Learning Self-Analysis",
        "Stress Management Navigating Ambiguity",
        "Attention to Detail Systems Thinking",
        "Lateral Thinking Transformation",
        "Rules of Business Cabinet Note",
        "Inventory Management Maintenance",
        "Change Readiness Accepting Change",
    ]
    violations = []
    for r in json_data:
        for b in r["behaviours"]:
            title = b.split(":")[0].strip()
            for marker in concatenated_markers:
                if marker in title:
                    violations.append(f"[{r['competency_id']}] Concatenated title: '{title}'")
    assert violations == [], f"Found concatenated titles:\n" + "\n".join(violations)


def test_exact_official_subtheme_counts(json_data):
    """Verify that each competency has its exact official sub-theme count from KCM."""
    expected_counts = {cid: len(titles) for cid, titles in EXPECTED_KCM_RECONCILIATION.items()}
    mismatches = []
    for r in json_data:
        cid = r["competency_id"]
        actual = len(r["behaviours"])
        expected = expected_counts[cid]
        if actual != expected:
            mismatches.append(f"{cid} ({r['competency_name']}): expected {expected}, got {actual}")
    assert mismatches == [], f"Count mismatches detected:\n" + "\n".join(mismatches)


def test_subtheme_titles_and_descriptions_against_reconciliation_fixture(json_data):
    """Verify that every extracted sub-theme title matches the ground truth and has a robust description."""
    for r in json_data:
        cid = r["competency_id"]
        expected_titles = EXPECTED_KCM_RECONCILIATION[cid]
        behaviours = r["behaviours"]

        assert len(behaviours) == len(expected_titles), (
            f"[{cid}] Count mismatch: expected {len(expected_titles)}, got {len(behaviours)}"
        )

        for idx, (b_str, exp_title) in enumerate(zip(behaviours, expected_titles)):
            prefix = f"{exp_title}: "
            assert b_str.startswith(prefix), (
                f"[{cid}] Behaviour #{idx + 1} does not start with expected title '{exp_title}'. Found: '{b_str[:60]}'"
            )
            desc = b_str[len(prefix):].strip()

            assert len(desc) >= 50, (
                f"[{cid}] Description too short ({len(desc)} chars) for '{exp_title}'"
            )
            assert not desc.startswith(":"), f"[{cid}] Description starts with colon in '{exp_title}'"


def test_project_management_subtheme_fidelity(json_data):
    """Verify that Project Management contains exactly 4 distinct sub-themes including Project KPIs Monitoring."""
    pm_rec = next((r for r in json_data if r["competency_id"] == "KCM-FUNC-05"), None)
    assert pm_rec is not None, "KCM-FUNC-05 not found"
    assert pm_rec["source_page"] == [74, 75]

    titles = [b.split(":", 1)[0].strip() for b in pm_rec["behaviours"]]
    assert titles == [
        "Project Planning",
        "Project Implementation",
        "Project Evaluation",
        "Project KPIs Monitoring",
    ]


def test_page_107_administration_matters_fidelity(json_data):
    """Verify that Page 107 is correctly mapped to Administration Matters despite its header typo."""
    admin_rec = next((r for r in json_data if r["competency_id"] == "KCM-FUNC-21"), None)
    assert admin_rec is not None, "KCM-FUNC-21 not found"
    assert admin_rec["source_page"] == [106, 107]
    assert admin_rec["competency_name"] == "Administration Matters"

    titles = [b.split(":", 1)[0].strip() for b in admin_rec["behaviours"]]
    assert titles == [
        "Allowances & Reimbursements",
        "Leave and Travel",
        "Miscellaneous matters (Telephone, Car, Residence, Personal Staff etc.)",
        "Implementing Official Language",
    ]

    # Verify Change Management is on pages 104 and 105
    cm_rec = next((r for r in json_data if r["competency_id"] == "KCM-FUNC-20"), None)
    assert cm_rec is not None, "KCM-FUNC-20 not found"
    assert cm_rec["source_page"] == [104, 105]
    cm_titles = [b.split(":", 1)[0].strip() for b in cm_rec["behaviours"]]
    assert cm_titles == ["Change Readiness", "Accepting Change", "Implementing Change"]


def test_csmop_repeated_definition_fidelity(json_data):
    """Verify that Office Management, Parliamentary Matters, and RTI Matters retain their verified source definitions."""
    rec_office = next((r for r in json_data if r["competency_id"] == "KCM-FUNC-13"), None)
    rec_parl = next((r for r in json_data if r["competency_id"] == "KCM-FUNC-14"), None)
    rec_rti = next((r for r in json_data if r["competency_id"] == "KCM-FUNC-15"), None)

    assert rec_office is not None and rec_parl is not None and rec_rti is not None

    # Definitions are identical in the government publication
    assert rec_office["description"] == rec_parl["description"] == rec_rti["description"]
    assert "Central Secretariat Manual of Office Procedure" in rec_office["description"]

    # But their sub-themes are completely distinct
    sub_office = [b.split(":", 1)[0].strip() for b in rec_office["behaviours"]]
    sub_parl = [b.split(":", 1)[0].strip() for b in rec_parl["behaviours"]]
    sub_rti = [b.split(":", 1)[0].strip() for b in rec_rti["behaviours"]]

    assert len(sub_office) == 5
    assert len(sub_parl) == 2
    assert len(sub_rti) == 2
    assert set(sub_office).isdisjoint(set(sub_parl))
    assert set(sub_office).isdisjoint(set(sub_rti))
    assert set(sub_parl).isdisjoint(set(sub_rti))
