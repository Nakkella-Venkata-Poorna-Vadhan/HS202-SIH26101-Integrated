"""
Pydantic Domain Models for the Competency Intelligence Engine.
Preserves official schemas from KCM and ACBP datasets while clearly tagging synthetic data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Official Data Models (KCM & ACBP)
# ============================================================================

class Competency(BaseModel):
    """Karmayogi Competency Model (KCM) record."""
    competency_id: str = Field(..., description="Unique KCM identifier (e.g. KCM-BEH-01, KCM-FUNC-11)")
    competency_name: str = Field(..., description="Official title of the competency")
    competency_type: Literal["behavioural", "functional"] = Field(..., description="Category in KCM")
    description: str = Field(..., description="Official definition of the competency")
    behaviours: List[str] = Field(default_factory=list, description="Sub-themes / behavioural indicators")
    level_information: Optional[Any] = Field(default=None, description="Explicit level information from source if any")
    source_id: str = Field(..., description="Source document register ID")
    source_page: List[int] = Field(default_factory=list, description="Source page numbers")
    provenance: str = Field(default="official_public", description="Data provenance classification")
    validation_status: str = Field(default="pending_review", description="Official validation state")
    extraction_notes: Optional[str] = Field(default=None, description="Curator / extraction notes")


class Course(BaseModel):
    """MoSPI Annual Capacity Building Plan (ACBP) course record."""
    record_id: str = Field(..., description="Unique course identifier (e.g. ACBP-CRS-001)")
    interim_record_id: Optional[str] = None
    cadre_role: str = Field(..., description="Target civil service cadre or administrative tier")
    course_name: str = Field(..., description="Official course title in ACBP schedule")
    competency_category: Literal["Domain", "Functional", "Behavioural"] = Field(..., description="Category in ACBP")
    duration: str = Field(..., description="Course duration string (HH.MM.SS or HH:MM.SS)")
    course_creator: str = Field(..., description="Listed course creator or provider institution")
    source_id: str = Field(..., description="Source document register ID")
    source_page: Optional[int] = None
    source_row: Optional[str] = None
    provenance: str = Field(default="official_public", description="Data provenance classification")
    validation_status: str = Field(default="pending_review", description="Validation status")
    is_uncertain: bool = False
    review_notes: Optional[str] = None


class CourseMapping(BaseModel):
    """Course-to-competency mapping registry record."""
    mapping_id: str = Field(..., description="Unique mapping identifier (e.g. MAP-ACBP-KCM-001)")
    course_record_id: str = Field(..., description="Referenced ACBP course ID")
    cadre_role: str = Field(..., description="Cadre string from course")
    course_name: str = Field(..., description="Course title")
    acbp_competency_category: str = Field(..., description="ACBP category")
    candidate_kcm_competency_id: Optional[str] = Field(default=None, description="Target KCM ID if mapped")
    candidate_kcm_competency_name: Optional[str] = None
    candidate_kcm_subtheme: Optional[str] = None
    candidate_kcm_competency_type: Optional[str] = None
    mapping_type: str = Field(..., description="Mapping type: exact_title_reference, unresolved, etc.")
    mapping_method: str = Field(..., description="Method: verbatim_title_containment, unresolved_domain_gap, etc.")
    evidence_or_rationale: str = Field(..., description="Curator rationale or evidentiary finding")
    confidence_score: Optional[float] = None
    validation_status: str = Field(..., description="Validation status: unresolved, pending_review, validated")
    course_source_id: str = Field(..., description="Source ID of course")
    kcm_source_id: Optional[str] = None


# ============================================================================
# Role & Learner Models (Synthetic Profiles clearly tagged)
# ============================================================================

class RoleRequirement(BaseModel):
    """Target competency level required for a specific role."""
    competency_id: str = Field(..., description="Referenced KCM competency ID")
    competency_name: str = Field(..., description="Competency title")
    required_level: int = Field(..., ge=1, le=5, description="Required proficiency level (1-5)")
    priority: Literal["critical", "high", "medium", "low"] = Field(
        default="high", description="Operational priority for this role"
    )
    rationale: str = Field(..., description="Explanation of why this competency is required for the role")


class Role(BaseModel):
    """Civil service role / job profile with competency requirements."""
    role_id: str = Field(..., description="Unique role identifier (e.g. ROLE-SSO-SO)")
    role_name: str = Field(..., description="Designation name")
    cadre_role: str = Field(..., description="Matching ACBP cadre string for course cross-referencing")
    description: str = Field(..., description="Job duties and operational scope")
    department: str = Field(default="MoSPI", description="Ministry or Directorate")
    required_competencies: List[RoleRequirement] = Field(default_factory=list)
    is_synthetic: bool = Field(default=True, description="Always True for prototype demonstration roles")
    provenance: str = Field(default="synthetic", description="Provenance marker: synthetic")


class CompetencyAssessment(BaseModel):
    """A learner's assessed level for a competency."""
    competency_id: str = Field(..., description="Referenced KCM competency ID")
    estimated_level: Optional[int] = Field(
        default=None, ge=1, le=5, description="Estimated level (1-5) or None if unassessed"
    )
    assessment_status: Literal["assessed", "partially_assessed", "unassessed"] = Field(
        default="unassessed", description="Assessment state"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence in this assessment (0.0 to 1.0)"
    )
    evidence_sources: List[str] = Field(
        default_factory=list, description="List of evidence items (e.g. synthetic_quiz_score, supervisor_review)"
    )
    last_assessed_date: Optional[str] = None
    assessment_method: Optional[str] = Field(
        default=None, description="Assessment method used, e.g. diagnostic_quiz_assessment"
    )
    is_provisional: bool = Field(
        default=False, description="True if derived from prototype diagnostic quiz assessment"
    )


