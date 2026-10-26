#!/usr/bin/env python3
"""
scripts/build_mapping_registry.py — Hardened Competency Mapping Registry & Review Queue Builder

Constructs the auditable Stage 3.2 mapping registry and human-review queue for all
226 MoSPI ACBP course allocations against the Karmayogi Competency Model (KCM).

Hardened Governance Features (Stage 3.2.2):
1. Safe Refusal by Default: If output artifacts already exist, refuses to overwrite
   without an explicit policy flag, preventing accidental destruction of human reviews.
2. Safe Merge Policy (--merge-existing): Preserves human decisions (validated, rejected,
   curated candidates, reviewer IDs, timestamps, notes, and rationales) across refreshes.
3. Conflict Detection: Fails safely without modifying files if source course metadata
   changed while an existing human decision was present.
4. Clean Re-initialization with Mandatory Backup (--init-clean --create-backup).
5. Output Directory Redirection (--output-dir).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
BACKUP_DIR = PROJECT_ROOT / "data" / "interim" / "backups"

ACBP_COURSES_PATH = DATA_PROCESSED / "acbp_courses.json"
KCM_COMPETENCIES_PATH = DATA_PROCESSED / "competencies_kcm.json"
CANDIDATE_MAPPINGS_PATH = DATA_PROCESSED / "acbp_kcm_candidate_mappings.json"

DEFAULT_MAPPINGS_JSON_PATH = DATA_PROCESSED / "acbp_kcm_mappings.json"
DEFAULT_MAPPINGS_CSV_PATH = DATA_PROCESSED / "acbp_kcm_mappings.csv"
DEFAULT_REVIEW_QUEUE_JSON_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.json"
DEFAULT_REVIEW_QUEUE_CSV_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.csv"

PIPELINE_VERSION = "3.2.2"
FIXED_GENERATION_TIMESTAMP = "2026-10-18T14:40:00+00:00"

# Explicit KCM page mappings for known competencies (def_page, subtheme_page)
KCM_PAGE_LOOKUP: Dict[str, tuple[int, int]] = {
    "KCM-BEH-06": (49, 50),   # Collaboration
    "KCM-FUNC-05": (74, 75),  # Project Management
    "KCM-BEH-10": (57, 58),   # Strategic Leadership
    "KCM-FUNC-11": (84, 85),  # Data Analytics
    "KCM-FUNC-13": (90, 91),  # Office Management
    "KCM-FUNC-14": (92, 93),  # Parliamentary Matters
    "KCM-FUNC-15": (94, 95),  # RTI Matters
    "KCM-FUNC-18": (100, 101), # Litigation Management
    "KCM-FUNC-19": (98, 99),  # Vigilance Administration
    "KCM-FUNC-20": (104, 105), # Change Management
    "KCM-FUNC-21": (106, 107), # Administration Matters
    "KCM-BEH-13": (63, 64),   # Decision Making
}


def compute_sha256(path: Path) -> str:
    """Compute cryptographic SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_input_datasets() -> tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Load and index baseline input datasets without modifying them."""
    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        course_data = json.load(f)
    courses = course_data.get("records", course_data) if isinstance(course_data, dict) else course_data

    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        kcm_list = json.load(f)
    kcm_by_id = {c["competency_id"]: c for c in kcm_list}

    with open(CANDIDATE_MAPPINGS_PATH, "r", encoding="utf-8") as f:
        cand_data = json.load(f)
    cand_by_course = {m["course_record_id"]: m for m in cand_data.get("mappings", [])}

    return courses, kcm_by_id, cand_by_course


def is_human_decision_record(rec: Dict[str, Any]) -> bool:
    """Determine whether an existing record contains human curation/decision data."""
    if rec.get("validation_status") in ("validated", "rejected"):
        return True
    if rec.get("mapping_type") == "curated_candidate":
        return True
    if rec.get("reviewer_id") is not None or rec.get("reviewed_at") is not None:
        return True
    if rec.get("reviewer_notes") and rec.get("reviewer_notes").strip():
        return True
    return False


def create_backup_archive(target_dir: Path) -> Path:
    """Create a timestamped backup of existing mapping artifacts before modification."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_sub = BACKUP_DIR / f"registry_backup_{ts}"
    backup_sub.mkdir(parents=True, exist_ok=True)

    for fname in ["acbp_kcm_mappings.json", "acbp_kcm_mappings.csv", "acbp_kcm_review_queue.json", "acbp_kcm_review_queue.csv"]:
        src = target_dir / fname
        if src.exists():
            shutil.copy2(src, backup_sub / fname)

    return backup_sub


