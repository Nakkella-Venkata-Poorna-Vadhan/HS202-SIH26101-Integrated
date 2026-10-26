"""
Repository Layer for loading, validating, and querying competency, course, role, and learner datasets.
Preserves official datasets and strictly isolates synthetic profiles.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from competency_engine.config import (
    ACBP_COURSES_PATH,
    ACBP_MAPPINGS_PATH,
    KCM_COMPETENCIES_PATH,
    PROVISIONAL_ESTIMATES_PATH,
    SYNTHETIC_LEARNERS_PATH,
    SYNTHETIC_ROLES_PATH,
)
from competency_engine.models import (
    Competency,
    Course,
    CourseMapping,
    Learner,
    Role,
)
from competency_engine.seed import seed_synthetic_data

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Raised when repository loading or data validation fails."""
    pass


class CompetencyRepository:
    """In-memory loaded and validated repository for the SIH26101 prototype."""

    def __init__(
        self,
        kcm_path: Path = KCM_COMPETENCIES_PATH,
        acbp_courses_path: Path = ACBP_COURSES_PATH,
        acbp_mappings_path: Path = ACBP_MAPPINGS_PATH,
        roles_path: Path = SYNTHETIC_ROLES_PATH,
        learners_path: Path = SYNTHETIC_LEARNERS_PATH,
        estimates_path: Path = PROVISIONAL_ESTIMATES_PATH,
        auto_seed_synthetic: bool = True,
    ):
        self.kcm_path = kcm_path
        self.acbp_courses_path = acbp_courses_path
        self.acbp_mappings_path = acbp_mappings_path
        self.roles_path = roles_path
        self.learners_path = learners_path
        self.estimates_path = estimates_path
        self.auto_seed_synthetic = auto_seed_synthetic

        self._competencies: Dict[str, Competency] = {}
        self._courses: Dict[str, Course] = {}
        self._mappings: Dict[str, CourseMapping] = {}
        self._mappings_by_course: Dict[str, List[CourseMapping]] = {}
        self._mappings_by_competency: Dict[str, List[CourseMapping]] = {}
        self._roles: Dict[str, Role] = {}
        self._learners: Dict[str, Learner] = {}

        self.load_all()

    def load_all(self) -> None:
        """Load and validate all official and synthetic data files."""
        self._load_competencies()
        self._load_courses()
        self._load_mappings()

        if self.auto_seed_synthetic:
            seed_synthetic_data(force=False)

        self._load_roles()
        self._load_learners()
        self._sync_persisted_estimates()

    def _load_competencies(self) -> None:
        if not self.kcm_path.exists():
            raise RepositoryError(f"Competencies file missing at: {self.kcm_path}")
        with open(self.kcm_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise RepositoryError("Expected list of competency records in competencies_kcm.json")

        self._competencies.clear()
        for idx, item in enumerate(raw_data):
            try:
                comp = Competency(**item)
                self._competencies[comp.competency_id] = comp
            except Exception as e:
                raise RepositoryError(f"Invalid competency record at index {idx}: {e}") from e

    def _load_courses(self) -> None:
        if not self.acbp_courses_path.exists():
            raise RepositoryError(f"ACBP courses file missing at: {self.acbp_courses_path}")
        with open(self.acbp_courses_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        records = raw_data.get("records", [])
        if not isinstance(records, list):
            raise RepositoryError("Expected 'records' list in acbp_courses.json")

        self._courses.clear()
        for idx, item in enumerate(records):
            try:
                course = Course(**item)
                self._courses[course.record_id] = course
            except Exception as e:
                raise RepositoryError(f"Invalid course record at index {idx}: {e}") from e

    def _load_mappings(self) -> None:
        if not self.acbp_mappings_path.exists():
            raise RepositoryError(f"ACBP mappings file missing at: {self.acbp_mappings_path}")
        with open(self.acbp_mappings_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        mappings_list = raw_data.get("mappings", [])
        if not isinstance(mappings_list, list):
            raise RepositoryError("Expected 'mappings' list in acbp_kcm_mappings.json")

        self._mappings.clear()
        self._mappings_by_course.clear()
        self._mappings_by_competency.clear()

        for idx, item in enumerate(mappings_list):
            try:
                mapping = CourseMapping(**item)
                self._mappings[mapping.mapping_id] = mapping

                # Index by course ID
                self._mappings_by_course.setdefault(mapping.course_record_id, []).append(mapping)

                # Index by candidate KCM ID if present
                if mapping.candidate_kcm_competency_id:
                    self._mappings_by_competency.setdefault(
                        mapping.candidate_kcm_competency_id, []
                    ).append(mapping)
            except Exception as e:
                raise RepositoryError(f"Invalid mapping record at index {idx}: {e}") from e

    def _load_roles(self) -> None:
        if not self.roles_path.exists():
            raise RepositoryError(f"Synthetic roles file missing at: {self.roles_path}")
        with open(self.roles_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        roles_list = raw_data.get("roles", [])
        self._roles.clear()
        for idx, item in enumerate(roles_list):
            try:
                role = Role(**item)
                # Verify referential integrity of required competencies
                for req in role.required_competencies:
                    if req.competency_id not in self._competencies:
                        raise RepositoryError(
                            f"Role '{role.role_id}' references unknown competency '{req.competency_id}'"
                        )
                self._roles[role.role_id] = role
            except Exception as e:
                raise RepositoryError(f"Invalid role record at index {idx}: {e}") from e

    def _load_learners(self) -> None:
        if not self.learners_path.exists():
            raise RepositoryError(f"Synthetic learners file missing at: {self.learners_path}")
        with open(self.learners_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        learners_list = raw_data.get("learners", [])
        self._learners.clear()
        for idx, item in enumerate(learners_list):
            try:
                learner = Learner(**item)
                # Verify referential integrity of assigned role
                if learner.role_id not in self._roles:
                    raise RepositoryError(
                        f"Learner '{learner.learner_id}' references unknown role '{learner.role_id}'"
                    )
                self._learners[learner.learner_id] = learner
            except Exception as e:
                raise RepositoryError(f"Invalid learner record at index {idx}: {e}") from e

    def _sync_persisted_estimates(self) -> None:
        """
        Merge persisted provisional assessment estimates into loaded learners without modifying baseline files.
        Maintains strict isolation: official datasets and synthetic baseline seed files remain untouched.
        Preserves baseline workplace evidence: existing non-provisional assessments are never overwritten.
        """
        if not self.estimates_path or not self.estimates_path.exists():
            return

        from competency_engine.models import CompetencyAssessment

        try:
            with open(self.estimates_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            estimates = data.get("provisional_estimates", {})
            for key, est in estimates.items():
                learner_id = est.get("learner_id")
                comp_id = est.get("competency_id")
                level = est.get("estimated_level")
                conf = est.get("confidence_score", 0.0)
                status = est.get("sufficiency_status", "insufficient_evidence")
                attempt_id = est.get("last_attempt_id", "persisted_attempt")
                updated_at = est.get("updated_at")

                # Insufficient evidence must remain unassessed / provisional
                if status != "sufficient" or level is None:
                    continue

                if not learner_id or not comp_id:
                    continue

                learner = self._learners.get(learner_id)
                if not learner:
                    continue

                evidence_source = f"Diagnostic Assessment Attempt {attempt_id} (provisional_quiz_estimate)"

                found = False
                for existing in learner.assessed_competencies:
                    if existing.competency_id == comp_id:
                        found = True
                        # Do not overwrite baseline workplace evidence!
                        if existing.assessment_status == "unassessed" or existing.assessment_method == "diagnostic_quiz_assessment":
                            existing.estimated_level = level
                            existing.assessment_status = "assessed"
                            existing.confidence = conf
                            existing.assessment_method = "diagnostic_quiz_assessment"
                            existing.is_provisional = True
                            if evidence_source not in existing.evidence_sources:
                                existing.evidence_sources.append(evidence_source)
                            existing.last_assessed_date = updated_at
                        else:
                            # Baseline evidence exists (e.g. supervisor_review).
                            # Keep baseline level and status intact, append quiz evidence.
                            if evidence_source not in existing.evidence_sources:
                                existing.evidence_sources.append(evidence_source)
                        break

                if not found:
                    new_assessment = CompetencyAssessment(
                        competency_id=comp_id,
                        estimated_level=level,
                        assessment_status="assessed",
                        confidence=conf,
                        evidence_sources=[evidence_source],
                        last_assessed_date=updated_at,
                        assessment_method="diagnostic_quiz_assessment",
                        is_provisional=True,
                    )
                    learner.assessed_competencies.append(new_assessment)
        except Exception as e:
            logger.error("Error syncing persisted estimates into repository: %s", e)

    # =========================================================================
    # Queries: Competencies
    # =========================================================================

    def get_competency(self, competency_id: str) -> Optional[Competency]:
        """Fetch a KCM competency by ID."""
        return self._competencies.get(competency_id)

    def list_competencies(
        self,
        competency_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Competency]:
        """List competencies with optional type filtering and search."""
        results = list(self._competencies.values())
        if competency_type:
            target_type = competency_type.lower()
            results = [c for c in results if c.competency_type.lower() == target_type]
        if search:
            query = search.lower()
            results = [
                c for c in results
                if query in c.competency_name.lower() or query in c.description.lower()
            ]
        return sorted(results, key=lambda x: x.competency_id)

    # =========================================================================
    # Queries: Courses
    # =========================================================================

    def get_course(self, course_id: str) -> Optional[Course]:
        """Fetch an ACBP course by ID."""
        return self._courses.get(course_id)

    def list_courses(
        self,
        cadre: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Course]:
        """List ACBP courses with optional cadre, category, and search filters."""
        results = list(self._courses.values())
        if cadre:
            cadre_lower = cadre.lower()
            results = [c for c in results if cadre_lower in c.cadre_role.lower()]
        if category:
            cat_lower = category.lower()
            results = [c for c in results if c.competency_category.lower() == cat_lower]
        if search:
            query = search.lower()
            results = [
                c for c in results
                if query in c.course_name.lower() or query in c.course_creator.lower()
            ]
        return sorted(results, key=lambda x: x.record_id)

    # =========================================================================
    # Queries: Mappings
    # =========================================================================

    def get_mappings_for_course(self, course_id: str) -> List[CourseMapping]:
        """Get all mappings referencing an ACBP course ID."""
        return self._mappings_by_course.get(course_id, [])

    def get_mappings_for_competency(self, competency_id: str) -> List[CourseMapping]:
        """Get all candidate mappings pointing to a KCM competency ID."""
        return self._mappings_by_competency.get(competency_id, [])

    # =========================================================================
    # Queries: Roles & Learners
    # =========================================================================

    def get_role(self, role_id: str) -> Optional[Role]:
        """Fetch a role by ID."""
        return self._roles.get(role_id)

    def list_roles(self) -> List[Role]:
        """List all available roles."""
        return sorted(list(self._roles.values()), key=lambda x: x.role_id)

    def get_learner(self, learner_id: str) -> Optional[Learner]:
        """Fetch a learner by ID."""
        return self._learners.get(learner_id)

    def list_learners(self) -> List[Learner]:
        """List all synthetic demonstration learners."""
        return sorted(list(self._learners.values()), key=lambda x: x.learner_id)

    def update_learner_provisional_assessment(
        self,
        learner_id: str,
        competency_id: str,
        estimated_level: int,
        confidence: float,
        evidence_source: str,
    ) -> bool:
        """Update or record a provisional competency assessment for a learner in memory."""
        from datetime import datetime, timezone
        from competency_engine.models import CompetencyAssessment

        learner = self.get_learner(learner_id)
        if not learner:
            return False

        for assessment in learner.assessed_competencies:
            if assessment.competency_id == competency_id:
                # Do not overwrite baseline workplace evidence if present and non-provisional!
                if assessment.assessment_status == "unassessed" or assessment.assessment_method == "diagnostic_quiz_assessment":
                    assessment.estimated_level = estimated_level
                    assessment.assessment_status = "assessed"
                    assessment.confidence = confidence
                    assessment.assessment_method = "diagnostic_quiz_assessment"
                    assessment.is_provisional = True
                    if evidence_source not in assessment.evidence_sources:
                        assessment.evidence_sources.append(evidence_source)
                    assessment.last_assessed_date = datetime.now(timezone.utc).isoformat()
                else:
                    # Baseline workplace assessment preserved! Only append quiz evidence.
                    if evidence_source not in assessment.evidence_sources:
                        assessment.evidence_sources.append(evidence_source)
                return True

        new_assessment = CompetencyAssessment(
            competency_id=competency_id,
            estimated_level=estimated_level,
            assessment_status="assessed",
            assessment_method="diagnostic_quiz_assessment",
            is_provisional=True,
            confidence=confidence,
            evidence_sources=[evidence_source],
            last_assessed_date=datetime.now(timezone.utc).isoformat(),
        )
        learner.assessed_competencies.append(new_assessment)
        return True

    # =========================================================================
    # Stats & Metrics
    # =========================================================================

    def get_stats(self) -> Dict[str, int]:
        """Return dataset counts."""
        candidate_count = sum(len(v) for v in self._mappings_by_competency.values())
        return {
            "total_competencies": len(self._competencies),
            "total_courses": len(self._courses),
            "total_mappings": len(self._mappings),
            "candidate_mappings": candidate_count,
            "unresolved_mappings": len(self._mappings) - candidate_count,
            "total_roles": len(self._roles),
            "total_learners": len(self._learners),
        }
