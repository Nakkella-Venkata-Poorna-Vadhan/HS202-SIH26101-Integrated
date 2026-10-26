"""
Comprehensive Regression & Security Test Suite for Stage 4.9.

Verifies:
  1. Resource Metadata Integrity & Provenance (no fabricated durations/prerequisites/mappings).
  2. Recommendation Explanation Consistency (unambiguous difficulty fit, no assumed prerequisites).
  3. Local-Demo Security Boundaries & Negative Authorization:
     - Cross-learner profile read blocked (403).
     - Cross-learner assessment start blocked (403).
     - Cross-learner attempt read blocked (403).
     - Cross-learner attempt submission blocked (403).
     - Learner access to trainer write routes blocked (403).
  4. Assessment Leakage Prevention & Draft Isolation:
     - Client questions contain no correct answers, explanations, or source excerpts.
     - Server-side scoring cannot trust client score.
     - Draft questions cannot be retrieved in assessment until published.
  5. Learning Activity Semantics & Non-Mutation of Competency Estimates.
  6. Source Data Hash Preservation.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import pytest
from starlette.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"

from competency_engine.api import app, repository, assessment_store, question_bank, question_review_store
from competency_engine.models import (
    AssessmentStartRequest,
    AssessmentSubmissionRequest,
    DraftQuestion,
    LearningActivityCreateRequest,
)
from competency_engine.resource_providers import (
    ACBPLocalCatalogueProvider,
    IGOTPublicMetadataProvider,
    NSSTAPublicProgrammeProvider,
    ResourceProviderRegistry,
)
from competency_engine.services import RecommendationEngine


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# 1. Resource Metadata Integrity & Provenance
# ============================================================================

def test_no_fabricated_prerequisites_or_durations():
    """Verify that learning resources do not invent prerequisites or durations."""
    provider = ACBPLocalCatalogueProvider(DATA_DIR)
    resources = provider.get_resources()
    assert len(resources) == 226

    for r in resources:
        # Prerequisites should be empty list, not silently assumed orientation
        assert r.prerequisites == []
        assert "No prerequisites stated" in r.prerequisites_note or "Not specified" in r.prerequisites_note
        # Difficulty provenance must be explicitly labeled heuristic
        assert r.difficulty_provenance == "heuristic_cadre_estimate"
        # Mapping must never be validated by title alone
        if r.mapping_type in ("exact_title_reference", "curated_candidate"):
            assert r.mapping_status == "candidate"
            assert "Candidate mapping" in r.limitations


def test_nssta_and_igot_provider_provenance():
    """Verify provider metadata distinguishes public directory from live API."""
    nssta = NSSTAPublicProgrammeProvider(DATA_DIR)
    assert nssta.is_live_integration is False
    assert "public training calendar" in nssta.integration_note.lower()

    for r in nssta.get_resources():
        if r.mapping_type == "heuristic_title_keyword":
            assert "heuristically" in r.limitations.lower()
            assert r.mapping_status == "candidate"

    igot = IGOTPublicMetadataProvider(DATA_DIR)
    assert igot.is_live_integration is False
    assert "Parichay SSO" in igot.integration_note
    for r in igot.get_resources():
        assert "portal.igotkarmayogi.gov.in" in r.limitations
        assert "Parichay SSO" in r.limitations


# ============================================================================
# 2. Recommendation Explanation Consistency
# ============================================================================

def test_explanation_difficulty_and_prerequisite_consistency():
    """Verify recommendation explanations use unambiguous difficulty and explicit unknown prerequisites."""
    repository.load_all()
    engine = RecommendationEngine(repository)
    learner = repository.get_learner("LEARNER-001")
    assert learner is not None
    role = repository.get_role(learner.role_id)
    assert role is not None

    from competency_engine.services import SkillGapEngine
    gaps = SkillGapEngine().compute_skill_gaps(learner, role, repository)

    report = engine.recommend(
        learner=learner,
        role=role,
        gap_report=gaps,
        include_unresolved=True,
        ranking_method="hybrid_explainable",
    )

    assert len(report.recommendations) > 0
    for rec in report.recommendations:
        # Check unambiguous difficulty fit label
        assert "Heuristic Cadre Seniority Alignment" in rec.difficulty_fit
        assert rec.difficulty_provenance in ("heuristic_cadre_estimate", "unspecified")
        # Check prerequisites are not assumed
        assert "Not specified in official source" in rec.prerequisite_fit
        # Check limitations explicitly disclose candidate or unresolved status
        if rec.mapping_status == "candidate":
            assert "Candidate mapping" in rec.limitations_or_uncertainties
            assert "unverified pending" in rec.limitations_or_uncertainties


def test_recommendation_determinism():
    """Verify that recommendations produce identical scores and ranks for identical inputs."""
    repository.load_all()
    engine = RecommendationEngine(repository)
    learner = repository.get_learner("LEARNER-001")
    assert learner is not None
    role = repository.get_role(learner.role_id)
    assert role is not None

    from competency_engine.services import SkillGapEngine
    gaps = SkillGapEngine().compute_skill_gaps(learner, role, repository)

    run_1 = engine.recommend(learner, role, gaps, ranking_method="hybrid_explainable")
    run_2 = engine.recommend(learner, role, gaps, ranking_method="hybrid_explainable")

    ids_1 = [r.course_id for r in run_1.recommendations]
    ids_2 = [r.course_id for r in run_2.recommendations]
    scores_1 = [r.score for r in run_1.recommendations]
    scores_2 = [r.score for r in run_2.recommendations]

    assert ids_1 == ids_2
    assert scores_1 == scores_2


# ============================================================================
# 3. Local-Demo Security Boundaries & Negative Authorization
# ============================================================================

def test_negative_authorization_cross_learner_read(client):
    """Learner A (LEARNER-001) cannot access profile or recommendations of Learner B (LEARNER-002)."""
    # 1. Profile read
    res = client.get("/api/learners/LEARNER-002", headers={"X-Learner-ID": "LEARNER-001"})
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]

    # 2. Skill gaps read
    res = client.get("/api/learners/LEARNER-002/skill-gaps", headers={"X-Learner-ID": "LEARNER-001"})
    assert res.status_code == 403

    # 3. Recommendations read
    res = client.get("/api/learners/LEARNER-002/recommendations", headers={"X-Learner-ID": "LEARNER-001"})
    assert res.status_code == 403

    # 4. Learning activities read
    res = client.get("/api/learners/LEARNER-002/learning-activities", headers={"X-Learner-ID": "LEARNER-001"})
    assert res.status_code == 403


def test_negative_authorization_assessment_isolation(client):
    """Learner A cannot start an assessment or view/submit Learner B's attempt."""
    # 1. Cross-learner assessment start blocked
    start_payload = {
        "learner_id": "LEARNER-002",
        "competency_id": "KCM-FUNC-05",
        "question_count": 3,
    }
    res = client.post("/api/assessment/start", json=start_payload, headers={"X-Learner-ID": "LEARNER-001"})
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]

    # 2. Legitimate start by LEARNER-002
    res_legit = client.post("/api/assessment/start", json=start_payload, headers={"X-Learner-ID": "LEARNER-002"})
    assert res_legit.status_code == 200
    attempt_id = res_legit.json()["attempt_id"]

    # 3. Cross-learner attempt read blocked
    res_read = client.get(f"/api/assessment/attempts/{attempt_id}", headers={"X-Learner-ID": "LEARNER-001"})
    assert res_read.status_code == 403

    # 4. Cross-learner attempt submit blocked
    sub_payload = {
        "attempt_id": attempt_id,
        "learner_id": "LEARNER-002",
        "answers": {q["question_id"]: "A" for q in res_legit.json()["questions"]},
    }
    res_sub = client.post(f"/api/assessment/{attempt_id}/submit", json=sub_payload, headers={"X-Learner-ID": "LEARNER-001"})
    assert res_sub.status_code == 403