class Learner(BaseModel):
    """Learner profile with assessed competencies and assigned role."""
    learner_id: str = Field(..., description="Unique learner identifier (e.g. LEARNER-001)")
    name: str = Field(..., description="Learner name")
    role_id: str = Field(..., description="Assigned role ID")
    cadre_role: str = Field(..., description="Civil service cadre")
    department: str = Field(..., description="Subordinate office or ministry division")
    assessed_competencies: List[CompetencyAssessment] = Field(default_factory=list)
    is_synthetic: bool = Field(default=True, description="Always True for prototype demonstration learners")
    provenance: str = Field(default="synthetic", description="Provenance marker: synthetic")


# ============================================================================
# Engine Output Models (Gaps & Recommendations)
# ============================================================================

class SkillGap(BaseModel):
    """Explainable skill gap for a single competency."""
    competency_id: str
    competency_name: str
    competency_type: str
    required_level: int
    estimated_level: Optional[int] = None
    gap: Optional[int] = None
    status: Literal["gap_identified", "competent", "unassessed"]
    priority: Literal["critical", "high", "medium", "low"]
    confidence: Optional[float] = None
    evidence_sources: List[str] = Field(default_factory=list)
    is_synthetic_estimate: bool = True
    is_provisional: bool = False
    explanation: str


class SkillGapReport(BaseModel):
    """Comprehensive skill-gap report for a learner against their role."""
    learner_id: str
    learner_name: str
    role_id: str
    role_name: str
    cadre_role: str
    department: str
    scale_min: int = 1
    scale_max: int = 5
    scale_description: str
    total_required_competencies: int
    gap_count: int
    competent_count: int
    unassessed_count: int
    gaps: List[SkillGap]
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CourseRecommendation(BaseModel):
    """Ranked course recommendation linked to an identified gap with full explainability."""
    rank: int
    course_id: str
    course_name: str
    cadre_role: str
    target_cadre_match: bool
    target_competency_id: Optional[str] = None
    target_competency_name: Optional[str] = None
    competency_category: str
    duration: str
    course_creator: str
    mapping_type: str
    mapping_status: Literal["validated", "candidate", "unresolved"]
    is_verified_mapping: bool
    provenance: str
    score: float
    recommendation_reason: str
    resource_type: str = "course"
    provider_source: str = "MoSPI ACBP (Local)"
    mapping_evidence: Optional[str] = None
    difficulty_fit: str = "Appropriate"
    difficulty_provenance: str = "heuristic_cadre_estimate"
    prerequisite_fit: str = "Prerequisites satisfied or none required"
    limitations_or_uncertainties: str = ""


