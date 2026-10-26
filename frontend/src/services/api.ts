/**
 * Centralized API Client for the SIH26101 Competency Intelligence Engine.
 * Configured via Vite environment variables with graceful error reporting.
 */

import {
  BackendCompetency,
  BackendCourse,
  BackendHealthResponse,
  BackendLearner,
  BackendRecommendationReport,
  BackendRole,
  BackendSkillGapReport,
  AssessmentTopic,
  AssessmentStartResponse,
  AssessmentResultResponse,
  AdminAnalyticsData,
  LearningActivityRecord,
  ProviderStatusSummary
} from '../types';

const TRAINER_IDENTITY = 'TRAINER';

export const API_BASE_URL =
  ((import.meta as any).env?.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, '') ||
  'http://127.0.0.1:8000';

class ApiClientError extends Error {
  status?: number;
  endpoint?: string;
  constructor(message: string, status?: number, endpoint?: string) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.endpoint = endpoint;
  }
}

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...(options?.headers || {})
      }
    });

    if (!response.ok) {
      let detail = '';
      try {
        const errorJson = await response.json();
        detail = errorJson.detail || JSON.stringify(errorJson);
      } catch {
        detail = response.statusText;
      }
      throw new ApiClientError(
        `API request failed: ${response.status} ${detail}`,
        response.status,
        endpoint
      );
    }

    return (await response.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiClientError) {
      throw err;
    }
    throw new ApiClientError(
      `Network error connecting to Competency Intelligence API at ${API_BASE_URL}: ${err.message || 'Offline'}`,
      0,
      endpoint
    );
  }
}

