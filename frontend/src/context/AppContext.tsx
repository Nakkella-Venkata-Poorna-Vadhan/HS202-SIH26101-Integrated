import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import confetti from 'canvas-confetti';
import {
  PageRoute,
  UserRole,
  UserProfile,
  CompetencyScore,
  DayProgress,
  WeeklyBreakdownItem,
  ActivityTimelineItem,
  Course,
  LearningHistoryRecord,
  Quiz,
  QuizSubmissionState,
  AdminEmployee,
  BackendHealthResponse,
  BackendLearner,
  BackendRole,
  BackendCompetency,
  BackendCourse,
  BackendSkillGapReport,
  BackendRecommendationReport,
  BackendSkillGap,
  BackendCourseRecommendationFixed,
  AssessmentTopic,
  AssessmentStartResponse,
  AssessmentResultResponse,
  AuthUser,
  AuthTokens,
  EmployeeApplicationStatus,
  OrgTaxonomy
} from '../types';
import { api, API_BASE_URL, setAuthTokens, getAuthTokens } from '../services/api';
import {
  initialWeeklyDays,
  initialWeeklyBreakdown,
  initialActivityTimeline,
  sampleQuiz,
  sampleCourses
} from '../data/mockData';

// Official synthetic demonstration profiles
export const SYNTHETIC_LEARNER_PROFILES: Record<string, UserProfile> = {
  'LEARNER-001': {
    name: 'Arun Kumar',
    employeeId: 'LEARNER-001',
    department: 'Field Operations Division (FOD), MoSPI',
    designation: 'Senior Statistical Officer / Section Officer',
    jobRole: 'Field survey operations supervisor and statistical tabulator',
    experience: '8 years in official statistics',
    education: 'M.Sc. Statistics',
    email: 'arun.kumar@mospi.gov.in',
    phone: '+91 98765 00001',
    location: 'Sardar Patel Bhawan, New Delhi',
    learningPreferences: [
      'MoSPI In-service training schedule',
      'NSSTA Academy training calendar',
      'Hands-on data analytics and survey methodology'
    ],
    currentGoals: [
      'Bridge identified skill gap in Data Analytics (KCM-FUNC-11)',
      'Fulfill annual cadre training requirements under MoSPI ACBP 2026-27'
    ],
    isSynthetic: true
  },
  'LEARNER-002': {
    name: 'Dr. Meenakshi Sundaram',
    employeeId: 'LEARNER-002',
    department: 'National Accounts Division (NAD), MoSPI',
    designation: 'Director / Joint Director',
    jobRole: 'Director, Macroeconomic Aggregates and National Accounts',
    experience: '16 years in economic statistics and national accounts',
    education: 'Ph.D. Economics & Quantitative Analytics',
    email: 'dr.meenakshi@mospi.gov.in',
    phone: '+91 98765 00002',
    location: 'Khurshid Lal Bhawan, Janpath, New Delhi',
    learningPreferences: [
      'Executive Leadership & Strategic Direction',
      'System of National Accounts (SNA 2025 Framework)',
      'Public Policy & Inter-Ministerial Coordination'
    ],
    currentGoals: [
      'Reinforce Procurement & Financial Management (KCM-FUNC-05)',
      'Executive Coaching under MoSPI Senior Leadership Track'
    ],
    isSynthetic: true
  },
  'LEARNER-003': {
    name: 'Pooja Verma',
    employeeId: 'LEARNER-003',
    department: 'Survey Design & Research Division (SDRD), MoSPI',
    designation: 'Junior Statistical Officer (JSO)',
    jobRole: 'Survey instrument designer, field questionnaire scrutiny, fresh recruit',
    experience: '6 months (Induction / Probationary Phase)',
    education: 'M.Sc. Applied Statistics, University of Delhi',
    email: 'pooja.verma@mospi.gov.in',
    phone: '+91 98765 00003',
    location: 'Mahalanobis Bhavan, Kolkata',
    learningPreferences: [
      'Foundation Induction Training Program (FITP)',
      'Sampling Techniques & Household Survey Methodologies',
      'Official IT Tools and Survey Tabulation Systems'
    ],
    currentGoals: [
      'Complete baseline diagnostic assessment across all cadre competencies',
      'Build core foundation in Official Statistics (KCM-FUNC-11)'
    ],
    isSynthetic: true
  },
  'LEARNER-004': {
    name: 'Rajesh Sharma',
    employeeId: 'LEARNER-004',
    department: 'Economic Statistics Division (ESD), MoSPI',
    designation: 'Deputy Director General / Joint Secretary Equivalent',
    jobRole: 'Head of Economic Statistics Division, enterprise surveys & index administration',
    experience: '24 years in Indian Statistical Service (ISS)',
    education: 'M.Stat, Indian Statistical Institute (ISI)',
    email: 'rajesh.sharma@mospi.gov.in',
    phone: '+91 98765 00004',
    location: 'Sardar Patel Bhawan, New Delhi',
    learningPreferences: [
      'Strategic Governance & Inter-Ministerial Policy',
      'International Statistical Standards (UNSD / IMF / World Bank)',
      'Stakeholder Consultation & Cadre Mentorship'
    ],
    currentGoals: [
      'Deepen stakeholder consultation frameworks (KCM-BEH-06)',
      'Mentor mid-level ISS officers in economic indices compilation'
    ],
    isSynthetic: true
  }
};

