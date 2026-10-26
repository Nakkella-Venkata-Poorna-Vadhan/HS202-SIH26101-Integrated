"""
import_expert_reviews.py
Stage 3.5.2 — Safe Expert Review Import and Validation CLI.

Validates and imports authorized expert review edits from a review CSV into
a separate review-results JSON artifact.

Key Safeguards:
- Strict validation against canonical expert triage packet (expert_triage_packet.json).
- Immutability of all core course, manifest, and evidence metadata.
- Rejection of invalid labels, out-of-range confidence ratings, and partial reviews.
- Strict isolation of Reviewer 1 and Reviewer 2 records.
- Surfaces reviewer conflicts explicitly (no silent merging).
- One reviewer alone cannot establish consensus or benchmark ground truth.
- Refuses to overwrite existing output files or canonical protected files.
- Never modifies raw PDFs, processed catalogues, or production mapping registry.

Usage:
  python scripts/import_expert_reviews.py --validate <path_to_csv>
  python scripts/import_expert_reviews.py --import <path_to_csv> --output <path_to_json>
  python scripts/import_expert_reviews.py --help
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_PACKET_JSON = PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.json"
CANONICAL_PACKET_CSV = PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.csv"
KCM_CATALOG_JSON = PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json"

# Explicit Canonical Packet Identity & Frozen Baselines
EXPECTED_PACKET_ID = "EXPERT-TRIAGE-PACKET-MOSPI-2026-V1"
EXPECTED_BENCHMARK_ID = "BM-PILOT-MOSPI-2026-V1"
EXPECTED_CANONICAL_PACKET_SHA256 = "ad2c517b2fca7aff5e26f455b38609f1a65f010f4c0ad9926af480d6825bc8db"
EXPECTED_CANONICAL_CSV_SHA256 = "fddefbd67a9a6d1af9a3076cd2d5692e3b3cc49820ed8c0cecc3dd6dfa0b6060"

PROTECTED_PATHS = {
    PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.json",
    PROJECT_ROOT / "data" / "interim" / "expert_triage_packet.csv",
    PROJECT_ROOT / "data" / "interim" / "mapping_benchmark_manifest.json",
    PROJECT_ROOT / "data" / "processed" / "acbp_courses.json",
    PROJECT_ROOT / "data" / "processed" / "competencies_kcm.json",
    PROJECT_ROOT / "data" / "processed" / "acbp_kcm_mappings.json",
    PROJECT_ROOT / "data" / "source_register.json",
}

ALLOWED_BENCHMARK_LABELS = {
    "supported_mapping",
    "plausible_insufficient_evidence",
    "incorrect_mapping",
    "unresolved_insufficient_source",
    "no_applicable_kcm_competency",
}

# All 43 canonical non-reviewer columns are strictly immutable during triage review
IMMUTABLE_CASE_FIELDS = [
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


class ExpertReviewValidator:
    """Validates human-reviewed CSV submissions against canonical packet and integrity rules."""

    def __init__(
        self,
        canonical_packet_path: Optional[Path] = None,
        kcm_path: Optional[Path] = None,
        expected_canonical_sha256: Optional[str] = EXPECTED_CANONICAL_PACKET_SHA256,
        enforce_canonical_hash: bool = True,
    ) -> None:
        self.canonical_packet_path = (canonical_packet_path or CANONICAL_PACKET_JSON).resolve()
        self.kcm_path = (kcm_path or KCM_CATALOG_JSON).resolve()
        self.expected_canonical_sha256 = expected_canonical_sha256
        self.enforce_canonical_hash = enforce_canonical_hash

        if not self.canonical_packet_path.exists():
            raise FileNotFoundError(f"Canonical packet not found: {self.canonical_packet_path}")
        if not self.kcm_path.exists():
            raise FileNotFoundError(f"KCM catalog not found: {self.kcm_path}")

        # 1. Enforce canonical packet checksum against trusted baseline
        actual_sha256 = compute_sha256(self.canonical_packet_path)
        if self.enforce_canonical_hash and self.expected_canonical_sha256:
            if actual_sha256 != self.expected_canonical_sha256:
                raise ValueError(
                    f"Canonical packet integrity check failed: SHA256 mismatch.\n"
                    f"  Expected baseline : {self.expected_canonical_sha256}\n"
                    f"  Actual file SHA256: {actual_sha256}\n"
                    f"Refusing to proceed: the canonical packet has been modified, corrupted, or replaced."
                )

        # 2. Validate canonical packet root structure and explicit identity
        self.canonical_data = load_json(self.canonical_packet_path)
        if not isinstance(self.canonical_data, dict):
            raise ValueError(f"Canonical packet root must be a JSON object: {self.canonical_packet_path}")

        packet_id = self.canonical_data.get("packet_id")
        if packet_id != EXPECTED_PACKET_ID:
            raise ValueError(
                f"Canonical packet identity mismatch: expected packet_id '{EXPECTED_PACKET_ID}', got '{packet_id}'."
            )

        benchmark_id = self.canonical_data.get("benchmark_id")
        if benchmark_id != EXPECTED_BENCHMARK_ID:
            raise ValueError(
                f"Canonical packet benchmark ID mismatch: expected benchmark_id '{EXPECTED_BENCHMARK_ID}', got '{benchmark_id}'."
            )

        # 3. Validate case collection and evidence provenance
        raw_cases = self.canonical_data.get("cases")
        if not isinstance(raw_cases, list) or len(raw_cases) != 26:
            raise ValueError(f"Canonical packet must contain exactly 26 cases in 'cases' list.")

        self.canonical_cases = {}
        for c in raw_cases:
            if not isinstance(c, dict) or "benchmark_case_id" not in c:
                raise ValueError("Canonical packet contains malformed case record without benchmark_case_id.")
            self.canonical_cases[c["benchmark_case_id"]] = c

        self.expected_case_ids = [f"BM-CASE-{i:03d}" for i in range(1, 27)]
        if sorted(self.canonical_cases.keys()) != self.expected_case_ids:
            raise ValueError("Canonical packet case IDs do not match expected BM-CASE-001 through BM-CASE-026.")

        # Validate canonical evidence verification status rules
        for cid, case in self.canonical_cases.items():
            ev_status = case.get("evidence_verification_status")
            if cid in {"BM-CASE-021", "BM-CASE-024", "BM-CASE-025"}:
                if ev_status != "verified_local_source":
                    raise ValueError(f"Canonical packet case {cid} must have evidence_verification_status 'verified_local_source'.")
            else:
                if ev_status != "external_reference_unverified":
                    raise ValueError(f"Canonical packet case {cid} must have evidence_verification_status 'external_reference_unverified'.")
            if case.get("is_exact_course_evidence") is not False:
                raise ValueError(f"Canonical packet case {cid} must have is_exact_course_evidence=False.")

        # 4. Load KCM catalog
        kcm_list = load_json(self.kcm_path)
        if not isinstance(kcm_list, list):
            raise ValueError(f"KCM catalog must be a list: {self.kcm_path}")
        self.valid_kcm_ids = {c["competency_id"] for c in kcm_list if isinstance(c, dict) and "competency_id" in c}

        # 5. Expected CSV column headers
        self.expected_fieldnames = list(self.canonical_data.get("csv_fieldnames", []))
        if not self.expected_fieldnames and CANONICAL_PACKET_CSV.exists():
            with open(CANONICAL_PACKET_CSV, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.expected_fieldnames = next(reader)

    def validate_csv(self, csv_path: Path) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
        """
        Validates the CSV file against all contract rules.
        Returns: (is_valid, list_of_errors, validated_case_records)
        """
        errors: List[str] = []
        validated_cases: List[Dict[str, Any]] = []

        if not csv_path.exists():
            return False, [f"CSV file not found: {csv_path}"], []

        try:
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                raw_reader = csv.reader(f)
                header_row = next(raw_reader, None)
                if not header_row:
                    return False, ["CSV file is empty or missing header row."], []

                seen_hdrs: Set[str] = set()
                dup_hdrs: Set[str] = set()
                for h in header_row:
                    if h in seen_hdrs:
                        dup_hdrs.add(h)
                    seen_hdrs.add(h)

                if dup_hdrs:
                    errors.append(f"Duplicate column headers found in CSV: {sorted(dup_hdrs)}")
                    return False, errors, []

                if header_row != self.expected_fieldnames:
                    errors.append(
                        f"CSV header mismatch. Expected {len(self.expected_fieldnames)} columns, found {len(header_row)}. "
                        "Columns must exactly match the canonical export header."
                    )
                    return False, errors, []

                f.seek(0)
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            return False, [f"Failed to read CSV (encoding or formatting defect): {e}"], []

        if len(rows) != len(self.expected_case_ids):
            errors.append(
                f"Case count mismatch: Expected exactly {len(self.expected_case_ids)} cases, found {len(rows)} rows."
            )
            return False, errors, []

        case_ids = [r.get("benchmark_case_id", "").strip() for r in rows]
        seen_ids: Set[str] = set()
        duplicate_ids: Set[str] = set()
        for cid in case_ids:
            if cid in seen_ids:
                duplicate_ids.add(cid)
            seen_ids.add(cid)

        if duplicate_ids:
            errors.append(f"Duplicate benchmark_case_id values found: {sorted(duplicate_ids)}")

        if sorted(case_ids) != self.expected_case_ids:
            missing_ids = set(self.expected_case_ids) - set(case_ids)
            unexpected_ids = set(case_ids) - set(self.expected_case_ids)
            if missing_ids:
                errors.append(f"Missing expected benchmark_case_id values: {sorted(missing_ids)}")
            if unexpected_ids:
                errors.append(f"Unexpected benchmark_case_id values found: {sorted(unexpected_ids)}")

        if errors:
            return False, errors, []

        actual_packet_sha256 = compute_sha256(self.canonical_packet_path)

        # Validate case by case
        for row in rows:
            cid = row["benchmark_case_id"].strip()
            base_case = self.canonical_cases[cid]

            # Optional canonical_packet_sha256 column validation if present
            if "canonical_packet_sha256" in row:
                csv_packet_hash = (row.get("canonical_packet_sha256") or "").strip()
                if csv_packet_hash and csv_packet_hash != actual_packet_sha256:
                    errors.append(
                        f"CSV canonical_packet_sha256 mismatch in {cid}: "
                        f"expected '{actual_packet_sha256}', found '{csv_packet_hash}'."
                    )

            # 1. Validate Immutable Baseline Metadata across all non-reviewer columns
            for field in IMMUTABLE_CASE_FIELDS:
                csv_val = (row.get(field) or "").strip()
                base_raw = base_case.get(field)
                if isinstance(base_raw, bool):
                    base_val = str(base_raw)
                elif base_raw is None:
                    base_val = ""
                else:
                    base_val = str(base_raw).strip()

                if csv_val != base_val:
                    errors.append(
                        f"Tampering detected in {cid}: field '{field}' modified from '{base_val}' to '{csv_val}'. "
                        "Course metadata and source provenance are strictly immutable."
                    )

            # Explicit check for evidence status escalation
            ev_status = (row.get("evidence_verification_status") or "").strip()
            if ev_status == "verified_local_source" and base_case["evidence_verification_status"] == "external_reference_unverified":
                errors.append(
                    f"Illegal evidence escalation in {cid}: cannot promote external_reference_unverified "
                    "to verified_local_source via CSV edit."
                )

            is_exact = (row.get("is_exact_course_evidence") or "").strip()
            if is_exact == "True" and not base_case["is_exact_course_evidence"]:
                errors.append(
                    f"Illegal evidence escalation in {cid}: cannot set is_exact_course_evidence to True via CSV edit."
                )

            # 2. Validate Reviewer 1 Submission
            r1_sub, r1_errs = self._validate_reviewer_slot(row, cid, slot=1)
            errors.extend(r1_errs)

            # 3. Validate Reviewer 2 Submission
            r2_sub, r2_errs = self._validate_reviewer_slot(row, cid, slot=2)
            errors.extend(r2_errs)

            # 4. Consensus & Status Evaluation
            consensus_eval = self._evaluate_consensus(cid, r1_sub, r2_sub, base_case)

            validated_cases.append({
                "benchmark_case_id": cid,
                "course_record_id": base_case["course_record_id"],
                "course_name": base_case["course_name"],
                "cadre_role": base_case["cadre_role"],
                "acbp_competency_category": base_case["acbp_competency_category"],
                "primary_source_citation": base_case["primary_source_citation"],
                "candidate_kcm_id": base_case.get("candidate_kcm_id"),
                "evidence_verification_status": base_case["evidence_verification_status"],
                "reviewer_1": r1_sub,
                "reviewer_2": r2_sub,
                "consensus_evaluation": consensus_eval,
            })

        is_valid = (len(errors) == 0)
        return is_valid, errors, validated_cases

    def _validate_reviewer_slot(self, row: Dict[str, str], cid: str, slot: int) -> Tuple[Dict[str, Any], List[str]]:
        prefix = f"r{slot}_"
        errs: List[str] = []

        rid = (row.get(f"{prefix}reviewer_id") or "").strip()
        role = (row.get(f"{prefix}reviewer_role") or "").strip()
        affil = (row.get(f"{prefix}reviewer_affiliation") or "").strip()
        date = (row.get(f"{prefix}review_date") or "").strip()
        label = (row.get(f"{prefix}expert_decision_label") or "").strip()
        kcm_id = (row.get(f"{prefix}expert_target_kcm_id") or "").strip()
        kcm_name = (row.get(f"{prefix}expert_target_kcm_name") or "").strip()
        subtheme = (row.get(f"{prefix}expert_subtheme") or "").strip()
        suff = (row.get(f"{prefix}evidence_sufficiency_verdict") or "").strip()
        depth = (row.get(f"{prefix}depth_assessment") or "").strip()
        conf_str = (row.get(f"{prefix}confidence_rating") or "").strip()
        rat = (row.get(f"{prefix}expert_rationale") or "").strip()
        notes = (row.get(f"{prefix}requisition_notes") or "").strip()

        has_any_field = any([rid, role, affil, date, label, kcm_id, kcm_name, subtheme, suff, depth, conf_str, rat, notes])

        if not has_any_field:
            # Completely blank review slot is valid (unreviewed)
            return {
                "reviewer_slot": slot,
                "is_reviewed": False,
                "reviewer_id": None,
                "reviewer_role": None,
                "reviewer_affiliation": None,
                "review_date": None,
                "decision_label": None,
                "target_kcm_id": None,
                "target_kcm_name": None,
                "subtheme": None,
                "evidence_sufficiency_verdict": None,
                "depth_assessment": None,
                "confidence_rating": None,
                "rationale": None,
                "requisition_notes": None,
            }, []

        # If review is partially started, enforce strict completeness
        if not label:
            errs.append(f"Incomplete Reviewer {slot} submission in {cid}: reviewer metadata provided without expert_decision_label.")
        elif label not in ALLOWED_BENCHMARK_LABELS:
            errs.append(
                f"Invalid Reviewer {slot} expert_decision_label in {cid}: '{label}'. "
                f"Must be one of {sorted(ALLOWED_BENCHMARK_LABELS)}."
            )

        if not rid:
            errs.append(f"Incomplete Reviewer {slot} submission in {cid}: decision label provided without reviewer_id.")
        if not rat or len(rat) < 5:
            errs.append(f"Incomplete Reviewer {slot} submission in {cid}: decision label provided without substantive rationale.")

        conf_val: Optional[int] = None
        if not conf_str:
            errs.append(f"Incomplete Reviewer {slot} submission in {cid}: decision label provided without confidence_rating.")
        else:
            try:
                conf_val = int(conf_str)
                if conf_val < 1 or conf_val > 5:
                    errs.append(f"Invalid Reviewer {slot} confidence_rating in {cid}: {conf_val}. Must be an integer 1-5.")
            except ValueError:
                errs.append(f"Malformed Reviewer {slot} confidence_rating in {cid}: '{conf_str}'. Must be an integer 1-5.")

        if kcm_id:
            if label == "no_applicable_kcm_competency":
                errs.append(
                    f"Contradiction in Reviewer {slot} for {cid}: target_kcm_id '{kcm_id}' assigned with label 'no_applicable_kcm_competency'. "
                    "Target KCM ID must be empty when declaring a domain gap."
                )
            elif kcm_id not in self.valid_kcm_ids:
                errs.append(f"Unknown target_kcm_id in Reviewer {slot} for {cid}: '{kcm_id}'. Must exist in KCM catalogue.")

        return {
            "reviewer_slot": slot,
            "is_reviewed": bool(label and rid and rat and conf_val),
            "reviewer_id": rid or None,
            "reviewer_role": role or None,
            "reviewer_affiliation": affil or None,
            "review_date": date or None,
            "decision_label": label or None,
            "target_kcm_id": kcm_id or None,
            "target_kcm_name": kcm_name or None,
            "subtheme": subtheme or None,
            "evidence_sufficiency_verdict": suff or None,
            "depth_assessment": depth or None,
            "confidence_rating": conf_val,
            "rationale": rat or None,
            "requisition_notes": notes or None,
        }, errs

    def _evaluate_consensus(
        self, cid: str, r1: Dict[str, Any], r2: Dict[str, Any], base_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluates reviewer consensus without setting benchmark ground truth."""
        r1_reviewed = r1["is_reviewed"]
        r2_reviewed = r2["is_reviewed"]

        if not r1_reviewed and not r2_reviewed:
            return {
                "status": "pending_reviews",
                "provisional_consensus_label": None,
                "provisional_consensus_kcm_id": None,
                "requires_panel_escalation": False,
                "escalation_reason": None,
                "ground_truth_finalized": False,
            }

        if r1_reviewed and not r2_reviewed:
            return {
                "status": "single_review_in_progress",
                "provisional_consensus_label": None,
                "provisional_consensus_kcm_id": None,
                "requires_panel_escalation": False,
                "escalation_reason": "Waiting for Reviewer 2 independent evaluation.",
                "ground_truth_finalized": False,
            }

        if r2_reviewed and not r1_reviewed:
            return {
                "status": "single_review_in_progress",
                "provisional_consensus_label": None,
                "provisional_consensus_kcm_id": None,
                "requires_panel_escalation": False,
                "escalation_reason": "Waiting for Reviewer 1 independent evaluation.",
                "ground_truth_finalized": False,
            }

        # Both reviewed
        r1_label = r1["decision_label"]
        r2_label = r2["decision_label"]

        if r1_label == r2_label:
            # Check target KCM ID agreement if applicable
            r1_kcm = r1["target_kcm_id"]
            r2_kcm = r2["target_kcm_id"]
            if r1_kcm != r2_kcm and r1_label in ["supported_mapping", "plausible_insufficient_evidence"]:
                return {
                    "status": "conflict_escalated",
                    "provisional_consensus_label": None,
                    "provisional_consensus_kcm_id": None,
                    "requires_panel_escalation": True,
                    "escalation_reason": f"Reviewers agree on label '{r1_label}' but disagree on target KCM ID ('{r1_kcm}' vs '{r2_kcm}').",
                    "ground_truth_finalized": False,
                }

            return {
                "status": "provisional_consensus_achieved",
                "provisional_consensus_label": r1_label,
                "provisional_consensus_kcm_id": r1["target_kcm_id"],
                "requires_panel_escalation": False,
                "escalation_reason": None,
                "ground_truth_finalized": False,  # Ground truth is never finalized automatically in triage
            }
        else:
            return {
                "status": "conflict_escalated",
                "provisional_consensus_label": None,
                "provisional_consensus_kcm_id": None,
                "requires_panel_escalation": True,
                "escalation_reason": f"Reviewer disagreement: Reviewer 1 assigned '{r1_label}', Reviewer 2 assigned '{r2_label}'.",
                "ground_truth_finalized": False,
            }


