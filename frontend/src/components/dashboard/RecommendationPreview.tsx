import React from 'react';
import { Sparkles, Clock, ArrowRight, ShieldCheck, BookOpen, CheckCircle, HelpCircle } from 'lucide-react';
import { Course } from '../../types';

interface RecommendationPreviewProps {
  courses: Course[];
  onViewPath: () => void;
  onOpenCourse: (courseId: string) => void;
}

export const RecommendationPreview: React.FC<RecommendationPreviewProps> = ({
  courses,
  onViewPath,
  onOpenCourse
}) => {
  // Show top 3 recommended
  const topRecommendations = courses.slice(0, 3);

  const getMappingBadge = (status?: Course['mappingStatus']) => {
    switch (status) {
      case 'validated':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            Validated Mapping
          </span>
        );
      case 'candidate':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
            Candidate Mapping
          </span>
        );
      case 'unresolved':
      default:
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
            Unresolved Domain
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1 rounded bg-purple-100 text-purple-700">
              <Sparkles className="w-4 h-4" />
            </div>
            <h3 className="text-base font-bold text-slate-900">
              ACBP Course Recommendations (Deterministic Ranking)
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real courses from MoSPI ACBP 2026-27 schedule prioritized by your identified skill gaps
          </p>
        </div>

        <button
          onClick={onViewPath}
          className="text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-colors flex items-center gap-1.5"
        >
          <span>View All {courses.length} Recommendations</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {topRecommendations.map((course, idx) => (
          <div
            key={course.id}
            className="rounded-xl border border-slate-200 p-4 bg-slate-50/50 hover:bg-white hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between gap-1 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Rank #{idx + 1} • {course.id}
                </span>
                {getMappingBadge(course.mappingStatus)}
              </div>

              <h4 className="text-sm font-bold text-slate-900 mb-1 leading-snug line-clamp-2">
                {course.title}
              </h4>

              <p className="text-[11px] text-slate-500 mb-2 truncate">
                Provider: {course.instructor || 'MoSPI / NSSTA'}
              </p>

              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 mb-3">
                <span className="bg-slate-100 text-slate-700 text-[11px] font-medium px-2 py-0.5 rounded">
                  {course.skillCategory}
                </span>
                <span className="flex items-center gap-1 text-[11px] font-medium text-slate-600">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {course.duration}
                </span>
              </div>

              {course.recommendationReason && (
                <p className="text-[11px] text-slate-600 bg-white p-2.5 rounded border border-slate-200 mb-3 leading-relaxed">
                  <span className="font-semibold text-slate-800">Recommendation Logic: </span>
                  {course.recommendationReason}
                </p>
              )}
            </div>

            <div className="pt-2 border-t border-slate-200/80 flex items-center justify-between">
              <span className="text-[10px] text-slate-500 font-medium">
                {course.provenance || 'official_public'}
              </span>

              <button
                onClick={() => onOpenCourse(course.id)}
                className="text-xs font-bold text-blue-700 hover:text-blue-900 flex items-center gap-1 hover:underline"
              >
                <span>Inspect Course</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}

        {topRecommendations.length === 0 && (
          <div className="col-span-3 text-center py-8 text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
            No course recommendations available. Please verify backend connection.
          </div>
        )}
      </div>
    </div>
  );
};
