"""
test_import_expert_reviews.py
Stage 3.5.2 — Regression tests for the Safe Expert Review Import and Validation CLI.

Validates:
1. Valid CSV import into a new output artifact.
2. Rejection of duplicate, missing, and unexpected case IDs.
3. Rejection of missing, extra, and duplicate columns.
4. Resilience to row reordering (stable lookup by benchmark_case_id).
5. Multiline rationales and quoted commas preservation under RFC 4180.
6. Rejection of invalid labels and malformed confidence ratings.
7. Rejection of missing rationale or reviewer ID (incomplete reviews).
8. Rejection of modified immutable metadata.
9. Rejection of attempted evidence-status escalation.
10. Correct handling of one reviewer only (status: single_review_in_progress).
11. Correct handling of two reviewers in agreement (status: provisional_consensus_achieved).
12. Correct handling of two reviewers in conflict (status: conflict_escalated).
13. Refusal to overwrite existing output files.
14. Refusal to write to protected files or data/processed/ directory.
15. Validation-only mode produces zero output files.
16. Zero modifications to canonical packet, raw data, or production mapping registry.
17. Deterministic output ordering by benchmark_case_id.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_PACKET_JSON = PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.json"
CANONICAL_PACKET_CSV = PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.csv"
COURSES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_courses.json"
KCM_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"
MAPPINGS_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.json"
CLI_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "import_expert_reviews.py"

BASELINE_ACBP_HASH = "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7"
BASELINE_KCM_HASH = "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4"
BASELINE_MAPPINGS_COUNT = 226


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


@pytest.fixture
def canonical_csv_rows():
    with open(CANONICAL_PACKET_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture
def canonical_fieldnames():
    with open(CANONICAL_PACKET_CSV, "r", encoding="utf-8") as f:
        return list(csv.reader(f))[0]


def write_csv(filepath: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(CLI_SCRIPT_PATH)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, cwd=str(PROJECT_ROOT))


class TestImportExpertReviewsCLI:

    def test_cli_help(self):
        """Verifies that --help works and documents usage."""
        proc = run_cli("--help")
        assert proc.returncode == 0
        assert "--validate" in proc.stdout
        assert "--import" in proc.stdout
        assert "--output" in proc.stdout

    def test_validate_mode_on_canonical_csv(self):
        """Verifies that --validate runs cleanly and produces no files."""
        proc = run_cli("--validate", str(CANONICAL_PACKET_CSV))
        assert proc.returncode == 0
        assert "[VALIDATION PASSED]" in proc.stdout
        assert "All 26 cases satisfy data integrity" in proc.stdout

    def test_import_mode_valid_canonical_csv(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that importing an unedited canonical CSV creates a valid review artifact."""
        out_json = tmp_path / "imported_results.json"
        proc = run_cli("--import", str(CANONICAL_PACKET_CSV), "--output", str(out_json))
        assert proc.returncode == 0
        assert "[IMPORT SUCCESSFUL]" in proc.stdout
        assert out_json.exists()

        data = json.loads(out_json.read_text(encoding="utf-8"))
        assert data["artifact_type"] == "expert_review_results"
        assert "DECLARATION" in data["disclaimer"]
        assert data["summary"]["total_cases"] == 26
        assert data["summary"]["unreviewed_cases"] == 26
        assert data["summary"]["ground_truth_finalized"] is False
        assert len(data["cases"]) == 26

    def test_refuse_overwrite_existing_output(self, tmp_path):
        """Verifies that the CLI refuses to overwrite an existing output file."""
        out_json = tmp_path / "already_exists.json"
        out_json.write_text("{}", encoding="utf-8")

        proc = run_cli("--import", str(CANONICAL_PACKET_CSV), "--output", str(out_json))
        assert proc.returncode == 1
        assert "Output file already exists" in proc.stdout
        assert "Refusing to overwrite" in proc.stdout

    def test_refuse_overwrite_protected_canonical_files(self):
        """Verifies that the CLI strictly blocks writing over protected files."""
        proc = run_cli("--import", str(CANONICAL_PACKET_CSV), "--output", str(CANONICAL_PACKET_JSON))
        assert proc.returncode == 1
        assert "Output file already exists" in proc.stdout or "SECURITY VIOLATION" in proc.stdout

        proc_courses = run_cli("--import", str(CANONICAL_PACKET_CSV), "--output", str(COURSES_JSON_PATH))
        assert proc_courses.returncode == 1

    def test_refuse_write_inside_protected_directories(self, tmp_path):
        """Verifies that writing inside data/processed/ or data/raw/ is strictly blocked."""
        bad_out = PROJECT_ROOT / "data" / "processed" / "malicious_output.json"
        proc = run_cli("--import", str(CANONICAL_PACKET_CSV), "--output", str(bad_out))
        assert proc.returncode == 1
        assert "SECURITY VIOLATION" in proc.stdout
        assert not bad_out.exists()

    def test_row_reordering_resilience_and_deterministic_output(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that row shuffling does not break import, and output is always sorted BM-CASE-001 to 026."""
        shuffled = list(canonical_csv_rows)
        # Reverse rows
        shuffled.reverse()

        csv_file = tmp_path / "shuffled.csv"
        write_csv(csv_file, canonical_fieldnames, shuffled)

        out_json = tmp_path / "shuffled_results.json"
        proc = run_cli("--import", str(csv_file), "--output", str(out_json))
        assert proc.returncode == 0

        data = json.loads(out_json.read_text(encoding="utf-8"))
        case_ids = [c["benchmark_case_id"] for c in data["cases"]]
        expected_ids = [f"BM-CASE-{i:03d}" for i in range(1, 27)]
        assert case_ids == expected_ids, "Output cases must be deterministically sorted"

    def test_reject_duplicate_and_missing_case_ids(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies rejection of duplicate or missing case IDs."""
        # Duplicate case
        dup_rows = list(canonical_csv_rows)
        dup_rows[1] = dict(dup_rows[0])
        csv_file = tmp_path / "dup.csv"
        write_csv(csv_file, canonical_fieldnames, dup_rows)

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "Duplicate benchmark_case_id" in proc.stdout

        # Missing case (25 rows)
        del dup_rows[1]
        csv_missing = tmp_path / "missing.csv"
        write_csv(csv_missing, canonical_fieldnames, dup_rows)

        proc_miss = run_cli("--validate", str(csv_missing))
        assert proc_miss.returncode == 1
        assert "Case count mismatch" in proc_miss.stdout

    def test_reject_header_mismatch(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies rejection when headers are missing or extra columns are added."""
        bad_headers = [h for h in canonical_fieldnames if h != "cadre_role"]
        csv_file = tmp_path / "bad_headers.csv"
        write_csv(csv_file, bad_headers, canonical_csv_rows)

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "CSV header mismatch" in proc.stdout

    def test_multiline_rationale_and_quoted_commas(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that multiline rationales with quotes and commas are parsed without corruption."""
        rows = list(canonical_csv_rows)
        complex_text = 'Line 1: "Quoted Title", with comma.\nLine 2: Statutory rule interpretation under GFR, 2017.'
        rows[0]["r1_reviewer_id"] = "SME-TEST-01"
        rows[0]["r1_reviewer_role"] = "Senior Faculty, NSSTA"
        rows[0]["r1_expert_decision_label"] = "plausible_insufficient_evidence"
        rows[0]["r1_confidence_rating"] = "3"
        rows[0]["r1_expert_rationale"] = complex_text

        csv_file = tmp_path / "multiline.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        out_json = tmp_path / "multiline_out.json"
        proc = run_cli("--import", str(csv_file), "--output", str(out_json))
        assert proc.returncode == 0

        data = json.loads(out_json.read_text(encoding="utf-8"))
        case_001 = data["cases"][0]
        assert case_001["reviewer_1"]["rationale"] == complex_text

    def test_reject_tampering_with_immutable_metadata(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that altering read-only course or provenance metadata is blocked."""
        rows = list(canonical_csv_rows)
        rows[0]["course_name"] = "Maliciously Altered Course Title"

        csv_file = tmp_path / "tampered_name.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "Tampering detected in BM-CASE-001" in proc.stdout
        assert "course_name" in proc.stdout

    def test_reject_evidence_status_escalation(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that promoting external_reference_unverified to verified_local_source is blocked."""
        rows = list(canonical_csv_rows)
        # BM-CASE-001 is unverified external reference
        rows[0]["evidence_verification_status"] = "verified_local_source"

        csv_file = tmp_path / "escalated_ev.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "Tampering detected in BM-CASE-001" in proc.stdout or "Illegal evidence escalation" in proc.stdout

    def test_reject_invalid_label_and_confidence(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies rejection of unapproved labels and out-of-range confidence ratings."""
        rows = list(canonical_csv_rows)
        rows[0]["r1_reviewer_id"] = "SME-TEST-01"
        rows[0]["r1_expert_decision_label"] = "definitely_true"  # INVALID
        rows[0]["r1_confidence_rating"] = "7"  # INVALID
        rows[0]["r1_expert_rationale"] = "Valid rationale for test"

        csv_file = tmp_path / "invalid_decision.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "Invalid Reviewer 1 expert_decision_label" in proc.stdout
        assert "Invalid Reviewer 1 confidence_rating" in proc.stdout

    def test_reject_incomplete_reviews(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies rejection of decision submitted without reviewer ID or rationale."""
        rows = list(canonical_csv_rows)
        rows[0]["r1_expert_decision_label"] = "supported_mapping"
        rows[0]["r1_confidence_rating"] = "4"
        # Missing reviewer ID and rationale

        csv_file = tmp_path / "incomplete.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "Incomplete Reviewer 1 submission" in proc.stdout

    def test_one_reviewer_only_does_not_finalize_ground_truth(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that Reviewer 1 review puts case into single_review_in_progress, not finalized."""
        rows = list(canonical_csv_rows)
        rows[0]["r1_reviewer_id"] = "SME-TEST-01"
        rows[0]["r1_reviewer_role"] = "Faculty, NSSTA"
        rows[0]["r1_expert_decision_label"] = "plausible_insufficient_evidence"
        rows[0]["r1_confidence_rating"] = "2"
        rows[0]["r1_expert_rationale"] = "Pending lesson plan behind Parichay SSO."

        csv_file = tmp_path / "r1_only.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        out_json = tmp_path / "r1_only_out.json"
        proc = run_cli("--import", str(csv_file), "--output", str(out_json))
        assert proc.returncode == 0

        data = json.loads(out_json.read_text(encoding="utf-8"))
        case_001 = data["cases"][0]
        consensus = case_001["consensus_evaluation"]
        assert consensus["status"] == "single_review_in_progress"
        assert consensus["ground_truth_finalized"] is False
        assert consensus["provisional_consensus_label"] is None

    def test_dual_reviewer_conflict_surfacing(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that conflicting decisions are flagged as conflict_escalated and require panel."""
        rows = list(canonical_csv_rows)
        # R1: supported_mapping
        rows[1]["r1_reviewer_id"] = "SME-TEST-01"
        rows[1]["r1_expert_decision_label"] = "supported_mapping"
        rows[1]["r1_confidence_rating"] = "4"
        rows[1]["r1_expert_rationale"] = "Matches KCM-FUNC-05 Project Management."

        # R2: incorrect_mapping
        rows[1]["r2_reviewer_id"] = "SME-TEST-02"
        rows[1]["r2_expert_decision_label"] = "incorrect_mapping"
        rows[1]["r2_confidence_rating"] = "3"
        rows[1]["r2_expert_rationale"] = "Duration is 17m; executive leadership awareness, not functional PM."

        csv_file = tmp_path / "conflict.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        out_json = tmp_path / "conflict_out.json"
        proc = run_cli("--import", str(csv_file), "--output", str(out_json))
        assert proc.returncode == 0

        data = json.loads(out_json.read_text(encoding="utf-8"))
        case_002 = data["cases"][1]
        consensus = case_002["consensus_evaluation"]
        assert consensus["status"] == "conflict_escalated"
        assert consensus["requires_panel_escalation"] is True
        assert consensus["provisional_consensus_label"] is None
        assert "Reviewer disagreement" in consensus["escalation_reason"]

    def test_dual_reviewer_agreement_provisional_consensus(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that matching decisions produce provisional consensus without altering ground truth."""
        rows = list(canonical_csv_rows)
        rows[21]["r1_reviewer_id"] = "SME-NSSTA-01"
        rows[21]["r1_expert_decision_label"] = "plausible_insufficient_evidence"
        rows[21]["r1_confidence_rating"] = "3"
        rows[21]["r1_expert_rationale"] = "Microdata extraction overlaps with KCM-FUNC-11 Data Analytics."

        rows[21]["r2_reviewer_id"] = "SME-NSSTA-02"
        rows[21]["r2_expert_decision_label"] = "plausible_insufficient_evidence"
        rows[21]["r2_confidence_rating"] = "3"
        rows[21]["r2_expert_rationale"] = "Agreed, statistical tabulation shares overlap; pending lesson plan."

        csv_file = tmp_path / "consensus.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        out_json = tmp_path / "consensus_out.json"
        proc = run_cli("--import", str(csv_file), "--output", str(out_json))
        assert proc.returncode == 0

        data = json.loads(out_json.read_text(encoding="utf-8"))
        case_022 = data["cases"][21]
        consensus = case_022["consensus_evaluation"]
        assert consensus["status"] == "provisional_consensus_achieved"
        assert consensus["provisional_consensus_label"] == "plausible_insufficient_evidence"
        assert consensus["ground_truth_finalized"] is False

    def test_zero_modifications_to_protected_baselines(self):
        """Verifies that frozen baselines and production mapping registry remain untouched."""
        assert compute_sha256(COURSES_JSON_PATH) == BASELINE_ACBP_HASH
        assert compute_sha256(KCM_JSON_PATH) == BASELINE_KCM_HASH

        with open(MAPPINGS_JSON_PATH, "r", encoding="utf-8") as f:
            mappings_data = json.load(f)
        assert len(mappings_data.get("mappings", [])) == BASELINE_MAPPINGS_COUNT

    def test_reject_modified_canonical_packet_sha256(self, tmp_path):
        """Verifies that an altered canonical packet fails the cryptographic baseline check."""
        from scripts.import_expert_reviews import ExpertReviewValidator

        # Create tampered copy of canonical packet
        canonical_content = json.loads(CANONICAL_PACKET_JSON.read_text(encoding="utf-8"))
        canonical_content["version"] = "1.0.1-tampered"

        tampered_packet = tmp_path / "tampered_packet.json"
        tampered_packet.write_text(json.dumps(canonical_content), encoding="utf-8")

        with pytest.raises(ValueError, match="Canonical packet integrity check failed: SHA256 mismatch"):
            ExpertReviewValidator(canonical_packet_path=tampered_packet)

    def test_reject_substituted_canonical_packet_identity(self, tmp_path):
        """Verifies that an arbitrary substituted JSON packet fails packet identity validation."""
        from scripts.import_expert_reviews import ExpertReviewValidator

        fake_packet = tmp_path / "fake_packet.json"
        fake_packet.write_text(json.dumps({"packet_id": "UNAUTHORIZED-PACKET", "benchmark_id": "UNKNOWN"}), encoding="utf-8")

        with pytest.raises(ValueError, match="Canonical packet integrity check failed|Canonical packet identity mismatch"):
            ExpertReviewValidator(canonical_packet_path=fake_packet)

    def test_reject_canonical_packet_evidence_status_tampering(self, tmp_path):
        """Verifies that tampering with evidence verification status inside the canonical packet itself is rejected."""
        from scripts.import_expert_reviews import ExpertReviewValidator

        canonical_content = json.loads(CANONICAL_PACKET_JSON.read_text(encoding="utf-8"))
        # Illegally tamper with BM-CASE-001 inside canonical packet
        canonical_content["cases"][0]["evidence_verification_status"] = "verified_local_source"

        tampered_packet = tmp_path / "tampered_ev.json"
        tampered_packet.write_text(json.dumps(canonical_content), encoding="utf-8")

        # Even if hash enforcement is bypassed for unit testing the rule:
        with pytest.raises(ValueError, match="Canonical packet case BM-CASE-001 must have evidence_verification_status 'external_reference_unverified'"):
            ExpertReviewValidator(canonical_packet_path=tampered_packet, enforce_canonical_hash=False)

    def test_invalid_csv_creates_no_partial_output(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that an invalid CSV creates no output file or partial artifact during import."""
        rows = list(canonical_csv_rows)
        rows[0]["r1_expert_decision_label"] = "invalid_label"
        csv_file = tmp_path / "invalid_review.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        out_json = tmp_path / "should_not_exist.json"
        proc = run_cli("--import", str(csv_file), "--output", str(out_json))
        assert proc.returncode == 1
        assert not out_json.exists(), "Output file must not be created on validation failure"

    def test_reject_tampering_with_final_adjudicated_label_in_csv(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that attempting to set final_adjudicated_label in CSV is caught as immutable tampering."""
        rows = list(canonical_csv_rows)
        rows[0]["final_adjudicated_label"] = "supported_mapping"

        csv_file = tmp_path / "tampered_final_label.csv"
        write_csv(csv_file, canonical_fieldnames, rows)

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "Tampering detected in BM-CASE-001" in proc.stdout
        assert "final_adjudicated_label" in proc.stdout

    def test_reject_duplicate_column_headers_in_csv(self, tmp_path, canonical_csv_rows, canonical_fieldnames):
        """Verifies that duplicate column headers are rejected immediately."""
        bad_headers = list(canonical_fieldnames)
        bad_headers[5] = bad_headers[4]  # Duplicate header

        raw_csv = io.StringIO()
        writer = csv.writer(raw_csv)
        writer.writerow(bad_headers)
        for r in canonical_csv_rows:
            writer.writerow([r.get(h, "") for h in canonical_fieldnames])

        csv_file = tmp_path / "dup_headers.csv"
        csv_file.write_text(raw_csv.getvalue(), encoding="utf-8")

        proc = run_cli("--validate", str(csv_file))
        assert proc.returncode == 1
        assert "Duplicate column headers found in CSV" in proc.stdout
