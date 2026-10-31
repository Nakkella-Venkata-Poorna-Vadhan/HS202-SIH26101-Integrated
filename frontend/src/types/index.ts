export type PageRoute = 
  | 'login'
  | 'dashboard'
  | 'weekly-progress'
  | 'competency-assessment'
  | 'skill-gap'
  | 'recommendations'
  | 'course-details'
  | 'quiz'
  | 'history'
  | 'profile'
  | 'admin'

  | 'pending-approval';

export type UserRole = 'employee' | 'admin' | 'project_staff';

export interface AuthUser {
  id: string;
  email: string;
  account_type: 'EMPLOYEE' | 'ADMINISTRATOR' | 'PROJECT_STAFF';
  account_status: 'UNVERIFIED_EMAIL' | 'ACTIVE' | 'SUSPENDED' | 'DEACTIVATED';
  is_approved: boolean;
  profile?: Record<string, any> | null;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token: string;
  user: AuthUser;
}

export interface EmployeeApplicationStatus {
  user_id: string;
  email: string;
  account_status: string;
  approval_status: string;
  has_profile: boolean;
  employee_code?: string;
  full_name?: string;
  application_id?: string;
  application_status?: string;
  submission_number?: number;
  approved_at?: string;
  assigned_admin_name?: string;
}

export interface OrgTaxonomy {
  ministries: Array<{ id: string; name: string; code: string }>;
  departments: Array<{ id: string; ministry_id: string; name: string; code: string }>;
  cadres: Array<{ id: string; name: string; controlling_authority: string }>;
  grade_bands: Array<{ id: string; name: string; rank: number }>;
  designations: Array<{ id: string; name: string; grade_band_id: string; cadre_id?: string }>;
  zones: Array<{ id: string; name: string; code: string }>;
  states: Array<{ id: string; zone_id: string; name: string; code: string }>;
  locations: Array<{ id: string; state_id: string; zone_id: string; city: string; building_name: string }>;
}

export interface UserProfile {
  name: string;
  employeeId: string;
  department: string;
  designation: string;
  jobRole: string;
  experience: string;
  education: string;
  email: string;
  phone: string;
  location: string;
  learningPreferences: string[];
  currentGoals: string[];
  avatarUrl?: string;
  isSynthetic?: boolean;
}

export interface CompetencyScore {
  name: string;
  current: number; // percentage or level
  required: number; // percentage or level
  gap: number; // percentage or level
  category: 'Statistical' | 'Technical' | 'Digital Governance' | 'Behavioural & Managerial' | 'Functional' | 'Behavioural' | 'Domain';
  level: 'strong' | 'developing' | 'needs-improvement' | 'critical-gap' | 'unassessed';
  trend?: string;
  competencyId?: string;
  priority?: 'critical' | 'high' | 'medium' | 'low';
  explanation?: string;
}

export interface DayProgress {
  day: string;
  shortDay: string;
  date: string;
  hours: number;
  targetHours: number;
  completedTasks: string[];
}

export interface WeeklyBreakdownItem {
  id: string;
  course: string;
  timeSpent: string;
  hoursSpent: number;
  progress: number; // percentage
  category: string;
}

export interface ActivityTimelineItem {
  id: string;
  day: string;
  date: string;
  title: string;
  type: 'module' | 'quiz' | 'training' | 'none';
  completed: boolean;
  score?: string;
  duration?: string;
}

export interface CourseModule {
  id: number;
  title: string;
  duration: string;
  completed: boolean;
  type: 'video' | 'interactive' | 'reading' | 'quiz';
}

export interface Course {
  id: string;
  title: string;
  instructor: string;
  organization: string;
  duration: string;
  difficulty: 'Beginner' | 'Beginner → Intermediate' | 'Intermediate' | 'Advanced';
  skillCategory: string;
  progress: number;
  rating: number;
  totalModules: number;
  completedModules: number;
  description: string;
  recommendationReason?: string;
  priority?: 'High' | 'Medium' | 'Standard' | 'Critical';
  targetGapReduction?: string;
  mappingStatus?: 'validated' | 'candidate' | 'unresolved';
  targetCompetencyId?: string;
  targetCompetencyName?: string;
  cadreRole?: string;
  provenance?: string;
  resourceType?: string;
  providerSource?: string;
  mappingEvidence?: string | null;
  difficultyFit?: string;
  prerequisiteFit?: string;
  limitationsOrUncertainties?: string;
  modules: CourseModule[];
}

export interface QuizQuestionItem {
  id: number;
  question: string;
  options: {
    key: 'A' | 'B' | 'C' | 'D';
    text: string;
  }[];
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
}

export interface QuizSubmissionState {
  completed: boolean;
  score: number;
  totalQuestions: number;
  percentage: number;
  skillName: string;
  previousSkillScore: number;
  newSkillScore: number;
  userAnswers: Record<number, 'A' | 'B' | 'C' | 'D'>;
  feedback: string;
}