def run_validate(csv_path: Path) -> int:
    """CLI mode: --validate <csv_path>"""
    print("=" * 70)
    print("MoSPI SIH26101: Validating Expert Review CSV Submission")
    print(f"Target CSV: {csv_path}")
    print("=" * 70)

    try:
        validator = ExpertReviewValidator()
        is_valid, errors, validated_cases = validator.validate_csv(csv_path)
    except Exception as e:
        print(f"\n[FATAL ERROR] Canonical packet integrity failure: {e}")
        return 1

    if not is_valid:
        print(f"\n[VALIDATION FAILED] Found {len(errors)} error(s):")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        print("\nReview CSV rejected. Fix errors before attempting import.")
        return 1

    # Print summary of valid cases
    r1_count = sum(1 for c in validated_cases if c["reviewer_1"]["is_reviewed"])
    r2_count = sum(1 for c in validated_cases if c["reviewer_2"]["is_reviewed"])
    consensus_count = sum(1 for c in validated_cases if c["consensus_evaluation"]["status"] == "provisional_consensus_achieved")
    conflict_count = sum(1 for c in validated_cases if c["consensus_evaluation"]["status"] == "conflict_escalated")

    print(f"\n[VALIDATION PASSED] All {len(validated_cases)} cases satisfy data integrity and review contract.")
    print(f"  - Cases with Reviewer 1 completed: {r1_count} / 26")
    print(f"  - Cases with Reviewer 2 completed: {r2_count} / 26")
    print(f"  - Cases with Provisional Consensus: {consensus_count}")
    print(f"  - Cases with Reviewer Conflict: {conflict_count}")
    print("  - Immutable Metadata & Source Provenance: 100% UNTOUCHED")
    print("\nFile is ready for import via --import <csv> --output <path>.")
    return 0


