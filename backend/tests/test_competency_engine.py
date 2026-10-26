"""
Automated Test Suite for the Competency Intelligence Engine (Stage 4.1).
Covers domain models, gap calculations, boundary conditions, recommendations, provenance, and API routes.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from competency_engine.api import app
from competency_engine.config import (
    DEFAULT_MAX_LEVEL,
    DEFAULT_MIN_LEVEL,
    LEVEL_SCALE_DESCRIPTION,
)
from competency_engine.models import (
    Competency,
    CompetencyAssessment,
    Course,
    CourseMapping,
    Learner,
    Role,
    RoleRequirement,
)
from competency_engine.repository import CompetencyRepository, RepositoryError
from competency_engine.services import RecommendationEngine, SkillGapEngine


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def repository() -> CompetencyRepository:
    """Pre-loaded production CompetencyRepository fixture."""
    return CompetencyRepository()


@pytest.fixture
def gap_engine() -> SkillGapEngine:
    """SkillGapEngine fixture."""
    return SkillGapEngine()


@pytest.fixture
def rec_engine(repository: CompetencyRepository) -> RecommendationEngine:
    """RecommendationEngine fixture."""
    return RecommendationEngine(repository)


# ============================================================================
# 1. Dataset Loading, Integrity, and Schema Validation
# ============================================================================

def test_repository_loads_official_datasets(repository: CompetencyRepository):
    """Confirm official KCM competencies and ACBP courses are loaded accurately."""
    stats = repository.get_stats()
    assert stats["total_competencies"] == 34
    assert stats["total_courses"] == 226
    assert stats["total_mappings"] == 226
    assert stats["total_roles"] >= 5
    assert stats["total_learners"] >= 4

    # Verify a known functional competency
    analytics = repository.get_competency("KCM-FUNC-11")
    assert analytics is not None
    assert analytics.competency_name == "Data Analytics"
    assert analytics.competency_type == "functional"
    assert analytics.provenance == "official_public"

    # Verify a known behavioural competency
    collab = repository.get_competency("KCM-BEH-06")
    assert collab is not None
    assert collab.competency_name == "Collaboration"
    assert collab.competency_type == "behavioural"


def test_repository_handles_invalid_competency_file():
    """Verify repository raises RepositoryError on corrupted or invalid competency JSON."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(json.dumps({"unexpected": "structure"}))
        temp_path = Path(tf.name)

    with pytest.raises(RepositoryError, match="Expected list of competency records"):
        CompetencyRepository(kcm_path=temp_path)

    temp_path.unlink()


def test_repository_handles_missing_file():
    """Verify repository raises RepositoryError on missing file paths."""
    missing_path = Path("non_existent_file_path.json")
    with pytest.raises(RepositoryError, match="missing at"):
        CompetencyRepository(kcm_path=missing_path)


# ============================================================================
# 2. Unknown IDs and Error Handling
# ============================================================================

