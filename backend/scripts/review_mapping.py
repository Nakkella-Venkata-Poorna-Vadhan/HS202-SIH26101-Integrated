#!/usr/bin/env python3
"""
scripts/review_mapping.py — Safe Human Review CLI Workflow

Provides a safe, auditable command-line interface for human reviewers to inspect,
curate, validate, reject, or mark unresolved competency mappings in accordance with
the Stage 3.1 status transition state machine.

Governance Constraints:
1. Invalid state transitions fail immediately without modifying the registry.
2. Rejected records are permanently retained with rejection rationale (never deleted).
3. Validated mappings strictly require reviewer identity, institutional role, and timestamp.
4. Input baseline datasets and the original 6-candidate artifact are never modified.
5. In prototype mode, unauthenticated CLI reviewer credentials are explicitly disclaimed.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

ACBP_COURSES_PATH = DATA_PROCESSED / "acbp_courses.json"
KCM_COMPETENCIES_PATH = DATA_PROCESSED / "competencies_kcm.json"
MAPPINGS_JSON_PATH = DATA_PROCESSED / "acbp_kcm_mappings.json"
MAPPINGS_CSV_PATH = DATA_PROCESSED / "acbp_kcm_mappings.csv"
REVIEW_QUEUE_JSON_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.json"
REVIEW_QUEUE_CSV_PATH = DATA_PROCESSED / "acbp_kcm_review_queue.csv"

# Reusable KCM page lookup
KCM_PAGE_LOOKUP: Dict[str, tuple[int, int]] = {
    "KCM-BEH-06": (49, 50),
    "KCM-FUNC-05": (74, 75),
    "KCM-BEH-10": (57, 58),
    "KCM-FUNC-11": (84, 85),
    "KCM-FUNC-13": (90, 91),
    "KCM-FUNC-14": (92, 93),
    "KCM-FUNC-15": (94, 95),
    "KCM-FUNC-18": (100, 101),
    "KCM-FUNC-19": (98, 99),
    "KCM-FUNC-20": (104, 105),
    "KCM-FUNC-21": (106, 107),
    "KCM-BEH-13": (63, 64),
}

# State machine allowed transitions: current_status -> {action: (target_mapping_type, target_validation_status)}
ALLOWED_TRANSITIONS: Dict[str, Dict[str, Tuple[str, str]]] = {
    "unresolved": {
        "promote_to_curated": ("curated_candidate", "pending_review"),
    },
    "pending_review": {
        "promote_to_curated": ("curated_candidate", "pending_review"),
        "reject": ("exact_title_reference", "rejected"),
        "validate": ("validated", "validated"),
        "mark_unresolved": ("unresolved", "unresolved"),
    },
}


def print_prototype_disclaimer() -> None:
    print("-" * 75)
    print("[PROTOTYPE AUDIT NOTICE]")
    print("Command-line reviewer credentials are simulated for prototype verification")
    print("and lack cryptographically verifiable institutional SSO/OAuth federation.")
    print("Formal production validation requires authenticated MoSPI/NSSTA/CBC identity assertion.")
    print("-" * 75)


def load_registry() -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Load current mapping registry, courses, and KCM reference."""
    if not MAPPINGS_JSON_PATH.exists():
        raise FileNotFoundError(f"Mapping registry not found: {MAPPINGS_JSON_PATH}")

    with open(MAPPINGS_JSON_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        kcm_list = json.load(f)
    kcm_by_id = {c["competency_id"]: c for c in kcm_list}

    return registry_data, registry_data.get("mappings", []), kcm_by_id


def save_registry_and_csv(registry_data: Dict[str, Any], mappings: List[Dict[str, Any]]) -> None:
    """Save updated registry JSON and regenerate CSV with parity."""
    # Update envelope counts
    explicit = sum(1 for m in mappings if m.get("candidate_kcm_competency_id") is not None)
    unresolved = sum(1 for m in mappings if m.get("candidate_kcm_competency_id") is None)
    registry_data["mapped_records_count"] = explicit
    registry_data["unresolved_records_count"] = unresolved
    registry_data["mappings"] = mappings

    with open(MAPPINGS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)

    # Save CSV
    if mappings:
        fieldnames = list(mappings[0].keys())
        with open(MAPPINGS_CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for r in mappings:
                row_dict = {k: ("" if v is None else v) for k, v in r.items()}
                writer.writerow(row_dict)


def sync_review_queue(mappings: List[Dict[str, Any]]) -> None:
    """Synchronize the review queue artifact to reflect updated mapping states."""
    if not REVIEW_QUEUE_JSON_PATH.exists():
        return

    with open(REVIEW_QUEUE_JSON_PATH, "r", encoding="utf-8") as f:
        queue_envelope = json.load(f)

    map_by_id = {m["mapping_id"]: m for m in mappings}
    queue = queue_envelope.get("queue", [])

    for item in queue:
        mid = item["mapping_id"]
        if mid in map_by_id:
            m = map_by_id[mid]
            item["candidate_kcm_competency_id"] = m["candidate_kcm_competency_id"]
            item["candidate_kcm_competency_name"] = m["candidate_kcm_competency_name"]
            item["mapping_type"] = m["mapping_type"]
            item["validation_status"] = m["validation_status"]
            item["evidence_or_rationale"] = m["evidence_or_rationale"]
            if m["validation_status"] == "validated":
                item["queue_category"] = "validated"
                item["priority"] = "resolved"
                item["recommended_action"] = f"Verified by {m.get('reviewer_id')} ({m.get('reviewer_role')})"
            elif m["validation_status"] == "rejected":
                item["queue_category"] = "rejected"
                item["priority"] = "resolved"
                item["recommended_action"] = f"Rejected by reviewer. Rationale: {m.get('evidence_or_rationale')}"

    queue_envelope["queue"] = queue
    with open(REVIEW_QUEUE_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(queue_envelope, f, indent=2, ensure_ascii=False)

    if queue:
        fieldnames = list(queue[0].keys())
        with open(REVIEW_QUEUE_CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for r in queue:
                row_dict = {k: ("" if v is None else v) for k, v in r.items()}
                writer.writerow(row_dict)


MAPPING_ID_RE = re.compile(r"^MAP-ACBP-KCM-[0-9]{3,}$")
COURSE_ID_RE = re.compile(r"^ACBP-CRS-[0-9]{3}$")


def execute_review(
    target_id: str,
    action: str,
    rationale: str,
    reviewer_id: Optional[str] = None,
    reviewer_role: Optional[str] = None,
    kcm_id: Optional[str] = None,
    reviewer_notes: Optional[str] = None,
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """Execute a safe state transition on a mapping record using an unambiguous mapping_id."""
    if not target_id or not str(target_id).strip():
        return False, "Identifier error: Mapping identifier cannot be empty."

    target_id = target_id.strip()

    # Reject course IDs with clear explanatory error (LIM-01)
    if COURSE_ID_RE.match(target_id):
        return False, (
            f"Ambiguous identifier: '{target_id}' is a course_record_id, not a mapping_id. "
            f"Review operations strictly require a unique mapping_id (e.g., 'MAP-ACBP-KCM-017') "
            f"because courses may have multiple candidate mappings in future stages."
        )

    # Validate mapping ID format
    if not MAPPING_ID_RE.match(target_id):
        return False, (
            f"Invalid identifier format: '{target_id}'. Mapping identifiers must match "
            f"pattern '^MAP-ACBP-KCM-[0-9]{{3,}}$' (e.g., 'MAP-ACBP-KCM-017')."
        )

    registry_data, mappings, kcm_by_id = load_registry()

    # Strictly search by mapping_id
    matches = [m for m in mappings if m.get("mapping_id") == target_id]
    if len(matches) == 0:
        return False, f"Record not found: No mapping record exists with mapping_id '{target_id}'."
    if len(matches) > 1:
        return False, f"Integrity error: Multiple mapping records ({len(matches)}) found with mapping_id '{target_id}'. Mapping IDs must be strictly unique."

    rec = matches[0]
    mid = rec["mapping_id"]
    cid = rec["course_record_id"]
    curr_status = rec["validation_status"]
    curr_type = rec["mapping_type"]

    # Check state machine permission
    status_transitions = ALLOWED_TRANSITIONS.get(curr_status, {})
    if action not in status_transitions:
        return False, f"Illegal transition: Cannot perform action '{action}' on record in status '{curr_status}' (mapping_type '{curr_type}')"

    target_type, target_status = status_transitions[action]

    # Specific action validation rules
    now_utc = datetime.now(timezone.utc).isoformat()

    if action == "validate":
        if curr_type not in ("curated_candidate", "exact_title_reference"):
            return False, f"Cannot validate mapping with type '{curr_type}'. Only 'curated_candidate' or 'exact_title_reference' can be validated."
        if not reviewer_id or not reviewer_id.strip():
            return False, "Validation rejected: '--reviewer-id' is mandatory to record approval provenance."
        if not reviewer_role or not reviewer_role.strip():
            return False, "Validation rejected: '--reviewer-role' is mandatory (e.g. 'MoSPI Nodal Officer', 'NSSTA Faculty')."
        if not rationale or len(rationale.strip()) < 20:
            return False, "Validation rejected: '--rationale' must provide at least 20 characters of auditable curricular evidence."

        rec["mapping_type"] = "validated"
        rec["validation_status"] = "validated"
        rec["reviewer_id"] = reviewer_id.strip()
        rec["reviewer_role"] = reviewer_role.strip()
        rec["reviewed_at"] = now_utc
        rec["evidence_or_rationale"] = rationale.strip()
        if reviewer_notes:
            rec["reviewer_notes"] = reviewer_notes.strip()

    elif action == "reject":
        if not rationale or len(rationale.strip()) < 20:
            return False, "Rejection rejected: '--rationale' must provide at least 20 characters explaining why the mapping was rejected."
        rec["validation_status"] = "rejected"
        rec["evidence_or_rationale"] = f"REJECTED: {rationale.strip()}"
        if reviewer_id:
            rec["reviewer_id"] = reviewer_id.strip()
        if reviewer_role:
            rec["reviewer_role"] = reviewer_role.strip()
        rec["reviewed_at"] = now_utc
        if reviewer_notes:
            rec["reviewer_notes"] = reviewer_notes.strip()

    elif action == "promote_to_curated":
        if not kcm_id and not rec.get("candidate_kcm_competency_id"):
            return False, "Cannot promote to curated candidate without specifying '--kcm-id'"
        target_kcm = kcm_id.strip() if kcm_id else rec["candidate_kcm_competency_id"]
        if target_kcm not in kcm_by_id:
            return False, f"Invalid KCM competency ID '{target_kcm}'. Not found in competencies_kcm.json."
        if rec.get("acbp_competency_category") == "Domain":
            return False, f"Cannot map Domain course '{cid}' to KCM competency '{target_kcm}'. KCM contains zero Domain competencies."

        k_rec = kcm_by_id[target_kcm]
        p_def, p_sub = KCM_PAGE_LOOKUP.get(target_kcm, (None, None))
        if not p_def:
            p_def = k_rec["source_page"][0] if isinstance(k_rec["source_page"], list) else k_rec["source_page"]
            p_sub = k_rec["source_page"][1] if isinstance(k_rec["source_page"], list) and len(k_rec["source_page"]) > 1 else p_def

        rec["candidate_kcm_competency_id"] = target_kcm
        rec["candidate_kcm_competency_name"] = k_rec["competency_name"]
        rec["candidate_kcm_competency_type"] = k_rec["competency_type"]
        rec["mapping_type"] = "curated_candidate"
        rec["mapping_method"] = "expert_curricular_review"
        rec["validation_status"] = "pending_review"
        rec["kcm_source_id"] = "SRC-CBC-KCM-2024"
        rec["kcm_source_page_def"] = p_def
        rec["kcm_source_page_sub"] = p_sub
        rec["evidence_or_rationale"] = rationale.strip()
        if reviewer_id:
            rec["reviewer_id"] = reviewer_id.strip()
        if reviewer_role:
            rec["reviewer_role"] = reviewer_role.strip()
        rec["reviewed_at"] = now_utc
        if reviewer_notes:
            rec["reviewer_notes"] = reviewer_notes.strip()

    elif action == "mark_unresolved":
        rec["candidate_kcm_competency_id"] = None
        rec["candidate_kcm_competency_name"] = None
        rec["candidate_kcm_competency_type"] = None
        rec["candidate_kcm_subtheme"] = None
        rec["kcm_source_id"] = None
        rec["kcm_source_page_def"] = None
        rec["kcm_source_page_sub"] = None
        rec["mapping_type"] = "unresolved"
        rec["mapping_method"] = "unresolved_no_match" if rec["acbp_competency_category"] != "Domain" else "unresolved_domain_gap"
        rec["validation_status"] = "unresolved"
        rec["evidence_or_rationale"] = rationale.strip()
        rec["reviewed_at"] = now_utc
        if reviewer_id:
            rec["reviewer_id"] = reviewer_id.strip()
        if reviewer_role:
            rec["reviewer_role"] = reviewer_role.strip()
        if reviewer_notes:
            rec["reviewer_notes"] = reviewer_notes.strip()

    if dry_run:
        return True, f"[DRY-RUN] Record {mid} ({cid}) successfully evaluated for action '{action}' -> {target_status} (no files changed)."

    # Save modifications
    save_registry_and_csv(registry_data, mappings)
    sync_review_queue(mappings)

    return True, f"[SUCCESS] Record {mid} ({cid}) transitioned to mapping_type='{rec['mapping_type']}', status='{rec['validation_status']}'."


def main() -> None:
    parser = argparse.ArgumentParser(description="MoSPI SIH26101: Competency Mapping Safe Review CLI")
    parser.add_argument(
        "--mapping-id",
        "--id",
        dest="mapping_id",
        required=True,
        help="Unique mapping identifier (e.g. MAP-ACBP-KCM-017). Course IDs are strictly prohibited.",
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["validate", "reject", "promote_to_curated", "mark_unresolved"],
        help="Action to perform on candidate mapping",
    )
    parser.add_argument("--rationale", required=True, help="Auditable evidence text or review critique")
    parser.add_argument("--kcm-id", help="Target KCM competency ID (e.g. KCM-BEH-10)")
    parser.add_argument("--reviewer-id", help="Reviewer username or ID")
    parser.add_argument("--reviewer-role", help="Reviewer official capacity (e.g. MoSPI Nodal Officer, NSSTA Faculty)")
    parser.add_argument("--notes", help="Additional reviewer notes or caveats")
    parser.add_argument("--dry-run", action="store_true", help="Simulate transition without writing to disk")

    args = parser.parse_args()

    print_prototype_disclaimer()

    success, msg = execute_review(
        target_id=args.mapping_id,
        action=args.action,
        rationale=args.rationale,
        reviewer_id=args.reviewer_id,
        reviewer_role=args.reviewer_role,
        kcm_id=args.kcm_id,
        reviewer_notes=args.notes,
        dry_run=args.dry_run,
    )

    if success:
        print(msg)
        sys.exit(0)
    else:
        print(f"[ERROR] {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
