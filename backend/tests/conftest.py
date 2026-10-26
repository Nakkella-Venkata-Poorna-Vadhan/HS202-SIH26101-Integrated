"""
Pytest configuration and test isolation fixtures for SIH26101-Integrated.
Ensures tests use temporary directories and never pollute the working demo's assessment history.
"""

from __future__ import annotations

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from competency_engine.api import (
    app,
    assessment_store,
    document_service,
    question_bank,
    question_review_store,
    repository,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_test_assessments(tmp_path: Path):
    """
    Ensure each test runs with isolated assessment storage, upload directories,
    draft stores, and fresh repository state, guaranteeing test runs never
    modify working demo data.
    """
    # 1. AssessmentStore
    orig_assessments_dir = assessment_store.assessments_dir
    orig_attempts_path = assessment_store.attempts_path
    orig_estimates_path = assessment_store.estimates_path
    orig_attempts = dict(assessment_store._attempts)
    orig_estimates = dict(assessment_store._estimates)

    test_assessments_dir = tmp_path / "assessments"
    test_attempts_path = test_assessments_dir / "attempts.json"
    test_estimates_path = test_assessments_dir / "provisional_estimates.json"

    assessment_store.assessments_dir = test_assessments_dir
    assessment_store.attempts_path = test_attempts_path
    assessment_store.estimates_path = test_estimates_path
    assessment_store._attempts = {}
    assessment_store._estimates = {}
    assessment_store._ensure_storage()

    # 2. DocumentService
    orig_uploads_dir = document_service.uploads_dir
    orig_docs_dir = document_service.docs_dir
    orig_extracted_dir = document_service.extracted_dir
    orig_reg_path = document_service.registry_path
    orig_doc_reg = dict(document_service._registry)

    test_uploads_dir = tmp_path / "uploads"
    document_service.uploads_dir = test_uploads_dir
    document_service.docs_dir = test_uploads_dir / "documents"
    document_service.extracted_dir = test_uploads_dir / "extracted"
    document_service.registry_path = test_uploads_dir / "registry.json"
    document_service._registry = {}
    document_service._ensure_storage()

    # 3. QuestionReviewStore
    orig_drafts_path = question_review_store.drafts_path
    orig_drafts = dict(question_review_store._drafts)

    test_drafts_path = tmp_path / "questions" / "draft_questions.json"
    question_review_store.drafts_path = test_drafts_path
    question_review_store._drafts = {}
    question_review_store._ensure_storage()

    # 4. QuestionBank
    orig_bank_path = question_bank.bank_path
    orig_bank_questions = dict(question_bank._questions)
    orig_bank_by_comp = {k: list(v) for k, v in question_bank._by_competency.items()}

    test_bank_path = tmp_path / "questions" / "question_bank.json"
    question_bank.bank_path = test_bank_path
    question_bank.load_bank()

    # 5. Repository
    repository.estimates_path = test_estimates_path
    repository.load_all()

    try:
        yield
    finally:
        # Restore references
        assessment_store.assessments_dir = orig_assessments_dir
        assessment_store.attempts_path = orig_attempts_path
        assessment_store.estimates_path = orig_estimates_path
        assessment_store._attempts = orig_attempts
        assessment_store._estimates = orig_estimates

        document_service.uploads_dir = orig_uploads_dir
        document_service.docs_dir = orig_docs_dir
        document_service.extracted_dir = orig_extracted_dir
        document_service.registry_path = orig_reg_path
        document_service._registry = orig_doc_reg

        question_review_store.drafts_path = orig_drafts_path
        question_review_store._drafts = orig_drafts

        question_bank.bank_path = orig_bank_path
        question_bank._questions = orig_bank_questions
        question_bank._by_competency = orig_bank_by_comp

        repository.estimates_path = orig_estimates_path
        repository.load_all()
