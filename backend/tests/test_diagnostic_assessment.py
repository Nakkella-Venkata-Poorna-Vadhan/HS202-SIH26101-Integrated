"""
Regression and Unit Test Suite for Stage 4.4:
Source-Grounded Quiz Generation, Diagnostic Assessment, and Estimator Integrity.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from competency_engine.api import app, repository, question_bank, diagnostic_estimator, adaptive_selector, assessment_store
from competency_engine.models import (
    ClientQuestion,
    ProvisionalEstimate,
    QuestionFeedback,
    SourceQuestion,
)
from competency_engine.quiz_generator import QuestionBank, QuestionValidator, QuestionValidationError
from competency_engine.diagnostic_estimator import DiagnosticEstimator, AdaptiveQuestionSelector


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# 1. Question Bank Integrity & Source Citations
# ============================================================================

def test_question_bank_loads_verified_questions():
    """Verify that QuestionBank loads valid grounded questions across multiple competencies."""
    topics = question_bank.get_topics()
    assert len(topics) >= 4

    comp_ids = [t.competency_id for t in topics]
    assert "KCM-FUNC-11" in comp_ids
    assert "KCM-FUNC-05" in comp_ids
    assert "KCM-BEH-06" in comp_ids
    assert "KCM-BEH-10" in comp_ids

    # Verify questions for Data Analytics (NAS Sources and Methods)
    nas_questions = question_bank.get_questions_for_competency("KCM-FUNC-11")
    assert len(nas_questions) >= 5

    for q in nas_questions:
        assert q.source_document_id == "SRC-CSO-NAS-SM-2012"
        assert q.source_page > 0
        assert len(q.source_excerpt.strip()) > 10
        assert set(q.options.keys()) == {"A", "B", "C", "D"}
        assert q.correct_answer in {"A", "B", "C", "D"}
        assert q.provenance == "source_grounded_verified"
        assert q.validation_status == "verified"


def test_question_validator_rejects_malformed_questions():
    """Ensure QuestionValidator strictly rejects invalid or malformed questions."""
    validator = QuestionValidator()

    # Empty question text
    with pytest.raises(QuestionValidationError, match="Empty question text"):
        validator.validate_question(
            SourceQuestion(
                question_id="Q-ERR-1",
                competency_id="KCM-FUNC-11",
                competency_name="Data Analytics",
                question_text="",
                options={"A": "1", "B": "2", "C": "3", "D": "4"},
                correct_answer="A",
                explanation="Exp",
                source_document_id="SRC-CSO-NAS-SM-2012",
                source_page=5,
                source_excerpt="Excerpt",
                difficulty="operational",
            )
        )

    # Missing option key
    with pytest.raises(QuestionValidationError, match="Options must have keys"):
        validator.validate_question(
            SourceQuestion(
                question_id="Q-ERR-2",
                competency_id="KCM-FUNC-11",
                competency_name="Data Analytics",
                question_text="Valid text?",
                options={"A": "1", "B": "2", "C": "3"},  # Missing D
                correct_answer="A",
                explanation="Exp",
                source_document_id="SRC-CSO-NAS-SM-2012",
                source_page=5,
                source_excerpt="Excerpt",
                difficulty="operational",
            )
        )

    # Duplicate options
    with pytest.raises(QuestionValidationError, match="Options must be distinct"):
        validator.validate_question(
            SourceQuestion(
                question_id="Q-ERR-3",
                competency_id="KCM-FUNC-11",
                competency_name="Data Analytics",
                question_text="Valid text?",
                options={"A": "Same", "B": "Same", "C": "Other", "D": "Fourth"},
                correct_answer="A",
                explanation="Exp",
                source_document_id="SRC-CSO-NAS-SM-2012",
                source_page=5,
                source_excerpt="Excerpt",
                difficulty="operational",
            )
        )


# ============================================================================
# 2. Correct-Answer Secrecy Before Submission
# ============================================================================

def test_correct_answers_not_leaked_at_assessment_start(client: TestClient):
    """Confirm server scrubs correct answers, explanations, and excerpts before delivery."""
    res = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-001", "competency_id": "KCM-FUNC-11", "question_count": 5},
    )
    assert res.status_code == 200
    data = res.json()

    assert "attempt_id" in data
    assert data["competency_id"] == "KCM-FUNC-11"
    assert len(data["questions"]) == 5

    for q in data["questions"]:
        # Must not contain correct_answer, explanation, or source_excerpt!
        assert "correct_answer" not in q
        assert "explanation" not in q
        assert "source_excerpt" not in q
        # Must contain question_id, text, options, and difficulty
        assert "question_id" in q
        assert "question_text" in q
        assert "options" in q
        assert set(q["options"].keys()) == {"A", "B", "C", "D"}


# ============================================================================
# 3. Server-Side Grading, Feedback, and Explanations
# ============================================================================

def test_server_grades_submission_truthfully(client: TestClient):
    """Test full assessment submission: server grades answers and returns grounded citations."""
    start_res = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-001", "competency_id": "KCM-FUNC-11", "question_count": 5},
    )
    assert start_res.status_code == 200
    session = start_res.json()
    attempt_id = session["attempt_id"]
    questions = session["questions"]

    # Deliberately submit 4 correct answers and 1 incorrect answer
    answers = {}
    for idx, q in enumerate(questions):
        # Look up true answer from bank for testing
        source_q = question_bank.get_question_by_id(q["question_id"])
        assert source_q is not None
        if idx == 0:
            # Pick a wrong answer
            wrong = "A" if source_q.correct_answer != "A" else "B"
            answers[q["question_id"]] = wrong
        else:
            answers[q["question_id"]] = source_q.correct_answer

    sub_res = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={"attempt_id": attempt_id, "learner_id": "LEARNER-001", "answers": answers},
    )
    assert sub_res.status_code == 200
    result = sub_res.json()

    assert result["score"] == 4
    assert result["total_questions"] == 5
    assert result["percentage"] == 80
    assert result["passed_threshold"] is True

    # Confirm feedback has citations and excerpts
    feedback = result["questions_feedback"]
    assert len(feedback) == 5
    for fb in feedback:
        assert "correct_answer" in fb
        assert "explanation" in fb
        assert "source_document_id" in fb
        assert "source_page" in fb
        assert "source_excerpt" in fb
        assert len(fb["source_excerpt"]) > 0

    # Confirm provisional estimate is returned
    estimate = result["provisional_estimate"]
    assert estimate["sufficiency_status"] == "sufficient"
    assert estimate["estimated_level"] in [3, 4]
    assert estimate["confidence_score"] >= 0.70


def test_reject_duplicate_and_unknown_submissions(client: TestClient):
    """Verify that submitting to non-existent attempt returns 404, and duplicate returns 400."""
    # Unknown attempt
    bad_res = client.post(
        "/api/assessment/ATT-NONEXISTENT/submit",
        json={"attempt_id": "ATT-NONEXISTENT", "learner_id": "LEARNER-001", "answers": {}},
    )
    assert bad_res.status_code == 404

    # Duplicate submission
    start_res = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-001", "competency_id": "KCM-FUNC-11", "question_count": 3},
    )
    attempt_id = start_res.json()["attempt_id"]

    sub1 = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={"attempt_id": attempt_id, "learner_id": "LEARNER-001", "answers": {}},
    )
    assert sub1.status_code == 200

    sub2 = client.post(
        f"/api/assessment/{attempt_id}/submit",
        json={"attempt_id": attempt_id, "learner_id": "LEARNER-001", "answers": {}},
    )
    assert sub2.status_code == 400
    assert "already been submitted" in sub2.json()["detail"]


# ============================================================================
# 4. Diagnostic Estimator Heuristics & Boundary Tests
# ============================================================================

def test_estimator_flags_insufficient_evidence():
    """Verify that fewer than 3 questions strictly returns insufficient_evidence."""
    estimator = DiagnosticEstimator()
    q1 = question_bank.get_question_by_id("Q-NAS-001")
    q2 = question_bank.get_question_by_id("Q-NAS-002")

    # Only 2 questions
    estimate = estimator.estimate_provisional_competency(
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics",
        graded_questions=[(q1, True), (q2, True)],
        previous_level=None,
    )

    assert estimate.sufficiency_status == "insufficient_evidence"
    assert estimate.estimated_level is None
    assert estimate.confidence_score < 0.30
    assert "Insufficient assessment evidence" in estimate.diagnostic_summary


def test_estimator_assigns_level_4_for_advanced_mastery():
    """Verify high performance across advanced questions produces Level 4/5 estimate."""
    estimator = DiagnosticEstimator()
    q_fnd = question_bank.get_question_by_id("Q-NAS-001")
    q_op = question_bank.get_question_by_id("Q-NAS-002")
    q_adv = question_bank.get_question_by_id("Q-NAS-003")

    estimate = estimator.estimate_provisional_competency(
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics",
        graded_questions=[(q_fnd, True), (q_op, True), (q_adv, True)],
        previous_level=1,
    )

    assert estimate.sufficiency_status == "sufficient"
    assert estimate.estimated_level in [4, 5]
    assert estimate.confidence_score >= 0.60


def test_estimator_assigns_level_1_for_poor_performance():
    """Verify zero correct answers places candidate at Level 1 (Foundation/Awareness)."""
    estimator = DiagnosticEstimator()
    q_fnd = question_bank.get_question_by_id("Q-NAS-001")
    q_op = question_bank.get_question_by_id("Q-NAS-002")
    q_adv = question_bank.get_question_by_id("Q-NAS-003")

    estimate = estimator.estimate_provisional_competency(
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics",
        graded_questions=[(q_fnd, False), (q_op, False), (q_adv, False)],
        previous_level=None,
    )

    assert estimate.sufficiency_status == "sufficient"
    assert estimate.estimated_level == 1


# ============================================================================
# 5. Deterministic Adaptive Question Selection
# ============================================================================

def test_deterministic_adaptive_branching():
    """Verify selector branches to advanced upon correct answer and foundation upon error."""
    selector = AdaptiveQuestionSelector()
    pool = question_bank.get_questions_for_competency("KCM-FUNC-11")

    # If last question was correct -> should pick advanced
    next_q = selector.select_next_adaptive_question(
        pool=pool, answered_ids=["Q-NAS-001"], last_was_correct=True
    )
    assert next_q is not None
    assert next_q.difficulty == "advanced"

    # If last question was incorrect -> should pick foundation
    next_q_fail = selector.select_next_adaptive_question(
        pool=pool, answered_ids=["Q-NAS-002"], last_was_correct=False
    )
    assert next_q_fail is not None
    assert next_q_fail.difficulty == "foundation"


# ============================================================================
# 6. End-to-End Learner Provisional Level Update
# ============================================================================

def test_unassessed_learner_receives_provisional_estimate_and_updates_skill_gaps(client: TestClient):
    """
    Verify full end-to-end flow:
    1. Check unassessed recruit Pooja Verma (LEARNER-003) has 0 assessed competencies.
    2. Start diagnostic assessment in KCM-FUNC-11.
    3. Submit correct answers.
    4. Confirm skill gaps update dynamically, turning KCM-FUNC-11 from unassessed to assessed!
    """
    # 1. Pre-check gaps
    pre_gaps = client.get("/api/learners/LEARNER-003/skill-gaps").json()
    assert pre_gaps["unassessed_count"] == 4
    func11_pre = next(g for g in pre_gaps["gaps"] if g["competency_id"] == "KCM-FUNC-11")
    assert func11_pre["status"] == "unassessed"
    assert func11_pre["estimated_level"] is None

    # 2. Start assessment
    start_res = client.post(
        "/api/assessment/start",
        json={"learner_id": "LEARNER-003", "competency_id": "KCM-FUNC-11", "question_count": 4},
    )
    attempt = start_res.json()
    att_id = attempt["attempt_id"]

    # 3. Submit all correct answers
    answers = {}
    for q in attempt["questions"]:
        sq = question_bank.get_question_by_id(q["question_id"])
        assert sq is not None
        answers[q["question_id"]] = sq.correct_answer

    sub_res = client.post(
        f"/api/assessment/{att_id}/submit",
        json={"attempt_id": att_id, "learner_id": "LEARNER-003", "answers": answers},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["provisional_estimate"]["estimated_level"] is not None
    assert sub_data["provisional_estimate"]["sufficiency_status"] == "sufficient"

    # 4. Post-check gaps: KCM-FUNC-11 is now assessed!
    post_gaps = client.get("/api/learners/LEARNER-003/skill-gaps").json()
    assert post_gaps["unassessed_count"] == 3  # Reduced from 4 to 3!
    func11_post = next(g for g in post_gaps["gaps"] if g["competency_id"] == "KCM-FUNC-11")
    assert func11_post["status"] != "unassessed"
    assert func11_post["estimated_level"] is not None
    assert func11_post["estimated_level"] >= 3
