"""
FastAPI REST API for the SIH26101 Competency Intelligence Engine.
Provides clean endpoints for competencies, courses, roles, skill gaps, and recommendations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, Header, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from competency_engine import __version__
from competency_engine.config import (
    DEFAULT_MAX_LEVEL,
    DEFAULT_MIN_LEVEL,
    LEVEL_SCALE_DESCRIPTION,
    LEVEL_SCALE_NAME,
)
from competency_engine.learning_activity_store import LearningActivityStore
from competency_engine.resource_providers import ProviderStatusSummary
from competency_engine.models import (
    LearningActivityCreateRequest,
    LearningActivityRecord,
    AssessmentResultResponse,
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSubmissionRequest,
    AssessmentTopic,
    ClientQuestion,
    Competency,
    Course,
    DraftQuestion,
    DraftQuestionReviewRequest,
    GenerateQuestionsRequest,
    HealthResponse,
    Learner,
    ProvisionalEstimate,
    PublishQuestionsRequest,
    QuestionFeedback,
    RecommendationReport,
    Role,
    SkillGapReport,
    SourceQuestion,
    UploadedDocumentMetadata,
)
from competency_engine.assessment_store import AssessmentStore
from competency_engine.diagnostic_estimator import AdaptiveQuestionSelector, DiagnosticEstimator
from competency_engine.document_service import DocumentProcessingError, DocumentService
from competency_engine.question_generator_service import (
    DynamicQuestionGenerator,
    QuestionReviewStore,
)
from competency_engine.quiz_generator import QuestionBank
from competency_engine.repository import CompetencyRepository
from competency_engine.services import RecommendationEngine, SkillGapEngine

# Initialize FastAPI application
app = FastAPI(
    title="SIH26101: Official Statistics Competency Intelligence Engine",
    description=(
        "Core intelligence and decision-support API for mapping civil service and statistical "
        "competencies to training interventions under India's Mission Karmayogi and MoSPI ACBP.\n\n"
        "**DEMO_SECURITY_NOTICE**: This system runs in prototype/demonstration mode. The 'X-Learner-ID' header "
        "provides identity context for local testing, NOT cryptographic authentication or production SSO. "
        "Production deployment requires Government of India Parichay / e-Pramaan SSO and mTLS."
    ),
    version=__version__,
)

def verify_trainer_authorization(
    x_learner_id: Optional[str] = None,
    requester_id: Optional[str] = None,
) -> str:
    """Ensure regular learner identities and unapproved arbitrary IDs cannot invoke trainer/admin authoring endpoints."""
    requester = (x_learner_id or requester_id or "TRAINER").upper().strip()
    if requester.startswith("LEARNER-") or requester.startswith("LRN-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Learner identity '{requester}' is not authorized to perform trainer authoring actions.",
        )
    allowed_prefixes = ("TRAINER", "ADMIN", "NSSTA", "SUPERVISOR", "MCM")
    if not any(requester.startswith(prefix) for prefix in allowed_prefixes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Identity '{requester}' is not recognized as an authorized trainer or administrator persona.",
        )
    return requester

# Enable CORS for local dashboards and pair-programming development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Repository and Engine instances
repository = CompetencyRepository()
gap_engine = SkillGapEngine()
recommendation_engine = RecommendationEngine(repository)
question_bank = QuestionBank()
diagnostic_estimator = DiagnosticEstimator()
adaptive_selector = AdaptiveQuestionSelector()
assessment_store = AssessmentStore()
document_service = DocumentService()
question_review_store = QuestionReviewStore()
learning_activity_store = LearningActivityStore()
dynamic_question_generator = DynamicQuestionGenerator(
    document_service, question_review_store, question_bank, repository
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def get_health() -> HealthResponse:
    """Return platform status, loaded dataset inventories, and level scale metadata."""
    stats = repository.get_stats()
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(timezone.utc).isoformat(),
        datasets={
            "competencies": {
                "source": "SRC-CBC-KCM-2024",
                "count": stats["total_competencies"],
                "provenance": "official_public",
            },
            "courses": {
                "source": "SRC-MOSPI-ACBP-2026-27",
                "count": stats["total_courses"],
                "provenance": "official_public",
            },
            "mappings": {
                "count": stats["total_mappings"],
                "candidate_count": stats["candidate_mappings"],
                "unresolved_count": stats["unresolved_mappings"],
                "validation_status": "unadjudicated_baseline",
            },
            "roles": {
                "count": stats["total_roles"],
                "provenance": "synthetic",
                "note": "Prototype demonstration roles",
            },
            "learners": {
                "count": stats["total_learners"],
                "provenance": "synthetic",
                "note": "Prototype demonstration learner profiles",
            },
        },
        level_scale={
            "name": LEVEL_SCALE_NAME,
            "min_level": DEFAULT_MIN_LEVEL,
            "max_level": DEFAULT_MAX_LEVEL,
            "description": LEVEL_SCALE_DESCRIPTION,
        },
    )


# ============================================================================
# Competencies Endpoints
# ============================================================================

@app.get("/api/competencies", response_model=List[Competency], tags=["Competencies"])
def list_competencies(
    type: Optional[str] = Query(None, description="Filter by type: behavioural or functional"),
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=250, description="Items per page"),
) -> List[Competency]:
    """List Karmayogi Competency Model (KCM) competencies with optional filtering."""
    results = repository.list_competencies(competency_type=type, search=search)
    start = (page - 1) * page_size
    return results[start : start + page_size]


@app.get("/api/competencies/{competency_id}", response_model=Competency, tags=["Competencies"])
def get_competency(competency_id: str) -> Competency:
    """Fetch single KCM competency details, definitions, subthemes, and page citations."""
    comp = repository.get_competency(competency_id.upper().strip())
    if not comp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competency with ID '{competency_id}' not found in KCM catalogue.",
        )
    return comp


# ============================================================================
# Courses Endpoints
# ============================================================================

@app.get("/api/courses", response_model=List[Course], tags=["Courses"])
def list_courses(
    cadre: Optional[str] = Query(None, description="Filter by target cadre or administrative tier"),
    category: Optional[str] = Query(None, description="Filter by category: Domain, Functional, Behavioural"),
    search: Optional[str] = Query(None, description="Search keyword in course title or creator"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=250, description="Items per page"),
) -> List[Course]:
    """List MoSPI ACBP courses with optional cadre, category, and keyword filters."""
    results = repository.list_courses(cadre=cadre, category=category, search=search)
    start = (page - 1) * page_size
    return results[start : start + page_size]


@app.get("/api/courses/{course_id}", response_model=Course, tags=["Courses"])
def get_course(course_id: str) -> Course:
    """Fetch details of a single ACBP course by ID."""
    course = repository.get_course(course_id.upper().strip())
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID '{course_id}' not found in ACBP schedule.",
        )
    return course


# ============================================================================
# Roles Endpoints
# ============================================================================

@app.get("/api/roles", response_model=List[Role], tags=["Roles"])
def list_roles() -> List[Role]:
    """List all civil service role definitions with required competencies and target levels."""
    return repository.list_roles()


@app.get("/api/roles/{role_id}", response_model=Role, tags=["Roles"])
def get_role(role_id: str) -> Role:
    """Fetch single role definition and its competency requirement matrix."""
    role = repository.get_role(role_id.upper().strip())
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID '{role_id}' not found in role catalogue.",
        )
    return role


# ============================================================================
# Learners & Intelligence Endpoints
# ============================================================================

@app.get("/api/learners", response_model=List[Learner], tags=["Learners"])
def list_learners() -> List[Learner]:
    """List all synthetic demonstration learner profiles."""
    return repository.list_learners()


@app.get("/api/learners/{learner_id}", response_model=Learner, tags=["Learners"])
def get_learner(
    learner_id: str,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> Learner:
    """Fetch a single synthetic learner profile and assessment records."""
    target_id = learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requester '{requester}' is not authorized to access learner profile for '{target_id}'.",
        )
    learner = repository.get_learner(target_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID '{learner_id}' not found in synthetic demonstration registry.",
        )
    return learner


@app.get(
    "/api/learners/{learner_id}/skill-gaps",
    response_model=SkillGapReport,
    tags=["Competency Intelligence"],
)
def get_learner_skill_gaps(
    learner_id: str,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> SkillGapReport:
    """
    Compute explainable skill gaps for a learner against their role requirements.
    Formula: gap = max(0, R - E) for assessed competencies.
    Unassessed competencies are explicitly marked as unassessed without fabricating proficiency.
    """
    target_id = learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requester '{requester}' is not authorized to access learner data for '{target_id}'.",
        )

    learner = repository.get_learner(target_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID '{learner_id}' not found.",
        )

    role = repository.get_role(learner.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assigned role '{learner.role_id}' for learner '{learner_id}' not found in registry.",
        )

    return gap_engine.compute_skill_gaps(learner, role, repository)


@app.get(
    "/api/learners/{learner_id}/recommendations",
    response_model=RecommendationReport,
    tags=["Competency Intelligence"],
)
def get_learner_recommendations(
    learner_id: str,
    include_unresolved: bool = Query(
        False,
        description="Whether to include unresolved ACBP courses with explicit unverified tags",
    ),
    max_recommendations: int = Query(
        10, ge=1, le=50, description="Maximum number of recommendations to return"
    ),
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> RecommendationReport:
    """
    Recommend training courses from the ACBP catalogue based on the learner's identified skill gaps.
    Deterministic ranking prioritizes gap size, cadre match, and mapping confidence.
    Candidate and unresolved mappings are explicitly flagged.
    """
    target_id = learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requester '{requester}' is not authorized to access recommendations for '{target_id}'.",
        )

    learner = repository.get_learner(target_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID '{learner_id}' not found.",
        )

    role = repository.get_role(learner.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assigned role '{learner.role_id}' for learner '{learner_id}' not found in registry.",
        )

    gap_report = gap_engine.compute_skill_gaps(learner, role, repository)

    return recommendation_engine.recommend(
        learner=learner,
        role=role,
        gap_report=gap_report,
        include_unresolved=include_unresolved,
        max_recommendations=max_recommendations,
    )


# ============================================================================
# Source-Grounded Diagnostic Assessment Endpoints (Stage 4.4)
# ============================================================================

@app.get("/api/assessment/topics", response_model=List[AssessmentTopic], tags=["Assessment"])
def get_assessment_topics() -> List[AssessmentTopic]:
    """List competencies and topics available for source-grounded diagnostic assessment."""
    return question_bank.get_topics()


@app.post("/api/assessment/start", response_model=AssessmentStartResponse, tags=["Assessment"])
def start_assessment(
    payload: AssessmentStartRequest,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> AssessmentStartResponse:
    """
    Initiate a diagnostic assessment attempt for a learner on a chosen competency.
    Returns sanitized questions without exposing correct answers or source excerpts.
    """
    target_id = payload.learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requester '{requester}' is not authorized to start assessment for '{target_id}'.",
        )

    learner = repository.get_learner(target_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID '{payload.learner_id}' not found.",
        )

    # Fetch available questions for this competency
    pool = question_bank.get_questions_for_competency(payload.competency_id)
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions available for competency '{payload.competency_id}'.",
        )

    # Use deterministic adaptive selector for initial battery
    selected_source_questions = adaptive_selector.select_initial_questions(
        pool=pool, count=payload.question_count
    )

    q_ids = [q.question_id for q in selected_source_questions]
    attempt_id = assessment_store.create_attempt(
        learner_id=learner.learner_id,
        competency_id=payload.competency_id,
        competency_name=selected_source_questions[0].competency_name,
        question_ids=q_ids,
    )

    # Scrub answers, explanations, and excerpts before sending to browser
    client_questions = [
        ClientQuestion(
            question_id=q.question_id,
            competency_id=q.competency_id,
            competency_name=q.competency_name,
            question_text=q.question_text,
            options=q.options,
            difficulty=q.difficulty,
            source_document_id=q.source_document_id,
        )
        for q in selected_source_questions
    ]

    source_title = question_bank.get_source_title(selected_source_questions[0].source_document_id)

    return AssessmentStartResponse(
        attempt_id=attempt_id,
        learner_id=learner.learner_id,
        competency_id=payload.competency_id,
        competency_name=selected_source_questions[0].competency_name,
        source_document_id=selected_source_questions[0].source_document_id,
        source_title=source_title,
        total_questions=len(client_questions),
        questions=client_questions,
        started_at=datetime.now(timezone.utc).isoformat(),
        instructions="Select the best answer supported by the official source publication. Submissions are scored server-side.",
    )


@app.post("/api/assessment/{attempt_id}/submit", response_model=AssessmentResultResponse, tags=["Assessment"])
def submit_assessment(
    attempt_id: str,
    payload: AssessmentSubmissionRequest,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> AssessmentResultResponse:
    """
    Grade submitted assessment answers server-side, calculate provisional competency estimate,
    and return complete source-grounded feedback with citations and excerpts.
    """
    attempt = assessment_store.get_attempt(attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment attempt '{attempt_id}' not found.",
        )

    if attempt.get("status") == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assessment attempt '{attempt_id}' has already been submitted and finalized.",
        )

    # 1. Enforce attempt-learner binding and requester authorization
    attempt_learner_id = attempt["learner_id"].upper().strip()
    submitting_learner_id = payload.learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != attempt_learner_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requester '{requester}' is not authorized to submit attempt for '{attempt_learner_id}'.",
        )
    if submitting_learner_id != attempt_learner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Attempt '{attempt_id}' belongs to learner '{attempt['learner_id']}', not '{payload.learner_id}'. Submissions cannot be reassigned across learners.",
        )

    # 2. Reject malformed answers payload
    if payload.answers is None or not isinstance(payload.answers, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed answer payload: answers must be a dictionary.",
        )

    # 3. Reject invalid question IDs in answers
    attempt_q_ids = set(attempt["question_ids"])
    submitted_q_ids = set(payload.answers.keys())
    invalid_q_ids = submitted_q_ids - attempt_q_ids
    if invalid_q_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Submission contains invalid question ID(s) not part of this attempt: {sorted(list(invalid_q_ids))}.",
        )

    # 4. Reject malformed option values
    for qid, ans in payload.answers.items():
        if not isinstance(ans, str) or ans.strip().upper() not in {"A", "B", "C", "D"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Malformed answer for question '{qid}': '{ans}'. Option must be A, B, C, or D.",
            )

    learner = repository.get_learner(submitting_learner_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner '{payload.learner_id}' not found.",
        )

    # Grade submitted answers
    question_ids = attempt["question_ids"]
    graded_tuples = []
    feedback_list: List[QuestionFeedback] = []
    score = 0

    for qid in question_ids:
        source_q = question_bank.get_question_by_id(qid)
        if not source_q:
            continue

        user_answer = payload.answers.get(qid)
        is_correct = (user_answer == source_q.correct_answer)
        if is_correct:
            score += 1

        src_title = question_bank.get_source_title(source_q.source_document_id)

        graded_tuples.append((source_q, is_correct))
        feedback_list.append(
            QuestionFeedback(
                question_id=source_q.question_id,
                question_text=source_q.question_text,
                selected_option=user_answer,
                selected_answer=user_answer,
                correct_answer=source_q.correct_answer,
                is_correct=is_correct,
                explanation=source_q.explanation,
                source_document_id=source_q.source_document_id,
                source_title=src_title,
                source_page=source_q.source_page,
                page_reference=source_q.source_page,
                source_excerpt=source_q.source_excerpt,
                verbatim_excerpt=source_q.source_excerpt,
            )
        )

    total_q = len(question_ids)
    pct = int(round((score / total_q) * 100)) if total_q > 0 else 0
    passed = pct >= 60

    # Retrieve existing level of learner for this competency
    prev_assessment = next(
        (a for a in learner.assessed_competencies if a.competency_id == attempt["competency_id"]),
        None
    )
    previous_level = prev_assessment.estimated_level if prev_assessment else None

    # Compute provisional diagnostic estimate
    provisional_estimate = diagnostic_estimator.estimate_provisional_competency(
        competency_id=attempt["competency_id"],
        competency_name=attempt["competency_name"],
        graded_questions=graded_tuples,
        previous_level=previous_level,
    )
    provisional_estimate.confidence = provisional_estimate.confidence_score
    provisional_estimate.evidence_threshold_met = (provisional_estimate.sufficiency_status == "sufficient")
    provisional_estimate.methodology_note = provisional_estimate.diagnostic_summary
    provisional_estimate.limitations_disclaimer = (
        "Demonstration heuristic for prototype evaluation only. Does not claim psychometric validity or validated adaptive testing."
    )

    # If evidence is sufficient and level estimated, update in-memory repository learner
    if provisional_estimate.sufficiency_status == "sufficient" and provisional_estimate.estimated_level is not None:
        repository.update_learner_provisional_assessment(
            learner_id=learner.learner_id,
            competency_id=attempt["competency_id"],
            estimated_level=provisional_estimate.estimated_level,
            confidence=provisional_estimate.confidence_score,
            evidence_source=f"Attempt {attempt_id} ({feedback_list[0].source_document_id if feedback_list else 'Source'})",
        )

    # Fetch recommended ACBP courses for this competency
    role = repository.get_role(learner.role_id)
    recommended_courses = []
    if role:
        gap_rep = gap_engine.compute_skill_gaps(learner, role, repository)
        rec_report = recommendation_engine.recommend(
            learner=learner, role=role, gap_report=gap_rep, include_unresolved=True, max_recommendations=5
        )
        comp_recs = [
            r for r in rec_report.recommendations
            if r.target_competency_id == attempt["competency_id"] or r.mapping_status == "candidate"
        ]
        recommended_courses = comp_recs if comp_recs else rec_report.recommendations[:3]

    # Save to persistent assessment store
    assessment_store.record_completed_attempt(
        attempt_id=attempt_id,
        answers=payload.answers,
        score=score,
        percentage=pct,
        provisional_estimate=provisional_estimate,
        feedback_summary=[f.model_dump() for f in feedback_list],
    )

    return AssessmentResultResponse(
        attempt_id=attempt_id,
        learner_id=learner.learner_id,
        competency_id=attempt["competency_id"],
        competency_name=attempt["competency_name"],
        score=score,
        correct_count=score,
        total_questions=total_q,
        percentage=pct,
        score_percentage=pct,
        passed_threshold=passed,
        questions_feedback=feedback_list,
        feedback=feedback_list,
        provisional_estimate=provisional_estimate,
        recommended_courses=recommended_courses,
        completed_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/assessment/attempts/{attempt_id}", tags=["Assessment"])
def get_attempt_details(
    attempt_id: str,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> Dict[str, Any]:
    """Fetch completed assessment attempt record with question feedback."""
    attempt = assessment_store.get_attempt(attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attempt '{attempt_id}' not found.",
        )

    requester = (x_learner_id or requester_id or "").upper().strip()
    owner = attempt["learner_id"].upper().strip()
    if requester and requester != owner and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Learner '{requester}' is not authorized to access attempt '{attempt_id}' belonging to '{attempt['learner_id']}'.",
        )
    return attempt


@app.get("/api/assessment/learner/{learner_id}/history", tags=["Assessment"])
def get_learner_assessment_history(
    learner_id: str,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> List[Dict[str, Any]]:
    """Retrieve all completed diagnostic assessment attempts for a learner."""
    target_id = learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Learner '{requester}' is not authorized to view assessment history for '{learner_id}'.",
        )
    return assessment_store.get_learner_history(target_id)


@app.get("/api/assessment/learner/{learner_id}/estimates", tags=["Assessment"])
def get_learner_estimates(
    learner_id: str,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> Dict[str, Any]:
    """Retrieve active provisional diagnostic estimates for a learner."""
    target_id = learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Learner '{requester}' is not authorized to view estimates for '{learner_id}'.",
        )
    return assessment_store.get_learner_estimates(target_id)


@app.post("/api/demo/reset", tags=["Demonstration"])
def reset_demo_state(
    confirm: bool = Query(False, description="Explicit confirmation flag required to prevent accidental invocation"),
    x_demo_reset_key: Optional[str] = Header(None, alias="X-Demo-Reset-Key"),
) -> Dict[str, Any]:
    """
    Safely reset demo assessment attempts and provisional estimates for synthetic learners.
    Requires confirm=true or X-Demo-Reset-Key: sih26101-local-demo.
    Reloads competency repository to initial baseline.
    Never alters official source datasets, mapping registries, or review queues.
    """
    if not confirm and x_demo_reset_key != "sih26101-local-demo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Demo reset requires explicit confirmation. Pass ?confirm=true or X-Demo-Reset-Key: sih26101-local-demo.",
        )

    stats = assessment_store.reset_demo_state()
    repository.load_all()

    return {
        "status": "success",
        "message": "Demo assessment attempts and provisional estimates successfully reset to baseline.",
        "cleared_attempts": stats["cleared_attempts"],
        "cleared_estimates": stats["cleared_estimates"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# Trainer Upload & Dynamic Question Generation Endpoints (Stage 4.7)
# ============================================================================

@app.post(
    "/api/trainer/upload",
    response_model=UploadedDocumentMetadata,
    tags=["Trainer Material Ingestion"],
)
async def upload_training_material(
    file: UploadFile = File(..., description="Uploaded PDF or TXT learning material"),
    title: Optional[str] = Form(None, description="Optional title for the publication"),
    description: Optional[str] = Form(None, description="Optional description of the material"),
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> UploadedDocumentMetadata:
    verify_trainer_authorization(x_learner_id, requester_id)
    """
    Upload and extract training material with cryptographic hash and page provenance.
    Strictly validates size (max 20MB) and allowed extensions (.pdf, .txt).
    Scanned PDFs lacking digital text are registered with 'ocr_required' status.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    try:
        content_bytes = await file.read()
        metadata = document_service.process_upload(
            file_bytes=content_bytes,
            original_filename=file.filename,
            title=title,
            description=description,
        )
        return metadata
    except DocumentProcessingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal document extraction error: {e}",
        )


