"""
MoSPI ACBP to KCM Competency Mapping Benchmark Builder (Stage 3.3).

Generates the 26-case human-reviewed benchmark manifest and reviewer template.
Strictly adheres to referential integrity and safeguards against fabricated labels:
  - 100% of cases reference real courses in data/processed/acbp_courses.json.
  - All target KCM competencies reference valid entries in data/processed/competencies_kcm.json.
  - All reviewer decision fields and ground-truth labels are left strictly null / unassigned.
  - Output artifacts are versioned and exported in both JSON and CSV formats.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input paths (strictly read-only)
ACBP_COURSES_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_COMPETENCIES_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
MAPPINGS_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.json"

# Output paths
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
BENCHMARK_MANIFEST_JSON = INTERIM_DIR / "mapping_benchmark_manifest.json"
BENCHMARK_MANIFEST_CSV = INTERIM_DIR / "mapping_benchmark_manifest.csv"
BENCHMARK_TEMPLATE_JSON = INTERIM_DIR / "mapping_benchmark_template.json"
BENCHMARK_TEMPLATE_CSV = INTERIM_DIR / "mapping_benchmark_template.csv"

# Stratified sampling definition for the 26 benchmark cases
BENCHMARK_CASE_SPECS = [
    # Strata A: The 6 Existing Title-Reference Candidates
    {
        "case_id": "BM-CASE-001",
        "stratum": "strata_a_title_candidate",
        "course_id": "ACBP-CRS-017",
        "target_kcm_id": "KCM-BEH-06",
        "sampling_rationale": "Existing title-reference candidate; tests whether 'Sahakaryata in Public Service' maps to Collaboration (KCM-BEH-06) or requires deeper syllabus proof.",
    },
    {
        "case_id": "BM-CASE-002",
        "stratum": "strata_a_title_candidate",
        "course_id": "ACBP-CRS-036",
        "target_kcm_id": "KCM-FUNC-05",
        "sampling_rationale": "Existing title-reference candidate; tests whether 'Leadership in Project Management' maps to Project Management (KCM-FUNC-05) or Behavioural Leadership.",
    },
    {
        "case_id": "BM-CASE-003",
        "stratum": "strata_a_title_candidate",
        "course_id": "ACBP-CRS-040",
        "target_kcm_id": "KCM-BEH-10",
        "sampling_rationale": "Existing title-reference candidate; tests whether 'Strategic Leadership: The Indic Way' maps to Strategic Leadership (KCM-BEH-10).",
    },
    {
        "case_id": "BM-CASE-004",
        "stratum": "strata_a_title_candidate",
        "course_id": "ACBP-CRS-041",
        "target_kcm_id": "KCM-BEH-06",
        "sampling_rationale": "Existing title-reference candidate; repeated course at Director level; tests cadre-specific syllabus variation against KCM-BEH-06.",
    },
    {
        "case_id": "BM-CASE-005",
        "stratum": "strata_a_title_candidate",
        "course_id": "ACBP-CRS-060",
        "target_kcm_id": "KCM-BEH-10",
        "sampling_rationale": "Existing title-reference candidate; repeated course at Deputy Secretary level; tests cadre consistency against KCM-BEH-10.",
    },
    {
        "case_id": "BM-CASE-006",
        "stratum": "strata_a_title_candidate",
        "course_id": "ACBP-CRS-061",
        "target_kcm_id": "KCM-BEH-06",
        "sampling_rationale": "Existing title-reference candidate; repeated course at Deputy Secretary level; tests cadre consistency against KCM-BEH-06.",
    },
    # Strata B: Stratified Unresolved Behavioural Courses
    {
        "case_id": "BM-CASE-007",
        "stratum": "strata_b_behavioural_unresolved",
        "course_id": "ACBP-CRS-014",
        "target_kcm_id": None,
        "sampling_rationale": "Broad cultural title ('Developing a Positive Work Culture'); highly repeated (11 cadres); tests whether broad organizational culture maps to specific KCM behavioural competencies.",
    },
    {
        "case_id": "BM-CASE-008",
        "stratum": "strata_b_behavioural_unresolved",
        "course_id": "ACBP-CRS-022",
        "target_kcm_id": None,
        "sampling_rationale": "Workplace wellness title ('Yoga Break at Workplace'); tests boundary condition of whether physical wellness is out-of-scope or maps to self-regulation/personal effectiveness.",
    },
    {
        "case_id": "BM-CASE-009",
        "stratum": "strata_b_behavioural_unresolved",
        "course_id": "ACBP-CRS-023",
        "target_kcm_id": None,
        "sampling_rationale": "Indic ethos title ('Happiness in Seva-Bhava: Lessons from Bhagavad-Gita'); tests alignment with Service Orientation (KCM-BEH-07) and civil service values.",
    },
    {
        "case_id": "BM-CASE-010",
        "stratum": "strata_b_behavioural_unresolved",
        "course_id": "ACBP-CRS-043",
        "target_kcm_id": None,
        "sampling_rationale": "Self-leadership title ('Leading from Within: Behavioural Strategies for Self-Leadership'); tests potential mapping to Self-Awareness (KCM-BEH-01) or Team Leadership.",
    },
    {
        "case_id": "BM-CASE-011",
        "stratum": "strata_b_behavioural_unresolved",
        "course_id": "ACBP-CRS-125",
        "target_kcm_id": None,
        "sampling_rationale": "Specific communication skill ('The Art of Listening'); tests whether granular interpersonal skill maps to Communication (KCM-BEH-04).",
    },
    {
        "case_id": "BM-CASE-012",
        "stratum": "strata_b_behavioural_unresolved",
        "course_id": "ACBP-CRS-142",
        "target_kcm_id": None,
        "sampling_rationale": "Social perspective title ('Revisiting Gender Equality through the Indian Spiritual Vision'); tests potential alignment with Citizen Centricity / Service Orientation.",
    },
    # Strata C: Stratified Unresolved Functional Courses
    {
        "case_id": "BM-CASE-013",
        "stratum": "strata_c_functional_unresolved",
        "course_id": "ACBP-CRS-008",
        "target_kcm_id": None,
        "sampling_rationale": "Quasi-judicial inquiry title ('Conduct of Inquiry in Disciplinary Matters'); tests potential mapping to Vigilance Administration (KCM-FUNC-17) or Administration Matters.",
    },
    {
        "case_id": "BM-CASE-014",
        "stratum": "strata_c_functional_unresolved",
        "course_id": "ACBP-CRS-010",
        "target_kcm_id": None,
        "sampling_rationale": "Policy analysis title ('Fundamentals of Public Policy'); tests potential mapping to Policy Architecture (KCM-FUNC-02) or Govt Program Formulation.",
    },
    {
        "case_id": "BM-CASE-015",
        "stratum": "strata_c_functional_unresolved",
        "course_id": "ACBP-CRS-011",
        "target_kcm_id": None,
        "sampling_rationale": "Financial evaluation title ('Project A ppraisal and Financial Evaluation Techniques'); tests multi-competency ambiguity between Financial Management (KCM-FUNC-09) and Project Management (KCM-FUNC-05).",
    },
    {
        "case_id": "BM-CASE-016",
        "stratum": "strata_c_functional_unresolved",
        "course_id": "ACBP-CRS-013",
        "target_kcm_id": None,
        "sampling_rationale": "Legislative process title ('Navigating Parliamentary Questions'); tests direct semantic mapping to Handling Parliamentary Matters (KCM-FUNC-14).",
    },
    {
        "case_id": "BM-CASE-017",
        "stratum": "strata_c_functional_unresolved",
        "course_id": "ACBP-CRS-053",
        "target_kcm_id": None,
        "sampling_rationale": "Procurement title ('Procurement of Works'); tests mapping to Public Procurement (GFR) (KCM-FUNC-06) under civil service financial regulations.",
    },
    {
        "case_id": "BM-CASE-018",
        "stratum": "strata_c_functional_unresolved",
        "course_id": "ACBP-CRS-055",
        "target_kcm_id": None,
        "sampling_rationale": "Statutory civil service rules ('FRSR Part [ General Rules'); tests mapping to Establishment & HR (KCM-FUNC-12) and Administration Matters (KCM-FUNC-21).",
    },
    {
        "case_id": "BM-CASE-019",
        "stratum": "strata_c_functional_unresolved",
        "course_id": "ACBP-CRS-057",
        "target_kcm_id": None,
        "sampling_rationale": "Technology productivity tool ('AI for Presentations'); tests whether modern software tool maps to Digital Fluency (KCM-FUNC-10) or lacks specific KCM coverage.",
    },
    # Strata D: Official Statistics & MoSPI Domain Courses
    {
        "case_id": "BM-CASE-020",
        "stratum": "strata_d_domain_statistical_gap",
        "course_id": "ACBP-CRS-001",
        "target_kcm_id": None,
        "sampling_rationale": "Domain data governance title ('Introduction to Big Data in Governance'); tests separation of Domain category from Functional data analytics.",
    },
    {
        "case_id": "BM-CASE-021",
        "stratum": "strata_d_domain_statistical_gap",
        "course_id": "ACBP-CRS-046",
        "target_kcm_id": None,
        "sampling_rationale": "Ministry orientation title ('Know Your Ministry Ministry of Statistics and Programme Implementation'); tests ministry-specific domain knowledge gap.",
    },
    {
        "case_id": "BM-CASE-022",
        "stratum": "strata_d_domain_statistical_gap",
        "course_id": "ACBP-CRS-067",
        "target_kcm_id": None,
        "sampling_rationale": "Core official statistics survey microdata ('Handling Unit Level Data of Household Consumption Expenditure Survey'); canonical gold standard test case for 'no_applicable_kcm_competency'.",
    },
    {
        "case_id": "BM-CASE-023",
        "stratum": "strata_d_domain_statistical_gap",
        "course_id": "ACBP-CRS-069",
        "target_kcm_id": None,
        "sampling_rationale": "Core official statistics economic survey ('Handling Unit Level Data of Annual Survey of Industries'); canonical gold standard test case for 'no_applicable_kcm_competency'.",
    },
    {
        "case_id": "BM-CASE-024",
        "stratum": "strata_d_domain_statistical_gap",
        "course_id": "ACBP-CRS-072",
        "target_kcm_id": None,
        "sampling_rationale": "Statistical computing tool ('Introduction to R and Python Programming_'); tests distinction between statistical domain computing and generic digital fluency.",
    },
    # Strata E: Cross-Cadre Context Comparison Pair
    {
        "case_id": "BM-CASE-025",
        "stratum": "strata_e_cross_cadre_contrast",
        "course_id": "ACBP-CRS-093",
        "target_kcm_id": None,
        "sampling_rationale": "Identical title 'Noting and Drafting' at Supervisory Cadre (SSO/SO/SAO/AO); paired with BM-CASE-026 to evaluate cadre-level context influence.",
    },
    {
        "case_id": "BM-CASE-026",
        "stratum": "strata_e_cross_cadre_contrast",
        "course_id": "ACBP-CRS-170",
        "target_kcm_id": None,
        "sampling_rationale": "Identical title 'Noting and Drafting' at Clerical Cadre (Assistants/UDC/LDC); paired with BM-CASE-025 to evaluate operational expectation differences.",
    },
]


def compute_sha256(filepath: Path) -> str:
    """Compute cryptographic SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_baselines() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Load courses, KCM competencies, and existing mappings."""
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        courses_doc = json.load(f)
        courses_by_id = {c["record_id"]: c for c in courses_doc["records"]}

    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        kcm_doc = json.load(f)
        kcm_by_id = {k["competency_id"]: k for k in kcm_doc}

    with open(MAPPINGS_JSON_PATH, "r", encoding="utf-8") as f:
        mappings_doc = json.load(f)
        mappings_by_course = {m["course_record_id"]: m for m in mappings_doc["mappings"]}

    return courses_by_id, kcm_by_id, mappings_by_course


def build_manifest_and_template() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Build benchmark manifest and unpopulated reviewer annotation template."""
    courses_by_id, kcm_by_id, mappings_by_course = load_baselines()

    manifest_cases = []
    template_cases = []

    for spec in BENCHMARK_CASE_SPECS:
        cid = spec["course_id"]
        if cid not in courses_by_id:
            raise KeyError(f"Course ID '{cid}' not found in acbp_courses.json!")

        c = courses_by_id[cid]
        m = mappings_by_course[cid]

        # Target KCM validation
        target_kcm_id = spec["target_kcm_id"]
        target_kcm_name = None
        target_kcm_type = None
        if target_kcm_id:
            if target_kcm_id not in kcm_by_id:
                raise KeyError(f"KCM Competency ID '{target_kcm_id}' not found in competencies_kcm.json!")
            k = kcm_by_id[target_kcm_id]
            target_kcm_name = k["competency_name"]
            target_kcm_type = k["competency_type"]

        manifest_cases.append({
            "benchmark_case_id": spec["case_id"],
            "stratum": spec["stratum"],
            "course_record_id": cid,
            "course_name": c["course_name"],
            "cadre_role": c["cadre_role"],
            "acbp_competency_category": c["competency_category"],
            "production_mapping_id": m["mapping_id"],
            "production_mapping_status": m["validation_status"],
            "candidate_kcm_competency_id": target_kcm_id,
            "candidate_kcm_competency_name": target_kcm_name,
            "candidate_kcm_competency_type": target_kcm_type,
            "course_source_id": c["source_id"],
            "course_source_page": c["source_page"],
            "course_source_row": c["source_row"],
            "sampling_rationale": spec["sampling_rationale"],
        })

        # Template for independent reviewer (all decision/ground-truth fields left strictly null)
        template_cases.append({
            "benchmark_case_id": spec["case_id"],
            "stratum": spec["stratum"],
            "course_record_id": cid,
            "course_name": c["course_name"],
            "cadre_role": c["cadre_role"],
            "acbp_competency_category": c["competency_category"],
            "candidate_kcm_competency_id": target_kcm_id,
            "candidate_kcm_competency_name": target_kcm_name,
            "reviewer_id": None,
            "reviewer_role": None,
            "annotation_date": None,
            "assigned_benchmark_label": None,  # MUST BE NULL until human review
            "target_kcm_competency_id": None,
            "target_kcm_subtheme": None,
            "evidence_sufficiency": None,  # "sufficient" | "insufficient" | "absent"
            "evidence_source_citation": None,
            "evidence_excerpt": None,
            "reviewer_rationale": None,
            "counter_evidence_notes": None,
            "adjudication_status": "pending_annotation",
            "adjudicator_id": None,
            "adjudicator_notes": None,
        })

    # Summary of strata
    strata_counts: Dict[str, int] = {}
    for sc in manifest_cases:
        strata_counts[sc["stratum"]] = strata_counts.get(sc["stratum"], 0) + 1

    timestamp_iso = datetime.now(timezone.utc).isoformat()

    manifest_doc = {
        "benchmark_id": "BM-PILOT-MOSPI-2026-V1",
        "benchmark_title": "MoSPI ACBP to KCM Competency Mapping Human-Reviewed Benchmark (Pilot)",
        "version": "1.0.0",
        "created_at": timestamp_iso,
        "source_hash_courses": compute_sha256(ACBP_COURSES_PATH),
        "source_hash_kcm": compute_sha256(KCM_COMPETENCIES_PATH),
        "total_cases": len(manifest_cases),
        "strata_summary": strata_counts,
        "cases": manifest_cases,
    }

    template_doc = {
        "template_id": "TPL-BM-PILOT-MOSPI-2026-V1",
        "benchmark_id": "BM-PILOT-MOSPI-2026-V1",
        "version": "1.0.0",
        "created_at": timestamp_iso,
        "total_cases": len(template_cases),
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
            "pending_annotation",
            "annotated_single",
            "agreement",
            "disagreement_pending_adjudication",
            "adjudicated",
        ],
        "annotations": template_cases,
    }

    return manifest_doc, template_doc