export interface Quiz {
  id: string;
  courseId: string;
  title: string;
  subject: string;
  relatedSkill: string;
  timeLimitMinutes: number;
  questions: QuizQuestionItem[];
}

export interface LearningHistoryRecord {
  id: string;
  date: string;
  course: string;
  activity: 'Module' | 'Quiz' | 'Interactive Lab' | 'Assessment' | 'Workshop';
  duration: string;
  score: string;
  status: 'Completed' | 'In Progress' | 'Evaluated';
  skill: string;
}

export interface AdminEmployee {
  id: string;
  name: string;
  employeeId: string;
  department: string;
  role: string;
  competency: number;
  skillGapsCount: number;
  weeklyHours: number;
  status: 'Active' | 'On Track' | 'Needs Attention' | 'Exceeding Target';
  isSynthetic?: boolean;
  assessedCount?: number;
  totalRequired?: number;
}

// ============================================================================
// Official Backend Intelligence API Schemas
// ============================================================================

export interface BackendCompetency {
  competency_id: string;
  competency_name: string;
  competency_type: 'behavioural' | 'functional';
  description: string;
  behaviours: string[];
  level_information?: any;
  source_id: string;
  source_page: number[];
  provenance: string;
  validation_status: string;
  extraction_notes?: string;
}

export interface BackendCourse {
  record_id: string;
  interim_record_id?: string;
  cadre_role: string;
  course_name: string;
  competency_category: 'Domain' | 'Functional' | 'Behavioural';
  duration: string;
  course_creator: string;
  source_id: string;
  source_page?: number;
  source_row?: string;
  provenance: string;
  validation_status: string;
  is_uncertain: boolean;
  review_notes?: string;
}

export interface BackendRoleRequirement {
  competency_id: string;
  competency_name: string;
  required_level: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  rationale: string;
}

export interface BackendRole {
  role_id: string;
  role_name: string;
  cadre_role: string;
  description: string;
  department: string;
  required_competencies: BackendRoleRequirement[];
  is_synthetic: boolean;
  provenance: string;
}

export interface BackendCompetencyAssessment {
  competency_id: string;
  estimated_level?: number | null;
  assessment_status: 'assessed' | 'partially_assessed' | 'unassessed';
  confidence: number;
  evidence_sources: string[];
  last_assessed_date?: string | null;
}

export interface BackendLearner {
  learner_id: string;
  name: string;
  role_id: string;
  cadre_role: string;
  department: string;
  assessed_competencies: BackendCompetencyAssessment[];
  is_synthetic: boolean;
  provenance: string;
}

export interface BackendSkillGap {
  competency_id: string;
  competency_name: string;
  competency_type: string;
  required_level: number;
  estimated_level?: number | null;
  gap?: number | null;
  status: 'gap_identified' | 'competent' | 'unassessed';
  priority: 'critical' | 'high' | 'medium' | 'low';
  confidence?: number | null;
  evidence_sources: string[];
  is_synthetic_estimate: boolean;
  is_provisional?: boolean;
  explanation: string;
}

export interface BackendSkillGapReport {
  learner_id: string;
  learner_name: string;
  role_id: string;
  role_name: string;
  cadre_role: string;
  department: string;
  scale_min: number;
  scale_max: number;
  scale_description: string;
  total_required_competencies: number;
  gap_count: number;
  competent_count: number;
  unassessed_count: number;
  gaps: BackendSkillGap[];
  generated_at: string;
}

export interface BackendCourseRecommendation {
  rank: number;
  course_id: string;
  course_name: string;
  cadre_role: string;
  target_cadre_match: boolean;
  target_competency_id?: string | null;
  target_competency_name?: string | null;
  competency_category: string;
  duration: string;
  course_creator: string;
  mapping_type: string;
  mapping_status: 'validated' | 'candidate' | 'unresolved';
  is_verified_mapping: boolean;
  provenance: string;
  score: number;
  recommendation_reason: string;
  resource_type?: string;
  provider_source?: string;
  mapping_evidence?: string | null;
  difficulty_fit?: string;
  prerequisite_fit?: string;
  limitations_or_uncertainties?: string;
}

export type BackendCourseRecommendationFixed = BackendCourseRecommendation;

export interface BackendRecommendationReport {
  learner_id: string;
  learner_name: string;
  role_id: string;
  total_gaps_addressed: number;
  recommendations: BackendCourseRecommendationFixed[];
  filtered_unresolved_count: number;
  include_unresolved_requested: boolean;
  generated_at: string;
}

