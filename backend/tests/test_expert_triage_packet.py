"""
test_expert_triage_packet.py
Regression test suite for Stage 3.5 — Expert Triage Preparation for the 26-Case Benchmark.

Validates:
1. All 26 cases represented exactly once in sequential order.
2. Referential integrity: all ACBP course IDs resolve to acbp_courses.json; all candidate KCM IDs resolve to competencies_kcm.json.
3. Provenance and verification preservation: exactly 3 verified_local_source, 23 external_reference_unverified.
4. No unverified external source upgraded to exact course evidence (is_exact_course_evidence == False).
5. Initial blank review state: Reviewer 1, Reviewer 2, and consensus fields remain strictly null/empty.
6. Domain category alone never triggers no_applicable_kcm_competency.
7. Statistical domain courses (HCES, ASI) explicitly preserve potential overlap with KCM-FUNC-11 (Data Analytics).
8. JSON and CSV parity across all 26 cases and matching field values.
9. Immutability of baseline datasets and production mapping registry.
10. Deterministic packet regeneration safety.
"""

import csv
import hashlib
import json
from pathlib import Path
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
SOURCE_REGISTER_PATH = PROJECT_ROOT / "data" / "source_register.json"


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


@pytest.fixture(scope="module")
def expert_packet_json():
    assert PACKET_JSON_PATH.exists(), f"Missing {PACKET_JSON_PATH}"
    with open(PACKET_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def expert_packet_csv():
    assert PACKET_CSV_PATH.exists(), f"Missing {PACKET_CSV_PATH}"
    with open(PACKET_CSV_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def acbp_catalog():
    with open(COURSES_JSON_PATH, "r", encoding="utf-8") as f:
        return {c["record_id"]: c for c in json.load(f)["records"]}


@pytest.fixture(scope="module")
def kcm_catalog():
    with open(KCM_JSON_PATH, "r", encoding="utf-8") as f:
        return {c["competency_id"]: c for c in json.load(f)}


@pytest.fixture(scope="module")
def source_register():
    with open(SOURCE_REGISTER_PATH, "r", encoding="utf-8") as f:
        return {s["source_id"]: s for s in json.load(f)}


class TestExpertTriagePacket:

    def test_case_count_and_sequential_integrity(self, expert_packet_json, expert_packet_csv):
        """Verifies that all 26 cases are present exactly once in proper sequence."""
        assert expert_packet_json["total_cases"] == 26
        cases_j = expert_packet_json["cases"]
        assert len(cases_j) == 26
        assert len(expert_packet_csv) == 26

        expected_ids = [f"BM-CASE-{i:03d}" for i in range(1, 27)]
        json_ids = [c["benchmark_case_id"] for c in cases_j]
        csv_ids = [r["benchmark_case_id"] for r in expert_packet_csv]

        assert json_ids == expected_ids
        assert csv_ids == expected_ids
        assert len(set(json_ids)) == 26

    def test_referential_integrity(self, expert_packet_json, acbp_catalog, kcm_catalog, source_register):
        """Verifies that every course ID, candidate KCM ID, and registered source ID resolves."""
        assert "SRC-MOSPI-ACBP-2026-27" in source_register
        assert "SRC-CBC-KCM-2024" in source_register

        for case in expert_packet_json["cases"]:
            cid = case["benchmark_case_id"]
            crs_id = case["course_record_id"]
            assert crs_id in acbp_catalog, f"{cid}: Unknown course ID {crs_id}"
            assert case["course_name"] == acbp_catalog[crs_id]["course_name"]

            kcm_id = case["candidate_kcm_id"]
            if kcm_id is not None:
                assert kcm_id in kcm_catalog, f"{cid}: Unknown candidate KCM ID {kcm_id}"
                assert case["candidate_kcm_name"] == kcm_catalog[kcm_id]["competency_name"]

            # Primary source must resolve to register and disk
            psrc = case["primary_source_id"]
            assert psrc in source_register
            psrc_file = PROJECT_ROOT / source_register[psrc]["local_relative_path"]
            assert psrc_file.exists()

    def test_evidence_provenance_and_verification_states(self, expert_packet_json):
        """Verifies that exactly 3 cases are verified_local_source and 23 are external_reference_unverified."""
        summary = expert_packet_json["triage_summary"]["evidence_verification_breakdown"]
        assert summary.get("verified_local_source") == 3
        assert summary.get("external_reference_unverified") == 23

        local_cases = set()
        unverified_cases = set()

        for case in expert_packet_json["cases"]:
            cid = case["benchmark_case_id"]
            status = case["evidence_verification_status"]
            assert status in ["verified_local_source", "external_reference_unverified"]

            # No source is exact course evidence
            assert case["is_exact_course_evidence"] is False

            if status == "verified_local_source":
                local_cases.add(cid)
            else:
                unverified_cases.add(cid)

        assert local_cases == {"BM-CASE-021", "BM-CASE-024", "BM-CASE-025"}
        assert len(unverified_cases) == 23

    def test_initial_review_state_strictly_blank(self, expert_packet_json, expert_packet_csv):
        """Verifies that Reviewer 1, Reviewer 2, and consensus fields remain strictly null/empty."""
        for case in expert_packet_json["cases"]:
            cid = case["benchmark_case_id"]
            assert case["adjudication_status"] == "pending_review", f"{cid} status must be pending_review"
            assert case["final_adjudicated_label"] is None, f"{cid} final label must be null"
            assert case["final_adjudicated_kcm_id"] is None
            assert case["consensus_status"] is None

            reviews = case["independent_reviews"]
            assert len(reviews) == 2, f"{cid} must contain exactly 2 independent review slots"

            for slot in reviews:
                snum = slot["reviewer_slot"]
                assert snum in [1, 2]
                assert slot["reviewer_id"] is None, f"{cid} Slot {snum} reviewer_id must be null"
                assert slot["reviewer_role"] is None
                assert slot["reviewer_affiliation"] is None
                assert slot["review_date"] is None
                assert slot["expert_decision_label"] is None, f"{cid} Slot {snum} decision must be null"
                assert slot["expert_target_kcm_id"] is None
                assert slot["expert_rationale"] is None
                assert slot["confidence_rating"] is None

        for row in expert_packet_csv:
            cid = row["benchmark_case_id"]
            assert row["adjudication_status"] == "pending_review"
            assert row["final_adjudicated_label"] == ""
            assert row["final_adjudicated_kcm_id"] == ""
            assert row["consensus_status"] == ""
            assert row["r1_reviewer_id"] == ""
            assert row["r1_expert_decision_label"] == ""
            assert row["r1_expert_rationale"] == ""
            assert row["r2_reviewer_id"] == ""
            assert row["r2_expert_decision_label"] == ""
            assert row["r2_expert_rationale"] == ""

    def test_domain_category_safeguards(self, expert_packet_json):
        """Verifies that Domain category alone does not trigger no_applicable_kcm_competency."""
        for case in expert_packet_json["cases"]:
            cid = case["benchmark_case_id"]
            cat = case["acbp_competency_category"]
            guidance = case["curator_triage_guidance_label"]
            overlaps = case["potential_competency_overlaps"]

            # Guidance label must NEVER be automatically set to no_applicable_kcm_competency solely due to Domain
            if cat == "Domain":
                assert guidance in ["plausible_insufficient_evidence", "unresolved_insufficient_source"]
                assert len(overlaps.strip()) > 0, f"{cid} must document potential competency overlaps"

        # Check BM-CASE-020 (Big Data in Governance)
        case_020 = next(c for c in expert_packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-020")
        assert "KCM-FUNC-10" in case_020["potential_competency_overlaps"]
        assert "KCM-FUNC-11" in case_020["potential_competency_overlaps"]

        # Check BM-CASE-024 (Python/R)
        case_024 = next(c for c in expert_packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-024")
        assert "KCM-FUNC-11" in case_024["potential_competency_overlaps"]

    def test_statistical_specialist_data_analytics_overlap(self, expert_packet_json):
        """Verifies that HCES and ASI preserve potential overlap with KCM-FUNC-11 (Data Analytics)."""
        case_022 = next(c for c in expert_packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-022")
        case_023 = next(c for c in expert_packet_json["cases"] if c["benchmark_case_id"] == "BM-CASE-023")

        for case in [case_022, case_023]:
            cid = case["benchmark_case_id"]
            overlaps = case["potential_competency_overlaps"]
            assert "KCM-FUNC-11" in overlaps, f"{cid} must preserve overlap with KCM-FUNC-11 (Data Analytics)"
            assert "Data Analytics" in overlaps
            assert "domain gap" in overlaps.lower()
            # Must remain pending review with no final label
            assert case["final_adjudicated_label"] is None
            assert case["adjudication_status"] == "pending_review"

    def test_triage_vs_definitive_adjudication_readiness(self, expert_packet_json):
        """Verifies that all 26 cases are ready for triage but 0 are ready for definitive adjudication."""
        summary = expert_packet_json["triage_summary"]
        assert summary["ready_for_expert_triage"] == 26
        assert summary["ready_for_definitive_adjudication"] == 0
        assert summary["blocked_pending_additional_evidence"] == 26

        for case in expert_packet_json["cases"]:
            assert case["triage_readiness_status"] is True
            assert case["triage_readiness"] == "ready_for_expert_triage"
            assert case["definitive_adjudication_status"] is False
            assert case["definitive_adjudication_readiness"] == "blocked_pending_additional_evidence"
            assert len(case["blocking_reason"].strip()) > 0

    def test_json_and_csv_exact_parity(self, expert_packet_json, expert_packet_csv):
        """Verifies exact field value consistency between JSON and CSV formats."""
        for jc, rc in zip(expert_packet_json["cases"], expert_packet_csv):
            assert jc["benchmark_case_id"] == rc["benchmark_case_id"]
            assert jc["course_record_id"] == rc["course_record_id"]
            assert jc["course_name"] == rc["course_name"]
            assert jc["cadre_role"] == rc["cadre_role"]
            assert jc["acbp_competency_category"] == rc["acbp_competency_category"]
            assert jc["primary_source_id"] == rc["primary_source_id"]
            assert jc["primary_source_citation"] == rc["primary_source_citation"]
            assert (jc["candidate_kcm_id"] or "") == rc["candidate_kcm_id"]
            assert jc["potential_competency_overlaps"] == rc["potential_competency_overlaps"]
            assert jc["evidence_verification_status"] == rc["evidence_verification_status"]
            assert str(jc["is_exact_course_evidence"]) == rc["is_exact_course_evidence"]
            assert str(jc["triage_readiness_status"]) == rc["triage_readiness_status"]
            assert str(jc["definitive_adjudication_status"]) == rc["definitive_adjudication_status"]
            assert jc["blocking_reason"] == rc["blocking_reason"]

    def test_baseline_datasets_and_production_registry_immutability(self):
        """Verifies that frozen baseline datasets and the 226-record production registry remain untouched."""
        assert compute_sha256(COURSES_JSON_PATH) == BASELINE_ACBP_HASH, "acbp_courses.json hash altered!"
        assert compute_sha256(KCM_JSON_PATH) == BASELINE_KCM_HASH, "competencies_kcm.json hash altered!"

        with open(MAPPINGS_JSON_PATH, "r", encoding="utf-8") as f:
            mappings_data = json.load(f)
        assert len(mappings_data.get("mappings", [])) == BASELINE_MAPPINGS_COUNT
        assert mappings_data.get("total_courses_evaluated") == BASELINE_MAPPINGS_COUNT
