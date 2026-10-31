import React from 'react';
import { useApp } from '../context/AppContext';
import { WeekSelector } from '../components/weekly/WeekSelector';
import { DailyProgressChart } from '../components/weekly/DailyProgressChart';
import { LearningBreakdownTable } from '../components/weekly/LearningBreakdownTable';
import { ActivityTimeline } from '../components/weekly/ActivityTimeline';
import { AIInsightCard } from '../components/weekly/AIInsightCard';
import { StatCard } from '../components/common/StatCard';
import { Clock, BookOpen, Award, TrendingUp, Sparkles, ArrowRight, Info } from 'lucide-react';

export const WeeklyProgressPage: React.FC = () => {
  const {
    weeklyHours,
    weeklyTarget,
    weeklyDays,
    weeklyBreakdown,
    activityTimeline,
    navigateTo,
    quizSubmission,
    coursesCompleted,
    userProfile,
    courses
  } = useApp();

  const handleOpenCourse = (courseName: string) => {
    const found = courses.find(
      (c) =>
        c.title.toLowerCase().includes(courseName.toLowerCase()) ||
        courseName.toLowerCase().includes(c.title.toLowerCase())
    );
    if (found) {
      navigateTo('course-details', found.id);
    } else if (courses.length > 0) {
      navigateTo('course-details', courses[0].id);
    } else {
      navigateTo('recommendations');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider bg-blue-100 text-blue-900 px-2 py-0.5 rounded">
              Learning Activity Hub
            </span>
            <span className="text-xs text-slate-500">• {userProfile.name} ({userProfile.employeeId})</span>
            <span className="text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full">
              Interactive Sandbox Log
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Weekly Learning Activity & Progress
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            Interactive client demonstration logging study time, completed course modules, and assessment activity for {userProfile.name}.
          </p>
        </div>

        <button
          onClick={() => navigateTo('skill-gap')}
          className="px-4 py-2.5 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow transition-colors flex items-center gap-1.5"
        >
          <span>Next: Competency Gap Analysis</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Week Selector (October 1 – October 7, 2026) */}
      <WeekSelector onExport={() => window.print()} />

      {/* Sandbox Notice */}
      <div className="flex items-start gap-2 bg-white p-3 rounded-xl border border-slate-200 text-xs text-slate-600 shadow-2xs">
        <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
        <span>
          <strong>Sandbox Notice:</strong> Weekly study metrics illustrate client-side study telemetry and interactive module completion within this demonstration session. Official backend authority governs KCM competency definitions, ACBP courses, and deterministic gap-reduction recommendations.
        </span>
      </div>

      {/* 4 SUMMARY CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Learning Hours */}
        <StatCard
          title="Recorded Learning Hours"
          value={`${weeklyHours} / ${weeklyTarget} hrs`}
          subtext={`${Math.max(0, +(weeklyTarget - weeklyHours).toFixed(1))}h remaining to weekly target`}
          badge="Sandbox Target"
          badgeType="success"
          icon={Clock}
          iconBg="bg-blue-50"
          iconColor="text-blue-800"
        />

        {/* Modules */}
        <StatCard
          title="LMS Course Completions"
          value={`${coursesCompleted} Verified`}
          subtext="No completion ledger records synced from LMS"
          badge="Sync Pending"
          badgeType="info"
          icon={BookOpen}
          iconBg="bg-slate-50"
          iconColor="text-slate-600"
        />

        {/* Quiz Score */}
        <StatCard
          title="Diagnostic Assessment"
          value={quizSubmission ? `${quizSubmission.percentage}%` : 'Not Attempted'}
          subtext={quizSubmission ? 'Calculated from live MCQ quiz' : 'Diagnostic testing available in /quiz'}
          badge={quizSubmission ? 'Live Result' : 'Unattempted'}
          badgeType={quizSubmission ? 'success' : 'info'}
          icon={Award}
          iconBg="bg-emerald-50"
          iconColor="text-emerald-700"
          onClick={() => navigateTo('quiz')}
        />

        {/* Competency Improvement */}
        <StatCard
          title="Proficiency Delta"
          value={quizSubmission ? '+4% (MCQ Quiz)' : '—'}
          subtext={quizSubmission ? 'Estimated improvement from assessment' : 'Requires post-diagnostic evaluation'}
          badge={quizSubmission ? 'Demonstrated' : 'Pending'}
          badgeType={quizSubmission ? 'warning' : 'info'}
          icon={TrendingUp}
          iconBg="bg-amber-50"
          iconColor="text-amber-700"
        />
      </div>

      {/* Daily Progress Chart & AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <DailyProgressChart days={weeklyDays} />
        </div>
        <div className="lg:col-span-5">
          <AIInsightCard onViewRecommendations={() => navigateTo('recommendations')} />
        </div>
      </div>

      {/* Weekly Breakdown Table & Activity Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6">
          <LearningBreakdownTable
            items={weeklyBreakdown}
            onOpenCourse={handleOpenCourse}
          />
        </div>
        <div className="lg:col-span-6">
          <ActivityTimeline timeline={activityTimeline} />
        </div>
      </div>
    </div>
  );
};