export interface BackendHealthResponse {
  status: string;
  version: string;
  timestamp: string;
  datasets: {
    competencies?: { source: string; count: number; provenance: string };
    courses?: { source: string; count: number; provenance: string };
    mappings?: { count: number; candidate_count: number; unresolved_count?: number; validation_status: string };
    roles?: { count: number; provenance: string; note: string };
    learners?: { count: number; provenance: string; note: string };
    [key: string]: any;
  };
  level_scale: {
    name: string;
    min_level: number;
    max_level: number;
    description: string;
  };
}

// ============================================================================
// Stage 4.4 Diagnostic Assessment Types
// ============================================================================

export interface AssessmentTopic {
  competency_id: string;
  competency_name: string;
  competency_type: string;
  description: string;
  source_document_id: string;
  source_title: string;
  available_questions_count: number;
}

export interface ClientQuestion {
  question_id: string;
  question_text: string;
  options: { [key: string]: string };
  difficulty: string;
  competency_id: string;
}

export interface AssessmentStartResponse {
  attempt_id: string;
  learner_id: string;
  competency_id: string;
  competency_name: string;
  source_document_id: string;
  source_title: string;
  total_questions: number;
  questions: ClientQuestion[];
  instructions: string;
}

export interface QuestionFeedback {
  question_id: string;
  question_text: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
  source_document_id: string;
  source_title: string;
  page_reference: number | string;
  verbatim_excerpt: string;
}

export interface ProvisionalEstimate {
  competency_id: string;
  competency_name: string;
  estimated_level: number;
  confidence: number;
  evidence_threshold_met: boolean;
  score_percentage: number;
  evidence_count: number;
  methodology_note: string;
  limitations_disclaimer: string;
}

export interface AssessmentResultResponse {
  attempt_id: string;
  learner_id: string;
  competency_id: string;
  competency_name: string;
  total_questions: number;
  correct_count: number;
  score_percentage: number;
  feedback: QuestionFeedback[];
  provisional_estimate: ProvisionalEstimate;
  recommended_courses: BackendCourseRecommendationFixed[];
  completed_at: string;
}

// ============================================================================
// Stage 4.7 — Trainer Studio & Dynamic Question Generation Types
// ============================================================================

export interface UploadedDocument {
  document_id: string;
  filename: string;
  file_type: 'pdf' | 'txt';
  file_size_bytes: number;
  sha256: string;
  uploaded_at: string;
  extraction_status: 'extracted' | 'ocr_required' | 'extraction_failed';
  page_count: number;
  character_count: number;
  provenance: string;
  title: string;
  description?: string;
  extraction_error?: string;
}

export interface DraftQuestion {
  question_id: string;
  document_id: string;
  source_document_id: string;
  competency_id: string;
  competency_name: string;
  question_text: string;
  options: Record<string, string>;
  correct_answer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
  source_page: number;
  source_excerpt: string;
  difficulty: 'foundation' | 'operational' | 'advanced';
  status: 'draft' | 'approved' | 'rejected' | 'published';
  provenance: string;
  validation_status: 'verified' | 'flagged_for_review';
  verification_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface ProviderStatus {
  configured: boolean;
  mode: string;
  model: string;
  demonstration_notice: string;
}

export interface PublishResult {
  status: string;
  published_count: number;
  published_ids: string[];
  published_questions: any[];
  message: string;
}




export interface ProviderStatusSummary {
  provider_id: string;
  provider_name: string;
  provider_type: 'local_catalogue' | 'public_curriculum' | 'public_metadata';
  status: 'available' | 'degraded' | 'offline';
  is_live_integration: boolean;
  integration_note: string;
  total_resources: number;
  last_retrieved: string;
  error?: string | null;
}

export interface LearningActivityRecord {
  activity_id: string;
  learner_id: string;
  resource_id: string;
  resource_title: string;
  target_competency_id?: string | null;
  activity_type: 'enrolled' | 'in_progress' | 'completed' | 'reference_consulted';
  timestamp: string;
  notes: string;
  is_live_sync: boolean;
  evidence_disclaimer: string;
}

export interface AdminAnalyticsData {
  assessment_coverage: {
    total_learners: number;
    assessed_learners: number;
    unassessed_learners: number;
    coverage_percentage: number;
    total_competency_evaluations: number;
    assessed_instances: number;
  };
  evidence_profile: {
    provisional_estimates_count: number;
    baseline_learner_records_count: number;
    evidence_mode: string;
  };
  critical_gaps: Array<{
    competency_name: string;
    learners_affected: number;
  }>;
  mapping_validation: {
    total_courses: number;
    total_mappings: number;
    validated_mappings: number;
    candidate_mappings: number;
    unresolved_mappings: number;
  };
  assessment_activity: {
    total_quizzes_attempted: number;
    average_score_percentage: number;
    recent_attempts_count: number;
  };
  providers: ProviderStatusSummary[];
  is_synthetic_cohort: boolean;
  cohort_disclaimer: string;
  timestamp: string;
}
