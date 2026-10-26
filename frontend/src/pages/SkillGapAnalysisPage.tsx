import React from 'react';
import { useApp } from '../context/AppContext';
import { RadarGapChart } from '../components/skillgap/RadarGapChart';
import { PriorityGaps } from '../components/skillgap/PriorityGaps';
import { TrendingDown, Sparkles, ArrowRight, ShieldAlert, Award, Users2 } from 'lucide-react';

export const SkillGapAnalysisPage: React.FC = () => {
  const {
    skills,
    navigateTo,
    userProfile,
    skillGapReport,
    availableLearners,
    selectedLearnerId,
    selectLearner,
    courses
  } = useApp();

  return (
    <div className="space-y-6">
      {/* Title & Introduction */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider bg-rose-100 text-rose-800 px-2 py-0.5 rounded">
              Competency Intelligence Diagnostic
            </span>
            <span className="text-xs text-slate-500">• MoSPI Cadre Benchmark</span>
            <span className="text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full">
              Synthetic Demonstration Profile
            </span>
          </div>

          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Competency Gap Analysis: {userProfile.name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
            Multi-variable gap modeling evaluating {userProfile.name} ({userProfile.employeeId}) against{' '}
            {userProfile.designation} role requirements on the Mission Karmayogi Prototype 5-Level Scale.
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

          <button
            onClick={() => navigateTo('recommendations')}
            className="px-5 py-2.5 text-xs font-bold text-slate-950 bg-amber-400 hover:bg-amber-300 rounded-lg shadow-sm flex items-center gap-2 transition-all"
          >
            <Sparkles className="w-4 h-4 fill-slate-950" />
            <span>Generate ACBP Path</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Radar Chart Component */}
      <RadarGapChart skills={skills} />

      {/* Priority Skill Gaps Section */}
      <PriorityGaps
        onGeneratePath={() => navigateTo('recommendations')}
        onSelectGapCourse={(competencyId, competencyName) => {
          // Find matching course in recommendations
          const matched = courses.find(
            (c) =>
              c.targetCompetencyId === competencyId ||
              c.skillCategory.toLowerCase().includes(competencyName.toLowerCase())
          );
          if (matched) {
            navigateTo('course-details', matched.id);
          } else {
            navigateTo('recommendations');
          }
        }}
      />
    </div>
  );
};
