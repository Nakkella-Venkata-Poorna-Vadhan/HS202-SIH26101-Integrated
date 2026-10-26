"""
Dedicated Persistence Store for Diagnostic Assessment Sessions and Provisional Competency Estimates.
Strictly isolates attempt logs and derived evidence from frozen source datasets.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from competency_engine.config import ASSESSMENTS_DIR, ATTEMPTS_PATH, PROVISIONAL_ESTIMATES_PATH
from competency_engine.models import ProvisionalEstimate

logger = logging.getLogger(__name__)


class AssessmentStore:
    """Safe local JSON persistence for attempts and provisional diagnostic estimates."""

    def __init__(
        self,
        assessments_dir: Path = ASSESSMENTS_DIR,
        attempts_path: Path = ATTEMPTS_PATH,
        estimates_path: Path = PROVISIONAL_ESTIMATES_PATH,
    ):
        self.assessments_dir = assessments_dir
        self.attempts_path = attempts_path
        self.estimates_path = estimates_path

        self._attempts: Dict[str, Dict[str, Any]] = {}
        self._estimates: Dict[str, Dict[str, Any]] = {}  # key: f"{learner_id}:{competency_id}"

        self._ensure_storage()
        self.load()

    def _ensure_storage(self) -> None:
        self.assessments_dir.mkdir(parents=True, exist_ok=True)
        if not self.attempts_path.exists():
            self._write_json(self.attempts_path, {"attempts": []})
        if not self.estimates_path.exists():
            self._write_json(self.estimates_path, {"provisional_estimates": {}})

    def load(self) -> None:
        """Load stored attempts and estimates from disk."""
        try:
            if self.attempts_path.exists():
                with open(self.attempts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for att in data.get("attempts", []):
                        self._attempts[att["attempt_id"]] = att

            if self.estimates_path.exists():
                with open(self.estimates_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._estimates = data.get("provisional_estimates", {})
        except Exception as e:
            logger.error("Error reading assessment store: %s", e)

    def _write_json(self, path: Path, data: Any) -> None:
        """Atomic safe write to prevent corruption."""
        temp_file = path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(path)

    def save_attempts(self) -> None:
        self._write_json(
            self.attempts_path,
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "total_attempts": len(self._attempts),
                "attempts": list(self._attempts.values()),
            },
        )

    def save_estimates(self) -> None:
        self._write_json(
            self.estimates_path,
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "total_estimates": len(self._estimates),
                "provisional_estimates": self._estimates,
            },
        )

    def create_attempt(
        self,
        learner_id: str,
        competency_id: str,
        competency_name: str,
        question_ids: List[str],
    ) -> str:
        """Create a new pending assessment attempt session."""
        attempt_id = f"ATT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        attempt_record = {
            "attempt_id": attempt_id,
            "learner_id": learner_id,
            "competency_id": competency_id,
            "competency_name": competency_name,
            "question_ids": question_ids,
            "status": "in_progress",
            "answers": {},
            "score": None,
            "percentage": None,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }
        self._attempts[attempt_id] = attempt_record
        self.save_attempts()
        return attempt_id

    def get_attempt(self, attempt_id: str) -> Optional[Dict[str, Any]]:
        """Look up an attempt by ID."""
        return self._attempts.get(attempt_id)

    def record_completed_attempt(
        self,
        attempt_id: str,
        answers: Dict[str, str],
        score: int,
        percentage: int,
        provisional_estimate: ProvisionalEstimate,
        feedback_summary: List[Dict[str, Any]],
    ) -> None:
        """Record completed attempt results and update provisional learner estimate."""
        if attempt_id in self._attempts:
            att = self._attempts[attempt_id]
            att["status"] = "completed"
            att["answers"] = answers
            att["score"] = score
            att["percentage"] = percentage
            att["provisional_estimate"] = provisional_estimate.model_dump()
            att["feedback"] = feedback_summary
            att["completed_at"] = datetime.now(timezone.utc).isoformat()
            self.save_attempts()

        # Update provisional estimate for (learner_id, competency_id)
        key = f"{provisional_estimate.competency_id}"
        learner_id = self._attempts[attempt_id]["learner_id"] if attempt_id in self._attempts else "UNKNOWN"
        store_key = f"{learner_id}:{key}"

        self._estimates[store_key] = {
            "learner_id": learner_id,
            "competency_id": provisional_estimate.competency_id,
            "competency_name": provisional_estimate.competency_name,
            "estimated_level": provisional_estimate.estimated_level,
            "previous_level": provisional_estimate.previous_level,
            "confidence_score": provisional_estimate.confidence_score,
            "evidence_count": provisional_estimate.evidence_count,
            "sufficiency_status": provisional_estimate.sufficiency_status,
            "diagnostic_summary": provisional_estimate.diagnostic_summary,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_attempt_id": attempt_id,
        }
        self.save_estimates()

    def get_learner_estimates(self, learner_id: str) -> Dict[str, Dict[str, Any]]:
        """Retrieve all provisional estimates for a given learner."""
        prefix = f"{learner_id}:"
        result = {}
        for k, v in self._estimates.items():
            if k.startswith(prefix):
                comp_id = k.split(":", 1)[1]
                result[comp_id] = v
        return result

    def get_all_provisional_estimates(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all active provisional diagnostic estimates across all learners."""
        return dict(self._estimates)

    def list_attempts(self) -> List[Dict[str, Any]]:
        """Retrieve all diagnostic assessment attempts."""
        return list(self._attempts.values())

    def get_learner_history(self, learner_id: str) -> List[Dict[str, Any]]:
        """Retrieve chronological assessment history for a learner."""
        history = [
            att for att in self._attempts.values()
            if att.get("learner_id") == learner_id and att.get("status") == "completed"
        ]
        return sorted(history, key=lambda x: x.get("completed_at", ""), reverse=True)

    def reset_demo_state(self) -> Dict[str, int]:
        """
        Safely reset local demo attempts and provisional estimates to clean initial state.
        Never touches official source datasets, KCM catalogue, ACBP records, or mapping registries.
        """
        cleared_attempts = len(self._attempts)
        cleared_estimates = len(self._estimates)
        self._attempts = {}
        self._estimates = {}
        self.save_attempts()
        self.save_estimates()
        return {
            "cleared_attempts": cleared_attempts,
            "cleared_estimates": cleared_estimates,
        }