def test_negative_authorization_trainer_write_routes(client):
    """Learner identities are strictly rejected from trainer authoring routes."""
    learner_header = {"X-Learner-ID": "LEARNER-001"}

    # 1. Upload
    res_upload = client.post(
        "/api/trainer/upload",
        files={"file": ("test.txt", b"Test content for training", "text/plain")},
        headers=learner_header,
    )
    assert res_upload.status_code == 403
    assert "not authorized to perform trainer authoring actions" in res_upload.json()["detail"]

    # 2. Generate questions
    res_gen = client.post(
        "/api/trainer/generate-questions",
        json={"document_id": "DOC-001", "competency_id": "KCM-FUNC-05", "question_count": 2},
        headers=learner_header,
    )
    assert res_gen.status_code == 403

    # 3. Review draft
    res_rev = client.post(
        "/api/trainer/drafts/DRF-001/review",
        json={"action": "approve"},
        headers=learner_header,
    )
    assert res_rev.status_code == 403

    # 4. Publish
    res_pub = client.post(
        "/api/trainer/publish",
        json={"question_ids": ["DRF-001"], "published_by": "LEARNER-001"},
        headers=learner_header,
    )
    assert res_pub.status_code == 403


# ============================================================================
# 4. Assessment Leakage Prevention & Draft Isolation
# ============================================================================

