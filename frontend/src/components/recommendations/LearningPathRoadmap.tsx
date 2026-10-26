import React from 'react';
import { ArrowDown, CheckCircle2, Sparkles, Clock, Target, ArrowRight, BookOpen } from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface LearningPathRoadmapProps {
  onSelectStepCourse: (courseId: string) => void;
}

export const LearningPathRoadmap: React.FC<LearningPathRoadmapProps> = ({
  onSelectStepCourse
}) => {
  const { courses, recommendationReport, userProfile } = useApp();

  // Take top 4 recommended courses from the engine
  const roadmapCourses = courses.slice(0, 4);

  const getMappingBadge = (status?: string) => {
    switch (status) {
      case 'validated':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
            Validated Mapping
          </span>
        );
      case 'candidate':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
            Candidate Mapping
          </span>
        );
      case 'unresolved':
      default:
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 text-slate-700">
            Unresolved Domain
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-400 text-slate-900 font-bold">
              <Sparkles className="w-4 h-4 fill-slate-900" />
            </div>
            <h3 className="text-base font-bold text-slate-900">
              Deterministic Recommendation Roadmap for {userProfile.name}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Sequential curriculum ordered by identified gap magnitude, cadre match, and mapping confidence
          </p>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-blue-50 text-blue-800 border border-blue-200">
          {recommendationReport?.total_gaps_addressed ?? 0} Skill Gaps Addressed
        </span>
      </div>

      {/* Sequential Roadmap Steps */}
      <div className="space-y-4">
        {roadmapCourses.length === 0 && (
          <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300 text-xs text-slate-500">
            No active course recommendations mapped for this cadre tier yet. Select another profile or explore all courses below.
          </div>
        )}
        {roadmapCourses.map((item, index) => (
          <React.Fragment key={item.id}>
            <div
              onClick={() => onSelectStepCourse(item.id)}
              className="group p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-white hover:border-blue-300 hover:shadow-md transition-all cursor-pointer flex flex-wrap md:flex-nowrap items-center justify-between gap-4"
            >
              <div className="flex items-start space-x-3.5">
                <div className="w-10 h-10 rounded-xl bg-blue-900 text-white font-extrabold flex items-center justify-center shrink-0 shadow-sm text-sm group-hover:bg-blue-800">
                  {index + 1}
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                      Step {index + 1} • {item.id}
                    </span>
                    {getMappingBadge(item.mappingStatus)}
                    {item.priority && (
                      <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                        {item.priority} Priority
                      </span>
                    )}
                  </div>

                  <h4 className="text-sm font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                    {item.title}
                  </h4>

                  <p className="text-xs text-slate-500 mt-0.5">
                    Provider: {item.instructor} • Target: {item.targetCompetencyName || item.skillCategory}
                  </p>

                  <div className="mt-2 text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-slate-200/80 leading-relaxed">
                    <span className="font-semibold text-slate-800">Recommendation Rationale: </span>
                    {item.recommendationReason}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 self-end md:self-center shrink-0">
                <div className="text-right">
                  <span className="flex items-center gap-1 text-xs font-semibold text-slate-600">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    {item.duration}
                  </span>
                  <span className="text-[10px] font-medium text-emerald-700 block">
                    {item.targetGapReduction || 'ACBP Curriculum'}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={() => onSelectStepCourse(item.id)}
                  className="px-3 py-1.5 text-xs font-bold text-blue-900 bg-blue-50 group-hover:bg-blue-600 group-hover:text-white rounded-lg transition-colors flex items-center gap-1 shadow-2xs"
                >
                  <span>Open Course</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {index < roadmapCourses.length - 1 && (
              <div className="flex justify-center -my-2">
                <div className="w-6 h-6 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400">
                  <ArrowDown className="w-3 h-3" />
                </div>
              </div>
            )}
          </React.Fragment>
        ))}

        {roadmapCourses.length === 0 && (
          <div className="text-center py-8 text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
            No roadmap steps available. Please connect backend service.
          </div>
        )}
      </div>
    </div>
  );
};
