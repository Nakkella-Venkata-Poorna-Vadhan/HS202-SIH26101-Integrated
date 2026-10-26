"""
Persistent store for recorded user learning activities without automated LMS sync claims.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from competency_engine.models import LearningActivityRecord

logger = logging.getLogger(__name__)


class LearningActivityStore:
    """Thread-safe file-backed store for user learning activity records."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            backend_dir = Path(__file__).resolve().parent.parent
            storage_path = backend_dir / "data" / "learners" / "learning_activities.json"
        self.storage_path = storage_path
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_records([])

    def _read_records(self) -> List[Dict[str, Any]]:
        try:
            if not self.storage_path.exists():
                return []
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error reading learning activities: {e}")
            return []

    def _write_records(self, records: List[Dict[str, Any]]) -> None:
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing learning activities: {e}")

    def record_activity(
        self,
        learner_id: str,
        resource_id: str,
        resource_title: str,
        activity_type: str = "enrolled",
        target_competency_id: Optional[str] = None,
        notes: str = "",
    ) -> LearningActivityRecord:
        """Log a deliberate user learning action."""
        labels = {
            "planned": "Planned",
            "enrolled": "Enrolled (learner-reported)",
            "in_progress": "In progress (learner-reported)",
            "completed": "Completed (learner-reported)",
            "reassessment_completed": "Reassessment completed",
            "reference_consulted": "Reference consulted",
        }
        status_label = labels.get(activity_type, "Learner-reported action")
        verification = "diagnostic_assessment_verified" if activity_type == "reassessment_completed" else "self_reported_unverified"

        record = LearningActivityRecord(
            activity_id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
            learner_id=learner_id.upper().strip(),
            resource_id=resource_id.strip(),
            resource_title=resource_title.strip(),
            target_competency_id=target_competency_id.strip() if target_competency_id else None,
            activity_type=activity_type,
            activity_status_label=status_label,
            verification_status=verification,
            timestamp=datetime.now(timezone.utc).isoformat(),
            notes=notes.strip(),
            is_live_sync=False,
        )
        records = self._read_records()
        records.append(record.model_dump())
        self._write_records(records)
        return record

    def get_activities_for_learner(self, learner_id: str) -> List[LearningActivityRecord]:
        """Fetch all recorded learning activities for a specific learner."""
        target_id = learner_id.upper().strip()
        records = self._read_records()
        return [
            LearningActivityRecord(**r)
            for r in records
            if r.get("learner_id", "").upper().strip() == target_id
        ]

    def get_all_activities(self) -> List[LearningActivityRecord]:
        records = self._read_records()
        return [LearningActivityRecord(**r) for r in records]

    def reset(self) -> None:
        self._write_records([])