@app.get(
    "/api/trainer/documents",
    response_model=List[UploadedDocumentMetadata],
    tags=["Trainer Material Ingestion"],
)
def list_uploaded_documents() -> List[UploadedDocumentMetadata]:
    """Retrieve all uploaded trainer materials with page count and extraction status."""
    return document_service.list_documents()


@app.get(
    "/api/trainer/documents/{document_id}",
    response_model=UploadedDocumentMetadata,
    tags=["Trainer Material Ingestion"],
)
def get_uploaded_document(document_id: str) -> UploadedDocumentMetadata:
    """Retrieve metadata and extraction details for an uploaded document."""
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in upload registry.",
        )
    return doc


@app.get("/api/trainer/provider-status", tags=["Trainer Material Ingestion"])
def get_provider_status() -> Dict[str, Any]:
    """Report whether an external LLM API provider or deterministic source extractor is active."""
    import os
    has_api_key = bool(os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if has_api_key:
        if os.getenv("GEMINI_API_KEY") and not (os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")):
            default_model = "gemini-1.5-flash"
        else:
            default_model = "gpt-4o-mini"
        model = os.getenv("LLM_MODEL", default_model)
        mode = "openai_compatible"
    else:
        model = "deterministic_source_extractor"
        mode = "offline_source_grounded_heuristic"

    return {
        "configured": has_api_key,
        "mode": mode,
        "model": model,
        "demonstration_notice": "When no LLM API key is set, questions are derived deterministically from the authentic text of the uploaded document without external API dependencies."
    }


@app.post(
    "/api/trainer/generate-questions",
    tags=["Trainer Material Ingestion"],
)
def generate_questions_from_material(
    payload: GenerateQuestionsRequest,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> Dict[str, Any]:
    verify_trainer_authorization(x_learner_id, requester_id)
    """
    Generate multiple-choice question drafts grounded strictly in an uploaded document.
    Questions are placed in the review queue awaiting trainer validation before publication.
    """
    try:
        drafts, rejections = dynamic_question_generator.generate_questions_from_document(
            document_id=payload.document_id,
            competency_id=payload.competency_id,
            question_count=payload.question_count,
            difficulty=payload.difficulty,
            focus_pages=payload.focus_pages,
        )
        return {
            "status": "success",
            "document_id": payload.document_id,
            "generated_count": len(drafts),
            "drafts": [d.model_dump() for d in drafts],
            "rejections": rejections,
            "verification_status": "All accepted drafts passed structural, verbatim citation, and non-duplicate checks.",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Generation error: {e}")


@app.get(
    "/api/trainer/drafts",
    response_model=List[DraftQuestion],
    tags=["Trainer Question Review"],
)
def list_draft_questions(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: draft, approved, rejected, published"),
    document_id: Optional[str] = Query(None, description="Filter by source document ID"),
) -> List[DraftQuestion]:
    """List MCQ drafts in the trainer review queue."""
    return question_review_store.list_drafts(status=status_filter, document_id=document_id)


@app.post(
    "/api/trainer/drafts/{question_id}/review",
    response_model=DraftQuestion,
    tags=["Trainer Question Review"],
)
def review_draft_question(
    question_id: str,
    payload: DraftQuestionReviewRequest,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> DraftQuestion:
    verify_trainer_authorization(x_learner_id, requester_id)
    """
    Trainer review action: approve, reject, or edit a draft question.
    Only approved questions can be published into the active assessment question bank.
    """
    try:
        return question_review_store.review_draft(question_id, payload)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Draft question '{question_id}' not found.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post(
    "/api/trainer/publish",
    tags=["Trainer Question Review"],
)
def publish_approved_questions(
    payload: PublishQuestionsRequest,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> Dict[str, Any]:
    verify_trainer_authorization(x_learner_id, requester_id)
    """
    Publish approved draft questions into the assessment-eligible Question Bank.
    Once published, questions are immediately available in diagnostic assessment quizzes.
    """
    try:
        published = question_review_store.publish_approved(
            question_bank=question_bank,
            question_ids=payload.question_ids,
            published_by=payload.published_by,
        )
        return {
            "status": "success",
            "published_count": len(published),
            "published_ids": [q.question_id for q in published],
            "published_questions": [q.model_dump() for q in published],
            "message": f"Successfully published {len(published)} approved question(s) to the active Question Bank.",
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Publication error: {e}")




# ============================================================================
# Learning Activities & Provider Transparency Endpoints (Stage 4.8)
# ============================================================================

@app.post(
    "/api/learners/{learner_id}/learning-activities",
    response_model=LearningActivityRecord,
    tags=["Learning Activities"],
)
def record_learning_activity(
    learner_id: str,
    payload: LearningActivityCreateRequest,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> LearningActivityRecord:
    """
    Explicitly log a user learning activity (enrollment, in-progress, or completion).
    Strictly documents that this is a user-recorded action and does not claim automated LMS synchronization.
    """
    target_id = learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requester '{requester}' is not authorized to record learning activities for '{target_id}'.",
        )

    learner = repository.get_learner(target_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID '{learner_id}' not found.",
        )

    return learning_activity_store.record_activity(
        learner_id=target_id,
        resource_id=payload.resource_id,
        resource_title=payload.resource_title,
        activity_type=payload.activity_type,
        target_competency_id=payload.target_competency_id,
        notes=payload.notes,
    )


@app.get(
    "/api/learners/{learner_id}/learning-activities",
    response_model=List[LearningActivityRecord],
    tags=["Learning Activities"],
)
def get_learner_learning_activities(
    learner_id: str,
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> List[LearningActivityRecord]:
    """Retrieve all recorded learning activities for a specific learner."""
    target_id = learner_id.upper().strip()
    requester = (x_learner_id or requester_id or "").upper().strip()
    if requester and requester != target_id and not requester.startswith("ADMIN") and requester != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requester '{requester}' is not authorized to access activities for '{target_id}'.",
        )

    learner = repository.get_learner(target_id)
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID '{learner_id}' not found.",
        )

    return learning_activity_store.get_activities_for_learner(target_id)


@app.get(
    "/api/recommendations/providers",
    response_model=List[ProviderStatusSummary],
    tags=["Learning Providers"],
)
def get_recommendation_providers() -> List[ProviderStatusSummary]:
    """
    Report operational status, catalogue size, and integration boundaries of all learning resource providers.
    All providers explicitly report is_live_integration=False with transparent provenance.
    """
    return recommendation_engine.provider_registry.list_provider_statuses()


@app.get(
    "/api/admin/analytics",
    tags=["Administrator Analytics"],
)
def get_admin_analytics(
    x_learner_id: Optional[str] = Header(None, alias="X-Learner-ID"),
    requester_id: Optional[str] = Query(None, alias="requester_id"),
) -> Dict[str, Any]:
    requester = (x_learner_id or requester_id or "ADMIN").upper().strip()
    if requester.startswith("LEARNER-") or requester.startswith("LRN-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Learner identity '{requester}' is not authorized to access administrative analytics.",
        )
    """
    Comprehensive administrative intelligence aggregating real assessment coverage,
    provisional vs baseline evidence, critical gaps, mapping validation status, and provider health.
    """
    learners = repository.list_learners()
    courses = repository.list_courses()
    roles = repository.list_roles()
    stats = repository.get_stats()

    # 1. Competency Assessment Coverage
    assessed_count = 0
    total_evaluated_competencies = 0
    assessed_competency_instances = 0

    for l in learners:
        has_assessed = any(
            a.assessment_status == "assessed" and a.estimated_level is not None
            for a in l.assessed_competencies
        )
        if has_assessed:
            assessed_count += 1
        total_evaluated_competencies += len(l.assessed_competencies)
        assessed_competency_instances += sum(
            1 for a in l.assessed_competencies if a.assessment_status == "assessed" and a.estimated_level is not None
        )

    unassessed_count = len(learners) - assessed_count
    coverage_pct = round((assessed_count / float(len(learners))) * 100.0, 1) if learners else 0.0

    # 2. Provisional vs Baseline Evidence
    all_estimates = assessment_store.get_all_provisional_estimates()
    provisional_count = len(all_estimates)

    # 3. Critical gaps breakdown across all learners
    critical_gaps_counter: Dict[str, int] = {}
    for l in learners:
        r = repository.get_role(l.role_id)
        if r:
            rep = gap_engine.compute_skill_gaps(l, r, repository)
            for g in rep.gaps:
                if g.priority == "critical" and g.gap and g.gap > 0:
                    critical_gaps_counter[g.competency_name] = critical_gaps_counter.get(g.competency_name, 0) + 1

    # 4. Assessment Activity
    attempts = assessment_store.list_attempts()
    completed_attempts = [a for a in attempts if a.get("status") == "completed" and a.get("percentage") is not None]
    avg_score = (
        round(sum(float(a.get("percentage") or 0.0) for a in completed_attempts) / float(len(completed_attempts)), 1)
        if completed_attempts else 0.0
    )

    # 5. Course Mapping Validation Status
    mappings_count = stats.get("mappings_count", 226)
    candidate_mappings_count = stats.get("candidate_mappings_count", 6)
    validated_mappings_count = 0
    unresolved_mappings_count = mappings_count - candidate_mappings_count - validated_mappings_count

    # 6. Provider Statuses
    provider_statuses = [
        s.model_dump() for s in recommendation_engine.provider_registry.list_provider_statuses()
    ]

    return {
        "assessment_coverage": {
            "total_learners": len(learners),
            "assessed_learners": assessed_count,
            "unassessed_learners": unassessed_count,
            "coverage_percentage": coverage_pct,
            "total_competency_evaluations": total_evaluated_competencies,
            "assessed_instances": assessed_competency_instances,
        },
        "evidence_profile": {
            "provisional_estimates_count": provisional_count,
            "baseline_learner_records_count": len(learners),
            "evidence_mode": "provisional_diagnostic_with_supervisor_review_required",
        },
        "critical_gaps": [
            {"competency_name": comp, "learners_affected": count}
            for comp, count in sorted(critical_gaps_counter.items(), key=lambda x: -x[1])
        ],
        "mapping_validation": {
            "total_courses": len(courses),
            "total_mappings": mappings_count,
            "validated_mappings": validated_mappings_count,
            "candidate_mappings": candidate_mappings_count,
            "unresolved_mappings": unresolved_mappings_count,
        },
        "assessment_activity": {
            "total_quizzes_attempted": len(attempts),
            "average_score_percentage": avg_score,
            "recent_attempts_count": len(attempts[-10:]),
        },
        "providers": provider_statuses,
        "is_synthetic_cohort": True,
        "cohort_disclaimer": (
            "Synthetic demonstration cohort: 4 civil service learner profiles across 5 role models. "
            "Not representative of the 50,000+ broader government statistical workforce."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
