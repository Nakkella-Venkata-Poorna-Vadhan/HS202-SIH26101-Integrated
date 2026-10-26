import React from 'react';
import { CheckCircle2, Award, Zap, Trophy } from 'lucide-react';

interface WeeklyAchievementsProps {
  weeklyHours: number;
}

export const WeeklyAchievements: React.FC<WeeklyAchievementsProps> = ({ weeklyHours }) => {
  const achievements = [
    {
      id: 1,
      title: 'ACBP Course Catalog Linked',
      category: 'Curriculum Schedule',
      icon: CheckCircle2,
      color: 'text-emerald-600 bg-emerald-50 border-emerald-200'
    },
    {
      id: 2,
      title: 'KCM Competencies Evaluated',
      category: 'Competency Framework',
      icon: Trophy,
      color: 'text-blue-600 bg-blue-50 border-blue-200'
    },
    {
      id: 3,
      title: 'Deterministic Recommendations Active',
      category: 'Intelligence Engine',
      icon: Award,
      color: 'text-purple-600 bg-purple-50 border-purple-200'
    },
    {
      id: 4,
      title: `${weeklyHours} hours recorded in sandbox`,
      category: 'Demonstration Log',
      icon: Zap,
      color: 'text-amber-600 bg-amber-50 border-amber-200'
    },
  ];

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Demonstration Highlights</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational status and demonstration milestones (Sandbox Log)
          </p>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
          Integrated
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {achievements.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.id}
              className="flex items-center space-x-3 p-3 rounded-lg border border-slate-200/80 bg-slate-50/50 hover:bg-slate-50 transition-colors"
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center border shrink-0 ${item.color}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-wider block">
                  {item.category}
                </span>
                <p className="text-xs font-bold text-slate-800 truncate">
                  ✓ {item.title}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
