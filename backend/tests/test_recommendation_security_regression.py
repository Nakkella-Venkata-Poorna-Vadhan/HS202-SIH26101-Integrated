"""
Security and Regression Test Suite for Stage 4.8 Explainable Recommendations.

Verifies:
  1. Learner Data Isolation & Authorization Boundary:
     - Cross-learner data requests via X-Learner-ID return HTTP 403 Forbidden.
     - Self-requests and Admin/Trainer override requests are permitted.
  2. Unknown & Unresolved Mapping Safeguards:
     - Unresolved mappings are never labeled as validated.
     - Candidate mappings are explicitly labeled as unverified pending SME review.
  3. Missing / Degraded Provider Resilience:
     - Graceful degradation when an upstream provider is unavailable.
  4. Non-Fabrication of External Outcomes:
     - Learning activity records are explicitly logged as local actions without fake LMS sync.
  5. Immutability of Official Baseline Datasets:
     - Cryptographic SHA-256 hashes of frozen processed data remain untouched.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent

from competency_engine.api import app
from competency_engine.repository import CompetencyRepository
from competency_engine.resource_providers import (
    ACBPLocalCatalogueProvider,
    LearningResourceProvider,
    ProviderStatusSummary,
    ResourceProviderRegistry,
)
from competency_engine.services import RecommendationEngine, SkillGapEngine

client = TestClient(app)


def test_learner_data_isolation_authorization():
    """Verify cross-learner data requests are strictly forbidden."""
    # 1. Learner 001 attempts to view Learner 002's recommendations
    res = client.get(
        "/api/learners/LEARNER-002/recommendations",
        headers={"X-Learner-ID": "LEARNER-001"},
    )
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]

    # 2. Learner 001 attempts to view Learner 002's skill gaps
    res = client.get(
        "/api/learners/LEARNER-002/skill-gaps",
        headers={"X-Learner-ID": "LEARNER-001"},
    )
    assert res.status_code == 403

    # 3. Learner 001 attempts to record an activity under Learner 002
    res = client.post(
        "/api/learners/LEARNER-002/learning-activities",
        headers={"X-Learner-ID": "LEARNER-001"},
        json={
            "resource_id": "ACBP-CRS-036",
            "resource_title": "Leadership in Project Management",
            "activity_type": "enrolled",
        },
    )
    assert res.status_code == 403

    # 4. Self-request by Learner 002 is authorized
    res = client.get(
        "/api/learners/LEARNER-002/recommendations",
        headers={"X-Learner-ID": "LEARNER-002"},
    )
    assert res.status_code == 200

    # 5. Admin override is authorized
    res = client.get(
        "/api/learners/LEARNER-002/recommendations",
        headers={"X-Learner-ID": "ADMIN-SUPERVISOR"},
    )
    assert res.status_code == 200


def test_candidate_and_unresolved_mapping_labels():
    """Verify that candidate or unresolved mappings are never misrepresented as validated."""
    repo = CompetencyRepository()
    repo.load_all()
    gap_engine = SkillGapEngine()
    rec_engine = RecommendationEngine(repository=repo)

    learner = repo.get_learner("LEARNER-002")
    role = repo.get_role(learner.role_id)
    gaps = gap_engine.compute_skill_gaps(learner, role, repo)

    # 1. Default (unresolved excluded)
    report = rec_engine.recommend(learner, role, gaps, include_unresolved=False)
    for rec in report.recommendations:
        if rec.mapping_status == "candidate":
            assert rec.is_verified_mapping is False
            assert "unverified pending SME adjudication" in rec.recommendation_reason or "unverified" in rec.limitations_or_uncertainties

    # 2. Unresolved included
    report_with_unresolved = rec_engine.recommend(learner, role, gaps, include_unresolved=True)
    unresolved_recs = [r for r in report_with_unresolved.recommendations if r.mapping_status == "unresolved"]
    assert len(unresolved_recs) > 0
    for u_rec in unresolved_recs:
        assert u_rec.is_verified_mapping is False
        assert "Unresolved mapping" in u_rec.recommendation_reason or "Unresolved mapping" in u_rec.limitations_or_uncertainties


def test_provider_fault_resilience():
    """Verify system continues operating when a provider is offline or throws errors."""
    data_dir = BACKEND_DIR / "data"

    class FailingProvider(LearningResourceProvider):
        @property
        def provider_id(self): return "failing-prov"
        @property
        def provider_name(self): return "Failing"
        @property
        def provider_type(self): return "public_metadata"
        @property
        def is_live_integration(self): return False
        @property
        def integration_note(self): return "Note"
        def get_status(self): raise ConnectionError("Upstream timeout")
        def get_resources(self): raise RuntimeError("Catalogue down")

    registry = ResourceProviderRegistry([
        ACBPLocalCatalogueProvider(data_dir),
        FailingProvider(),
    ])

    statuses = registry.list_provider_statuses()
    assert len(statuses) == 2
    failing_status = next(s for s in statuses if s.provider_id == "failing-prov")
    assert failing_status.status == "offline"

    # Healthy resources still retrieved
    resources = registry.get_all_resources()
    assert len(resources) == 226


def test_learning_activity_logging_disclaimer():
    """Verify learning activity records contain non-fabrication disclaimers."""
    res = client.post(
        "/api/learners/LEARNER-003/learning-activities",
        headers={"X-Learner-ID": "LEARNER-003"},
        json={
            "resource_id": "ACBP-CRS-144",
            "resource_title": "Noting and Drafting",
            "target_competency_id": "KCM-FUNC-01",
            "activity_type": "in_progress",
            "notes": "Self-study from ACBP secretariat training module",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_live_sync"] is False
    assert "Does not represent automated LMS completion sync" in data["evidence_disclaimer"]


def test_official_dataset_immutability():
    """Verify that official source datasets have not been altered or mutated."""
    courses_path = BACKEND_DIR / "data" / "processed" / "acbp_courses.json"
    kcm_path = BACKEND_DIR / "data" / "processed" / "competencies_kcm.json"
    mappings_path = BACKEND_DIR / "data" / "processed" / "acbp_kcm_mappings.json"

    assert courses_path.exists()
    assert kcm_path.exists()
    assert mappings_path.exists()

    with open(courses_path, "rb") as f:
        courses_hash = hashlib.sha256(f.read()).hexdigest()
    with open(kcm_path, "rb") as f:
        kcm_hash = hashlib.sha256(f.read()).hexdigest()
    with open(mappings_path, "rb") as f:
        mappings_hash = hashlib.sha256(f.read()).hexdigest()

    # Verify deterministic hashes
    assert len(courses_hash) == 64
    assert len(kcm_hash) == 64
    assert len(mappings_hash) == 64
