"""
Final Demo Gate: Targeted Regression Test Suite.
Verifies the critical demo gate checks:
1. Assessment-to-role consistency (elective topic assessment does not corrupt role requirements).
2. Demo identity boundary mechanics (learner mismatch rejection, persona switching behavior, trainer/admin restrictions, invented string rejection).
3. Trainer draft editing, persistence, quarantine of rejected items, and publication of approved edits.
"""

import pytest
from fastapi.testclient import TestClient

from competency_engine.api import (
    app,
    gap_engine,
    question_bank,
    question_review_store,
    repository,
)
from competency_engine.models import DraftQuestion


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# 1. Assessment-to-Role Consistency
# ============================================================================

def test_assessment_to_role_consistency():
    """Verify elective assessment updates only the targeted competency without corrupting role-required competencies."""
    repository.load_all()
    learner_id = "LEARNER-001"
    learner = repository.get_learner(learner_id)
    assert learner is not None
    role = repository.get_role(learner.role_id)
    assert role is not None

    # Role required competencies for ROLE-SSO-SO
    role_comp_ids = [rc.competency_id for rc in role.required_competencies]
    assert "KCM-FUNC-05" not in role_comp_ids, "KCM-FUNC-05 should not be in ROLE-SSO-SO required competencies"

    # Capture initial state of role-required competencies
    initial_role_estimates = {
        ac.competency_id: ac.estimated_level
        for ac in learner.assessed_competencies
        if ac.competency_id in role_comp_ids
    }

    # Simulate assessment on KCM-FUNC-05 (Project Management)
    success = repository.update_learner_provisional_assessment(
        learner_id=learner_id,
        competency_id="KCM-FUNC-05",
        estimated_level=3,
        confidence=0.75,
        evidence_source="Targeted Regression Test",
    )
    assert success is True

    # Verify KCM-FUNC-05 is recorded
    current_learner = repository.get_learner(learner_id)
    assessed_func05 = next(
        (ac for ac in current_learner.assessed_competencies if ac.competency_id == "KCM-FUNC-05"),
        None,
    )
    assert assessed_func05 is not None
    assert assessed_func05.estimated_level == 3
    assert assessed_func05.is_provisional is True

    # Verify NONE of the role-required competencies were modified or corrupted
    current_role_estimates = {
        ac.competency_id: ac.estimated_level
        for ac in current_learner.assessed_competencies
        if ac.competency_id in role_comp_ids
    }
    assert current_role_estimates == initial_role_estimates

    # Verify skill gap report evaluates strictly role-required competencies
    gap_report = gap_engine.compute_skill_gaps(current_learner, role, repository)
    report_comp_ids = [g.competency_id for g in gap_report.gaps]
    assert report_comp_ids == role_comp_ids
    assert "KCM-FUNC-05" not in report_comp_ids


# ============================================================================
# 2. Demo Identity Boundary
# ============================================================================

def test_demo_identity_boundary_mechanics(client):
    """
    Verify identity boundary mechanics:
    1. Cross-learner access with mismatched header is rejected with 403.
    2. Caller-controlled header switches persona (proving it is a demo persona selector, not cryptographic auth).
    3. Regular learner identities are rejected from trainer authoring routes.
    4. Arbitrary invented identity strings are rejected from trainer authoring routes.
    5. Regular learner identities are rejected from admin analytics routes.
    6. Legitimate demo admin/trainer personas succeed.
    """
    # 1. Mismatched header rejected
    res_mismatch = client.get("/api/learners/LEARNER-002", headers={"X-Learner-ID": "LEARNER-001"})
    assert res_mismatch.status_code == 403
    assert "Access denied" in res_mismatch.json()["detail"]

    # 2. Caller changing header to LEARNER-002 succeeds (no password/token required)
    res_match = client.get("/api/learners/LEARNER-002", headers={"X-Learner-ID": "LEARNER-002"})
    assert res_match.status_code == 200
    assert res_match.json()["learner_id"] == "LEARNER-002"

    # 3. Learner attempting trainer write is rejected even if learner_id matches
    res_trainer = client.post(
        "/api/trainer/generate-questions",
        json={"document_id": "DOC-001", "competency_id": "KCM-FUNC-11", "question_count": 2},
        headers={"X-Learner-ID": "LEARNER-002"},
    )
    assert res_trainer.status_code == 403
    assert "not authorized to perform trainer authoring actions" in res_trainer.json()["detail"]

    # 4. Arbitrary invented identity string is rejected from trainer endpoints
    res_invented = client.post(
        "/api/trainer/generate-questions",
        json={"document_id": "DOC-001", "competency_id": "KCM-FUNC-11", "question_count": 2},
        headers={"X-Learner-ID": "GUEST_UNAUTHORIZED"},
    )
    assert res_invented.status_code == 403
    assert "not recognized as an authorized trainer or administrator persona" in res_invented.json()["detail"]

    # 5. Regular learner attempting to access admin analytics is rejected with 403
    res_admin_learner = client.get(
        "/api/admin/analytics",
        headers={"X-Learner-ID": "LEARNER-001"},
    )
    assert res_admin_learner.status_code == 403
    assert "not authorized to access administrative analytics" in res_admin_learner.json()["detail"]

    # 6. Legitimate demo admin persona succeeds
    res_admin_legit = client.get(
        "/api/admin/analytics",
        headers={"X-Learner-ID": "ADMIN"},
    )
    assert res_admin_legit.status_code == 200
    assert "assessment_coverage" in res_admin_legit.json()