def build_mapping_records(
    courses: List[Dict[str, Any]],
    kcm_by_id: Dict[str, Dict[str, Any]],
    cand_by_course: Dict[str, Dict[str, Any]],
    source_hash_course: str,
    source_hash_kcm: str,
    existing_records: Optional[Dict[str, Dict[str, Any]]] = None,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Build the 226 mapping records and corresponding review queue items.
    If existing_records is provided, safely merges human decisions and detects conflicts.
    """
    mapping_records: List[Dict[str, Any]] = []
    review_queue: List[Dict[str, Any]] = []

    # Sequence counter for mapping IDs
    map_idx = 1

    for course in courses:
        cid = course["record_id"]
        c_title = course["course_name"]
        cadre = course["cadre_role"]
        category = course["competency_category"]
        page = course["source_page"]
        row = course["source_row"]

        mapping_id = f"MAP-ACBP-KCM-{map_idx:03d}"
        queue_id = f"REV-{map_idx:03d}"
        map_idx += 1

        # Check if an existing human decision exists for this mapping
        existing_rec = existing_records.get(mapping_id) if existing_records else None
        if not existing_rec and existing_records:
            # Fallback check by course_record_id
            for ex in existing_records.values():
                if ex.get("course_record_id") == cid:
                    existing_rec = ex
                    break

        if existing_rec and is_human_decision_record(existing_rec):
            # SOURCE CONFLICT DETECTION: Verify whether underlying source course changed
            if (
                existing_rec.get("course_name") != c_title
                or existing_rec.get("cadre_role") != cadre
                or existing_rec.get("acbp_competency_category") != category
                or existing_rec.get("course_source_page") != page
                or existing_rec.get("course_source_row") != row
            ):
                raise ValueError(
                    f"Conflict detected for course '{cid}' ({mapping_id}): Source course metadata in acbp_courses.json "
                    f"has changed since human decision was rendered (old title='{existing_rec.get('course_name')}', "
                    f"new title='{c_title}'). Merging this decision would compromise curricular integrity. "
                    f"Re-review is required before this mapping can be refreshed."
                )

            # Preserve human decision with full fidelity
            merged_rec = dict(existing_rec)
            merged_rec["mapping_id"] = mapping_id
            merged_rec["course_record_id"] = cid
            merged_rec["source_hash_course"] = source_hash_course
            merged_rec["source_hash_kcm"] = source_hash_kcm
            mapping_records.append(merged_rec)

            # Mirror into review queue
            val_status = merged_rec.get("validation_status", "pending_review")
            m_type = merged_rec.get("mapping_type", "curated_candidate")
            kid = merged_rec.get("candidate_kcm_competency_id")
            kname = merged_rec.get("candidate_kcm_competency_name")
            p_def = merged_rec.get("kcm_source_page_def")
            p_sub = merged_rec.get("kcm_source_page_sub")

            if val_status == "validated":
                q_cat = "validated"
                prio = "resolved"
                rec_act = f"Verified by {merged_rec.get('reviewer_id')} ({merged_rec.get('reviewer_role')})"
            elif val_status == "rejected":
                q_cat = "rejected"
                prio = "resolved"
                rec_act = f"Rejected by reviewer. Rationale: {merged_rec.get('evidence_or_rationale')}"
            else:
                q_cat = "curated_candidate"
                prio = "high"
                rec_act = "Curated candidate awaiting institutional validation sign-off."

            review_queue.append({
                "queue_id": queue_id,
                "mapping_id": mapping_id,
                "course_record_id": cid,
                "course_name": c_title,
                "cadre_role": cadre,
                "acbp_competency_category": category,
                "candidate_kcm_competency_id": kid,
                "candidate_kcm_competency_name": kname,
                "mapping_type": m_type,
                "validation_status": val_status,
                "queue_category": q_cat,
                "priority": prio,
                "evidence_or_rationale": merged_rec.get("evidence_or_rationale", ""),
                "course_source_reference": f"SRC-MOSPI-ACBP-2026-27 (Page {page}, Row {row})",
                "kcm_source_reference": f"SRC-CBC-KCM-2024 ({kid}, Pages [{p_def}, {p_sub}])" if kid else None,
                "missing_evidence_or_ambiguity": "Human review recorded. Verify institutional authorization before final deployment." if val_status != "validated" else "None. Fully validated.",
                "recommended_action": rec_act,
            })
            continue

        # Standard deterministic initial generation
        cand = cand_by_course.get(cid)
        has_cand = cand is not None and cand.get("candidate_kcm_competency_id") is not None

        if has_cand:
            kcm_id = cand["candidate_kcm_competency_id"]
            kcm_rec = kcm_by_id.get(kcm_id, {})
            kcm_name = kcm_rec.get("competency_name", cand.get("candidate_kcm_competency_name"))
            kcm_type = kcm_rec.get("competency_type", cand.get("candidate_kcm_competency_type"))
            p_def, p_sub = KCM_PAGE_LOOKUP.get(kcm_id, (None, None))

            mapping_type = "exact_title_reference"
            mapping_method = "verbatim_title_containment"
            evidence = (
                f"Course title contains verbatim token match for KCM competency '{kcm_name}'. "
                f"Curricular alignment across sub-themes and learning outcomes remains unverified "
                f"pending iGOT syllabus review."
            )
            val_status = "pending_review"

            queue_category = "title_reference_candidate"
            missing_evidence = (
                "Absence of modular course syllabus, lesson plan, and target proficiency depth. "
                "Requires confirmation that course content comprehensively addresses KCM sub-themes."
            )
            rec_action = (
                f"Audit course syllabus against KCM {kcm_id} sub-themes on Page {p_sub} to determine "
                "if candidate should be promoted to curated_candidate or rejected."
            )
            priority = "high"

            rec: Dict[str, Any] = {
                "mapping_id": mapping_id,
                "course_record_id": cid,
                "cadre_role": cadre,
                "course_name": c_title,
                "acbp_competency_category": category,
                "candidate_kcm_competency_id": kcm_id,
                "candidate_kcm_competency_name": kcm_name,
                "candidate_kcm_subtheme": None,
                "candidate_kcm_competency_type": kcm_type,
                "mapping_type": mapping_type,
                "mapping_method": mapping_method,
                "evidence_or_rationale": evidence,
                "course_source_id": "SRC-MOSPI-ACBP-2026-27",
                "course_source_page": page,
                "course_source_row": row,
                "kcm_source_id": "SRC-CBC-KCM-2024",
                "kcm_source_page_def": p_def,
                "kcm_source_page_sub": p_sub,
                "confidence_score": None,
                "confidence_metric": None,
                "validation_status": val_status,
                "reviewer_id": None,
                "reviewer_role": None,
                "reviewed_at": None,
                "reviewer_notes": "",
                "creation_method": "automated_pipeline",
                "pipeline_version": PIPELINE_VERSION,
                "created_at": FIXED_GENERATION_TIMESTAMP,
                "source_hash_course": source_hash_course,
                "source_hash_kcm": source_hash_kcm,
            }

        else:
            kcm_id = None
            kcm_name = None
            kcm_type = None
            p_def = None
            p_sub = None
            mapping_type = "unresolved"
            val_status = "unresolved"

            if category == "Domain":
                mapping_method = "unresolved_domain_gap"
                evidence = (
                    "Official MoSPI Domain category course. The CBC KCM baseline defines zero "
                    "Domain competencies (Ministry-specific). Retained as unresolved pending "
                    "MoSPI/NSSTA Domain Competency Dictionary integration."
                )
                queue_category = "unresolved_domain_gap"
                missing_evidence = (
                    "MoSPI Official Statistics Domain Competency Dictionary absent from CBC KCM. "
                    "Do not force-map to generic functional competencies."
                )
                rec_action = (
                    "Await publication and integration of official MoSPI/NSSTA Domain Competency "
                    "Dictionary under Stage 4."
                )
                priority = "low"
            else:
                mapping_method = "unresolved_no_match"
                evidence = (
                    "No explicit title reference to KCM competencies in ACBP source text. "
                    "Curricular alignment requires modular iGOT course syllabi and learning outcome indicators."
                )
                queue_category = "unresolved_no_match"
                missing_evidence = (
                    "No textual match in course title. Absence of modular syllabus and learning outcomes "
                    "prevents defensible competency mapping."
                )
                rec_action = (
                    "Acquire iGOT modular curriculum outline to perform semantic and curricular comparison "
                    "in Stage 3.3+."
                )
                priority = "medium"

            rec = {
                "mapping_id": mapping_id,
                "course_record_id": cid,
                "cadre_role": cadre,
                "course_name": c_title,
                "acbp_competency_category": category,
                "candidate_kcm_competency_id": None,
                "candidate_kcm_competency_name": None,
                "candidate_kcm_subtheme": None,
                "candidate_kcm_competency_type": None,
                "mapping_type": mapping_type,
                "mapping_method": mapping_method,
                "evidence_or_rationale": evidence,
                "course_source_id": "SRC-MOSPI-ACBP-2026-27",
                "course_source_page": page,
                "course_source_row": row,
                "kcm_source_id": None,
                "kcm_source_page_def": None,
                "kcm_source_page_sub": None,
                "confidence_score": None,
                "confidence_metric": None,
                "validation_status": val_status,
                "reviewer_id": None,
                "reviewer_role": None,
                "reviewed_at": None,
                "reviewer_notes": "",
                "creation_method": "automated_pipeline",
                "pipeline_version": PIPELINE_VERSION,
                "created_at": FIXED_GENERATION_TIMESTAMP,
                "source_hash_course": source_hash_course,
                "source_hash_kcm": source_hash_kcm,
            }

        mapping_records.append(rec)

        # Build review queue entry
        q_entry = {
            "queue_id": queue_id,
            "mapping_id": mapping_id,
            "course_record_id": cid,
            "course_name": c_title,
            "cadre_role": cadre,
            "acbp_competency_category": category,
            "candidate_kcm_competency_id": kcm_id,
            "candidate_kcm_competency_name": kcm_name,
            "mapping_type": mapping_type,
            "validation_status": val_status,
            "queue_category": queue_category,
            "priority": priority,
            "evidence_or_rationale": evidence,
            "course_source_reference": f"SRC-MOSPI-ACBP-2026-27 (Page {page}, Row {row})",
            "kcm_source_reference": f"SRC-CBC-KCM-2024 ({kcm_id}, Pages [{p_def}, {p_sub}])" if kcm_id else None,
            "missing_evidence_or_ambiguity": missing_evidence,
            "recommended_action": rec_action,
        }
        review_queue.append(q_entry)

    return mapping_records, review_queue


def serialize_mappings_csv(records: List[Dict[str, Any]], output_path: Path) -> None:
    """Serialize mapping records to CSV with exact 1-to-1 parity."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in records:
            row_dict = {k: ("" if v is None else v) for k, v in r.items()}
            writer.writerow(row_dict)


def serialize_review_queue_csv(records: List[Dict[str, Any]], output_path: Path) -> None:
    """Serialize review queue entries to CSV."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in records:
            row_dict = {k: ("" if v is None else v) for k, v in r.items()}
            writer.writerow(row_dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MoSPI SIH26101: Hardened Competency Mapping Registry Builder (Stage 3.2.2)"
    )
    parser.add_argument(
        "--merge-existing",
        action="store_true",
        help="Safely refresh registry while preserving human review decisions, rejections, and rationales.",
    )
    parser.add_argument(
        "--init-clean",
        action="store_true",
        help="Re-initialize the registry from scratch. Requires --create-backup if registry exists.",
    )
    parser.add_argument(
        "--create-backup",
        action="store_true",
        help="Mandatory flag required with --init-clean to create an automatic timestamped backup.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATA_PROCESSED,
        help="Directory to write output artifacts (defaults to data/processed).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.output_dir
    mappings_json_path = out_dir / "acbp_kcm_mappings.json"
    mappings_csv_path = out_dir / "acbp_kcm_mappings.csv"
    review_queue_json_path = out_dir / "acbp_kcm_review_queue.json"
    review_queue_csv_path = out_dir / "acbp_kcm_review_queue.csv"

    # 1. OVERWRITE SAFETY CHECK (LIM-02)
    artifacts_exist = mappings_json_path.exists()

    if artifacts_exist and not (args.merge_existing or args.init_clean):
        print("=" * 75, file=sys.stderr)
        print("[SAFETY HALT] Target mapping registry already exists:", file=sys.stderr)
        print(f"  Path: {mappings_json_path}", file=sys.stderr)
        print(file=sys.stderr)
        print("To protect human review decisions and audit history, re-running the builder", file=sys.stderr)
        print("will not overwrite existing records by default.", file=sys.stderr)
        print(file=sys.stderr)
        print("Safe Alternatives:", file=sys.stderr)
        print("  1. Merge human decisions with updated source data:", file=sys.stderr)
        print("     python scripts/build_mapping_registry.py --merge-existing", file=sys.stderr)
        print("  2. Write to an alternate destination directory:", file=sys.stderr)
        print("     python scripts/build_mapping_registry.py --output-dir <path>", file=sys.stderr)
        print("  3. Re-initialize from scratch with mandatory timestamped backup:", file=sys.stderr)
        print("     python scripts/build_mapping_registry.py --init-clean --create-backup", file=sys.stderr)
        print("=" * 75, file=sys.stderr)
        sys.exit(1)

    if artifacts_exist and args.init_clean and not args.create_backup:
        print("[ERROR] Re-initialization from scratch requires '--create-backup' to protect data.", file=sys.stderr)
        sys.exit(1)

    # 2. Backup on re-init or merge
    existing_records: Optional[Dict[str, Dict[str, Any]]] = None
    if artifacts_exist:
        backup_path = create_backup_archive(out_dir)
        print(f"[BACKUP] Created safety archive at: {backup_path}")

        if args.merge_existing:
            with open(mappings_json_path, "r", encoding="utf-8") as f:
                ex_data = json.load(f)
            existing_records = {m["mapping_id"]: m for m in ex_data.get("mappings", [])}
            human_decisions_count = sum(1 for m in existing_records.values() if is_human_decision_record(m))
            print(f"[MERGE] Loaded {len(existing_records)} existing records ({human_decisions_count} human decisions identified for preservation).")

    print("[1/5] Verifying baseline input datasets and recording hashes...")
    source_hash_kcm = compute_sha256(KCM_COMPETENCIES_PATH)
    source_hash_course = compute_sha256(ACBP_COURSES_PATH)
    source_hash_cand = compute_sha256(CANDIDATE_MAPPINGS_PATH)

    print(f"  - KCM Baseline SHA-256:       {source_hash_kcm}")
    print(f"  - ACBP Courses SHA-256:       {source_hash_course}")
    print(f"  - Candidate Mappings SHA-256: {source_hash_cand}")

    print("[2/5] Loading datasets...")
    courses, kcm_by_id, cand_by_course = load_input_datasets()
    print(f"  Loaded {len(courses)} ACBP courses, {len(kcm_by_id)} KCM competencies.")

    print("[3/5] Building mapping registry records and human-review queue...")
    try:
        mapping_records, review_queue = build_mapping_records(
            courses, kcm_by_id, cand_by_course, source_hash_course, source_hash_kcm, existing_records=existing_records
        )
    except ValueError as exc:
        print(f"\n[CONFLICT ERROR] {exc}", file=sys.stderr)
        print("[SAFETY ABORT] Registry build aborted safely. Existing files were left untouched.", file=sys.stderr)
        sys.exit(1)

    explicit_count = sum(1 for m in mapping_records if m["candidate_kcm_competency_id"] is not None)
    unresolved_count = sum(1 for m in mapping_records if m["candidate_kcm_competency_id"] is None)
    domain_gap_count = sum(1 for m in mapping_records if m["mapping_method"] == "unresolved_domain_gap")
    no_match_count = sum(1 for m in mapping_records if m["mapping_method"] == "unresolved_no_match")
    validated_count = sum(1 for m in mapping_records if m["validation_status"] == "validated")
    rejected_count = sum(1 for m in mapping_records if m["validation_status"] == "rejected")

    print(f"  - Total Courses Evaluated:  {len(mapping_records)}")
    print(f"  - Explicit Candidates:      {explicit_count} (pending: {explicit_count - validated_count}, validated: {validated_count})")
    print(f"  - Rejected Records:         {rejected_count}")
    print(f"  - Total Unresolved Records: {unresolved_count}")
    print(f"    * Domain Gaps:            {domain_gap_count}")
    print(f"    * No Explicit Matches:    {no_match_count}")

    print("[4/5] Serializing mapping registry JSON & CSV...")
    out_dir.mkdir(parents=True, exist_ok=True)
    registry_envelope = {
        "dataset_name": "MoSPI ACBP to Karmayogi Competency Model Mapping Registry",
        "course_source_id": "SRC-MOSPI-ACBP-2026-27",
        "kcm_source_id": "SRC-CBC-KCM-2024",
        "pipeline_version": PIPELINE_VERSION,
        "generation_timestamp": FIXED_GENERATION_TIMESTAMP,
        "total_courses_evaluated": len(mapping_records),
        "mapped_records_count": explicit_count,
        "unresolved_records_count": unresolved_count,
        "mappings": mapping_records,
    }
    with open(mappings_json_path, "w", encoding="utf-8") as f:
        json.dump(registry_envelope, f, indent=2, ensure_ascii=False)
    serialize_mappings_csv(mapping_records, mappings_csv_path)
    print(f"  Saved {mappings_json_path.name} and {mappings_csv_path.name}")

    print("[5/5] Serializing review queue JSON & CSV...")
    queue_envelope = {
        "dataset_name": "MoSPI ACBP to KCM Human Review Queue",
        "pipeline_version": PIPELINE_VERSION,
        "generation_timestamp": FIXED_GENERATION_TIMESTAMP,
        "total_queue_items": len(review_queue),
        "title_reference_candidates_count": explicit_count,
        "unresolved_domain_gaps_count": domain_gap_count,
        "unresolved_no_match_count": no_match_count,
        "queue": review_queue,
    }
    with open(review_queue_json_path, "w", encoding="utf-8") as f:
        json.dump(queue_envelope, f, indent=2, ensure_ascii=False)
    serialize_review_queue_csv(review_queue, review_queue_csv_path)
    print(f"  Saved {review_queue_json_path.name} and {review_queue_csv_path.name}")
    print("\n[SUCCESS] Competency mapping registry and review queue processed safely.")


if __name__ == "__main__":
    main()