class RecommendationReport(BaseModel):
    """Collection of recommended courses for a learner."""
    learner_id: str
    learner_name: str
    role_id: str
    total_gaps_addressed: int
    recommendations: List[CourseRecommendation]
    filtered_unresolved_count: int
    include_unresolved_requested: bool
    ranking_method: str = "hybrid_explainable"
    providers_consulted: List[str] = Field(default_factory=lambda: [
        "MoSPI ACBP Local Catalogue",
        "NSSTA Public Programmes & Curriculum",
        "iGOT Karmayogi Public Directory Metadata"
    ])
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LearningActivityRecord(BaseModel):
    """Explicitly recorded user learning activity without claiming automated external LMS sync."""
    activity_id: str
    learner_id: str
    resource_id: str
    resource_title: str
    target_competency_id: Optional[str] = None
    activity_type: Literal["planned", "enrolled", "in_progress", "completed", "reassessment_completed", "reference_consulted"]
    activity_status_label: str = "Learner-reported action"
    verification_status: Literal["self_reported_unverified", "diagnostic_assessment_verified", "supervisor_validated"] = "self_reported_unverified"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    notes: str = ""
    is_live_sync: bool = False
    evidence_disclaimer: str = (
        "Recorded via deliberate user activity logging. Does not represent automated LMS completion "
        "sync or verified competency level reassessment. Self-reported action does not imply "
        "verified completion in iGOT or NSSTA, nor does it automatically alter competency estimates."
    )


class LearningActivityCreateRequest(BaseModel):
    """Payload to record a deliberate learning activity."""
    resource_id: str
    resource_title: str
    target_competency_id: Optional[str] = None
    activity_type: Literal["planned", "enrolled", "in_progress", "completed", "reassessment_completed", "reference_consulted"] = "enrolled"
    notes: str = ""


class HealthResponse(BaseModel):
    """System health check and dataset inventory."""
    status: str
    version: str
    timestamp: str
    datasets: Dict[str, Any]
    level_scale: Dict[str, Any]


# ============================================================================
# Source-Grounded Diagnostic Assessment Models (Stage 4.4)
# ============================================================================

class SourceQuestion(BaseModel):
    """Authoritative source-grounded assessment question in the question bank."""
    question_id: str
    competency_id: str
    competency_name: str
    question_text: str
    options: Dict[str, str] = Field(..., description="Map of 'A', 'B', 'C', 'D' to option text")
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str
    source_document_id: str
    source_page: int
    source_excerpt: str = Field(..., description="Verbatim supporting text excerpt from the source publication")
    difficulty: Literal["foundation", "operational", "advanced"]
    provenance: str = "source_grounded_verified"
    validation_status: Literal["verified", "flagged_for_review"] = "verified"


class ClientQuestion(BaseModel):
    """Sanitized question delivered to learner browser before submission. Never reveals answer or excerpt."""
    question_id: str
    competency_id: str
    competency_name: str
    question_text: str
    options: Dict[str, str]
    difficulty: Literal["foundation", "operational", "advanced"]
    source_document_id: str


class AssessmentTopic(BaseModel):
    """Topic or competency available for diagnostic assessment."""
    competency_id: str
    competency_name: str
    competency_type: str
    description: str
    source_document_id: str
    source_title: str
    available_questions_count: int


class AssessmentStartRequest(BaseModel):
    """Payload to initiate a diagnostic assessment session."""
    learner_id: str
    competency_id: str
    question_count: int = Field(default=5, ge=1, le=10)


class AssessmentStartResponse(BaseModel):
    """Active diagnostic session returned to client with questions scrubbed of answers."""
    attempt_id: str
    learner_id: str
    competency_id: str
    competency_name: str
    source_document_id: str
    source_title: str = ""
    total_questions: int
    questions: List[ClientQuestion]
    started_at: str
    instructions: str = "Select the best answer supported by the official source publication. Answers are evaluated server-side."



class AssessmentSubmissionRequest(BaseModel):
    """Payload submitted by learner containing their chosen answers."""
    attempt_id: str
    learner_id: str
    answers: Dict[str, Literal["A", "B", "C", "D"]] = Field(
        ..., description="Map of question_id to selected answer option"
    )