def save_manifest_and_template(manifest: Dict[str, Any], template: Dict[str, Any]) -> None:
    """Save both manifest and template to JSON and CSV formats under data/interim/."""
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Manifest JSON
    with open(BENCHMARK_MANIFEST_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # 2. Manifest CSV
    manifest_cases = manifest["cases"]
    if manifest_cases:
        with open(BENCHMARK_MANIFEST_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(manifest_cases[0].keys()))
            writer.writeheader()
            for row in manifest_cases:
                writer.writerow(row)

    # 3. Template JSON
    with open(BENCHMARK_TEMPLATE_JSON, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    # 4. Template CSV
    template_cases = template["annotations"]
    if template_cases:
        with open(BENCHMARK_TEMPLATE_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(template_cases[0].keys()))
            writer.writeheader()
            for row in template_cases:
                # Replace None with empty string for CSV clarity
                clean_row = {k: ("" if v is None else str(v)) for k, v in row.items()}
                writer.writerow(clean_row)

    print(f"[SUCCESS] Benchmark manifest saved: {BENCHMARK_MANIFEST_JSON} ({len(manifest_cases)} cases)")
    print(f"[SUCCESS] Benchmark template saved: {BENCHMARK_TEMPLATE_JSON}")


def main() -> None:
    print("======================================================================")
    print("MoSPI SIH26101: Benchmark Manifest & Template Generator (Stage 3.3)")
    print("======================================================================")
    manifest, template = build_manifest_and_template()
    save_manifest_and_template(manifest, template)
    print("======================================================================")


if __name__ == "__main__":
    main()