const initialBackendLearners: BackendLearner[] = [
  {
    learner_id: 'LEARNER-001',
    name: 'Arun Kumar',
    role_id: 'ROLE-SSO-SO',
    department: 'Field Operations Division (FOD), MoSPI',
    cadre_role: 'Senior Statistical Officers / Section Officer / Senior Administrative Officer / Administrative Officer',
    is_synthetic: true,
    provenance: 'synthetic',
    assessed_competencies: [
      { competency_id: 'KCM-FUNC-11', estimated_level: 2, assessment_status: 'assessed', confidence: 0.85, evidence_sources: ['synthetic_statistical_coding_quiz_score_68pct'], last_assessed_date: '2026-08-15T10:00:00Z' },
      { competency_id: 'KCM-FUNC-21', estimated_level: 3, assessment_status: 'assessed', confidence: 0.9, evidence_sources: ['synthetic_supervisor_annual_evaluation_satisfactory'], last_assessed_date: '2026-07-20T14:30:00Z' },
      { competency_id: 'KCM-BEH-04', estimated_level: 2, assessment_status: 'assessed', confidence: 0.7, evidence_sources: ['synthetic_peer_feedback_survey_communication_q2'], last_assessed_date: '2026-06-10T09:15:00Z' },
      { competency_id: 'KCM-BEH-02', estimated_level: null, assessment_status: 'unassessed', confidence: 0.0, evidence_sources: [], last_assessed_date: null }
    ]
  },
  {
    learner_id: 'LEARNER-002',
    name: 'Dr. Meenakshi Sundaram',
    role_id: 'ROLE-DIR-JD',
    department: 'National Accounts Division (NAD), MoSPI',
    cadre_role: 'Director / Joint Director',
    is_synthetic: true,
    provenance: 'synthetic',
    assessed_competencies: [
      { competency_id: 'KCM-FUNC-05', estimated_level: 2, assessment_status: 'assessed', confidence: 0.8, evidence_sources: ['synthetic_management_assessment_simulation_mid_score'], last_assessed_date: '2026-09-01T11:00:00Z' },
      { competency_id: 'KCM-BEH-10', estimated_level: 3, assessment_status: 'assessed', confidence: 0.85, evidence_sources: ['synthetic_executive_leadership_360_feedback'], last_assessed_date: '2026-08-25T16:00:00Z' },
      { competency_id: 'KCM-BEH-06', estimated_level: 3, assessment_status: 'assessed', confidence: 0.9, evidence_sources: ['synthetic_inter_ministerial_working_group_chair_appraisal'], last_assessed_date: '2026-07-30T10:00:00Z' },
      { competency_id: 'KCM-FUNC-01', estimated_level: 3, assessment_status: 'assessed', confidence: 0.85, evidence_sources: ['synthetic_public_data_portal_user_satisfaction_audit'], last_assessed_date: '2026-07-15T15:00:00Z' }
    ]
  },
  {
    learner_id: 'LEARNER-003',
    name: 'Pooja Verma',
    role_id: 'ROLE-JSO-ASO',
    department: 'Survey Design & Research Division (SDRD), MoSPI',
    cadre_role: 'Junior Statistical Officers / Assistant Section Officers / Data Processing Assistant (All Grades)',
    is_synthetic: true,
    provenance: 'synthetic',
    assessed_competencies: [
      { competency_id: 'KCM-FUNC-11', estimated_level: null, assessment_status: 'unassessed', confidence: 0.0, evidence_sources: [], last_assessed_date: null },
      { competency_id: 'KCM-BEH-01', estimated_level: null, assessment_status: 'unassessed', confidence: 0.0, evidence_sources: [], last_assessed_date: null },
      { competency_id: 'KCM-BEH-04', estimated_level: null, assessment_status: 'unassessed', confidence: 0.0, evidence_sources: [], last_assessed_date: null },
      { competency_id: 'KCM-FUNC-21', estimated_level: null, assessment_status: 'unassessed', confidence: 0.0, evidence_sources: [], last_assessed_date: null }
    ]
  },
  {
    learner_id: 'LEARNER-004',
    name: 'Rajesh Sharma',
    role_id: 'ROLE-DDG-JS',
    department: 'Economic Statistics Division (ESD), MoSPI',
    cadre_role: 'Deputy Director General / Joint Secretary Equivalent and Above',
    is_synthetic: true,
    provenance: 'synthetic',
    assessed_competencies: [
      { competency_id: 'KCM-BEH-10', estimated_level: 4, assessment_status: 'assessed', confidence: 0.85, evidence_sources: ['synthetic_executive_mentorship_panel_review'], last_assessed_date: '2026-08-10T12:00:00Z' },
      { competency_id: 'KCM-BEH-06', estimated_level: 2, assessment_status: 'assessed', confidence: 0.75, evidence_sources: ['synthetic_inter_agency_stakeholder_survey_2026'], last_assessed_date: '2026-07-12T14:00:00Z' },
      { competency_id: 'KCM-FUNC-17', estimated_level: 4, assessment_status: 'assessed', confidence: 0.9, evidence_sources: ['synthetic_inquiry_officer_empanelment_certificate'], last_assessed_date: '2026-06-25T11:00:00Z' },
      { competency_id: 'KCM-FUNC-09', estimated_level: 3, assessment_status: 'assessed', confidence: 0.8, evidence_sources: ['synthetic_budget_standing_committee_appraisal'], last_assessed_date: '2026-05-18T16:30:00Z' }
    ]
  }
];

const initialBackendRoles: BackendRole[] = [
  {
    role_id: 'ROLE-SSO-SO',
    role_name: 'Senior Statistical Officer / Section Officer',
    cadre_role: 'Senior Statistical Officers / Section Officer / Senior Administrative Officer / Administrative Officer',
    description: 'Supervises field survey operations, data scrutiny, statistical tabulations, and section administration.',
    department: 'Field Operations Division (FOD), MoSPI',
    required_competencies: [],
    is_synthetic: true,
    provenance: 'synthetic'
  },
  {
    role_id: 'ROLE-DIR-JD',
    role_name: 'Director / Joint Director',
    cadre_role: 'Director / Joint Director',
    description: 'Programme director leading national survey rounds, macro-statistical compilations, and inter-cadre supervision.',
    department: 'National Accounts Division (NAD), MoSPI',
    required_competencies: [],
    is_synthetic: true,
    provenance: 'synthetic'
  },
  {
    role_id: 'ROLE-JSO-ASO',
    role_name: 'Junior Statistical Officer (JSO)',
    cadre_role: 'Junior Statistical Officers / Assistant Section Officers / Data Processing Assistant (All Grades)',
    description: 'Induction statistical officer executing primary survey validation, sampling frames, and field data tabulation.',
    department: 'Survey Design & Research Division (SDRD), MoSPI',
    required_competencies: [],
    is_synthetic: true,
    provenance: 'synthetic'
  },
  {
    role_id: 'ROLE-DDG-JS',
    role_name: 'Deputy Director General / Joint Secretary Equivalent',
    cadre_role: 'Deputy Director General / Joint Secretary Equivalent and Above',
    description: 'Head of Economic Statistics Division, enterprise surveys & index administration.',
    department: 'Economic Statistics Division (ESD), MoSPI',
    required_competencies: [],
    is_synthetic: true,
    provenance: 'synthetic'
  }
];