export const api = {
  /** Check health and dataset inventory */
  getHealth(): Promise<BackendHealthResponse> {
    return fetchJson<BackendHealthResponse>('/health');
  },

  /** List KCM competencies with optional filtering */
  getCompetencies(params?: {
    type?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<BackendCompetency[]> {
    const searchParams = new URLSearchParams();
    if (params?.type) searchParams.set('type', params.type);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
    const query = searchParams.toString();
    return fetchJson<BackendCompetency[]>(`/api/competencies${query ? `?${query}` : ''}`);
  },

  /** Get a single KCM competency */
  getCompetency(id: string): Promise<BackendCompetency> {
    return fetchJson<BackendCompetency>(`/api/competencies/${encodeURIComponent(id)}`);
  },

  /** List MoSPI ACBP courses */
  getCourses(params?: {
    cadre?: string;
    category?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<BackendCourse[]> {
    const searchParams = new URLSearchParams();
    if (params?.cadre) searchParams.set('cadre', params.cadre);
    if (params?.category) searchParams.set('category', params.category);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
    const query = searchParams.toString();
    return fetchJson<BackendCourse[]>(`/api/courses${query ? `?${query}` : ''}`);
  },

  /** Get single ACBP course */
  getCourse(id: string): Promise<BackendCourse> {
    return fetchJson<BackendCourse>(`/api/courses/${encodeURIComponent(id)}`);
  },

  /** List civil service roles */
  getRoles(): Promise<BackendRole[]> {
    return fetchJson<BackendRole[]>('/api/roles');
  },

  /** Get single role */
  getRole(id: string): Promise<BackendRole> {
    return fetchJson<BackendRole>(`/api/roles/${encodeURIComponent(id)}`);
  },

  /** List synthetic demonstration learners */
  getLearners(): Promise<BackendLearner[]> {
    return fetchJson<BackendLearner[]>('/api/learners');
  },

  /** Get single synthetic learner */
  getLearner(id: string): Promise<BackendLearner> {
    return fetchJson<BackendLearner>(`/api/learners/${encodeURIComponent(id)}`);
  },

  /** Get explainable skill gaps for a learner against their role */
  getLearnerSkillGaps(learnerId: string): Promise<BackendSkillGapReport> {
    return fetchJson<BackendSkillGapReport>(
      `/api/learners/${encodeURIComponent(learnerId)}/skill-gaps`,
      { headers: { 'X-Learner-ID': learnerId } }
    );
  },

  /** Get deterministic, ranked recommendations from ACBP */
  getLearnerRecommendations(
    learnerId: string,
    includeUnresolved = false,
    maxRecommendations = 10
  ): Promise<BackendRecommendationReport> {
    const params = new URLSearchParams({
      include_unresolved: includeUnresolved.toString(),
      max_recommendations: maxRecommendations.toString()
    });
    return fetchJson<BackendRecommendationReport>(
      `/api/learners/${encodeURIComponent(learnerId)}/recommendations?${params.toString()}`,
      { headers: { 'X-Learner-ID': learnerId } }
    );
  },

  /** List recorded learning activities for a learner */
  getLearningActivities(learnerId: string): Promise<LearningActivityRecord[]> {
    return fetchJson<LearningActivityRecord[]>(
      `/api/learners/${encodeURIComponent(learnerId)}/learning-activities`,
      { headers: { 'X-Learner-ID': learnerId } }
    );
  },

  /** Record a learner-reported course action (not live LMS sync) */
  recordLearningActivity(
    learnerId: string,
    payload: {
      resource_id: string;
      resource_title: string;
      activity_type: 'enrolled' | 'in_progress' | 'completed' | 'reference_consulted';
      target_competency_id?: string | null;
      notes?: string;
    }
  ): Promise<LearningActivityRecord> {
    return fetchJson<LearningActivityRecord>(
      `/api/learners/${encodeURIComponent(learnerId)}/learning-activities`,
      {
        method: 'POST',
        headers: { 'X-Learner-ID': learnerId },
        body: JSON.stringify(payload)
      }
    );
  },

  /** Provider catalogue status (iGOT / NSSTA / ACBP) — not live SSO */
  getRecommendationProviders(): Promise<ProviderStatusSummary[]> {
    return fetchJson<ProviderStatusSummary[]>('/api/recommendations/providers');
  },

  /** Completed diagnostic attempts for a learner */
  getLearnerAssessmentHistory(learnerId: string): Promise<any[]> {
    return fetchJson<any[]>(
      `/api/assessment/learner/${encodeURIComponent(learnerId)}/history`,
      { headers: { 'X-Learner-ID': learnerId } }
    );
  },

  /** Get available assessment topics grounded in source documents */
  getAssessmentTopics(): Promise<AssessmentTopic[]> {
    return fetchJson<AssessmentTopic[]>('/api/assessment/topics');
  },

  /** Start a source-grounded diagnostic assessment */
  startAssessment(payload: {
    learner_id: string;
    competency_id?: string;
    question_count?: number;
  }): Promise<AssessmentStartResponse> {
    return fetchJson<AssessmentStartResponse>('/api/assessment/start', {
      method: 'POST',
      headers: { 'X-Learner-ID': payload.learner_id },
      body: JSON.stringify(payload)
    });
  },

  /** Submit answers for grading, explanation, and provisional competency update */
  submitAssessment(
    attemptId: string,
    payload: {
      attempt_id: string;
      learner_id: string;
      answers: Record<string, string>;
    }
  ): Promise<AssessmentResultResponse> {
    return fetchJson<AssessmentResultResponse>(
      `/api/assessment/${encodeURIComponent(attemptId)}/submit`,
      {
        method: 'POST',
        headers: { 'X-Learner-ID': payload.learner_id },
        body: JSON.stringify(payload)
      }
    );
  },

  /** Get details of a recorded assessment attempt */
  getAssessmentAttempt(attemptId: string, learnerId?: string): Promise<any> {
    const headers = learnerId ? { 'X-Learner-ID': learnerId } : undefined;
    return fetchJson<any>(`/api/assessment/attempts/${encodeURIComponent(attemptId)}`, { headers });
  },

  /** Get provisional estimates for a learner */
  getLearnerEstimates(learnerId: string): Promise<{
    learner_id: string;
    total_provisional_estimates: number;
    estimates: Record<string, any>;
  }> {
    return fetchJson<any>(
      `/api/assessment/learner/${encodeURIComponent(learnerId)}/estimates`,
      { headers: { 'X-Learner-ID': learnerId } }
    );
  },

  /** Safely reset demonstration assessment attempts and provisional estimates */
  resetDemoState(): Promise<{
    status: string;
    message: string;
    cleared_attempts: number;
    cleared_estimates: number;
    timestamp: string;
  }> {
    return fetchJson<any>('/api/demo/reset?confirm=true', {
      method: 'POST',
      headers: {
        'X-Demo-Reset-Key': 'sih26101-local-demo'
      }
    });
  },

  // ==========================================================================
  // Trainer Studio & Dynamic Question Generation (Stage 4.7)
  // ==========================================================================

  /** Upload PDF or TXT learning material */
  async uploadMaterial(file: File, title?: string, description?: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);

    const url = `${API_BASE_URL}/api/trainer/upload`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'X-Learner-ID': TRAINER_IDENTITY },
      body: formData,
    });

    if (!response.ok) {
      let detail = '';
      try {
        const errorJson = await response.json();
        detail = errorJson.detail || JSON.stringify(errorJson);
      } catch {
        detail = response.statusText;
      }
      throw new Error(`Upload failed (${response.status}): ${detail}`);
    }

    return response.json();
  },

  /** Get inventory of uploaded learning materials */
  getUploadedDocuments(): Promise<any[]> {
    return fetchJson<any[]>('/api/trainer/documents');
  },

  /** Check LLM provider configuration and status */
  getProviderStatus(): Promise<any> {
    return fetchJson<any>('/api/trainer/provider-status');
  },

  /** Generate source-grounded MCQ drafts from an uploaded document */
  generateQuestions(params: {
    documentId: string;
    questionCount?: number;
    difficulty?: 'foundation' | 'operational' | 'advanced';
    competencyId?: string;
  }): Promise<{
    status: string;
    document_id: string;
    generated_count: number;
    drafts: any[];
    rejections: string[];
    verification_status: string;
  }> {
    return fetchJson<any>('/api/trainer/generate-questions', {
      method: 'POST',
      headers: { 'X-Learner-ID': TRAINER_IDENTITY },
      body: JSON.stringify({
        document_id: params.documentId,
        question_count: params.questionCount ?? 3,
        difficulty: params.difficulty,
        competency_id: params.competencyId,
      }),
    });
  },

  /** List generated MCQ drafts in review queue */
  getDraftQuestions(params?: { status?: string; documentId?: string }): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set('status', params.status);
    if (params?.documentId) searchParams.set('document_id', params.documentId);
    const query = searchParams.toString();
    return fetchJson<any[]>(`/api/trainer/drafts${query ? `?${query}` : ''}`);
  },

  /** Trainer review action: approve, reject, or edit a draft question */
  reviewDraftQuestion(
    questionId: string,
    action: 'approve' | 'reject' | 'edit',
    options?: {
      reviewedBy?: string;
      rejectionReason?: string;
      editedQuestion?: any;
    }
  ): Promise<any> {
    return fetchJson<any>(`/api/trainer/drafts/${encodeURIComponent(questionId)}/review`, {
      method: 'POST',
      headers: { 'X-Learner-ID': TRAINER_IDENTITY },
      body: JSON.stringify({
        action,
        reviewed_by: options?.reviewedBy || 'trainer_admin',
        rejection_reason: options?.rejectionReason,
        edited_question: options?.editedQuestion,
      }),
    });
  },

  /** Publish approved drafts into active assessment question bank */
  publishApprovedQuestions(params?: {
    questionIds?: string[];
    publishedBy?: string;
  }): Promise<{
    status: string;
    published_count: number;
    published_ids: string[];
    published_questions: any[];
    message: string;
  }> {
    return fetchJson<any>('/api/trainer/publish', {
      method: 'POST',
      headers: { 'X-Learner-ID': TRAINER_IDENTITY },
      body: JSON.stringify({
        question_ids: params?.questionIds,
        published_by: params?.publishedBy || 'trainer_admin',
      }),
    });
  },

  /** Get administrator analytics overview */
  getAdminAnalytics(requesterId?: string): Promise<AdminAnalyticsData> {
    const requester = requesterId || 'ADMIN';
    return fetchJson<AdminAnalyticsData>(
      `/api/admin/analytics?requester_id=${encodeURIComponent(requester)}`,
      { headers: { 'X-Learner-ID': requester } }
    );
  }
};

