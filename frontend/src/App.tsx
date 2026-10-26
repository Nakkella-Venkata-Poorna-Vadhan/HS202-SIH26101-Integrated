import React, { useState } from 'react';
import { useApp } from './context/AppContext';
import { Header } from './components/common/Header';
import { Sidebar } from './components/common/Sidebar';
import { DemoFlowBanner } from './components/common/DemoFlowBanner';
import { AlertCircle, RefreshCw, Server, ShieldAlert } from 'lucide-react';

// Pages
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { WeeklyProgressPage } from './pages/WeeklyProgressPage';
import { CompetencyAssessmentPage } from './pages/CompetencyAssessmentPage';
import { SkillGapAnalysisPage } from './pages/SkillGapAnalysisPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { CourseDetailPage } from './pages/CourseDetailPage';
import { QuizPage } from './pages/QuizPage';
import { LearningHistoryPage } from './pages/LearningHistoryPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';

import { ErrorBoundary } from './components/common/ErrorBoundary';

export const AppContent: React.FC = () => {
  const {
    currentRoute,
    isLoggedIn,
    isBackendOffline,
    apiError,
    apiBaseUrl,
    reloadBackendData,
    isLoading
  } = useApp();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // If user is not logged in or on the login page
  if (!isLoggedIn || currentRoute === 'login') {
    return (
      <ErrorBoundary>
        <LoginPage />
      </ErrorBoundary>
    );
  }

  const renderActivePage = () => {
    switch (currentRoute) {
      case 'dashboard':
        return <DashboardPage />;
      case 'weekly-progress':
        return <WeeklyProgressPage />;
      case 'competency-assessment':
        return <CompetencyAssessmentPage />;
      case 'skill-gap':
        return <SkillGapAnalysisPage />;
      case 'recommendations':
        return <RecommendationsPage />;
      case 'course-details':
        return <CourseDetailPage />;
      case 'quiz':
        return <QuizPage />;
      case 'history':
        return <LearningHistoryPage />;
      case 'profile':
        return <ProfilePage />;
      case 'admin':
        return <AdminDashboardPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col text-slate-800">
      {/* Header */}
      <Header onToggleMobileSidebar={() => setMobileSidebarOpen(!mobileSidebarOpen)} />

      {/* SIH Hackathon Interactive Demo Flow Banner */}
      <DemoFlowBanner />

      {/* Backend Offline / Connection Failure Notice */}
      {isBackendOffline && (
        <div className="bg-amber-500 text-slate-950 px-4 py-2.5 border-b border-amber-600 font-medium text-xs flex flex-wrap items-center justify-between gap-3 shadow-sm">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-slate-950" />
            <span>
              <strong>Backend Disconnected:</strong> Could not reach Competency Intelligence Engine at{' '}
              <code className="bg-amber-400/80 px-1.5 py-0.5 rounded text-[11px] font-mono">
                {apiBaseUrl}
              </code>
              .{' '}
              {apiError ? `(${apiError}) ` : ''}
              Please start the FastAPI service:
              <code className="bg-amber-400/80 px-1.5 py-0.5 rounded text-[11px] font-mono ml-1">
                python -m uvicorn competency_engine.api:app --reload
              </code>
            </span>
          </div>

          <button
            onClick={() => reloadBackendData()}
            disabled={isLoading}
            className="px-3 py-1 bg-slate-900 text-white rounded font-bold hover:bg-slate-800 transition-colors flex items-center gap-1.5 shrink-0"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Retry Connection</span>
          </button>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() => setMobileSidebarOpen(false)}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          <ErrorBoundary>
            {renderActivePage()}
          </ErrorBoundary>

          {/* Official Portal Footer */}
          <footer className="mt-12 pt-6 border-t border-slate-200 text-xs text-slate-500 flex flex-wrap items-center justify-between gap-3 pb-6">
            <div>
              <p className="font-semibold text-slate-700">
                StatSkill AI — Competency Intelligence & Capacity Building System
              </p>
              <p className="text-[11px] text-slate-400">
                Ministry of Statistics and Programme Implementation (MoSPI) • Government of India
              </p>
            </div>

            <div className="flex items-center gap-4 text-[11px]">
              <span className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-medium">
                Prototype Integrated v1.0
              </span>
              <span>Smart India Hackathon 2026</span>
              <span className="text-slate-300">|</span>
              <span className="flex items-center gap-1 text-slate-600">
                <Server className="w-3 h-3 text-emerald-600" />
                <span>Backend Engine: FastAPI</span>
              </span>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
};

export default App;