interface AppContextType {
  currentRoute: PageRoute;
  userRole: UserRole;
  isLoggedIn: boolean;
  userProfile: UserProfile;
  skills: CompetencyScore[];
  overallCompetency: number;
  weeklyHours: number;
  weeklyTarget: number;
  coursesCompleted: number;
  totalCourses: number;
  skillGapsCount: number;
  highPriorityGaps: number;
  weeklyDays: DayProgress[];
  weeklyBreakdown: WeeklyBreakdownItem[];
  activityTimeline: ActivityTimelineItem[];
  courses: Course[];
  selectedCourseId: string;
  activeQuiz: Quiz;
  quizSubmission: QuizSubmissionState | null;
  history: LearningHistoryRecord[];
  notificationCount: number;
  unreadNotifications: { id: string; title: string; time: string; read: boolean }[];
  navigateTo: (route: PageRoute, courseId?: string, extras?: { tab?: string }) => void;
  setUserRole: (role: UserRole) => void;
  adminTab: 'analytics' | 'trainer-studio';
  setAdminTab: (tab: 'analytics' | 'trainer-studio') => void;
  recordLearningActivity: (
    courseId: string,
    title: string,
    activityType: 'enrolled' | 'in_progress' | 'completed' | 'reference_consulted',
    competencyId?: string,
    notes?: string
  ) => Promise<boolean>;
  loginAs: (role: UserRole, learnerId?: string) => void;
  logout: () => void;
  toggleModuleCompletion: (courseId: string, moduleId: number) => void;
  submitQuizAnswers: (answers: Record<number, 'A' | 'B' | 'C' | 'D'>) => void;
  retakeQuiz: () => void;
  updateUserProfile: (profile: Partial<UserProfile>) => void;
  resetDemoData: () => void;
  markNotificationRead: (id: string) => void;

  // Real Backend Integration State
  isLoading: boolean;
  isBackendOffline: boolean;
  apiError: string | null;
  apiBaseUrl: string;
  healthData: BackendHealthResponse | null;
  availableLearners: BackendLearner[];
  availableRoles: BackendRole[];
  allCompetencies: BackendCompetency[];
  allCourses: BackendCourse[];
  selectedLearnerId: string;
  selectLearner: (learnerId: string) => Promise<void>;
  skillGapReport: BackendSkillGapReport | null;
  recommendationReport: BackendRecommendationReport | null;
  reloadBackendData: () => Promise<void>;
  adminEmployeesList: AdminEmployee[];

  // Diagnostic Assessment State
  assessmentTopics: AssessmentTopic[];
  activeAssessment: AssessmentStartResponse | null;
  assessmentResult: AssessmentResultResponse | null;
  isAssessmentLoading: boolean;
  assessmentError: string | null;
  selectedAssessmentTopicId: string | null;
  setSelectedAssessmentTopicId: (id: string | null) => void;
  startDiagnosticAssessment: (competencyId?: string) => Promise<void>;
  submitDiagnosticAssessment: (answers: Record<string, string>) => Promise<void>;
  resetDiagnosticAssessment: () => void;
  resetDemoState: () => Promise<void>;