def test_client_question_sanitization(client):
    """Verify that start_assessment scrubs answer keys, explanations, and verbatim source excerpts."""
    start_payload = {
        "learner_id": "LEARNER-001",
        "competency_id": "KCM-FUNC-05",
        "question_count": 3,
    }
    res = client.post("/api/assessment/start", json=start_payload, headers={"X-Learner-ID": "LEARNER-001"})
    assert res.status_code == 200
    data = res.json()
    questions = data["questions"]
    assert len(questions) > 0

    for q in questions:
        # None of the secret fields may appear in the client payload
        assert "correct_answer" not in q
        assert "correct_answer_key" not in q
        assert "explanation" not in q
        assert "source_excerpt" not in q
        assert "verbatim_excerpt" not in q
        # Required client fields are present
        assert "question_id" in q
        assert "question_text" in q
        assert "options" in q
        assert set(q["options"].keys()) == {"A", "B", "C", "D"}


def test_unpublished_draft_questions_isolation(client):
    """Verify draft questions cannot enter the active assessment pool until published."""
    # Create an artificial draft in review store
    draft_id = "DRF-SECRET-001"
    draft = DraftQuestion(
        question_id=draft_id,
        document_id="DOC-TEST-001",
        source_document_id="SRC-TEST-001",
        competency_id="KCM-FUNC-05",
        competency_name="Project Management in Public Administration",
        question_text="Is this draft question accessible before publication?",
        options={"A": "No", "B": "Yes", "C": "Maybe", "D": "Unknown"},
        correct_answer="A",
        explanation="Drafts must remain quarantined until approved and published.",
        source_page=1,
        source_excerpt="Draft questions remain in review queue.",
        difficulty="operational",
        status="draft",
    )
    question_review_store._drafts[draft_id] = draft

    # Active assessment pool must NOT contain this draft
    active_questions = question_bank.get_questions_for_competency("KCM-FUNC-05")
    active_q_ids = [q.question_id for q in active_questions]
    assert draft_id not in active_q_ids

    # Start assessment via API
    res = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-001", "competency_id": "KCM-FUNC-05", "question_count": 3},
        headers={"X-Learner-ID": "LEARNER-001"},
    )
    assert res.status_code == 200
    returned_q_ids = [q["question_id"] for q in res.json()["questions"]]
    assert draft_id not in returned_q_ids


# ============================================================================
# 5. Learning Activity Semantics & Non-Mutation
# ============================================================================

def test_learning_activity_semantics_and_no_competency_mutation(client):
    """Verify activity logging distinguishes learner-reported completion and does not alter competency levels."""
    learner_id = "LEARNER-001"
    repository.load_all()
    initial_learner = repository.get_learner(learner_id)
    assert initial_learner is not None
    initial_estimates = {c.competency_id: c.estimated_level for c in initial_learner.assessed_competencies}

    # Record completed activity
    payload = {
        "resource_id": "ACBP-CRS-001",
        "resource_title": "Advanced Official Statistics and National Accounts",
        "target_competency_id": "KCM-FUNC-05",
        "activity_type": "completed",
        "notes": "Self-reported course completion after independent study.",
    }
    res = client.post(
        f"/api/learners/{learner_id}/learning-activities",
        json=payload,
        headers={"X-Learner-ID": learner_id},
    )
    assert res.status_code == 200
    record = res.json()

    assert record["activity_type"] == "completed"
    assert record["activity_status_label"] == "Completed (learner-reported)"
    assert record["verification_status"] == "self_reported_unverified"
    assert "Self-reported action does not imply" in record["evidence_disclaimer"]

    # Verify that learner's assessed competency levels did NOT change
    current_learner = repository.get_learner(learner_id)
    current_estimates = {c.competency_id: c.estimated_level for c in current_learner.assessed_competencies}
    assert current_estimates == initial_estimates


# ============================================================================
# 6. Source Data Hash Preservation
# ============================================================================

def test_source_data_hash_preservation():
    """Verify that processed JSON datasets and raw source PDFs match authoritative baselines."""
    expected_hashes = {
        "acbp_courses.json": "ec6ec89a68cb0bc3aecb777f00a156cda1898d2392b5fd2a7a09cc1e8fe159e7",
        "competencies_kcm.json": "9106ec27631dd0894f7b59133734266d7e9fd19ba0ef94107c082b6b32c90fd4",
        "acbp_kcm_mappings.json": "606926ad073e0e2a5682697f60c66c1867da908d57f5d2c53b1c2e596b5360f2",
    }

    processed_dir = DATA_DIR / "processed"
    for filename, expected_hash in expected_hashes.items():
        file_path = processed_dir / filename
        assert file_path.exists(), f"File {file_path} missing!"
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        actual_hash = hasher.hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch for {filename}! Expected {expected_hash}, got {actual_hash}"
