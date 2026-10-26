import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { LearningPathRoadmap } from '../components/recommendations/LearningPathRoadmap';
import { CourseCard } from '../components/recommendations/CourseCard';
import { ExternalIntegrations } from '../components/recommendations/ExternalIntegrations';
import { Sparkles, ArrowRight, BookOpen, Layers, Users2, Filter } from 'lucide-react';

export const RecommendationsPage: React.FC = () => {
  const {
    courses,
    navigateTo,
    userProfile,
    availableLearners,
    selectedLearnerId,
    selectLearner,
    recommendationReport
  } = useApp();

  const [categoryFilter, setCategoryFilter] = useState<string>('All');

  const filteredCourses = courses.filter((c) => {
    if (categoryFilter === 'All') return true;
    if (categoryFilter === 'Mapped') return c.mappingStatus === 'candidate' || c.mappingStatus === 'validated';
    if (categoryFilter === 'Unresolved') return c.mappingStatus === 'unresolved';
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider bg-purple-100 text-purple-900 px-2 py-0.5 rounded">
              ACBP Recommendation Engine
            </span>
            <span className="text-xs text-slate-500">• MoSPI Competency Intelligence Engine</span>
            <span className="text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full">
              Deterministic Ranking
            </span>
          </div>

          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Curriculum Recommendations for {userProfile.name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
            Deterministic ranking matching MoSPI Annual Capacity Building Plan courses to{' '}
            {userProfile.name}&apos;s identified competency gaps, administrative cadre tier, and mapping confidence.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-lg border border-slate-200">
            <Users2 className="w-4 h-4 text-blue-800 ml-1.5" />
            <select
              value={selectedLearnerId}
              onChange={(e) => selectLearner(e.target.value)}
              className="bg-transparent text-xs font-bold text-slate-800 focus:outline-none cursor-pointer pr-2"
              title="Switch demonstration learner profile"
            >
              {availableLearners.map((l) => (
                <option key={l.learner_id} value={l.learner_id}>
                  {l.name} ({l.learner_id})
                </option>
              ))}
            </select>
          </div>

          {courses.length > 0 && (
            <button
              onClick={() => navigateTo('course-details', courses[0].id)}
              className="px-5 py-2.5 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-sm flex items-center gap-2 transition-all"
            >
              <span>Inspect Rank #1 Course</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Sequential Roadmap (Step 1 -> Step 2 -> Step 3 -> Step 4) */}
      <LearningPathRoadmap
        onSelectStepCourse={(courseId) => navigateTo('course-details', courseId)}
      />

      {/* Recommended Courses Grid */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Ranked ACBP Course Catalogue ({filteredCourses.length} Interventions)
            </h3>
            <p className="text-xs text-slate-500">
              Preserving official validation states: Candidate Mappings, Validated Mappings, and Unresolved Domain Gaps
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 flex items-center gap-1 font-medium mr-1">
              <Filter className="w-3.5 h-3.5" /> Filter:
            </span>
            {['All', 'Mapped', 'Unresolved'].map((filterKey) => (
              <button
                key={filterKey}
                onClick={() => setCategoryFilter(filterKey)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-colors ${
                  categoryFilter === filterKey
                    ? 'bg-blue-900 text-white shadow-2xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {filterKey}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCourses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onOpen={(id) => navigateTo('course-details', id)}
            />
          ))}
        </div>

        {filteredCourses.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl border border-slate-200 text-xs text-slate-500">
            No courses match the selected filter.
          </div>
        )}
      </div>

      {/* External Training Programs: iGOT Karmayogi, NSSTA, Workshop */}
      <ExternalIntegrations />
    </div>
  );
};
