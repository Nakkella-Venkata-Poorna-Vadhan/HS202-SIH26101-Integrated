"""
test_source_citation_verification.py
Regression tests for Stage 3.4.3.1 — Source Resolution and Citation Verification.

Verifies:
1. All 26 benchmark cases covered
2. Authoritative source IDs resolve correctly to source register and local filesystem
3. Missing or unverified sources flagged, not silently passed
4. No citation marked verified solely because it is non-empty
5. ACBP course identity and citation consistency with baseline and table extractions
6. OCR uncertainty preservation without silent alterations
7. Controlled taxonomy enforcement (verified_local_source vs external_reference_unverified)
8. Claim strength proportionality and hypothesis framing
9. Production registry and baseline dataset immutability
"""

import hashlib
import json
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

BASELINE_ACBP_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
BASELINE_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


@pytest.fixture(scope="module")
def verification_data():
    vpath = BASE_DIR / "data" / "interim" / "source_citation_verification.json"
    assert vpath.exists(), f"Verification artifact missing: {vpath}"
    with open(vpath, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def source_register():
    sr_path = BASE_DIR / "data" / "source_register.json"
    with open(sr_path, "r", encoding="utf-8") as f:
        return {s["source_id"]: s for s in json.load(f)}


@pytest.fixture(scope="module")
def acbp_courses():
    cpath = BASE_DIR / "data" / "processed" / "acbp_courses.json"
    with open(cpath, "r", encoding="utf-8") as f:
        return {c["record_id"]: c for c in json.load(f)["records"]}


@pytest.fixture(scope="module")
def kcm_competencies():
    kpath = BASE_DIR / "data" / "processed" / "competencies_kcm.json"
    with open(kpath, "r", encoding="utf-8") as f:
        return {c["competency_id"]: c for c in json.load(f)}


@pytest.fixture(scope="module")
def adjudication_packet():
    ppath = BASE_DIR / "data" / "interim" / "mapping_adjudication_packet.json"
    with open(ppath, "r", encoding="utf-8") as f:
        return json.load(f)


class TestSourceCitationVerification:

    def test_artifact_structure_and_coverage(self, verification_data):
        assert "VERIF-STAGE-3.4.3" in verification_data["verification_id"]
        assert verification_data["stage"] in ["3.4.3.1", "3.4.3.2", "3.4.3.3"]
        assert verification_data["total_cases_verified"] == 26
        cases = verification_data["case_verifications"]
        assert len(cases) == 26

        expected_ids = [f"BM-CASE-{i:03d}" for i in range(1, 27)]
        actual_ids = [c["benchmark_case_id"] for c in cases]
        assert actual_ids == expected_ids, "All 26 benchmark cases must be covered in sequence"

    def test_acbp_course_identity_and_citation_consistency(self, verification_data, acbp_courses, source_register):
        assert "SRC-MOSPI-ACBP-2026-27" in source_register
        acbp_sr = source_register["SRC-MOSPI-ACBP-2026-27"]
        local_acbp_file = BASE_DIR / acbp_sr["local_relative_path"]
        assert local_acbp_file.exists(), "Raw ACBP PDF file must exist"

        for case in verification_data["case_verifications"]:
            cid = case["benchmark_case_id"]
            crs_id = case["course_record_id"]
            acbp_v = case["acbp_citation"]

            assert crs_id in acbp_courses, f"{crs_id} must exist in processed ACBP courses"
            p_crs = acbp_courses[crs_id]

            # Check identity matching
            assert case["course_name"] == p_crs["course_name"], f"Title mismatch in {cid}"
            assert case["cadre_role"] == p_crs["cadre_role"], f"Cadre mismatch in {cid}"
            assert acbp_v["course_identity_verified"] is True
            assert acbp_v["duration_verified"] is True
            assert acbp_v["category_verified"] is True
            assert acbp_v["creator_verified"] is True

            # Check citation string and page/row alignment
            expected_cit = f"SRC-MOSPI-ACBP-2026-27 (Annexure I, Page {p_crs['source_page']}, Row {p_crs['source_row']})"
            assert acbp_v["citation_string"] == expected_cit, f"Citation mismatch in {cid}"
            assert acbp_v["citation_string_match"] is True
            assert acbp_v["source_id_in_register"] is True
            assert acbp_v["local_file_exists"] is True
            assert acbp_v["resolution_status"] == "verified_local_source"
            assert acbp_v["claim_support_scope"] == "course_identity_and_administrative_intent_only"

    def test_ocr_uncertainty_explicitly_preserved(self, verification_data, acbp_courses):
        for case in verification_data["case_verifications"]:
            crs_id = case["course_record_id"]
            p_crs = acbp_courses[crs_id]
            acbp_v = case["acbp_citation"]

            raw_ocr = acbp_v["ocr_uncertainty"]["raw_ocr_values"]
            assert isinstance(raw_ocr, dict)
            assert raw_ocr == p_crs.get("raw_ocr_values", {})
            assert "course_name" in raw_ocr
            assert "duration" in raw_ocr

    def test_kcm_target_citations_resolution(self, verification_data, kcm_competencies, source_register):
        assert "SRC-CBC-KCM-2024" in source_register
        kcm_sr = source_register["SRC-CBC-KCM-2024"]
        local_kcm_file = BASE_DIR / kcm_sr["local_relative_path"]
        assert local_kcm_file.exists(), "Raw KCM PDF file must exist"

        resolved_count = 0
        unmapped_count = 0

        for case in verification_data["case_verifications"]:
            kcm_v = case["kcm_citation"]
            kcm_id = kcm_v["candidate_kcm_id"]

            if kcm_id is not None:
                assert kcm_id in kcm_competencies, f"Candidate KCM {kcm_id} must exist in KCM dataset"
                assert kcm_v["source_id"] == "SRC-CBC-KCM-2024"
                assert kcm_v["source_id_in_register"] is True
                assert kcm_v["local_file_exists"] is True
                assert kcm_v["verbatim_definition_verified"] is True
                assert kcm_v["resolution_status"] == "verified_local_source"
                resolved_count += 1
            else:
                assert kcm_v["resolution_status"] == "not_applicable_domain_gap"
                unmapped_count += 1

        assert resolved_count == 16, "Exactly 16 cases have a candidate KCM competency"
        assert unmapped_count == 10, "Exactly 10 cases have domain gap or unmapped KCM"

    def test_evidence_citations_controlled_taxonomy(self, verification_data, source_register):
        valid_statuses = {
            "verified_local_source",
            "registered_source_not_locally_available",
            "external_reference_unverified",
            "citation_mismatch",
            "source_reference_missing",
        }

        tax_summary = verification_data["verification_summary"]["evidence_citations_taxonomy"]
        assert tax_summary["verified_local_source"] == 3
        assert tax_summary["registered_source_not_locally_available"] == 0
        assert tax_summary["external_reference_unverified"] == 23
        assert tax_summary["citation_mismatch"] == 0
        assert tax_summary["source_reference_missing"] == 0

        for case in verification_data["case_verifications"]:
            cid = case["benchmark_case_id"]
            ev_v = case["evidence_citation"]
            status = ev_v["classification"]
            assert status in valid_statuses, f"Invalid taxonomy status {status} in {cid}"

            if status == "verified_local_source":
                assert ev_v["source_id_in_register"] is True
                assert ev_v["local_file_exists"] is True
                assert ev_v["evidence_source_id"] in ["SRC-MOSPI-AR-2023-24", "SRC-NSSTA-TRG-CAL-2025-26"]
                assert (BASE_DIR / ev_v["local_relative_path"]).exists()
            elif status == "external_reference_unverified":
                assert ev_v["source_id_in_register"] is False
                assert ev_v["local_file_exists"] is False
                assert ev_v["evidence_source_id"].startswith("SRC-EXT-")
                assert ev_v["url_verification_status"] == "external_url_recorded_unverified_locally"

    def test_no_citation_marked_verified_solely_because_non_empty(self, verification_data):
        """Zero external references may be labeled verified_local_source without physical files."""
        for case in verification_data["case_verifications"]:
            ev_v = case["evidence_citation"]
            if ev_v["local_file_exists"] is False:
                assert ev_v["classification"] != "verified_local_source", (
                    f"{case['benchmark_case_id']} cannot be verified_local_source without physical local file"
                )

    def test_claim_strength_and_proportionality(self, verification_data, adjudication_packet):
        for case in verification_data["case_verifications"]:
            cid = case["benchmark_case_id"]
            ev_v = case["evidence_citation"]
            checks = ev_v["claim_strength_checks"]

            assert ev_v["is_exact_course_evidence"] is False, f"is_exact_course_evidence must be False for {cid}"
            assert checks["proportionality_valid"] is True
            assert checks["classroom_syllabus_conflation"] is False
            assert checks["competency_alignment_framed_as_hypothesis"] is True
            assert checks["competency_depth_unwarranted_inference"] is False

            # Check matching packet case
            packet_case = next(p for p in adjudication_packet["cases"] if p["benchmark_case_id"] == cid)
            assert packet_case["adjudication_status"] == "pending_review"
            assert packet_case["adjudicated_label"] is None
            assert len(packet_case["sme_adjudication_questions"].strip()) > 0

    def test_benchmark_and_production_baseline_immutability(self):
        """Verifies that production mapping registry and frozen baseline datasets have not changed."""
        courses_file = BASE_DIR / "data" / "processed" / "acbp_courses.json"
        kcm_file = BASE_DIR / "data" / "processed" / "competencies_kcm.json"
        mappings_file = BASE_DIR / "data" / "processed" / "acbp_kcm_mappings.json"

        assert compute_sha256(courses_file) == BASELINE_ACBP_HASH, "acbp_courses.json must remain immutable"
        assert compute_sha256(kcm_file) == BASELINE_KCM_HASH, "competencies_kcm.json must remain immutable"

        with open(mappings_file, "r", encoding="utf-8") as f:
            mappings_data = json.load(f)
        assert len(mappings_data.get("mappings", [])) == 226, "Production mappings registry must contain exactly 226 records"
        assert mappings_data.get("total_courses_evaluated") == 226

    def test_six_distinct_verification_outcomes(self, verification_data):
        """Verifies that the six distinct verification outcomes are strictly separated in reporting."""
        outcomes = verification_data["verification_summary"]["distinct_verification_outcomes"]
        assert "68 / 68" in outcomes["citation_field_exists"]
        assert "45 / 68" in outcomes["source_id_registered"]
        assert "45 / 68" in outcomes["local_source_file_exists"]
        assert "45 / 68" in outcomes["page_section_inspected_locally"]
        assert "45 / 68" in outcomes["local_source_content_inspected_and_supports_claim"]
        assert "23 / 68" in outcomes["external_source_content_unverified"]
        assert "0 / 68" in outcomes["external_source_authenticated"]
        assert "68 / 68" in outcomes["claim_scope_appropriately_limited"]

    def test_no_universal_content_verification_with_unverified_references(self, verification_data):
        """Regression test: Cannot claim universal content verification while 23 external references remain unverified."""
        outcomes = verification_data["verification_summary"]["distinct_verification_outcomes"]
        # Must NOT claim 68 / 68 for local content inspection or support
        assert "45 / 68" in outcomes["local_source_content_inspected_and_supports_claim"]
        assert "23 / 68" in outcomes["external_source_content_unverified"]

        # Check every case's evidence citation
        local_content_support_count = 0
        external_unverified_count = 0

        for case in verification_data["case_verifications"]:
            ev_v = case["evidence_citation"]
            status = ev_v["classification"]

            if status == "verified_local_source":
                assert ev_v["local_content_inspected_and_supports_claim"] is True
                assert ev_v["source_content_supports_claim"] is True
                assert ev_v["external_content_unverified"] is False
                local_content_support_count += 1
            elif status == "external_reference_unverified":
                # External references must NEVER be counted as content-verified solely because URL/title exists
                assert ev_v["local_content_inspected_and_supports_claim"] is False
                assert ev_v["source_content_supports_claim"] is False
                assert ev_v["external_content_unverified"] is True
                external_unverified_count += 1

        assert local_content_support_count == 3
        assert external_unverified_count == 23

    def test_verified_local_sources_traceable_locations(self, verification_data):
        """Verifies that the 3 verified_local_source records have physical files and traceable page/sections."""
        local_details = verification_data["verification_summary"]["verified_local_sources_details"]
        assert len(local_details) == 3

        case_ids = {d["benchmark_case_id"] for d in local_details}
        assert case_ids == {"BM-CASE-021", "BM-CASE-024", "BM-CASE-025"}

        for detail in local_details:
            cid = detail["benchmark_case_id"]
            local_rel = detail["local_relative_path"]
            assert (BASE_DIR / local_rel).exists(), f"Physical file missing for {cid}"
            assert "Page" in detail["inspected_page_section"]
            assert detail["claim_scope"] is not None

        # Check BM-CASE-021 in cases
        case_021 = next(c for c in verification_data["case_verifications"] if c["benchmark_case_id"] == "BM-CASE-021")
        assert case_021["evidence_citation"]["classification"] == "verified_local_source"
        assert "Page 35" in case_021["evidence_citation"]["inspected_location"]

        # Check BM-CASE-024 in cases
        case_024 = next(c for c in verification_data["case_verifications"] if c["benchmark_case_id"] == "BM-CASE-024")
        assert case_024["evidence_citation"]["classification"] == "verified_local_source"
        assert "Page 2" in case_024["evidence_citation"]["inspected_location"]

        # Check BM-CASE-025 in cases
        case_025 = next(c for c in verification_data["case_verifications"] if c["benchmark_case_id"] == "BM-CASE-025")
        assert case_025["evidence_citation"]["classification"] == "verified_local_source"
        assert "Page 3" in case_025["evidence_citation"]["inspected_location"]

    def test_twenty_three_external_references_strictly_unverified(self, verification_data):
        """Verifies that all 23 external references remain external_reference_unverified and unauthenticated."""
        unverified_count = 0
        for case in verification_data["case_verifications"]:
            ev_v = case["evidence_citation"]
            if ev_v["classification"] == "external_reference_unverified":
                unverified_count += 1
                assert ev_v["external_source_authenticated"] is False
                assert ev_v["local_file_exists"] is False
                assert ev_v["source_id_in_register"] is False
        assert unverified_count == 23, "Exactly 23 cases must remain external_reference_unverified"

    def test_packet_readiness_explicit_statuses(self, verification_data):
        """Verifies that expert triage, definitive adjudication, and evidence blocking are reported separately."""
        readiness = verification_data["verification_summary"]["packet_readiness_evaluation"]
        assert readiness["ready_for_expert_triage"]["status"] is True
        assert len(readiness["ready_for_expert_triage"]["rationale"].strip()) > 0

        assert readiness["ready_for_definitive_adjudication"]["status"] is False
        assert len(readiness["ready_for_definitive_adjudication"]["rationale"].strip()) > 0

        assert readiness["blocked_pending_additional_evidence"]["status"] is True
        assert len(readiness["blocked_pending_additional_evidence"]["rationale"].strip()) > 0

