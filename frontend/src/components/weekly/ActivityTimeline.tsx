import React from 'react';
import { ActivityTimelineItem } from '../../types';
import { CheckCircle2, Circle, Clock, Award, BookOpen, Sparkles } from 'lucide-react';

interface ActivityTimelineProps {
  timeline: ActivityTimelineItem[];
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ timeline }) => {
  const getIcon = (type: ActivityTimelineItem['type'], completed: boolean) => {
    if (!completed) {
      return <Circle className="w-4 h-4 text-slate-300" />;
    }
    switch (type) {
      case 'quiz':
        return <Award className="w-4 h-4 text-purple-600" />;
      case 'training':
        return <Sparkles className="w-4 h-4 text-amber-600" />;
      case 'module':
      default:
        return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Weekly Activity Timeline</h3>
          <p className="text-xs text-slate-500 mt-0.5">Chronological record of completed lessons and assessments</p>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200">
          7 Days Logged
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {timeline.map((item) => (
          <div key={item.id} className="relative group">
            {/* Timeline icon dot */}
            <div className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-white flex items-center justify-center">
              {getIcon(item.type, item.completed)}
            </div>

            <div className="bg-slate-50/70 group-hover:bg-slate-50 border border-slate-200/80 rounded-lg p-3 transition-colors">
              <div className="flex flex-wrap items-center justify-between gap-1 mb-1">
                <span className="text-xs font-bold text-blue-900">
                  {item.day} <span className="text-slate-500 font-normal">({item.date})</span>
                </span>
                {item.duration && (
                  <span className="text-[11px] font-medium text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    {item.duration}
                  </span>
                )}
              </div>

              <p className="text-xs font-semibold text-slate-800 flex items-center gap-1.5">
                {item.completed ? (
                  <span className="text-emerald-700">✓</span>
                ) : (
                  <span className="text-slate-400">○</span>
                )}
                <span>{item.title}</span>
              </p>

              {item.score && (
                <div className="mt-1.5 inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <Award className="w-3 h-3" />
                  Assessment Score: {item.score}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