class QuestionFeedback(BaseModel):
    """Source-grounded post-submission feedback for a single question."""
    question_id: str
    question_text: str
    selected_option: Optional[Literal["A", "B", "C", "D"]] = None
    selected_answer: Optional[Literal["A", "B", "C", "D"]] = None
    correct_answer: Literal["A", "B", "C", "D"]
    is_correct: bool
    explanation: str
    source_document_id: str
    source_title: str = ""
    source_page: int
    page_reference: Optional[int] = None
    source_excerpt: str
    verbatim_excerpt: Optional[str] = None


class ProvisionalEstimate(BaseModel):
    """Transparent heuristic provisional competency level estimate."""
    competency_id: str
    competency_name: str
    estimated_level: Optional[int] = None
    previous_level: Optional[int] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence: Optional[float] = None
    evidence_count: int
    sufficiency_status: Literal["sufficient", "insufficient_evidence"]
    evidence_threshold_met: Optional[bool] = None
    diagnostic_summary: str
    methodology_note: Optional[str] = None
    limitations_disclaimer: Optional[str] = None
    scale_min: int = 1
    scale_max: int = 5
    is_statutory_standard: bool = False


class AssessmentResultResponse(BaseModel):
    """Comprehensive diagnostic evaluation returned upon assessment completion."""
    attempt_id: str
    learner_id: str
    competency_id: str
    competency_name: str
    score: int
    correct_count: Optional[int] = None
    total_questions: int
    percentage: int
    score_percentage: Optional[int] = None
    passed_threshold: bool
    questions_feedback: List[QuestionFeedback]
    feedback: List[QuestionFeedback] = Field(default_factory=list)
    provisional_estimate: ProvisionalEstimate
    completed_at: str


# ============================================================================
# Dynamic Assessment & Upload Models (Stage 4.7)
# ============================================================================

class UploadedDocumentMetadata(BaseModel):
    """Metadata for trainer-uploaded learning material."""
    document_id: str
    filename: str
    file_type: Literal["pdf", "txt"]
    file_size_bytes: int
    sha256: str
    uploaded_at: str
    extraction_status: Literal["extracted", "ocr_required", "extraction_failed"]
    page_count: int
    character_count: int
    provenance: str = "trainer_uploaded_material"
    title: str
    description: Optional[str] = None
    extraction_error: Optional[str] = None


class DocumentPageChunk(BaseModel):
    """Segmented text chunk with document and page provenance."""
    chunk_id: str
    document_id: str
    page_number: int
    character_count: int
    text: str


class GenerateQuestionsRequest(BaseModel):
    """Request payload to generate MCQ drafts from an uploaded document."""
    document_id: str
    competency_id: Optional[str] = None
    question_count: int = Field(default=3, ge=1, le=10)
    difficulty: Optional[Literal["foundation", "operational", "advanced"]] = None
    focus_pages: Optional[List[int]] = None


class DraftQuestion(BaseModel):
    """Generated draft multiple-choice question pending trainer review."""
    question_id: str
    document_id: str
    source_document_id: str
    competency_id: str
    competency_name: str
    question_text: str
    options: Dict[str, str] = Field(..., description="Map of 'A', 'B', 'C', 'D' to option text")
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str
    source_page: int
    source_excerpt: str
    difficulty: Literal["foundation", "operational", "advanced"]
    status: Literal["draft", "approved", "rejected", "published"] = "draft"
    provenance: str = "dynamic_source_generated"
    validation_status: Literal["verified", "flagged_for_review"] = "flagged_for_review"
    verification_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DraftQuestionReviewRequest(BaseModel):
    """Trainer action to approve, reject, or edit a draft question."""
    action: Literal["approve", "reject", "edit"]
    reviewed_by: str = "trainer_admin"
    rejection_reason: Optional[str] = None
    edited_question: Optional[Dict[str, Any]] = None


class PublishQuestionsRequest(BaseModel):
    """Request payload to commit approved draft questions to the assessment question bank."""
    question_ids: Optional[List[str]] = Field(default=None, description="List of approved question IDs to publish. If omitted, publishes all approved drafts.")
    published_by: str = "trainer_admin"

