"""
test_expert_triage_safeguards.py
Stage 3.5.1 — Expert Triage Packet Round-Trip and Decision Safeguards.

Audits and verifies:
1. Stable case identification by benchmark_case_id (immune to row shuffling).
2. Detection of duplicate or missing case IDs in CSV.
3. Detection of missing or unexpected CSV column headers.
4. Quoting, commas, double-quotes, and multiline rationale preservation.
5. Empty strings in CSV strictly mapping to nulls in JSON.
6. Boolean field serialization integrity.
7. Validation of expert decision labels against approved taxonomy.
8. Validation of confidence ratings on 1–5 integer scale.
9. Detection of incomplete review submissions (missing rationale/confidence).
10. Protection of immutable case and course metadata against tampering.
11. Protection of evidence provenance (no escalation from unverified to verified).
12. Dual reviewer conflict surfacing (disagreements cannot silently merge).
13. Single reviewer cannot finalize benchmark ground truth.
14. Baseline datasets and production mapping registry immutability.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASELINE_ACBP_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
BASELINE_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"
BASELINE_MAPPINGS_COUNT = 226

PACKET_JSON_PATH = PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.json"
PACKET_CSV_PATH = PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.csv"
COURSES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
MAPPINGS_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.json"

ALLOWED_BENCHMARK_LABELS = {
    "supported_mapping",
    "plausible_insufficient_evidence",
    "incorrect_mapping",
    "unresolved_insufficient_source",
    "no_applicable_kcm_competency",
}

IMMUTABLE_CASE_FIELDS = [
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
    "evidence_source_id",
    "evidence_verification_status",
    "is_exact_course_evidence",
]


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


# Reference validation contract function for CSV edits
def validate_and_simulate_import(csv_content: str, baseline_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal, robust reference validator for the future CSV import contract.
    Ensures that an edited CSV satisfies all data integrity and evidence safeguards.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    fieldnames = list(reader.fieldnames or [])
    expected_fieldnames = list(csv.DictReader(open(PACKET_CSV_PATH, "r", encoding="utf-8")).fieldnames or [])

    if fieldnames != expected_fieldnames:
        raise ValueError(f"CSV header mismatch. Expected {len(expected_fieldnames)} columns, found {len(fieldnames)}.")

    rows = list(reader)
    if len(rows) != 26:
        raise ValueError(f"Expected exactly 26 cases, found {len(rows)}.")

    case_ids = [r["benchmark_case_id"] for r in rows]
    if len(set(case_ids)) != 26:
        raise ValueError(f"Duplicate benchmark_case_id detected: {len(case_ids) - len(set(case_ids))} duplicates.")

    expected_ids = [f"BM-CASE-{i:03d}" for i in range(1, 27)]
    if sorted(case_ids) != expected_ids:
        raise ValueError("Missing or unknown benchmark_case_id in CSV.")

    baseline_cases_map = {c["benchmark_case_id"]: c for c in baseline_json["cases"]}
    validated_cases = []

    for row in rows:
        cid = row["benchmark_case_id"]
        base_case = baseline_cases_map[cid]

        # 1. Guard against tampering with immutable metadata
        for field in IMMUTABLE_CASE_FIELDS:
            csv_val = row[field]
            base_val = str(base_case[field]) if isinstance(base_case[field], bool) else base_case[field]
            if csv_val != base_val:
                raise ValueError(
                    f"Tampering detected in {cid}: field '{field}' was modified from '{base_val}' to '{csv_val}'. "
                    f"This field is immutable."
                )

        # 2. Guard against evidence provenance escalation
        if row["evidence_verification_status"] == "verified_local_source" and base_case["evidence_verification_status"] == "external_reference_unverified":
            raise ValueError(f"Illegal evidence escalation in {cid}: cannot convert unverified reference to verified_local_source via CSV.")
        if row["is_exact_course_evidence"] == "True" and not base_case["is_exact_course_evidence"]:
            raise ValueError(f"Illegal evidence escalation in {cid}: cannot mark is_exact_course_evidence as True via CSV.")

        # 3. Validate Reviewer 1 decision and fields
        r1_label = row.get("r1_expert_decision_label", "").strip()
        r1_conf = row.get("r1_confidence_rating", "").strip()
        r1_rat = row.get("r1_expert_rationale", "").strip()
        r1_id = row.get("r1_reviewer_id", "").strip()

        if r1_label:
            if r1_label not in ALLOWED_BENCHMARK_LABELS:
                raise ValueError(f"Invalid r1_expert_decision_label in {cid}: '{r1_label}'.")
            if not r1_conf:
                raise ValueError(f"Incomplete review in {cid}: r1_expert_decision_label provided without confidence rating.")
            try:
                r1_conf_int = int(r1_conf)
                if r1_conf_int < 1 or r1_conf_int > 5:
                    raise ValueError(f"Out of range confidence rating in {cid}: {r1_conf_int}. Must be 1-5.")
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Malformed confidence rating in {cid}: '{r1_conf}'. Must be an integer 1-5.") from None
                raise
            if not r1_rat:
                raise ValueError(f"Incomplete review in {cid}: r1_expert_decision_label provided without rationale.")
            if not r1_id:
                raise ValueError(f"Incomplete review in {cid}: r1_expert_decision_label provided without reviewer ID.")

        # 4. Validate Reviewer 2 decision and fields
        r2_label = row.get("r2_expert_decision_label", "").strip()
        r2_conf = row.get("r2_confidence_rating", "").strip()
        r2_rat = row.get("r2_expert_rationale", "").strip()
        r2_id = row.get("r2_reviewer_id", "").strip()

        if r2_label:
            if r2_label not in ALLOWED_BENCHMARK_LABELS:
                raise ValueError(f"Invalid r2_expert_decision_label in {cid}: '{r2_label}'.")
            if not r2_conf:
                raise ValueError(f"Incomplete review in {cid}: r2_expert_decision_label provided without confidence rating.")
            try:
                r2_conf_int = int(r2_conf)
                if r2_conf_int < 1 or r2_conf_int > 5:
                    raise ValueError(f"Out of range confidence rating in {cid}: {r2_conf_int}. Must be 1-5.")
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Malformed confidence rating in {cid}: '{r2_conf}'. Must be an integer 1-5.") from None
                raise
            if not r2_rat:
                raise ValueError(f"Incomplete review in {cid}: r2_expert_decision_label provided without rationale.")
            if not r2_id:
                raise ValueError(f"Incomplete review in {cid}: r2_expert_decision_label provided without reviewer ID.")

        # 5. Consensus & Adjudication Status Logic
        adjudication_status = "pending_review"
        consensus_status = None
        final_label = None

        if r1_label and not r2_label:
            adjudication_status = "review_in_progress"
            consensus_status = "pending_second_reviewer"
            final_label = None
        elif r2_label and not r1_label:
            adjudication_status = "review_in_progress"
            consensus_status = "pending_first_reviewer"
            final_label = None
        elif r1_label and r2_label:
            if r1_label == r2_label:
                adjudication_status = "adjudicated"
                consensus_status = "consensus_achieved"
                final_label = r1_label
            else:
                adjudication_status = "requires_more_evidence"
                consensus_status = "reviewer_disagreement_escalated"
                final_label = None

        validated_cases.append({
            "benchmark_case_id": cid,
            "adjudication_status": adjudication_status,
            "consensus_status": consensus_status,
            "final_adjudicated_label": final_label,
            "r1_label": r1_label or None,
            "r2_label": r2_label or None,
        })

    return {
        "status": "VALID",
        "cases_validated": len(validated_cases),
        "cases": validated_cases,
    }


class TestExpertTriageSafeguards:

    @pytest.fixture
    def base_json(self):
        with open(PACKET_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def base_csv_text(self):
        with open(PACKET_CSV_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def test_case_lookup_resilience_to_row_reordering(self, base_json, base_csv_text):
        """Verifies that case matching is strictly by benchmark_case_id and immune to CSV row shuffling."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))
        shuffled_rows = list(reader)
        random.seed(12345)
        random.shuffle(shuffled_rows)

        # Write out shuffled CSV
        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(shuffled_rows)
        shuffled_csv_text = out_buf.getvalue()

        # Validation must pass without errors
        res = validate_and_simulate_import(shuffled_csv_text, base_json)
        assert res["status"] == "VALID"
        assert res["cases_validated"] == 26

    def test_detect_duplicate_or_missing_case_ids(self, base_json, base_csv_text):
        """Verifies that duplicate IDs or missing IDs in CSV are strictly rejected."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        # 1. Duplicate row
        dup_rows = list(reader)
        dup_rows[1] = dict(dup_rows[0])  # Duplicate BM-CASE-001
        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(dup_rows)
        with pytest.raises(ValueError, match="Duplicate benchmark_case_id detected"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

        # 2. Missing row (25 rows)
        del dup_rows[1]
        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(dup_rows)
        with pytest.raises(ValueError, match="Expected exactly 26 cases, found 25"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

    def test_detect_missing_or_extra_csv_columns(self, base_json, base_csv_text):
        """Verifies that missing headers or unexpected columns in CSV are caught."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        # Missing a column
        bad_fieldnames = [f for f in reader[0].keys() if f != "duration"]
        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=bad_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(reader)
        with pytest.raises(ValueError, match="CSV header mismatch"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

    def test_quoting_multiline_commas_and_quotes(self, base_json, base_csv_text):
        """Verifies that reviewer rationales with quotes, commas, and newlines round-trip without corruption."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        complex_rationale = (
            'The syllabus explicitly covers "Rule 14 of CCS (CCA) Rules, 1965",\n'
            'including statutory procedures, disciplinary authorities, and quasi-judicial inquiries.\n'
            'Therefore, it aligns with KCM-FUNC-17, sub-theme "Inquiry Procedures".'
        )

        reader[12]["r1_reviewer_id"] = "SME-TEST-01"
        reader[12]["r1_reviewer_role"] = "Faculty, ISTM"
        reader[12]["r1_expert_decision_label"] = "supported_mapping"
        reader[12]["r1_confidence_rating"] = "4"
        reader[12]["r1_expert_rationale"] = complex_rationale

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)
        edited_csv = out_buf.getvalue()

        # Re-parse through reader to ensure RFC 4180 parsing holds
        re_reader = list(csv.DictReader(io.StringIO(edited_csv)))
        assert re_reader[12]["r1_expert_rationale"] == complex_rationale

        res = validate_and_simulate_import(edited_csv, base_json)
        assert res["status"] == "VALID"
        case_13 = next(c for c in res["cases"] if c["benchmark_case_id"] == "BM-CASE-013")
        assert case_13["r1_label"] == "supported_mapping"

    def test_reject_invalid_expert_decision_labels(self, base_json, base_csv_text):
        """Verifies that unapproved decision labels are rejected."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        reader[0]["r1_reviewer_id"] = "SME-TEST-01"
        reader[0]["r1_expert_decision_label"] = "approved_mapping"  # INVALID
        reader[0]["r1_confidence_rating"] = "4"
        reader[0]["r1_expert_rationale"] = "Valid reason"

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        with pytest.raises(ValueError, match="Invalid r1_expert_decision_label in BM-CASE-001: 'approved_mapping'"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

    def test_reject_malformed_confidence_ratings(self, base_json, base_csv_text):
        """Verifies that out-of-range or non-numeric confidence ratings are rejected."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        # Rating = 6
        reader[0]["r1_reviewer_id"] = "SME-TEST-01"
        reader[0]["r1_expert_decision_label"] = "supported_mapping"
        reader[0]["r1_confidence_rating"] = "6"
        reader[0]["r1_expert_rationale"] = "Valid rationale"

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        with pytest.raises(ValueError, match="Out of range confidence rating in BM-CASE-001: 6"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

        # Rating = "high"
        reader[0]["r1_confidence_rating"] = "high"
        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        with pytest.raises(ValueError, match="Malformed confidence rating in BM-CASE-001: 'high'"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

    def test_detect_incomplete_review_submissions(self, base_json, base_csv_text):
        """Verifies that reviews missing rationale, reviewer ID, or confidence are caught."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        # Decision without rationale
        reader[0]["r1_reviewer_id"] = "SME-TEST-01"
        reader[0]["r1_expert_decision_label"] = "supported_mapping"
        reader[0]["r1_confidence_rating"] = "4"
        reader[0]["r1_expert_rationale"] = ""  # MISSING

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        with pytest.raises(ValueError, match="r1_expert_decision_label provided without rationale"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

    def test_protect_immutable_course_and_case_metadata(self, base_json, base_csv_text):
        """Verifies that attempts to tamper with course name or metadata in CSV are blocked."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        reader[0]["course_name"] = "Altered Course Name for Testing"

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        with pytest.raises(ValueError, match="Tampering detected in BM-CASE-001: field 'course_name' was modified"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

    def test_protect_evidence_provenance_against_escalation(self, base_json, base_csv_text):
        """Verifies that unverified external references cannot be upgraded via CSV edits."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        # Attempt to escalate BM-CASE-001 evidence status
        reader[0]["evidence_verification_status"] = "verified_local_source"

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        with pytest.raises(ValueError, match="field 'evidence_verification_status' was modified"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

        # Attempt to set is_exact_course_evidence = True
        reader[0]["evidence_verification_status"] = "external_reference_unverified"
        reader[0]["is_exact_course_evidence"] = "True"

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        with pytest.raises(ValueError, match="field 'is_exact_course_evidence' was modified"):
            validate_and_simulate_import(out_buf.getvalue(), base_json)

    def test_single_reviewer_cannot_finalize_ground_truth(self, base_json, base_csv_text):
        """Verifies that Reviewer 1 submitting a review leaves status in review_in_progress and final label null."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        reader[0]["r1_reviewer_id"] = "SME-TEST-01"
        reader[0]["r1_reviewer_role"] = "Faculty, NSSTA"
        reader[0]["r1_expert_decision_label"] = "plausible_insufficient_evidence"
        reader[0]["r1_confidence_rating"] = "2"
        reader[0]["r1_expert_rationale"] = "Requires iGOT lesson plan behind SSO."

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        res = validate_and_simulate_import(out_buf.getvalue(), base_json)
        case_001 = next(c for c in res["cases"] if c["benchmark_case_id"] == "BM-CASE-001")
        assert case_001["adjudication_status"] == "review_in_progress"
        assert case_001["consensus_status"] == "pending_second_reviewer"
        assert case_001["final_adjudicated_label"] is None

    def test_dual_reviewer_conflict_surfacing(self, base_json, base_csv_text):
        """Verifies that conflicting expert decisions surface as requires_more_evidence rather than merging."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        # Reviewer 1 says supported_mapping, Reviewer 2 says incorrect_mapping
        reader[1]["r1_reviewer_id"] = "SME-TEST-01"
        reader[1]["r1_expert_decision_label"] = "supported_mapping"
        reader[1]["r1_confidence_rating"] = "4"
        reader[1]["r1_expert_rationale"] = "Project management aligns with KCM-FUNC-05."

        reader[1]["r2_reviewer_id"] = "SME-TEST-02"
        reader[1]["r2_expert_decision_label"] = "incorrect_mapping"
        reader[1]["r2_confidence_rating"] = "3"
        reader[1]["r2_expert_rationale"] = "Duration is 17 minutes; this is leadership awareness, not functional PM."

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        res = validate_and_simulate_import(out_buf.getvalue(), base_json)
        case_002 = next(c for c in res["cases"] if c["benchmark_case_id"] == "BM-CASE-002")
        assert case_002["adjudication_status"] == "requires_more_evidence"
        assert case_002["consensus_status"] == "reviewer_disagreement_escalated"
        assert case_002["final_adjudicated_label"] is None
        assert case_002["r1_label"] == "supported_mapping"
        assert case_002["r2_label"] == "incorrect_mapping"

    def test_dual_reviewer_consensus_achievement(self, base_json, base_csv_text):
        """Verifies that when both reviewers agree, consensus is achieved."""
        reader = list(csv.DictReader(io.StringIO(base_csv_text)))

        reader[21]["r1_reviewer_id"] = "SME-NSSTA-01"
        reader[21]["r1_expert_decision_label"] = "plausible_insufficient_evidence"
        reader[21]["r1_confidence_rating"] = "3"
        reader[21]["r1_expert_rationale"] = "HCES unit level data overlaps with KCM-FUNC-11 but requires syllabus proof."

        reader[21]["r2_reviewer_id"] = "SME-NSSTA-02"
        reader[21]["r2_expert_decision_label"] = "plausible_insufficient_evidence"
        reader[21]["r2_confidence_rating"] = "3"
        reader[21]["r2_expert_rationale"] = "Agreed, microdata handling shares analytics overlap; pending practical exercises."

        out_buf = io.StringIO()
        writer = csv.DictWriter(out_buf, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)

        res = validate_and_simulate_import(out_buf.getvalue(), base_json)
        case_022 = next(c for c in res["cases"] if c["benchmark_case_id"] == "BM-CASE-022")
        assert case_022["adjudication_status"] == "adjudicated"
        assert case_022["consensus_status"] == "consensus_achieved"
        assert case_022["final_adjudicated_label"] == "plausible_insufficient_evidence"

    def test_production_mapping_registry_and_baseline_immutability(self):
        """Verifies that the frozen baseline files and 226-record mapping registry remain immutable."""
        assert compute_sha256(COURSES_JSON_PATH) == BASELINE_ACBP_HASH
        assert compute_sha256(KCM_JSON_PATH) == BASELINE_KCM_HASH

        with open(MAPPINGS_JSON_PATH, "r", encoding="utf-8") as f:
            mappings_data = json.load(f)
        assert len(mappings_data.get("mappings", [])) == BASELINE_MAPPINGS_COUNT