def run_import(csv_path: Path, output_path: Path) -> int:
    """CLI mode: --import <csv_path> --output <output_path>"""
    print("=" * 70)
    print("MoSPI SIH26101: Importing Expert Review Results")
    print(f"Source CSV : {csv_path}")
    print(f"Output JSON: {output_path}")
    print("=" * 70)

    # 1. Guard output file existence
    if output_path.exists():
        print(f"\n[ERROR] Output file already exists: {output_path}")
        print("Refusing to overwrite existing file. Choose a new output path to ensure reproducibility.")
        return 1

    # 2. Guard canonical protected files
    resolved_out = output_path.resolve()
    for protected in PROTECTED_PATHS:
        if resolved_out == protected.resolve():
            print(f"\n[SECURITY VIOLATION] Output path matches canonical protected file: {protected}")
            print("The importer strictly refuses to overwrite core registry or benchmark files.")
            return 1

    # 3. Guard protected directories
    try:
        if resolved_out.is_relative_to(PROJECT_ROOT / "data" / "processed") or \
           resolved_out.is_relative_to(PROJECT_ROOT / "data" / "raw"):
            print("\n[SECURITY VIOLATION] Output cannot be written inside data/raw/ or data/processed/.")
            return 1
    except AttributeError:
        if str(PROJECT_ROOT / "data" / "processed") in str(resolved_out) or \
           str(PROJECT_ROOT / "data" / "raw") in str(resolved_out):
            print("\n[SECURITY VIOLATION] Output cannot be written inside data/raw/ or data/processed/.")
            return 1

    # 4. Validate Canonical Packet and CSV
    try:
        validator = ExpertReviewValidator()
        is_valid, errors, validated_cases = validator.validate_csv(csv_path)
    except Exception as e:
        print(f"\n[FATAL ERROR] Canonical packet integrity failure: {e}")
        return 1

    if not is_valid:
        print(f"\n[VALIDATION FAILED] Cannot import invalid review file ({len(errors)} errors):")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    # 5. Compile review-results artifact
    r1_count = sum(1 for c in validated_cases if c["reviewer_1"]["is_reviewed"])
    r2_count = sum(1 for c in validated_cases if c["reviewer_2"]["is_reviewed"])
    both_count = sum(1 for c in validated_cases if c["reviewer_1"]["is_reviewed"] and c["reviewer_2"]["is_reviewed"])
    consensus_count = sum(1 for c in validated_cases if c["consensus_evaluation"]["status"] == "provisional_consensus_achieved")
    conflict_count = sum(1 for c in validated_cases if c["consensus_evaluation"]["status"] == "conflict_escalated")
    unreviewed_count = sum(1 for c in validated_cases if not c["reviewer_1"]["is_reviewed"] and not c["reviewer_2"]["is_reviewed"])

    # Ensure deterministic ordering by benchmark_case_id
    sorted_cases = sorted(validated_cases, key=lambda c: c["benchmark_case_id"])

    artifact = {
        "artifact_type": "expert_review_results",
        "disclaimer": (
            "DECLARATION: This is a human-review evaluation artifact and does NOT constitute the "
            "production mapping registry or finalized benchmark ground truth. Reviewer credentials "
            "are self-declared in the review submission and are NOT cryptographically or institutionally "
            "authenticated. Reviewer consensus is provisional and is not legally or institutionally "
            "binding on MoSPI, NSSTA, or CBC."
        ),
        "packet_id": validator.canonical_data.get("packet_id", EXPECTED_PACKET_ID),
        "benchmark_id": validator.canonical_data.get("benchmark_id", EXPECTED_BENCHMARK_ID),
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "source_csv_filename": csv_path.name,
        "source_csv_sha256": compute_sha256(csv_path),
        "canonical_packet_sha256": compute_sha256(validator.canonical_packet_path),
        "canonical_packet_expected_sha256": validator.expected_canonical_sha256,
        "summary": {
            "total_cases": len(sorted_cases),
            "unreviewed_cases": unreviewed_count,
            "reviewer_1_completed": r1_count,
            "reviewer_2_completed": r2_count,
            "both_reviewers_completed": both_count,
            "provisional_consensus_achieved": consensus_count,
            "conflicts_requiring_escalation": conflict_count,
            "ground_truth_finalized": False,
        },
        "cases": sorted_cases,
    }

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write to temporary file before replacing target
    temp_output_path = output_path.with_suffix(output_path.suffix + f".tmp_{os.getpid()}")
    try:
        with open(temp_output_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        temp_output_path.replace(output_path)
    except Exception as e:
        if temp_output_path.exists():
            try:
                temp_output_path.unlink()
            except OSError:
                pass
        print(f"\n[ERROR] Failed to write review results artifact: {e}")
        return 1

    print(f"\n[IMPORT SUCCESSFUL] Review results written to {output_path}")
    print(f"  - Total cases processed: {len(validated_cases)}")
    print(f"  - Provisional consensus: {consensus_count}")
    print(f"  - Conflicts escalated: {conflict_count}")
    print("  - Production registry & benchmark ground truth remain untouched.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MoSPI SIH26101: Safe Expert Review Import and Validation CLI (Stage 3.5.2).",
        epilog="Security Note: This tool strictly refuses to overwrite core datasets or finalized benchmark ground truth.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--validate",
        metavar="CSV_PATH",
        type=Path,
        help="Validate a human-edited review CSV against the canonical packet and contract rules without writing files.",
    )
    group.add_argument(
        "--import",
        dest="import_csv",
        metavar="CSV_PATH",
        type=Path,
        help="Import a validated review CSV into a separate review-results JSON artifact (requires --output).",
    )
    parser.add_argument(
        "--output",
        metavar="OUTPUT_PATH",
        type=Path,
        help="Path for the new review-results JSON artifact (required with --import). Refuses to overwrite existing files.",
    )

    args = parser.parse_args()

    if args.validate:
        sys.exit(run_validate(args.validate))
    elif args.import_csv:
        if not args.output:
            parser.error("--import requires --output <path_to_json>")
        sys.exit(run_import(args.import_csv, args.output))


if __name__ == "__main__":
    main()
