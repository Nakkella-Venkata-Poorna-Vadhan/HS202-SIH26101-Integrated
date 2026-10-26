import React from 'react';
import { Course } from '../../types';
import { ProgressBar } from '../common/ProgressBar';
import {
  CheckCircle2,
  Circle,
  PlayCircle,
  Clock,
  User,
  Building,
  Award,
  BookOpen,
  ArrowRight,
  ClipboardCheck,
  ChevronLeft,
  Video,
  FileText,
  Code2,
  ShieldCheck,
  Tag,
  Info
} from 'lucide-react';

interface CourseDetailViewProps {
  course: Course | null | undefined;
  onToggleModule: (moduleId: number) => void;
  onGoToQuiz: () => void;
  onBack: () => void;
}

export const CourseDetailView: React.FC<CourseDetailViewProps> = ({
  course,
  onToggleModule,
  onGoToQuiz,
  onBack
}) => {
  if (!course) {
    return (
      <div className="space-y-6">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-blue-900 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Back to Courses & AI Recommendations</span>
        </button>

        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm">
          <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800 mb-1">No Course Selected</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto mb-6">
            Please browse the MoSPI capacity building catalogue and select an ACBP or iGOT Karmayogi course to view curriculum modules and syllabus details.
          </p>
          <button
            onClick={onBack}
            className="px-5 py-2.5 bg-blue-900 hover:bg-blue-800 text-white font-bold text-xs rounded-lg shadow transition-colors inline-flex items-center gap-2"
          >
            <span>Browse Recommended Courses</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  const getModuleTypeIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="w-4 h-4 text-blue-600" />;
      case 'interactive':
        return <Code2 className="w-4 h-4 text-purple-600" />;
      case 'reading':
      default:
        return <FileText className="w-4 h-4 text-slate-500" />;
    }
  };

  const getMappingBadge = (status?: Course['mappingStatus']) => {
    switch (status) {
      case 'validated':
        return (
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
            <CheckCircle2 className="w-2.5 h-2.5" />
            Validated Mapping
          </span>
        );
      case 'candidate':
        return (
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
            Candidate Mapping
          </span>
        );
      case 'unresolved':
      default:
        return (
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-300">
            Unresolved Domain
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-blue-900 transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
        <span>Back to Courses & AI Recommendations</span>
      </button>

      {/* Course Hero Card */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider bg-blue-100 text-blue-900 px-2.5 py-0.5 rounded">
              {course.id}
            </span>
            <span className="text-xs font-semibold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
              {course.skillCategory}
            </span>
            {getMappingBadge(course.mappingStatus)}
          </div>

          <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
            <Building className="w-3.5 h-3.5" />
            <span>{course.organization || 'MoSPI / NSSTA'}</span>
          </div>
        </div>

        <h1 className="text-2xl font-extrabold text-slate-900 mb-2 leading-tight">
          {course.title}
        </h1>

        {course.targetCompetencyName && (
          <div className="flex items-center gap-2 text-xs text-blue-900 bg-blue-50 border border-blue-200 rounded-lg p-2.5 mb-3 max-w-2xl">
            <Tag className="w-4 h-4 text-blue-700 shrink-0" />
            <span>
              <strong>Target KCM Competency:</strong> {course.targetCompetencyName} (
              <code className="font-mono text-blue-800">{course.targetCompetencyId}</code>)
            </span>
          </div>
        )}

        {course.cadreRole && (
          <p className="text-xs text-slate-600 mb-2">
            <strong className="text-slate-800">Target Cadre Tier:</strong> {course.cadreRole}
          </p>
        )}

        <p className="text-sm text-slate-600 max-w-3xl mb-4 leading-relaxed">
          {course.description}
        </p>

        {/* Course Info Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 mb-5 text-xs">
          <div>
            <span className="text-slate-500 block text-[11px]">Provider Institution</span>
            <span className="font-bold text-slate-900 truncate block">{course.instructor}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Official Duration</span>
            <span className="font-bold text-slate-900">{course.duration}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Official Source Register</span>
            <span className="font-bold text-blue-900">SRC-MOSPI-ACBP-2026-27</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Mapping Status</span>
            <span className="font-bold text-slate-900 capitalize">{course.mappingStatus || 'Candidate'}</span>
          </div>
        </div>

        {/* Sandbox Demonstration Notice */}
        <div className="flex items-start gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-xs text-slate-500 mb-4">
          <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
          <span>
            <strong>Interactive Module Sandbox:</strong> Module completion tracking is demonstrated locally within the client sandbox. It does not alter official ACBP course documents or assert active external LMS synchronization.
          </span>
        </div>

        {/* Progress Bar Header */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-medium">
            <span className="text-slate-700 font-bold">Demonstration Progress</span>
            <span className="text-blue-900 font-extrabold text-sm">{course.progress}%</span>
          </div>
          <ProgressBar
            value={course.progress}
            level={course.progress >= 70 ? 'strong' : 'developing'}
            height="md"
          />
          <span className="text-[11px] text-slate-500 block">
            {course.completedModules} of {course.totalModules} modules marked completed in local session
          </span>
        </div>
      </div>

      {/* Module Curriculum List */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-slate-900">Curriculum & Learning Modules</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Click checkboxes to toggle completed lessons or launch interactive sessions
            </p>
          </div>

          <button
            onClick={() => onToggleModule(course.modules[course.completedModules % course.modules.length].id)}
            className="px-4 py-2 text-xs font-bold text-white bg-blue-800 hover:bg-blue-700 rounded-lg flex items-center gap-1.5 transition-colors shadow-2xs"
          >
            <PlayCircle className="w-4 h-4" />
            <span>Toggle Next Lesson</span>
          </button>
        </div>

        <div className="divide-y divide-slate-100">
          {course.modules.map((mod) => (
            <div
              key={mod.id}
              onClick={() => onToggleModule(mod.id)}
              className={`p-4 flex items-center justify-between gap-4 transition-colors cursor-pointer hover:bg-slate-50 ${
                mod.completed ? 'bg-emerald-50/20' : ''
              }`}
            >
              <div className="flex items-center space-x-3.5">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleModule(mod.id);
                  }}
                  className="focus:outline-none"
                  aria-label={`Toggle module ${mod.id}`}
                >
                  {mod.completed ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 fill-emerald-100" />
                  ) : (
                    <Circle className="w-5 h-5 text-slate-300 hover:text-slate-400" />
                  )}
                </button>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">
                      Module {mod.id}: {mod.title}
                    </span>
                    {mod.completed && (
                      <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-1.5 py-0.2 rounded">
                        Done
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-0.5">
                    <span className="flex items-center gap-1 capitalize">
                      {getModuleTypeIcon(mod.type)}
                      {mod.type} lesson
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      {mod.duration}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-blue-700 hover:text-blue-900 hidden sm:inline">
                  {mod.completed ? 'Review Lesson' : 'Start Lesson'}
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Banner: Complete Quiz CTA */}
        <div className="p-6 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <ClipboardCheck className="w-5 h-5 text-purple-600" />
              <h4 className="text-sm font-bold text-slate-900">Ready for Competency Validation?</h4>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Take the interactive MCQ assessment to evaluate statistical problem solving.
            </p>
          </div>

          <button
            onClick={onGoToQuiz}
            className="px-6 py-2.5 text-xs font-extrabold text-white bg-purple-700 hover:bg-purple-800 rounded-lg shadow-sm flex items-center gap-2 transition-all transform hover:scale-[1.02]"
          >
            <Award className="w-4 h-4" />
            <span>Complete Assessment Quiz</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