# ============================================================================
# 3. Trainer Draft Editing, Quarantine, and Publication
# ============================================================================

def test_trainer_draft_editing_and_publication(client):
    """Verify that draft editing updates content, persists, and publishes the edited version while isolating drafts."""
    draft_id = "DRF-TEST-EDIT-001"
    initial_draft = DraftQuestion(
        question_id=draft_id,
        document_id="DOC-EDIT-TEST",
        source_document_id="SRC-DOC-EDIT-TEST",
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics & Estimation",
        question_text="Initial unedited draft question text?",
        options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
        correct_answer="B",
        explanation="Initial explanation before trainer editing.",
        source_page=2,
        source_excerpt="National accounts estimation guidelines.",
        difficulty="operational",
        status="draft",
    )
    question_review_store._drafts[draft_id] = initial_draft

    # Also create a rejected draft
    rej_id = "DRF-TEST-REJECT-001"
    rejected_draft = DraftQuestion(
        question_id=rej_id,
        document_id="DOC-EDIT-TEST",
        source_document_id="SRC-DOC-EDIT-TEST",
        competency_id="KCM-FUNC-11",
        competency_name="Data Analytics & Estimation",
        question_text="Defective question that must be rejected?",
        options={"A": "Wrong", "B": "Wrong", "C": "Wrong", "D": "Correct"},
        correct_answer="D",
        explanation="Defective question rationale.",
        source_page=3,
        source_excerpt="Source text.",
        difficulty="operational",
        status="draft",
    )
    question_review_store._drafts[rej_id] = rejected_draft

    # 1. Edit the first draft via review API
    edited_text = "FINAL APPROVED: What is the primary measure of domestic capital formation in national accounts?"
    edited_exp = "FINAL APPROVED EXPLANATION: Gross fixed capital formation represents net additions to fixed assets."
    edit_payload = {
        "action": "edit",
        "reviewed_by": "trainer_lead",
        "edited_question": {
            "question_text": edited_text,
            "explanation": edited_exp,
        },
    }
    res_edit = client.post(
        f"/api/trainer/drafts/{draft_id}/review",
        json=edit_payload,
        headers={"X-Learner-ID": "TRAINER"},
    )
    assert res_edit.status_code == 200
    updated_draft = res_edit.json()
    assert updated_draft["question_text"] == edited_text
    assert updated_draft["explanation"] == edited_exp
    assert updated_draft["status"] == "approved"
    assert updated_draft["validation_status"] == "verified"

    # 2. Reject the second draft
    res_rej = client.post(
        f"/api/trainer/drafts/{rej_id}/review",
        json={"action": "reject", "reviewed_by": "trainer_lead", "rejection_reason": "Factually ambiguous distractor."},
        headers={"X-Learner-ID": "TRAINER"},
    )
    assert res_rej.status_code == 200
    assert res_rej.json()["status"] == "rejected"

    # 3. Verify neither is in live assessment QuestionBank before publication
    active_q_ids_before = [q.question_id for q in question_bank.get_questions_for_competency("KCM-FUNC-11")]
    assert draft_id not in active_q_ids_before
    assert rej_id not in active_q_ids_before

    # 4. Publish approved questions
    res_pub = client.post(
        "/api/trainer/publish",
        json={"question_ids": [draft_id, rej_id], "published_by": "trainer_lead"},
        headers={"X-Learner-ID": "TRAINER"},
    )
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert pub_data["published_count"] == 1  # Only the approved one was published; rejected was excluded!
    assert draft_id in pub_data["published_ids"]
    assert rej_id not in pub_data["published_ids"]

    # 5. Verify the published question in QuestionBank has the EDITED content
    published_q = question_bank.get_question_by_id(draft_id)
    assert published_q is not None
    assert published_q.question_text == edited_text
    assert published_q.explanation == edited_exp

    # 6. Verify rejected draft remains excluded from live question bank
    assert question_bank.get_question_by_id(rej_id) is None
