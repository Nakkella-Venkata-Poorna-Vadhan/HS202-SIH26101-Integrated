import React from 'react';
import { CompetencyScore } from '../../types';
import { ProgressBar } from '../common/ProgressBar';
import { ArrowRight, AlertTriangle, CheckCircle, TrendingUp, HelpCircle } from 'lucide-react';

interface SkillProgressListProps {
  skills: CompetencyScore[];
  onViewAll: () => void;
  onSelectSkill?: (skillName: string) => void;
}

export const SkillProgressList: React.FC<SkillProgressListProps> = ({
  skills,
  onViewAll,
  onSelectSkill
}) => {
  const getBadge = (level: CompetencyScore['level']) => {
    switch (level) {
      case 'strong':
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
            <CheckCircle className="w-2.5 h-2.5" />
            Strong
          </span>
        );
      case 'developing':
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            Developing
          </span>
        );
      case 'needs-improvement':
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1">
            <AlertTriangle className="w-2.5 h-2.5" />
            Needs Improvement
          </span>
        );
      case 'critical-gap':
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1">
            <AlertTriangle className="w-2.5 h-2.5 text-rose-600" />
            Critical Gap
          </span>
        );
      case 'unassessed':
      default:
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-300 flex items-center gap-1">
            <HelpCircle className="w-2.5 h-2.5 text-slate-500" />
            Unassessed
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Required Role Competencies</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Mission Karmayogi Prototype 5-Level Scale (Level 1 Foundation - Level 5 Expert)
          </p>
        </div>
        <button
          onClick={onViewAll}
          className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1 hover:underline"
        >
          Detailed Matrix
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 p-2.5 bg-slate-50 rounded-lg text-[11px] font-medium text-slate-600">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          <span>Strong / Competent</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
          <span>Developing</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
          <span>Needs Improvement</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span>
          <span>Unassessed</span>
        </div>
      </div>

      {/* Skill List */}
      <div className="space-y-4">
        {skills.map((skill) => (
          <div
            key={skill.name}
            onClick={() => onSelectSkill && onSelectSkill(skill.name)}
            className="group p-2 rounded-lg hover:bg-slate-50/80 transition-colors cursor-pointer"
          >
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-800 group-hover:text-blue-700 transition-colors">
                  {skill.name}
                </span>
                {skill.trend && (
                  <span className="text-[10px] text-slate-500 font-medium">
                    ({skill.trend})
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {getBadge(skill.level)}
                <span className="text-xs font-bold text-slate-900">
                  {skill.level === 'unassessed' ? 'Unassessed' : `${skill.current}%`}
                </span>
              </div>
            </div>

            <ProgressBar
              value={skill.level === 'unassessed' ? 0 : skill.current}
              target={skill.required}
              level={skill.level === 'unassessed' ? 'developing' : skill.level}
              height="sm"
            />

            <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1">
              <span>Category: {skill.category}</span>
              <span>
                Required: {skill.required}%
                {skill.level === 'unassessed' ? (
                  <span className="text-slate-600 font-semibold ml-1">(Assessment Pending)</span>
                ) : skill.gap > 0 ? (
                  <span className="text-rose-600 font-semibold ml-1">(-{skill.gap}% gap)</span>
                ) : (
                  <span className="text-emerald-600 font-semibold ml-1">(Met)</span>
                )}
              </span>
            </div>
          </div>
        ))}
        {skills.length === 0 && (
          <p className="text-xs text-slate-500 text-center py-4">
            No required competencies loaded for this role.
          </p>
        )}
      </div>
    </div>
  );
};
