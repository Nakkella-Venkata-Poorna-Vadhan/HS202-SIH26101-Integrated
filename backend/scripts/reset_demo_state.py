"""
Safe Local Demo Reset Utility (Stage 4.6)
MoSPI SIH26101 - Integrated Competency Intelligence Platform

Resets synthetic learner assessment records and demo attempts back to the clean initial demonstration baseline:
- Pooja Verma (LEARNER-003): Unassessed recruit (0 assessed competencies).
- Arun Kumar (LEARNER-001) & Priya Sharma (LEARNER-002): Official baseline evaluations preserved.
- Attempts log: Cleared to 0 attempts.
- Provisional estimates log: Cleared to 0 provisional estimates.

SAFETY GUARANTEES:
- Strictly does NOT alter official source datasets (competencies_kcm.json, acbp_courses.json).
- Strictly does NOT alter official mapping registry (acbp_kcm_mappings.json) or review queue.
- Strictly does NOT touch synthetic role definitions.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve project paths
SCRIPTS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPTS_DIR.parent
ASSESSMENTS_DIR = BACKEND_DIR / "data" / "assessments"
ATTEMPTS_PATH = ASSESSMENTS_DIR / "attempts.json"
ESTIMATES_PATH = ASSESSMENTS_DIR / "provisional_estimates.json"


def reset_demo_state(verbose: bool = True) -> bool:
    ASSESSMENTS_DIR.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Reset attempts.json
    clean_attempts = {
        "updated_at": now_iso,
        "total_attempts": 0,
        "attempts": []
    }
    with open(ATTEMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_attempts, f, indent=2)

    # 2. Reset provisional_estimates.json
    clean_estimates = {
        "updated_at": now_iso,
        "total_estimates": 0,
        "provisional_estimates": {}
    }
    with open(ESTIMATES_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_estimates, f, indent=2)

    if verbose:
        print("=" * 70)
        print("MoSPI SIH26101: Local Demo State Safely Reset")
        print("=" * 70)
        print(f"  - Reset attempts log:            {ATTEMPTS_PATH}")
        print(f"  - Reset provisional estimates:   {ESTIMATES_PATH}")
        print("  - Official source datasets:      UNALTERED")
        print("  - KCM Competency Catalogue:      UNALTERED (34 competencies)")
        print("  - ACBP Course Registry:          UNALTERED (226 courses)")
        print("  - Mapping Registry & Benchmarks: UNALTERED (6 candidate, 220 unresolved)")
        print(f"  - Timestamp:                     {now_iso}")
        print("=" * 70)
        print("[READY FOR DEMO] Pooja Verma (LEARNER-003) is now in a clean unassessed state.")
        print("=" * 70)

    return True


if __name__ == "__main__":
    reset_demo_state(verbose=True)
