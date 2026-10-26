"""
Stage 4.5: Diagnostic Assessment Persistence and Integrity Hardening Tests.
Verifies restart persistence, attempt-learner binding, answer secrecy,
access control boundaries, baseline evidence preservation, and strict mastery thresholds.
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from competency_engine.api import app, repository, assessment_store
from competency_engine.assessment_store import AssessmentStore
from competency_engine.config import (
    ACBP_COURSES_PATH,
    ACBP_MAPPINGS_PATH,
    KCM_COMPETENCIES_PATH,
    SYNTHETIC_LEARNERS_PATH,
    SYNTHETIC_ROLES_PATH,
)
from competency_engine.diagnostic_estimator import DiagnosticEstimator
from competency_engine.models import ProvisionalEstimate, SourceQuestion
from competency_engine.repository import CompetencyRepository
from competency_engine.services import RecommendationEngine, SkillGapEngine

client = TestClient(app)


def test_persistence_across_backend_restart(tmp_path: Path):
    """
    Integration Test:
    1. Starts with clearly unassessed learner (LEARNER-003, Pooja Verma).
    2. Records a completed assessment into an isolated AssessmentStore.
    3. Simulates backend restart by constructing a new CompetencyRepository pointing to that store.
    4. Confirms estimate is loaded, reflected in skill gaps, and drives recommendations.
    """
    isolated_assessments_dir = tmp_path / "assessments"
    isolated_attempts_path = isolated_assessments_dir / "attempts.json"
    isolated_estimates_path = isolated_assessments_dir / "provisional_estimates.json"

    # Step 1: Fresh repository before assessment
    repo_pre = CompetencyRepository(
        estimates_path=isolated_estimates_path,
        auto_seed_synthetic=False,
    )
    learner_pre = repo_pre.get_learner("LEARNER-003")
    assert learner_pre is not None
    role_pre = repo_pre.get_role(learner_pre.role_id)
    assert role_pre is not None

    gap_engine = SkillGapEngine()
    initial_report = gap_engine.compute_skill_gaps(learner_pre, role_pre, repo_pre)
    assert initial_report.unassessed_count == 4
    func11_gap_pre = next(g for g in initial_report.gaps if g.competency_id == "KCM-FUNC-11")
    assert func11_gap_pre.status == "unassessed"
    assert func11_gap_pre.estimated_level is None

    # Step 2: Complete diagnostic assessment and save to isolated store
    store = AssessmentStore(
        assessments_dir=isolated_assessments_dir,
        attempts_path=isolated_attempts_path,
        estimates_path=isolated_estimates_path,
    )
    attempt_id = store.create_attempt(
        learner_id="LEARNER-003",
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics",
        question_ids=["Q-NAS-001", "Q-NAS-002", "Q-NAS-003", "Q-NAS-005"],
    )
    estimate = ProvisionalEstimate(
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics",
        estimated_level=1,
        previous_level=None,
        confidence_score=0.75,
        evidence_count=4,
        sufficiency_status="sufficient",
        diagnostic_summary="Demonstrated 1/4 accuracy. Provisional level 1.",
    )
    store.record_completed_attempt(
        attempt_id=attempt_id,
        answers={"Q-NAS-001": "B", "Q-NAS-002": "B", "Q-NAS-003": "A", "Q-NAS-005": "A"},
        score=1,
        percentage=25,
        provisional_estimate=estimate,
        feedback_summary=[],
    )

    # Confirm estimate saved on disk
    assert isolated_estimates_path.exists()
    with open(isolated_estimates_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert "LEARNER-003:KCM-FUNC-11" in saved_data["provisional_estimates"]

    # Step 3: Reconstruct/restart backend repository using the same data directory
    repo_post = CompetencyRepository(
        estimates_path=isolated_estimates_path,
        auto_seed_synthetic=False,
    )

    # Step 4: Confirm estimate is loaded and active in the reconstructed repository
    learner_post = repo_post.get_learner("LEARNER-003")
    assert learner_post is not None
    kcm_func11_assessment = next(
        (a for a in learner_post.assessed_competencies if a.competency_id == "KCM-FUNC-11"),
        None,
    )
    assert kcm_func11_assessment is not None
    assert kcm_func11_assessment.estimated_level == 1
    assert kcm_func11_assessment.assessment_status == "assessed"
    assert kcm_func11_assessment.is_provisional is True
    assert kcm_func11_assessment.confidence == 0.75

    # Step 5: Verify gap report reflects the updated estimate across restart
    role_post = repo_post.get_role(learner_post.role_id)
    updated_report = gap_engine.compute_skill_gaps(learner_post, role_post, repo_post)
    assert updated_report.unassessed_count == 3  # Reduced from 4 to 3
    func11_gap_post = next(g for g in updated_report.gaps if g.competency_id == "KCM-FUNC-11")
    assert func11_gap_post.status == "gap_identified"
    assert func11_gap_post.gap == 2  # required 3 - estimated 1 = 2
    assert func11_gap_post.estimated_level == 1
    assert func11_gap_post.is_provisional is True
    assert "[Provisional Quiz Estimate]" in func11_gap_post.explanation

    # Step 6: Verify recommendations address the gap
    rec_engine = RecommendationEngine(repo_post)
    rec_report = rec_engine.recommend(
        learner=learner_post,
        role=role_post,
        gap_report=updated_report,
        include_unresolved=True,
    )
    assert len(rec_report.recommendations) > 0


def test_baseline_workplace_evidence_not_overwritten(tmp_path: Path):
    """
    Verifies that a diagnostic quiz does not overwrite an existing baseline workplace assessment
    (e.g., supervisor evaluation), preserving official evidence integrity.
    """
    isolated_estimates = tmp_path / "provisional_estimates.json"
    repo = CompetencyRepository(estimates_path=isolated_estimates, auto_seed_synthetic=False)

    # LEARNER-001 (Arun Kumar) has baseline assessment for KCM-FUNC-21 (Level 3, supervisor_annual_evaluation_satisfactory)
    learner = repo.get_learner("LEARNER-001")
    assert learner is not None
    baseline_assessment = next(a for a in learner.assessed_competencies if a.competency_id == "KCM-FUNC-21")
    assert baseline_assessment.estimated_level == 3
    assert "synthetic_supervisor_annual_evaluation_satisfactory" in baseline_assessment.evidence_sources

    # Attempt to apply a quiz result of Level 1
    updated = repo.update_learner_provisional_assessment(
        learner_id="LEARNER-001",
        competency_id="KCM-FUNC-21",
        estimated_level=1,
        confidence=0.60,
        evidence_source="Attempt ATT-QUIZ-01 (quiz_test)",
    )
    assert updated is True

    # Baseline level MUST remain Level 3 (not overwritten by Level 1 quiz result)
    assert baseline_assessment.estimated_level == 3
    # Quiz evidence appended as supporting record
    assert "Attempt ATT-QUIZ-01 (quiz_test)" in baseline_assessment.evidence_sources


def test_insufficient_evidence_remains_unassessed(tmp_path: Path):
    """
    Verifies that when evidence threshold (< 3 questions) is not met, the competency
    remains strictly insufficient/unassessed and is never converted to Level 1.
    """
    estimator = DiagnosticEstimator()
    q = SourceQuestion(
        question_id="Q-TEST-01",
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics",
        question_text="Test question",
        options={"A": "1", "B": "2", "C": "3", "D": "4"},
        correct_answer="B",
        explanation="Test explanation",
        source_document_id="SRC-CSO-NAS-SM-2012",
        source_page=10,
        source_excerpt="Test excerpt",
        difficulty="foundation",
    )

    # Only 1 question provided
    estimate = estimator.estimate_provisional_competency(
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics",
        graded_questions=[(q, False)],  # 0% accuracy
        previous_level=None,
    )

    assert estimate.sufficiency_status == "insufficient_evidence"
    assert estimate.estimated_level is None  # Must NOT be silently set to Level 1
    assert estimate.confidence_score < 0.30

    # Ensure repository _sync_persisted_estimates ignores insufficient estimates
    isolated_estimates = tmp_path / "provisional_estimates.json"
    with open(isolated_estimates, "w", encoding="utf-8") as f:
        json.dump(
            {
                "provisional_estimates": {
                    "LEARNER-003:KCM-FUNC-11": {
                        "learner_id": "LEARNER-003",
                        "competency_id": "KCM-FUNC-11",
                        "estimated_level": None,
                        "confidence_score": 0.15,
                        "sufficiency_status": "insufficient_evidence",
                        "last_attempt_id": "ATT-INSUFFICIENT",
                    }
                }
            },
            f,
        )

    repo = CompetencyRepository(estimates_path=isolated_estimates, auto_seed_synthetic=False)
    learner = repo.get_learner("LEARNER-003")
    kcm_func11 = next(a for a in learner.assessed_competencies if a.competency_id == "KCM-FUNC-11")
    assert kcm_func11.assessment_status == "unassessed"
    assert kcm_func11.estimated_level is None


def test_level_5_mastery_requires_5_questions_and_100_percent():
    """
    Verifies that Level 5 (Expert) cannot be awarded on short quizzes (e.g. 4 questions),
    strictly requiring at least 5 questions and 100% accuracy.
    """
    estimator = DiagnosticEstimator()

    def make_q(qid: str, diff: str) -> SourceQuestion:
        return SourceQuestion(
            question_id=qid,
            competency_id="KCM-FUNC-11",
            competency_name="Data Analytics",
            question_text=f"Question {qid}",
            options={"A": "1", "B": "2", "C": "3", "D": "4"},
            correct_answer="B",
            explanation="Explanation",
            source_document_id="SRC-CSO-NAS-SM-2012",
            source_page=10,
            source_excerpt="Excerpt",
            difficulty=diff,
        )

    # 4 questions with 100% accuracy: should cap at Level 4 (Advanced)
    q4 = [
        (make_q("Q1", "foundation"), True),
        (make_q("Q2", "operational"), True),
        (make_q("Q3", "advanced"), True),
        (make_q("Q4", "advanced"), True),
    ]
    est_4 = estimator.estimate_provisional_competency("KCM-FUNC-11", "Data Analytics", q4)
    assert est_4.estimated_level == 4
    assert est_4.sufficiency_status == "sufficient"

    # 5 questions with 100% accuracy: eligible for Level 5
    q5 = q4 + [(make_q("Q5", "advanced"), True)]
    est_5 = estimator.estimate_provisional_competency("KCM-FUNC-11", "Data Analytics", q5)
    assert est_5.estimated_level == 5


def test_attempt_learner_binding_enforced():
    """
    Verifies that an attempt created for Learner A cannot be submitted under Learner B.
    """
    start_resp = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-003", "competency_id": "KCM-FUNC-11", "question_count": 4},
    )
    assert start_resp.status_code == 200
    attempt_id = start_resp.json()["attempt_id"]

    # Attempt to submit under LEARNER-001
    submit_resp = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={
            "attempt_id": attempt_id,
            "learner_id": "LEARNER-001",  # Mismatch!
            "answers": {"Q-NAS-001": "B"},
        },
    )
    assert submit_resp.status_code == 403
    assert "belongs to learner 'LEARNER-003'" in submit_resp.json()["detail"]


def test_malformed_and_invalid_question_ids_rejected():
    """
    Verifies rejection of empty answer payloads and unknown/invalid question IDs.
    """
    start_resp = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-003", "competency_id": "KCM-FUNC-11", "question_count": 4},
    )
    assert start_resp.status_code == 200
    attempt_id = start_resp.json()["attempt_id"]

    # 1. Malformed answer (invalid option value) rejected by schema validation
    malformed_resp = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={
            "attempt_id": attempt_id,
            "learner_id": "LEARNER-003",
            "answers": {"Q-NAS-001": "INVALID_OPTION"},
        },
    )
    assert malformed_resp.status_code in (400, 422)

    # 2. Invalid question ID not part of the attempt
    invalid_q_resp = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={
            "attempt_id": attempt_id,
            "learner_id": "LEARNER-003",
            "answers": {"Q-INVALID-999": "A"},
        },
    )
    assert invalid_q_resp.status_code == 400
    assert "invalid question ID" in invalid_q_resp.json()["detail"]


def test_duplicate_submission_rejected():
    """
    Verifies that submitting the same attempt twice returns HTTP 400.
    """
    start_resp = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-003", "competency_id": "KCM-FUNC-11", "question_count": 4},
    )
    attempt_id = start_resp.json()["attempt_id"]
    q_ids = [q["question_id"] for q in start_resp.json()["questions"]]

    # First submission
    sub1 = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={"attempt_id": attempt_id, "learner_id": "LEARNER-003", "answers": {qid: "B" for qid in q_ids}},
    )
    assert sub1.status_code == 200
    original_score = sub1.json()["score"]

    # Duplicate submission
    sub2 = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={"attempt_id": attempt_id, "learner_id": "LEARNER-003", "answers": {qid: "A" for qid in q_ids}},
    )
    assert sub2.status_code == 400
    assert "already been submitted" in sub2.json()["detail"]


def test_access_boundaries_on_private_records():
    """
    Verifies that a learner cannot view another learner's private attempt details,
    assessment history, or active estimates when requester identity is provided.
    """
    start_resp = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-003", "competency_id": "KCM-FUNC-11", "question_count": 4},
    )
    attempt_id = start_resp.json()["attempt_id"]

    # Attempt details: LEARNER-001 accessing LEARNER-003's attempt
    resp_unauth = client.get(
        f"/api/assessment/attempts/{attempt_id}",
        headers={"X-Learner-ID": "LEARNER-001"},
    )
    assert resp_unauth.status_code == 403

    # Attempt details: Owner accessing own attempt
    resp_auth = client.get(
        f"/api/assessment/attempts/{attempt_id}",
        headers={"X-Learner-ID": "LEARNER-003"},
    )
    assert resp_auth.status_code == 200

    # History: LEARNER-001 accessing LEARNER-003's history
    hist_unauth = client.get(
        "/api/assessment/learner/LEARNER-003/history",
        headers={"X-Learner-ID": "LEARNER-001"},
    )
    assert hist_unauth.status_code == 403

    # Estimates: LEARNER-001 accessing LEARNER-003's estimates
    est_unauth = client.get(
        "/api/assessment/learner/LEARNER-003/estimates",
        headers={"X-Learner-ID": "LEARNER-001"},
    )
    assert est_unauth.status_code == 403


def test_official_source_data_files_remain_unaltered():
    """
    Verifies that official dataset files and mapping registries are unchanged.
    """
    assert KCM_COMPETENCIES_PATH.exists()
    assert ACBP_COURSES_PATH.exists()
    assert ACBP_MAPPINGS_PATH.exists()
    assert SYNTHETIC_ROLES_PATH.exists()
    assert SYNTHETIC_LEARNERS_PATH.exists()

    with open(KCM_COMPETENCIES_PATH, "r", encoding="utf-8") as f:
        comps = json.load(f)
    assert len(comps) == 34  # Official 34 KCM competencies

    with open(ACBP_COURSES_PATH, "r", encoding="utf-8") as f:
        courses = json.load(f)
    assert len(courses["records"]) == 226  # Official 226 courses


def test_safe_demo_reset_endpoint():
    """
    Verifies that POST /api/demo/reset safely resets demo attempts and provisional estimates
    without touching official catalogues, returning unassessed learners to baseline.
    """
    # 1. Reject reset without confirmation
    bad_req = client.post("/api/demo/reset")
    assert bad_req.status_code == 400
    assert "requires explicit confirmation" in bad_req.json()["detail"]

    # 2. Record an assessment for LEARNER-003
    start = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-003", "competency_id": "KCM-FUNC-11", "question_count": 4},
    )
    attempt_id = start.json()["attempt_id"]
    client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={
            "attempt_id": attempt_id,
            "learner_id": "LEARNER-003",
            "answers": {"Q-NAS-001": "B", "Q-NAS-002": "B", "Q-NAS-003": "A", "Q-NAS-005": "A"},
        },
    )
    gaps_during = client.get("/api/learners/LEARNER-003/skill-gaps").json()
    assert gaps_during["unassessed_count"] == 3

    # 3. Invoke demo reset
    reset_resp = client.post("/api/demo/reset?confirm=true")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"

    # 4. Confirm unassessed status restored to 4
    gaps_after = client.get("/api/learners/LEARNER-003/skill-gaps").json()
    assert gaps_after["unassessed_count"] == 4

