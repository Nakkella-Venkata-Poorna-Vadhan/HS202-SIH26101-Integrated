import React, { useState } from 'react';
import { Course } from '../../types';
import {
  Clock,
  BookOpen,
  Sparkles,
  ArrowRight,
  User,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Tag,
  Building2,
  Layers,
  CheckCheck,
  BookmarkCheck,
  Send
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface CourseCardProps {
  course: Course;
  onOpen: (courseId: string) => void;
}

export const CourseCard: React.FC<CourseCardProps> = ({ course, onOpen }) => {
  const { recordLearningActivity } = useApp();
  const [isRecording, setIsRecording] = useState(false);
  const [recordedStatus, setRecordedStatus] = useState<string | null>(null);
  const [activityNote, setActivityNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [recordError, setRecordError] = useState<string | null>(null);

  const getMappingBadge = (status?: Course['mappingStatus']) => {
    switch (status) {
      case 'validated':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 flex items-center gap-1 shadow-2xs">
            <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
            Validated Mapping
          </span>
        );
      case 'candidate':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-900 border border-amber-300 flex items-center gap-1 shadow-2xs">
            <AlertTriangle className="w-2.5 h-2.5 text-amber-600" />
            Candidate Mapping
          </span>
        );
      case 'unresolved':
      default:
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-300 flex items-center gap-1">
            <HelpCircle className="w-2.5 h-2.5 text-slate-500" />
            Unresolved Mapping
          </span>
        );
    }
  };

  const handleRecordActivity = async (activityType: 'enrolled' | 'in_progress' | 'completed') => {
    setSubmitting(true);
    setRecordError(null);
    try {
      const ok = await recordLearningActivity(
        course.id,
        course.title,
        activityType,
        course.targetCompetencyId,
        activityNote || `Logged as ${activityType} from recommendation card.`
      );
      if (ok) {
        setRecordedStatus(activityType);
        setIsRecording(false);
        setActivityNote('');
      } else {
        setRecordError('Could not record this learning action. Confirm the backend is running, then retry.');
      }
    } catch (err) {
      console.error('Failed to record learning activity:', err);
      setRecordError('Could not record this learning action. Confirm the backend is running, then retry.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm hover:shadow-md hover:border-blue-300 transition-all p-5 flex flex-col justify-between">
      <div>
        {/* Top Badges */}
        <div className="flex flex-wrap items-center justify-between gap-1.5 mb-2.5">
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-800 border border-blue-200 px-2 py-0.5 rounded">
              {course.id}
            </span>
            <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded">
              {course.resourceType || 'Course'}
            </span>
            <span className="text-[10px] font-semibold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
              {course.skillCategory}
            </span>
          </div>

          <div className="flex items-center gap-1">
            {getMappingBadge(course.mappingStatus)}
            {course.priority && (
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  course.priority === 'Critical' || course.priority === 'High'
                    ? 'bg-rose-50 text-rose-700 border-rose-200'
                    : 'bg-amber-50 text-amber-700 border-amber-200'
                }`}
              >
                {course.priority}
              </span>
            )}
          </div>
        </div>

        <h3 className="text-base font-bold text-slate-900 mb-1 leading-snug line-clamp-2">
          {course.title}
        </h3>

        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500 mb-2.5">
          <span className="flex items-center gap-1 truncate">
            <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>{course.providerSource || 'MoSPI ACBP (Local)'}</span>
          </span>
          <span className="flex items-center gap-1 truncate">
            <User className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>{course.instructor || 'Official Faculty'}</span>
          </span>
        </div>

        {course.targetCompetencyName && (
          <div className="flex items-center gap-1.5 text-xs text-blue-900 bg-blue-50/80 border border-blue-200 rounded-md px-2.5 py-1 mb-2.5">
            <Tag className="w-3 h-3 text-blue-700 shrink-0" />
            <span className="font-semibold truncate">
              Target Competency: {course.targetCompetencyName} ({course.targetCompetencyId})
            </span>
          </div>
        )}

        {/* Difficulty Fit & Duration */}
        <div className="flex flex-wrap items-center gap-1.5 mb-3 text-xs">
          {course.difficultyFit && (
            <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-medium px-2 py-0.5 rounded flex items-center gap-1">
              <Layers className="w-3 h-3 text-emerald-600" />
              {course.difficultyFit}
            </span>
          )}
          <span className="flex items-center gap-1 text-[11px] text-slate-600 bg-slate-50 px-2 py-0.5 rounded border border-slate-200 font-medium">
            <Clock className="w-3 h-3 text-slate-400" />
            {course.duration}
          </span>
        </div>

        {/* Explainable Recommendation Reason */}
        {course.recommendationReason && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 mb-3">
            <div className="flex items-start gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-700 shrink-0 mt-0.5" />
              <p className="text-[11px] text-slate-700 leading-snug">
                <span className="font-bold text-slate-900">Explainable Rationale: </span>
                {course.recommendationReason}
              </p>
            </div>
          </div>
        )}

        {/* Limitations & Provenance Disclosure */}
        {course.limitationsOrUncertainties && (
          <div className="bg-amber-50/60 border border-amber-200/80 rounded-lg p-2 mb-3">
            <div className="flex items-start gap-1.5">
              <AlertTriangle className="w-3 h-3 text-amber-700 shrink-0 mt-0.5" />
              <p className="text-[10.5px] text-amber-900 leading-tight">
                <span className="font-bold">Provenance & Constraint Notice: </span>
                {course.limitationsOrUncertainties}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer / Learning Action Recording */}
      <div className="pt-3 border-t border-slate-100 space-y-2">
        {recordedStatus ? (
          <div className="p-2 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center justify-between text-xs text-emerald-800">
            <span className="flex items-center gap-1.5 font-semibold">
              <BookmarkCheck className="w-4 h-4 text-emerald-600" />
              Activity Recorded: {recordedStatus.toUpperCase()}
            </span>
            <span className="text-[10px] text-emerald-600 font-normal">(Local User Log)</span>
          </div>
        ) : isRecording ? (
          <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
            <div className="text-[11px] font-bold text-slate-800">Record Action (No Automated Sync):</div>
            <input
              type="text"
              placeholder="Optional notes (e.g. nomination order, offline module)"
              value={activityNote}
              onChange={(e) => setActivityNote(e.target.value)}
              className="w-full text-xs p-1.5 border border-slate-300 rounded bg-white text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            {recordError && (
              <p className="text-[11px] text-rose-700 bg-rose-50 border border-rose-200 rounded px-2 py-1">
                {recordError}
              </p>
            )}
            <div className="flex items-center gap-1.5">
              <button
                disabled={submitting}
                onClick={() => handleRecordActivity('enrolled')}
                className="flex-1 py-1 px-2 text-[11px] font-semibold bg-blue-800 hover:bg-blue-900 text-white rounded transition-colors"
              >
                Mark Enrolled
              </button>
              <button
                disabled={submitting}
                onClick={() => handleRecordActivity('completed')}
                className="flex-1 py-1 px-2 text-[11px] font-semibold bg-emerald-700 hover:bg-emerald-800 text-white rounded transition-colors"
              >
                Mark Completed
              </button>
              <button
                onClick={() => setIsRecording(false)}
                className="py-1 px-2 text-[11px] text-slate-600 hover:bg-slate-200 rounded transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={() => onOpen(course.id)}
              className="flex-1 py-2 px-3 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg flex items-center justify-center gap-1.5 transition-colors shadow-2xs"
            >
              <span>Inspect Course Details</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setIsRecording(true)}
              title="Record deliberate learning action"
              className="py-2 px-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-lg flex items-center gap-1 transition-colors"
            >
              <BookmarkCheck className="w-3.5 h-3.5 text-slate-600" />
              <span>Log Action</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
