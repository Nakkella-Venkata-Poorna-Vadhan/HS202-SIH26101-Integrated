import React from 'react';
import { useApp } from '../context/AppContext';
import { StatCard } from '../components/common/StatCard';
import { WeeklyChart } from '../components/dashboard/WeeklyChart';
import { SkillProgressList } from '../components/dashboard/SkillProgressList';
import { WeeklyAchievements } from '../components/dashboard/WeeklyAchievements';
import { RecommendationPreview } from '../components/dashboard/RecommendationPreview';
import {
  Award,
  Clock,
  BookOpen,
  TrendingDown,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CalendarCheck,
  HelpCircle,
  Users2
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const {
    userProfile,
    overallCompetency,
    weeklyHours,
    weeklyTarget,
    coursesCompleted,
    totalCourses,
    skillGapsCount,
    highPriorityGaps,
    skills,
    weeklyDays,
    courses,
    navigateTo,
    availableLearners,
    selectedLearnerId,
    selectLearner,
    skillGapReport
  } = useApp();

  return (
    <div className="space-y-6">
      {/* Welcome & Profile Selection Banner */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-900 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
              {userProfile.department}
            </span>
            <span className="text-xs text-slate-500">• ID: {userProfile.employeeId}</span>
            <span className="text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full">
              Synthetic Demonstration Profile
            </span>
          </div>

          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Officer Dashboard: {userProfile.name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            {userProfile.designation} — Competency requirements evaluated against official KCM & ACBP schedules.
          </p>
        </div>

        {/* Quick Profile Switcher & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-lg border border-slate-200">
            <Users2 className="w-4 h-4 text-blue-800 ml-1.5" />
            <select
              value={selectedLearnerId}
              onChange={(e) => selectLearner(e.target.value)}
              className="bg-transparent text-xs font-bold text-slate-800 focus:outline-none cursor-pointer pr-2"
              title="Select demonstration learner profile"
            >
              {availableLearners.map((l) => (
                <option key={l.learner_id} value={l.learner_id}>
                  {l.name} ({l.learner_id})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => navigateTo('skill-gap')}
            className="px-4 py-2.5 text-xs font-bold text-blue-900 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors flex items-center gap-1.5 shadow-2xs"
          >
            <TrendingDown className="w-4 h-4 text-rose-600" />
            <span>Skill Gaps ({skillGapsCount})</span>
          </button>

          <button
            onClick={() => navigateTo('recommendations')}
            className="px-4 py-2.5 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow transition-colors flex items-center gap-1.5"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>ACBP Recommendations</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* TOP 4 AUTHORITATIVE KPI CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Overall Role Competency */}
        <StatCard
          title="Role Competency"
          value={`${overallCompetency}%`}
          subtext={`${skillGapReport?.competent_count ?? 0} of ${skillGapReport?.total_required_competencies ?? skills.length} requirements met`}
          badge="Prototype 5-Level Scale"
          badgeType={overallCompetency >= 75 ? 'success' : overallCompetency >= 50 ? 'info' : 'warning'}
          icon={Award}
          iconBg="bg-blue-50"
          iconColor="text-blue-800"
          onClick={() => navigateTo('competency-assessment')}
        />

        {/* 2. Assessment Coverage */}
        <StatCard
          title="Assessed Coverage"
          value={`${(skillGapReport?.total_required_competencies ?? 0) - (skillGapReport?.unassessed_count ?? 0)} / ${skillGapReport?.total_required_competencies ?? skills.length}`}
          subtext={`${skillGapReport?.unassessed_count ?? 0} unassessed on prototype scale`}
          badge={skillGapReport?.unassessed_count ? `${skillGapReport.unassessed_count} Unassessed` : '100% Evaluated'}
          badgeType={skillGapReport?.unassessed_count ? 'warning' : 'success'}
          icon={ShieldCheck}
          iconBg="bg-emerald-50"
          iconColor="text-emerald-700"
          onClick={() => navigateTo('skill-gap')}
        />

        {/* 3. Recommended ACBP Courses */}
        <StatCard
          title="ACBP Recommendations"
          value={courses.length}
          subtext={`${courses.filter(c => c.mappingStatus === 'candidate' || c.mappingStatus === 'validated').length} candidate/validated mappings`}
          badge={`${courses.length} Interventions`}
          badgeType="info"
          icon={BookOpen}
          iconBg="bg-purple-50"
          iconColor="text-purple-700"
          onClick={() => navigateTo('recommendations')}
        />

        {/* 4. Identified Skill Gaps */}
        <StatCard
          title="Identified Skill Gaps"
          value={skillGapsCount}
          subtext={`${highPriorityGaps} critical/high priority`}
          badge={highPriorityGaps > 0 ? `${highPriorityGaps} High Priority` : 'No Critical Gaps'}
          badgeType={highPriorityGaps > 0 ? 'danger' : 'success'}
          icon={TrendingDown}
          iconBg="bg-rose-50"
          iconColor="text-rose-700"
          onClick={() => navigateTo('skill-gap')}
        />
      </div>

      {/* Main Grid: Weekly Progress Chart & Required Competencies List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Weekly Progress Chart (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <WeeklyChart
            days={weeklyDays}
            totalHours={weeklyHours}
            targetHours={weeklyTarget}
            onViewDetailed={() => navigateTo('weekly-progress')}
          />

          <WeeklyAchievements weeklyHours={weeklyHours} />
        </div>

        {/* Right Column: Required Competencies Horizontal Bars (5 cols) */}
        <div className="lg:col-span-5">
          <SkillProgressList
            skills={skills}
            onViewAll={() => navigateTo('skill-gap')}
            onSelectSkill={(skillName) => {
              const matchedCourse = courses.find(
                (c) =>
                  c.skillCategory.toLowerCase().includes(skillName.toLowerCase()) ||
                  c.targetCompetencyName?.toLowerCase().includes(skillName.toLowerCase())
              );
              if (matchedCourse) {
                navigateTo('course-details', matchedCourse.id);
              } else {
                navigateTo('skill-gap');
              }
            }}
          />
        </div>
      </div>

      {/* Real Recommendations Preview Section */}
      <RecommendationPreview
        courses={courses}
        onViewPath={() => navigateTo('recommendations')}
        onOpenCourse={(id) => navigateTo('course-details', id)}
      />
    </div>
  );
};