def test_unknown_competency_id(repository: CompetencyRepository, client: TestClient):
    """Test lookup of non-existent competency ID in repo and API."""
    assert repository.get_competency("KCM-FAKE-999") is None

    res = client.get("/api/competencies/KCM-FAKE-999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_unknown_course_id(repository: CompetencyRepository, client: TestClient):
    """Test lookup of non-existent course ID in repo and API."""
    assert repository.get_course("ACBP-CRS-999") is None

    res = client.get("/api/courses/ACBP-CRS-999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_unknown_role_id(repository: CompetencyRepository, client: TestClient):
    """Test lookup of non-existent role ID in repo and API."""
    assert repository.get_role("ROLE-NONEXISTENT") is None

    res = client.get("/api/roles/ROLE-NONEXISTENT")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_unknown_learner_id(repository: CompetencyRepository, client: TestClient):
    """Test lookup of non-existent learner ID in repo and API."""
    assert repository.get_learner("LEARNER-999") is None

    res = client.get("/api/learners/LEARNER-999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

    res = client.get("/api/learners/LEARNER-999/skill-gaps")
    assert res.status_code == 404

    res = client.get("/api/learners/LEARNER-999/recommendations")
    assert res.status_code == 404


# ============================================================================
# 3. Gap Calculations & Boundary Conditions
# ============================================================================

def test_gap_calculation_positive_gap(gap_engine: SkillGapEngine, repository: CompetencyRepository):
    """Test standard skill gap where Estimated < Required."""
    role = Role(
        role_id="ROLE-TEST-1",
        role_name="Test Role",
        cadre_role="Test Cadre",
        description="Testing",
        required_competencies=[
            RoleRequirement(
                competency_id="KCM-FUNC-11",
                competency_name="Data Analytics",
                required_level=4,
                priority="critical",
                rationale="Test",
            )
        ],
    )
    learner = Learner(
        learner_id="LEARNER-TEST-1",
        name="Test Learner",
        role_id="ROLE-TEST-1",
        cadre_role="Test Cadre",
        department="Test Dept",
        assessed_competencies=[
            CompetencyAssessment(
                competency_id="KCM-FUNC-11",
                estimated_level=2,
                assessment_status="assessed",
                confidence=0.8,
            )
        ],
    )

    report = gap_engine.compute_skill_gaps(learner, role, repository)
    assert report.total_required_competencies == 1
    assert report.gap_count == 1
    assert report.competent_count == 0
    assert report.unassessed_count == 0

    gap_item = report.gaps[0]
    assert gap_item.gap == 2  # max(0, 4 - 2) = 2
    assert gap_item.status == "gap_identified"
    assert "Skill gap: 2 levels" in gap_item.explanation


def test_gap_calculation_exact_match(gap_engine: SkillGapEngine, repository: CompetencyRepository):
    """Test boundary where Estimated == Required (gap = 0)."""
    role = Role(
        role_id="ROLE-TEST-2",
        role_name="Test Role",
        cadre_role="Test Cadre",
        description="Testing",
        required_competencies=[
            RoleRequirement(
                competency_id="KCM-FUNC-21",
                competency_name="Administration Matters",
                required_level=3,
                priority="high",
                rationale="Test",
            )
        ],
    )
    learner = Learner(
        learner_id="LEARNER-TEST-2",
        name="Test Learner",
        role_id="ROLE-TEST-2",
        cadre_role="Test Cadre",
        department="Test Dept",
        assessed_competencies=[
            CompetencyAssessment(
                competency_id="KCM-FUNC-21",
                estimated_level=3,
                assessment_status="assessed",
                confidence=0.9,
            )
        ],
    )

    report = gap_engine.compute_skill_gaps(learner, role, repository)
    assert report.gap_count == 0
    assert report.competent_count == 1
    gap_item = report.gaps[0]
    assert gap_item.gap == 0
    assert gap_item.status == "competent"
    assert "meeting or exceeding" in gap_item.explanation


def test_gap_calculation_exceeds_requirement(gap_engine: SkillGapEngine, repository: CompetencyRepository):
    """Test boundary where Estimated > Required (gap = max(0, R - E) = 0)."""
    role = Role(
        role_id="ROLE-TEST-3",
        role_name="Test Role",
        cadre_role="Test Cadre",
        description="Testing",
        required_competencies=[
            RoleRequirement(
                competency_id="KCM-BEH-04",
                competency_name="Communication",
                required_level=2,
                priority="medium",
                rationale="Test",
            )
        ],
    )
    learner = Learner(
        learner_id="LEARNER-TEST-3",
        name="Test Learner",
        role_id="ROLE-TEST-3",
        cadre_role="Test Cadre",
        department="Test Dept",
        assessed_competencies=[
            CompetencyAssessment(
                competency_id="KCM-BEH-04",
                estimated_level=5,  # Exceeds required level 2
                assessment_status="assessed",
                confidence=0.95,
            )
        ],
    )

    report = gap_engine.compute_skill_gaps(learner, role, repository)
    gap_item = report.gaps[0]
    assert gap_item.gap == 0  # max(0, 2 - 5) = 0
    assert gap_item.status == "competent"


def test_gap_calculation_unassessed_boundary(gap_engine: SkillGapEngine, repository: CompetencyRepository):
    """Test unassessed competency (estimated_level is None)."""
    role = Role(
        role_id="ROLE-TEST-4",
        role_name="Test Role",
        cadre_role="Test Cadre",
        description="Testing",
        required_competencies=[
            RoleRequirement(
                competency_id="KCM-BEH-01",
                competency_name="Self-Awareness",
                required_level=3,
                priority="medium",
                rationale="Test",
            )
        ],
    )
    learner = Learner(
        learner_id="LEARNER-TEST-4",
        name="Fresh Learner",
        role_id="ROLE-TEST-4",
        cadre_role="Test Cadre",
        department="Test Dept",
        assessed_competencies=[],  # Empty assessment evidence
    )

    report = gap_engine.compute_skill_gaps(learner, role, repository)
    assert report.unassessed_count == 1
    assert report.gap_count == 0
    assert report.competent_count == 0

    gap_item = report.gaps[0]
    assert gap_item.gap is None
    assert gap_item.estimated_level is None
    assert gap_item.status == "unassessed"
    assert "No assessment evidence recorded" in gap_item.explanation


# ============================================================================
# 4. Deterministic Recommendations & Candidate Mapping Handling
# ============================================================================

def test_recommendations_for_learner_002(
    repository: CompetencyRepository,
    gap_engine: SkillGapEngine,
    rec_engine: RecommendationEngine,
):
    """
    Test recommendation logic on Learner 002 (Director / Joint Director).
    Should recommend ACBP-CRS-036 (Leadership in Project Management) for KCM-FUNC-05
    and ACBP-CRS-040 (Strategic Leadership: The Indic Way) for KCM-BEH-10.
    """
    learner = repository.get_learner("LEARNER-002")
    assert learner is not None
    role = repository.get_role(learner.role_id)
    assert role is not None

    gaps = gap_engine.compute_skill_gaps(learner, role, repository)
    assert gaps.gap_count == 2  # KCM-FUNC-05 (gap 2) and KCM-BEH-10 (gap 1)

    recs = rec_engine.recommend(learner, role, gaps, include_unresolved=False)
    assert len(recs.recommendations) > 0

    # Top recommendation should address the largest critical gap: Project Management (ACBP-CRS-036)
    top_rec = recs.recommendations[0]
    assert top_rec.course_id == "ACBP-CRS-036"
    assert top_rec.target_competency_id == "KCM-FUNC-05"
    assert top_rec.target_cadre_match is True
    assert top_rec.mapping_status == "candidate"
    assert top_rec.is_verified_mapping is False
    assert "Directly addresses skill gap" in top_rec.recommendation_reason


def test_recommendation_determinism_across_runs(
    repository: CompetencyRepository,
    gap_engine: SkillGapEngine,
    rec_engine: RecommendationEngine,
):
    """Ensure that repeated recommendation calls yield identical ordering, ranks, and scores."""
    learner = repository.get_learner("LEARNER-001")
    role = repository.get_role(learner.role_id)
    gaps = gap_engine.compute_skill_gaps(learner, role, repository)

    run1 = rec_engine.recommend(learner, role, gaps, include_unresolved=True)
    run2 = rec_engine.recommend(learner, role, gaps, include_unresolved=True)

    assert len(run1.recommendations) == len(run2.recommendations)
    for r1, r2 in zip(run1.recommendations, run2.recommendations):
        assert r1.course_id == r2.course_id
        assert r1.score == r2.score
        assert r1.rank == r2.rank
        assert r1.mapping_status == r2.mapping_status


def test_unresolved_mapping_exclusion_and_inclusion(
    repository: CompetencyRepository,
    gap_engine: SkillGapEngine,
    rec_engine: RecommendationEngine,
):
    """Test that unresolved mappings are filtered out by default and clearly tagged when included."""
    learner = repository.get_learner("LEARNER-001")
    role = repository.get_role(learner.role_id)
    gaps = gap_engine.compute_skill_gaps(learner, role, repository)

    # 1. Default: exclude unresolved courses
    report_filtered = rec_engine.recommend(learner, role, gaps, include_unresolved=False)
    assert report_filtered.include_unresolved_requested is False
    for r in report_filtered.recommendations:
        assert r.mapping_status != "unresolved"

    # 2. Explicitly include unresolved courses
    report_included = rec_engine.recommend(learner, role, gaps, include_unresolved=True)
    assert report_included.include_unresolved_requested is True

    unresolved_items = [r for r in report_included.recommendations if r.mapping_status == "unresolved"]
    if unresolved_items:
        for u in unresolved_items:
            assert u.is_verified_mapping is False
            assert "NOTICE: Unresolved mapping" in u.recommendation_reason


# ============================================================================
# 5. Provenance & Synthetic Data Isolation
# ============================================================================

def test_provenance_isolation(repository: CompetencyRepository):
    """Confirm official datasets retain 'official_public' and synthetic profiles retain 'synthetic'."""
    # Official KCM competencies
    for comp in repository.list_competencies():
        assert comp.provenance == "official_public"

    # Official ACBP courses
    for course in repository.list_courses():
        assert course.provenance == "official_public"

    # Synthetic roles
    for role in repository.list_roles():
        assert role.provenance == "synthetic"
        assert role.is_synthetic is True

    # Synthetic learners
    for learner in repository.list_learners():
        assert learner.provenance == "synthetic"
        assert learner.is_synthetic is True


# ============================================================================
# 6. API Endpoints Integration Tests
# ============================================================================

def test_api_health_endpoint(client: TestClient):
    """Test /health endpoint structure and contents."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["datasets"]["competencies"]["count"] == 34
    assert data["datasets"]["courses"]["count"] == 226
    assert data["level_scale"]["min_level"] == 1
    assert data["level_scale"]["max_level"] == 5


def test_api_competencies_filtering(client: TestClient):
    """Test /api/competencies with type and search filters."""
    # All competencies
    res = client.get("/api/competencies")
    assert res.status_code == 200
    assert len(res.json()) == 34

    # Behavioural only
    res = client.get("/api/competencies?type=behavioural")
    assert res.status_code == 200
    assert all(c["competency_type"] == "behavioural" for c in res.json())
    assert len(res.json()) == 13

    # Functional only
    res = client.get("/api/competencies?type=functional")
    assert res.status_code == 200
    assert all(c["competency_type"] == "functional" for c in res.json())
    assert len(res.json()) == 21

    # Search keyword
    res = client.get("/api/competencies?search=analytics")
    assert res.status_code == 200
    assert any("Analytics" in c["competency_name"] for c in res.json())


def test_api_courses_filtering(client: TestClient):
    """Test /api/courses with category and search filters."""
    # Domain category
    res = client.get("/api/courses?category=Domain")
    assert res.status_code == 200
    assert all(c["competency_category"] == "Domain" for c in res.json())

    # Search by keyword
    res = client.get("/api/courses?search=Python")
    assert res.status_code == 200
    assert any("Python" in c["course_name"] for c in res.json())


def test_api_skill_gaps_endpoint(client: TestClient):
    """Test /api/learners/{id}/skill-gaps endpoint."""
    res = client.get("/api/learners/LEARNER-001/skill-gaps")
    assert res.status_code == 200
    data = res.json()
    assert data["learner_id"] == "LEARNER-001"
    assert data["learner_name"] == "Arun Kumar"
    assert data["gap_count"] >= 1
    assert len(data["gaps"]) == data["total_required_competencies"]

    # Check unassessed learner (LEARNER-003)
    res_unassessed = client.get("/api/learners/LEARNER-003/skill-gaps")
    assert res_unassessed.status_code == 200
    data_unassessed = res_unassessed.json()
    assert data_unassessed["unassessed_count"] == data_unassessed["total_required_competencies"]
    assert data_unassessed["gap_count"] == 0


def test_api_recommendations_endpoint(client: TestClient):
    """Test /api/learners/{id}/recommendations endpoint."""
    res = client.get("/api/learners/LEARNER-002/recommendations")
    assert res.status_code == 200
    data = res.json()
    assert data["learner_id"] == "LEARNER-002"
    assert len(data["recommendations"]) > 0

    first_rec = data["recommendations"][0]
    assert first_rec["rank"] == 1
    assert "score" in first_rec
    assert "recommendation_reason" in first_rec
    assert first_rec["is_verified_mapping"] is False  # Candidate mapping