  // Phase 2: Auth & Identity State & Methods
  authUser: AuthUser | null;
  authTokens: AuthTokens | null;
  employeeStatus: EmployeeApplicationStatus | null;
  isAuthenticating: boolean;
  loginWithCredentials: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  registerEmployee: (payload: any) => Promise<{ success: boolean; message?: string; error?: string; user?: AuthUser }>;
  verifyEmailToken: (token: string) => Promise<{ success: boolean; message?: string; error?: string; user?: AuthUser }>;
  requestPasswordReset: (email: string) => Promise<{ success: boolean; message?: string; error?: string }>;
  confirmPasswordReset: (token: string, newPassword: string) => Promise<{ success: boolean; message?: string; error?: string }>;
  acceptAdminInvite: (payload: { token: string; fullName: string; password: string }) => Promise<{ success: boolean; error?: string }>;
  refreshApplicationStatus: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const getInitialParams = () => {
    if (typeof window === 'undefined') {
      return { route: 'login' as PageRoute, role: 'employee' as UserRole, loggedIn: false, learner: 'LEARNER-001', adminTabInit: 'analytics' as const };
    }
    const hashStr = window.location.hash.replace(/^#\/?/, '');
    const hashParams = new URLSearchParams(hashStr);
    const searchParams = new URLSearchParams(window.location.search);
    const routeParam = hashParams.get('route') || searchParams.get('route');
    const validRoutes: PageRoute[] = [
      'login', 'dashboard', 'weekly-progress', 'competency-assessment',
      'skill-gap', 'recommendations', 'course-details', 'quiz',
      'history', 'profile', 'admin'
    ];
    const route: PageRoute = (routeParam && validRoutes.includes(routeParam as PageRoute))
      ? (routeParam as PageRoute)
      : 'login';
    const roleParam = hashParams.get('role') || searchParams.get('role');
    const role: UserRole = (roleParam === 'admin' || route === 'admin') ? 'admin' : 'employee';
    const learner = hashParams.get('learner') || searchParams.get('learner') || 'LEARNER-001';
    const loggedIn = route !== 'login';
    const tabParam = hashParams.get('tab') || searchParams.get('tab');
    const adminTabInit: 'analytics' | 'trainer-studio' =
      tabParam === 'trainer-studio' ? 'trainer-studio' : 'analytics';
    return { route, role, loggedIn, learner, adminTabInit };
  };

  const initialParams = getInitialParams();
  const [currentRoute, setCurrentRoute] = useState<PageRoute>(initialParams.route);
  const [userRole, setUserRole] = useState<UserRole>(initialParams.role);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(initialParams.loggedIn);
  const [adminTab, setAdminTab] = useState<'analytics' | 'trainer-studio'>(
    initialParams.adminTabInit
  );

  // Phase 2: Authentication & Identity State
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [authTokensState, setAuthTokensState] = useState<AuthTokens | null>(null);
  const [employeeStatus, setEmployeeStatus] = useState<EmployeeApplicationStatus | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState<boolean>(false);

  // Backend state
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isBackendOffline, setIsBackendOffline] = useState<boolean>(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [healthData, setHealthData] = useState<BackendHealthResponse | null>(null);
  const [availableLearners, setAvailableLearners] = useState<BackendLearner[]>(initialBackendLearners);
  const [availableRoles, setAvailableRoles] = useState<BackendRole[]>(initialBackendRoles);
  const [allCompetencies, setAllCompetencies] = useState<BackendCompetency[]>([]);
  const [allCourses, setAllCourses] = useState<BackendCourse[]>([]);
  const [selectedLearnerId, setSelectedLearnerId] = useState<string>(initialParams.learner);
  const [skillGapReport, setSkillGapReport] = useState<BackendSkillGapReport | null>(null);
  const [recommendationReport, setRecommendationReport] = useState<BackendRecommendationReport | null>(null);

  // Diagnostic Assessment State
  const [assessmentTopics, setAssessmentTopics] = useState<AssessmentTopic[]>([]);
  const [activeAssessment, setActiveAssessment] = useState<AssessmentStartResponse | null>(null);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResultResponse | null>(null);
  const [isAssessmentLoading, setIsAssessmentLoading] = useState<boolean>(false);
  const [assessmentError, setAssessmentError] = useState<string | null>(null);
  const [selectedAssessmentTopicId, setSelectedAssessmentTopicId] = useState<string | null>(null);

  // Profile and domain state
  const [userProfile, setUserProfile] = useState<UserProfile>(
    SYNTHETIC_LEARNER_PROFILES[initialParams.learner] || SYNTHETIC_LEARNER_PROFILES['LEARNER-001']
  );

  const [skills, setSkills] = useState<CompetencyScore[]>([]);
  const [overallCompetency, setOverallCompetency] = useState<number>(0);
  const [weeklyHours, setWeeklyHours] = useState<number>(0);
  const weeklyTarget = 8.0;
  const [coursesCompleted, setCoursesCompleted] = useState<number>(0);
  const [totalCourses, setTotalCourses] = useState<number>(sampleCourses.length);
  const [courses, setCourses] = useState<Course[]>(sampleCourses);
  const [selectedCourseId, setSelectedCourseId] = useState<string>(sampleCourses[0]?.id || 'ACBP-CRS-001');
  const [activeQuiz] = useState<Quiz>(sampleQuiz);
  const [quizSubmission, setQuizSubmission] = useState<QuizSubmissionState | null>(null);
  const [weeklyDays, setWeeklyDays] = useState<DayProgress[]>(initialWeeklyDays);
  const [weeklyBreakdown, setWeeklyBreakdown] = useState<WeeklyBreakdownItem[]>(initialWeeklyBreakdown);
  const [activityTimeline, setActivityTimeline] = useState<ActivityTimelineItem[]>(initialActivityTimeline);
  const [history, setHistory] = useState<LearningHistoryRecord[]>([]);
  const selectedLearnerIdRef = useRef(initialParams.learner);

  const [unreadNotifications, setUnreadNotifications] = useState([
    { id: '1', title: 'Competency Intelligence Engine loaded official KCM & ACBP schedules', time: 'Just now', read: false },
    { id: '2', title: 'Deterministic course recommendation ranking updated for active cadre', time: '10m ago', read: false },
    { id: '3', title: 'NSSTA Annual Capacity Building Plan 2026-27 active', time: '1h ago', read: false }
  ]);

  // Transform backend gaps into frontend CompetencyScore format
  const mapBackendGapsToCompetencies = (gaps: BackendSkillGap[]): CompetencyScore[] => {
    return gaps.map((gap) => {
      const currentPct = gap.estimated_level !== null && gap.estimated_level !== undefined
        ? Math.round((gap.estimated_level / 5) * 100)
        : 0;
      const reqPct = Math.round((gap.required_level / 5) * 100);
      const gapPct = gap.gap !== null && gap.gap !== undefined
        ? Math.round((gap.gap / 5) * 100)
        : gap.status === 'unassessed' ? reqPct : 0;

      let levelStatus: CompetencyScore['level'] = 'developing';
      if (gap.status === 'unassessed') {
        levelStatus = 'unassessed';
      } else if (gap.gap === 0 || gap.status === 'competent') {
        levelStatus = 'strong';
      } else if (gap.priority === 'critical' || (gap.gap && gap.gap > 1)) {
        levelStatus = 'critical-gap';
      } else {
        levelStatus = 'needs-improvement';
      }

      const trendText = gap.status === 'unassessed'
        ? 'Unassessed on prototype scale'
        : gap.is_provisional
        ? `Provisional Level ${gap.estimated_level} / 5 (${gap.confidence ? Math.round(gap.confidence * 100) : 75}% conf)`
        : `Level ${gap.estimated_level} / 5 (${gap.confidence ? Math.round(gap.confidence * 100) : 85}% conf)`;

      return {
        name: gap.competency_name,
        competencyId: gap.competency_id,
        current: currentPct,
        required: reqPct,
        gap: gapPct,
        category: gap.competency_type === 'behavioural' ? 'Behavioural & Managerial' : 'Technical',
        level: levelStatus,
        trend: trendText,
        priority: gap.priority,
        explanation: gap.explanation
      };
    });
  };

  // Transform backend recommendations into frontend Course format
  const mapBackendRecommendationsToCourses = (
    recommendations: BackendCourseRecommendationFixed[]
  ): Course[] => {
    return recommendations.map((rec, idx) => {
      let priority: Course['priority'] = 'Standard';
      if (rec.rank === 1 || rec.score >= 10) priority = 'Critical';
      else if (rec.rank <= 3 || rec.score >= 5) priority = 'High';
      else priority = 'Medium';

      return {
        id: rec.course_id,
        title: rec.course_name,
        instructor: rec.course_creator,
        organization: rec.course_creator,
        duration: rec.duration.replace(/^0(\d)/, '$1').replace(/\.00$/, ' hrs').replace(/\./g, 'h '),
        difficulty: rec.competency_category === 'Domain' ? 'Intermediate' : 'Beginner → Intermediate',
        skillCategory: rec.target_competency_name || rec.competency_category,
        progress: 0,
        rating: 4.8,
        totalModules: 4,
        completedModules: 0,
        description: rec.recommendation_reason,
        recommendationReason: rec.recommendation_reason,
        priority,
        targetGapReduction: rec.target_competency_name
          ? `Targets ${rec.target_competency_name} (${rec.mapping_status} mapping)`
          : `Addresses cadre training schedule (${rec.mapping_status})`,
        mappingStatus: rec.mapping_status,
        targetCompetencyId: rec.target_competency_id || undefined,
        targetCompetencyName: rec.target_competency_name || undefined,
        cadreRole: rec.cadre_role,
        provenance: rec.provenance,
        resourceType: rec.resource_type || 'course',
        providerSource: rec.provider_source || 'MoSPI ACBP (Local)',
        mappingEvidence: rec.mapping_evidence || null,
        difficultyFit: rec.difficulty_fit || 'Aligned',
        prerequisiteFit: rec.prerequisite_fit || 'Standard Prerequisites',
        limitationsOrUncertainties: rec.limitations_or_uncertainties || '',
        modules: [
          { id: 1, title: 'Introduction & Official Administrative Background', duration: '30 mins', completed: false, type: 'video' },
          { id: 2, title: 'Methodology, Data Structures & Guidelines', duration: '45 mins', completed: false, type: 'interactive' },
          { id: 3, title: 'Field Operations & Scrutiny Case Study', duration: '40 mins', completed: false, type: 'reading' },
          { id: 4, title: 'Evaluation & Knowledge Check Assessment', duration: '20 mins', completed: false, type: 'quiz' },
        ]
      };
    });
  };

  // Load a learner's data from the backend
  const loadLearnerIntelligence = useCallback(async (
    learnerId: string,
    learnersList?: BackendLearner[],
    rolesList?: BackendRole[]
  ) => {
    try {
      setIsLoading(true);
      setApiError(null);

      // 1. Fetch skill gaps
      const gapReport = await api.getLearnerSkillGaps(learnerId);
      setSkillGapReport(gapReport);

      // 2. Fetch recommendations (including unresolved so all courses can be explored)
      const recReport = await api.getLearnerRecommendations(learnerId, true, 20);
      setRecommendationReport(recReport);

      // 3. Update competencies
      const mappedSkills = mapBackendGapsToCompetencies(gapReport.gaps);
      setSkills(mappedSkills);

      // 4. Update courses
      const mappedCourses = mapBackendRecommendationsToCourses(recReport.recommendations);
      setCourses(mappedCourses);
      if (mappedCourses.length > 0) {
        setSelectedCourseId(mappedCourses[0].id);
      }

      // 5. Calculate overall competency
      // Ratio of required competencies that have no gap or level calculation
      const competentCount = gapReport.competent_count;
      const totalReq = gapReport.total_required_competencies;
      const compScore = totalReq > 0 ? Math.round((competentCount / totalReq) * 100) : 70;
      setOverallCompetency(compScore);

      // 6. Update user profile from learner object
      const allLearners = learnersList && learnersList.length > 0 ? learnersList : (availableLearners.length > 0 ? availableLearners : initialBackendLearners);
      const currentLearner = allLearners.find((l) => l.learner_id === learnerId);
      const allRoles = rolesList && rolesList.length > 0 ? rolesList : (availableRoles.length > 0 ? availableRoles : initialBackendRoles);
      const currentRole = allRoles.find((r) => r.role_id === currentLearner?.role_id);
      const staticProfile = SYNTHETIC_LEARNER_PROFILES[learnerId];

      if (currentLearner) {
        setUserProfile({
          name: currentLearner.name,
          employeeId: currentLearner.learner_id,
          department: currentLearner.department,
          designation: currentRole?.role_name || gapReport.role_name || staticProfile?.designation || 'Statistical Cadre Officer',
          jobRole: currentRole?.description || staticProfile?.jobRole || gapReport.role_name,
          experience: staticProfile?.experience || 'In-Service Statistical Cadre',
          education: staticProfile?.education || 'Government of India MoSPI Officer',
          email: staticProfile?.email || `${currentLearner.name.toLowerCase().replace(/[^a-z]/g, '.') || 'officer'}@mospi.gov.in`,
          phone: staticProfile?.phone || '+91 98765 00000',
          location: staticProfile?.location || 'Ministry of Statistics & Programme Implementation',
          learningPreferences: staticProfile?.learningPreferences || [
            'Annual Capacity Building Plan (ACBP 2026-27)',
            'National Statistical Systems Training Academy (NSSTA)',
            'Official Survey Validation and Analysis'
          ],
          currentGoals: gapReport.gaps
            .filter((g) => g.status === 'gap_identified')
            .map((g) => `Close gap in ${g.competency_name} (Level ${g.required_level})`),
          isSynthetic: true
        });
      } else if (staticProfile) {
        setUserProfile(staticProfile);
      }

      setTotalCourses(mappedCourses.length);

      const [activities, attempts] = await Promise.all([
        api.getLearningActivities(learnerId).catch(() => []),
        api.getLearnerAssessmentHistory(learnerId).catch(() => [])
      ]);

      const completedActivities = activities.filter((a) => a.activity_type === 'completed');
      setCoursesCompleted(completedActivities.length);

      const activityHours = Math.min(8, Number((activities.length * 0.75).toFixed(1)));
      const isFullyUnassessed = gapReport.unassessed_count === gapReport.total_required_competencies;
      if (activities.length > 0) {
        setWeeklyHours(activityHours || 0.5);
        setWeeklyDays(initialWeeklyDays.map((d, idx) => ({
          ...d,
          hours: idx < activities.length ? Math.min(d.targetHours, 1.5) : (isFullyUnassessed ? 0 : d.hours * 0.3)
        })));
      } else if (isFullyUnassessed) {
        setWeeklyHours(0.0);
        setWeeklyDays(initialWeeklyDays.map((d) => ({ ...d, hours: 0 })));
      } else {
        setWeeklyHours(6.5);
        setWeeklyDays(initialWeeklyDays);
      }

      const attemptHistory: LearningHistoryRecord[] = (attempts || []).map((attempt: any) => ({
        id: attempt.attempt_id || `attempt-${Math.random()}`,
        date: attempt.completed_at
          ? new Date(attempt.completed_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
          : '—',
        course: `Diagnostic Assessment: ${attempt.competency_name || attempt.competency_id || 'Competency'}`,
        activity: 'Assessment' as const,
        duration: '10 min',
        score: attempt.score_percentage != null ? `${attempt.score_percentage}%` : '—',
        status: 'Completed' as const,
        skill: attempt.competency_name || attempt.competency_id || 'Diagnostic'
      }));

      const activityHistory: LearningHistoryRecord[] = (activities || []).map((act) => ({
        id: act.activity_id,
        date: act.timestamp
          ? new Date(act.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
          : '—',
        course: act.resource_title,
        activity: act.activity_type === 'completed' ? 'Module' : 'Workshop',
        duration: '—',
        score: '—',
        status: act.activity_type === 'completed' ? 'Completed' : 'In Progress',
        skill: act.target_competency_id || 'Capacity Building'
      }));

      setHistory([...attemptHistory, ...activityHistory]);
      setIsBackendOffline(false);
    } catch (err: any) {
      console.error('Failed to load learner intelligence:', err);
      setApiError(err.message || 'Error communicating with backend');
      setIsBackendOffline(true);
      if (SYNTHETIC_LEARNER_PROFILES[learnerId]) {
        setUserProfile(SYNTHETIC_LEARNER_PROFILES[learnerId]);
      }
    } finally {
      setIsLoading(false);
    }
  }, [availableLearners, availableRoles]);

  // Initial load of platform metadata and datasets from backend
  const reloadBackendData = useCallback(async () => {
    setIsLoading(true);
    setApiError(null);
    try {
      // Fetch health, learners, roles, competencies, courses, and assessment topics in parallel
      const [health, learners, roles, comps, crsList, topics] = await Promise.all([
        api.getHealth(),
        api.getLearners(),
        api.getRoles(),
        api.getCompetencies({ page_size: 100 }),
        api.getCourses({ page_size: 250 }),
        api.getAssessmentTopics().catch(() => [] as AssessmentTopic[])
      ]);

      setHealthData(health);
      setAvailableLearners(learners);
      setAvailableRoles(roles);
      setAllCompetencies(comps);
      setAllCourses(crsList);
      setAssessmentTopics(topics);
      if (topics.length > 0 && !selectedAssessmentTopicId) {
        setSelectedAssessmentTopicId(topics[0].competency_id);
      }
      setIsBackendOffline(false);

      // Preserve the currently selected officer instead of always snapping to LEARNER-001
      const preferredId = selectedLearnerIdRef.current;
      const resolvedId = learners.some((l) => l.learner_id === preferredId)
        ? preferredId
        : (learners.length > 0 ? learners[0].learner_id : 'LEARNER-001');
      selectedLearnerIdRef.current = resolvedId;
      setSelectedLearnerId(resolvedId);
      await loadLearnerIntelligence(resolvedId, learners, roles);
    } catch (err: any) {
      console.error('Backend connection failed:', err);
      setIsBackendOffline(true);
      setApiError(err.message || 'Cannot reach backend API');
    } finally {
      setIsLoading(false);
    }
  }, [loadLearnerIntelligence]);

  useEffect(() => {
    reloadBackendData();
  }, [reloadBackendData]);

  // Switch learner dynamically
  const selectLearner = async (learnerId: string) => {
    selectedLearnerIdRef.current = learnerId;
    setSelectedLearnerId(learnerId);
    if (SYNTHETIC_LEARNER_PROFILES[learnerId]) {
      setUserProfile(SYNTHETIC_LEARNER_PROFILES[learnerId]);
    }
    await loadLearnerIntelligence(learnerId);
  };

  const skillGapsCount = skillGapReport?.gap_count ?? skills.filter((s) => s.gap > 0).length;
  const highPriorityGaps =
    skillGapReport?.gaps.filter(
      (g) => g.status === 'gap_identified' && (g.priority === 'critical' || g.priority === 'high')
    ).length ?? 0;

  const navigateTo = (route: PageRoute, courseId?: string, extras?: { tab?: string }) => {
    if (courseId) {
      setSelectedCourseId(courseId);
    }
    if (route === 'admin') {
      setUserRole('admin');
      if (extras?.tab === 'trainer-studio' || extras?.tab === 'analytics') {
        setAdminTab(extras.tab);
      }
    }
    setCurrentRoute(route);
    try {
      const params = new URLSearchParams();
      params.set('route', route);
      params.set('learner', selectedLearnerIdRef.current);
      params.set('role', route === 'admin' ? 'admin' : 'employee');
      if (courseId) params.set('course', courseId);
      if (extras?.tab) params.set('tab', extras.tab);
      window.location.hash = params.toString();
    } catch {}
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const loginAs = (role: UserRole, learnerId?: string) => {
    setUserRole(role);
    setIsLoggedIn(true);
    const targetId = learnerId || selectedLearnerIdRef.current;
    if (targetId) {
      selectedLearnerIdRef.current = targetId;
      setSelectedLearnerId(targetId);
      if (SYNTHETIC_LEARNER_PROFILES[targetId]) {
        setUserProfile(SYNTHETIC_LEARNER_PROFILES[targetId]);
      }
      selectLearner(targetId);
    }
    if (role === 'admin') {
      setAdminTab('analytics');
      setCurrentRoute('admin');
    } else {
      setCurrentRoute('dashboard');
    }
    try {
      const params = new URLSearchParams();
      params.set('route', role === 'admin' ? 'admin' : 'dashboard');
      params.set('learner', targetId);
      params.set('role', role);
      window.location.hash = params.toString();
    } catch {}
  };

  const logout = () => {
    const tokens = getAuthTokens();
    if (tokens.refreshToken) {
      api.authLogout(tokens.refreshToken).catch(() => {});
    }
    setAuthTokens(null);
    setAuthTokensState(null);
    setAuthUser(null);
    setEmployeeStatus(null);
    setIsLoggedIn(false);
    setCurrentRoute('login');
    try {
      window.location.hash = 'route=login';
    } catch {}
  };

  // Phase 2 Auth Methods
  const refreshApplicationStatus = useCallback(async () => {
    try {
      const statusData = await api.getEmployeeApplicationStatus();
      setEmployeeStatus(statusData);
    } catch (err) {
      console.error('Failed to fetch employee application status:', err);
    }
  }, []);

  const loginWithCredentials = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setIsAuthenticating(true);
    try {
      const tokens = await api.authLogin({ email, password });
      setAuthTokens({ access_token: tokens.access_token, refresh_token: tokens.refresh_token });
      setAuthTokensState(tokens);
      setAuthUser(tokens.user);
      setIsLoggedIn(true);

      if (tokens.user.account_type === 'EMPLOYEE') {
        setUserRole('employee');
        if (tokens.user.profile?.full_name) {
          setUserProfile((prev) => ({
            ...prev,
            name: tokens.user.profile?.full_name || prev.name,
            employeeId: tokens.user.profile?.employee_code || prev.employeeId,
            email: tokens.user.email,
          }));
        }

        if (!tokens.user.is_approved) {
          try {
            const statusData = await api.getEmployeeApplicationStatus();
            setEmployeeStatus(statusData);
          } catch {}
          setCurrentRoute('pending-approval');
          try { window.location.hash = 'route=pending-approval'; } catch {}
        } else {
          setCurrentRoute('dashboard');
          try { window.location.hash = 'route=dashboard'; } catch {}
        }
      } else if (tokens.user.account_type === 'ADMINISTRATOR') {
        setUserRole('admin');
        setAdminTab('analytics');
        setCurrentRoute('admin');
        try { window.location.hash = 'route=admin&tab=analytics'; } catch {}
      } else if (tokens.user.account_type === 'PROJECT_STAFF') {
        setUserRole('project_staff');
        setAdminTab('analytics');
        setCurrentRoute('admin');
        try { window.location.hash = 'route=admin&tab=analytics'; } catch {}
      }
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || 'Login failed. Please check your credentials.' };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const registerEmployee = async (payload: any): Promise<{ success: boolean; message?: string; error?: string; user?: AuthUser }> => {
    setIsAuthenticating(true);
    try {
      const resp = await api.authRegister(payload);
      return { success: true, message: resp.message, user: resp.user };
    } catch (err: any) {
      return { success: false, error: err.message || 'Registration failed.' };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const verifyEmailToken = async (token: string): Promise<{ success: boolean; message?: string; error?: string; user?: AuthUser }> => {
    setIsAuthenticating(true);
    try {
      const resp = await api.authVerifyEmail(token);
      return { success: true, message: resp.message, user: resp.user };
    } catch (err: any) {
      return { success: false, error: err.message || 'Email verification failed.' };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const requestPasswordReset = async (email: string): Promise<{ success: boolean; message?: string; error?: string }> => {
    setIsAuthenticating(true);
    try {
      const resp = await api.authRequestPasswordReset(email);
      return { success: true, message: resp.message };
    } catch (err: any) {
      return { success: false, error: err.message || 'Failed to request password reset.' };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const confirmPasswordReset = async (token: string, newPassword: string): Promise<{ success: boolean; message?: string; error?: string }> => {
    setIsAuthenticating(true);
    try {
      const resp = await api.authConfirmPasswordReset(token, newPassword);
      return { success: true, message: resp.message };
    } catch (err: any) {
      return { success: false, error: err.message || 'Failed to reset password.' };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const acceptAdminInvite = async (payload: { token: string; fullName: string; password: string }): Promise<{ success: boolean; error?: string }> => {
    setIsAuthenticating(true);
    try {
      const tokens = await api.authAcceptAdminInvite({
        token: payload.token,
        full_name: payload.fullName,
        password: payload.password,
      });
      setAuthTokens({ access_token: tokens.access_token, refresh_token: tokens.refresh_token });
      setAuthTokensState(tokens);
      setAuthUser(tokens.user);
      setUserRole('admin');
      setIsLoggedIn(true);
      setCurrentRoute('admin');
      try { window.location.hash = 'route=admin&tab=analytics'; } catch {}
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message || 'Failed to accept invitation.' };
    } finally {
      setIsAuthenticating(false);
    }
  };

  // Restore authenticated session on mount if token is stored
  useEffect(() => {
    const tokens = getAuthTokens();
    if (tokens.accessToken) {
      api.authGetMe()
        .then(async (user) => {
          setAuthUser(user);
          setIsLoggedIn(true);
          if (user.account_type === 'EMPLOYEE') {
            setUserRole('employee');
            if (!user.is_approved) {
              try {
                const statusData = await api.getEmployeeApplicationStatus();
                setEmployeeStatus(statusData);
              } catch {}
              setCurrentRoute('pending-approval');
            }
          } else if (user.account_type === 'ADMINISTRATOR') {
            setUserRole('admin');
          } else if (user.account_type === 'PROJECT_STAFF') {
            setUserRole('project_staff');
          }
        })
        .catch(() => {
          setAuthTokens(null);
          setAuthUser(null);
        });
    }
  }, []);


  const markNotificationRead = (id: string) => {
    setUnreadNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const toggleModuleCompletion = (courseId: string, moduleId: number) => {
    setCourses((prevCourses) =>
      prevCourses.map((course) => {
        if (course.id !== courseId) return course;
        const updatedModules = course.modules.map((mod) => {
          if (mod.id === moduleId) {
            return { ...mod, completed: !mod.completed };
          }
          return mod;
        });
        const completedCount = updatedModules.filter((m) => m.completed).length;
        const newProgress = Math.round((completedCount / updatedModules.length) * 100);
        return {
          ...course,
          modules: updatedModules,
          completedModules: completedCount,
          progress: newProgress
        };
      })
    );
  };

  const submitQuizAnswers = (answers: Record<number, 'A' | 'B' | 'C' | 'D'>) => {
    let correctCount = 0;
    activeQuiz.questions.forEach((q) => {
      if (answers[q.id] === q.correctAnswer) {
        correctCount++;
      }
    });

    const calculatedPercentage = Math.round(
      (correctCount / activeQuiz.questions.length) * 100
    );

    const submission: QuizSubmissionState = {
      completed: true,
      score: correctCount,
      totalQuestions: activeQuiz.questions.length,
      percentage: calculatedPercentage,
      skillName: 'Data Analytics / Statistics',
      previousSkillScore: 68,
      newSkillScore: 72,
      userAnswers: answers,
      feedback:
        calculatedPercentage >= 70
          ? 'Proficiency demonstrated! Score reflects command of official survey tabulations and statistical principles.'
          : 'Assessment complete. Recommended course modules will reinforce areas requiring deeper review.'
    };

    setQuizSubmission(submission);

    // Update weekly hours: +0.5h
    setWeeklyHours((prev) => Math.min(8.0, +(prev + 0.5).toFixed(1)));

    // Add to learning history
    const newHistoryEntry: LearningHistoryRecord = {
      id: `hist-${Date.now()}`,
      date: 'Today',
      course: 'Statistical Assessment',
      activity: 'Quiz',
      duration: '15 min',
      score: `${calculatedPercentage}%`,
      status: 'Completed',
      skill: 'Data Analytics'
    };
    setHistory((prev) => [newHistoryEntry, ...prev]);

    // Trigger celebratory confetti
    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
    } catch {
      // ignore
    }
  };

  const retakeQuiz = () => {
    setQuizSubmission(null);
  };

  const updateUserProfile = (newProfile: Partial<UserProfile>) => {
    setUserProfile((prev) => ({ ...prev, ...newProfile }));
  };

  const resetDemoData = () => {
    void resetDemoState();
  };

  const recordLearningActivity = async (
    courseId: string,
    title: string,
    activityType: 'enrolled' | 'in_progress' | 'completed' | 'reference_consulted',
    competencyId?: string,
    notes?: string
  ): Promise<boolean> => {
    const learnerId = selectedLearnerIdRef.current;
    if (!learnerId) return false;
    try {
      await api.recordLearningActivity(learnerId, {
        resource_id: courseId,
        resource_title: title,
        activity_type: activityType,
        target_competency_id: competencyId || null,
        notes: notes || `Logged as ${activityType} from recommendation card.`
      });
      await loadLearnerIntelligence(learnerId);
      return true;
    } catch (err) {
      console.error('Failed to record learning activity:', err);
      return false;
    }
  };

  // =========================================================================
  // Stage 4.4 Diagnostic Assessment Implementation
  // =========================================================================

  const startDiagnosticAssessment = async (competencyId?: string) => {
    let targetCompId = competencyId || selectedAssessmentTopicId || undefined;
    if (assessmentTopics.length > 0 && targetCompId) {
      const topicExists = assessmentTopics.some((t) => t.competency_id === targetCompId);
      if (!topicExists) {
        targetCompId = assessmentTopics[0].competency_id;
      }
    }

    setIsAssessmentLoading(true);
    setAssessmentError(null);
    setAssessmentResult(null);
    try {
      const resp = await api.startAssessment({
        learner_id: selectedLearnerId,
        competency_id: targetCompId,
        question_count: 4
      });
      setActiveAssessment(resp);
      if (resp.competency_id) {
        setSelectedAssessmentTopicId(resp.competency_id);
      }
    } catch (err: any) {
      console.error('Failed to start diagnostic assessment:', err);
      // If requested competency has no questions, fallback to available primary assessment topic
      if (targetCompId && targetCompId !== 'KCM-FUNC-11') {
        try {
          const fallbackResp = await api.startAssessment({
            learner_id: selectedLearnerId,
            competency_id: 'KCM-FUNC-11',
            question_count: 4
          });
          setActiveAssessment(fallbackResp);
          setSelectedAssessmentTopicId('KCM-FUNC-11');
          return;
        } catch {
          // ignore fallback error
        }
      }
      setAssessmentError(err.message || 'Failed to start diagnostic assessment');
    } finally {
      setIsAssessmentLoading(false);
    }
  };

  const submitDiagnosticAssessment = async (answers: Record<string, string>) => {
    if (!activeAssessment) return;
    setIsAssessmentLoading(true);
    setAssessmentError(null);
    try {
      const res = await api.submitAssessment(activeAssessment.attempt_id, {
        attempt_id: activeAssessment.attempt_id,
        learner_id: selectedLearnerId,
        answers
      });
      setAssessmentResult(res);
      setQuizSubmission({
        completed: true,
        score: res.correct_count,
        totalQuestions: res.total_questions,
        percentage: res.score_percentage,
        skillName: res.competency_name,
        previousSkillScore: 0,
        newSkillScore: Math.round((res.provisional_estimate.estimated_level / 5) * 100),
        userAnswers: {},
        feedback: res.provisional_estimate.methodology_note
      });

      // Re-query skill gaps and recommendations for the learner so the UI profile reflects the provisional assessment
      await loadLearnerIntelligence(selectedLearnerId);

      // Refresh learners list so admin overview reflects updated counts
      const updatedLearners = await api.getLearners();
      setAvailableLearners(updatedLearners);

      // Add to learning history
      const newHistoryEntry: LearningHistoryRecord = {
        id: `hist-${Date.now()}`,
        date: 'Today',
        course: `Diagnostic Assessment: ${res.competency_name}`,
        activity: 'Assessment',
        duration: '10 min',
        score: `${res.score_percentage}% (${res.correct_count}/${res.total_questions})`,
        status: 'Completed',
        skill: res.competency_name
      };
      setHistory((prev) => [newHistoryEntry, ...prev]);

      // Confetti celebration if passing or good score
      if (res.score_percentage >= 50) {
        try {
          confetti({
            particleCount: 80,
            spread: 70,
            origin: { y: 0.6 }
          });
        } catch {
          // ignore
        }
      }
    } catch (err: any) {
      console.error('Failed to submit diagnostic assessment:', err);
      setAssessmentError(err.message || 'Failed to submit diagnostic assessment');
    } finally {
      setIsAssessmentLoading(false);
    }
  };

  const resetDiagnosticAssessment = () => {
    setActiveAssessment(null);
    setAssessmentResult(null);
    setAssessmentError(null);
  };

  const resetDemoState = async () => {
    setIsLoading(true);
    try {
      await api.resetDemoState();
      setActiveAssessment(null);
      setAssessmentResult(null);
      await reloadBackendData();
    } catch (err: any) {
      console.error('Failed to reset demo state:', err);
      setApiError(err.message || 'Failed to reset demo state');
    } finally {
      setIsLoading(false);
    }
  };

  // Build real AdminEmployee objects from availableLearners
  const adminEmployeesList: AdminEmployee[] = availableLearners.map((l) => {
    const roleObj = availableRoles.find((r) => r.role_id === l.role_id);
    const assessedCount = l.assessed_competencies.filter(
      (a) => a.assessment_status === 'assessed' && a.estimated_level !== null
    ).length;
    const totalRequired = roleObj?.required_competencies.length || 4;
    const isCurrent = l.learner_id === selectedLearnerId;

    let status: AdminEmployee['status'] = 'On Track';
    if (assessedCount === 0) status = 'Needs Attention';
    else if (assessedCount >= totalRequired) status = 'Exceeding Target';

    return {
      id: l.learner_id,
      name: l.name,
      employeeId: l.learner_id,
      department: l.department,
      role: roleObj?.role_name || l.role_id,
      competency: Math.round((assessedCount / totalRequired) * 100),
      skillGapsCount: isCurrent && skillGapReport ? skillGapReport.gap_count : totalRequired - assessedCount,
      weeklyHours: 6.5,
      status,
      isSynthetic: true,
      assessedCount,
      totalRequired
    };
  });

  return (
    <AppContext.Provider
      value={{
        currentRoute,
        userRole,
        isLoggedIn,
        userProfile,
        skills,
        overallCompetency,
        weeklyHours,
        weeklyTarget,
        coursesCompleted,
        totalCourses,
        skillGapsCount,
        highPriorityGaps,
        weeklyDays,
        weeklyBreakdown,
        activityTimeline,
        courses,
        selectedCourseId,
        activeQuiz,
        quizSubmission,
        history,
        notificationCount: unreadNotifications.filter((n) => !n.read).length,
        unreadNotifications,
        navigateTo,
        setUserRole,
        adminTab,
        setAdminTab,
        recordLearningActivity,
        loginAs,
        logout,
        toggleModuleCompletion,
        submitQuizAnswers,
        retakeQuiz,
        updateUserProfile,
        resetDemoData,
        markNotificationRead,

        // Real Backend Integrations
        isLoading,
        isBackendOffline,
        apiError,
        apiBaseUrl: API_BASE_URL,
        healthData,
        availableLearners,
        availableRoles,
        allCompetencies,
        allCourses,
        selectedLearnerId,
        selectLearner,
        skillGapReport,
        recommendationReport,
        reloadBackendData,
        adminEmployeesList,

        // Diagnostic Assessment
        assessmentTopics,
        activeAssessment,
        assessmentResult,
        isAssessmentLoading,
        assessmentError,
        selectedAssessmentTopicId,
        setSelectedAssessmentTopicId,
        startDiagnosticAssessment,
        submitDiagnosticAssessment,
        resetDiagnosticAssessment,
        resetDemoState,

        // Phase 2
        authUser,
        authTokens: authTokensState,
        employeeStatus,
        isAuthenticating,
        loginWithCredentials,
        registerEmployee,
        verifyEmailToken,
        requestPasswordReset,
        confirmPasswordReset,
        acceptAdminInvite,
        refreshApplicationStatus
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
