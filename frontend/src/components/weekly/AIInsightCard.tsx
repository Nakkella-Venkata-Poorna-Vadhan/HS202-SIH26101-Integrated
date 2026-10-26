import React from 'react';
import { Sparkles, ArrowRight, TrendingUp, AlertCircle, Lightbulb, ShieldCheck } from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface AIInsightCardProps {
  onViewRecommendations: () => void;
}

export const AIInsightCard: React.FC<AIInsightCardProps> = ({ onViewRecommendations }) => {
  const { userProfile, skillGapReport, courses } = useApp();

  const highestGap = skillGapReport?.gaps.find(
    (g) => g.status === 'gap_identified' && (g.priority === 'critical' || g.priority === 'high')
  ) || skillGapReport?.gaps.find((g) => g.status === 'gap_identified');

  const topCourse = courses[0];

  return (
    <div className="bg-linear-to-br from-blue-900 via-indigo-900 to-slate-900 rounded-xl p-6 text-white shadow-md relative overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute top-0 right-0 -mt-8 -mr-8 w-48 h-48 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-amber-400 text-slate-950 font-bold">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-wider text-amber-300 font-bold block">
                Competency Intelligence Engine
              </span>
              <h3 className="text-base font-bold text-white">Diagnostic Insights: {userProfile.name}</h3>
            </div>
          </div>

          <span className="text-xs bg-white/10 text-blue-200 px-2.5 py-0.5 rounded-full border border-white/10 font-medium">
            Active Evaluation
          </span>
        </div>

        <div className="bg-white/10 backdrop-blur-xs rounded-lg p-4 border border-white/15 my-4">
          {highestGap ? (
            <p className="text-sm text-slate-100 leading-relaxed font-normal">
              &ldquo;Based on official KCM evaluation for <strong className="text-white font-semibold">{userProfile.designation}</strong>,{' '}
              <strong className="text-amber-300 font-semibold">{highestGap.competency_name} ({highestGap.competency_id})</strong> is identified as the highest-priority competency deficit ({highestGap.gap} level gap).{' '}
              {topCourse && (
                <>
                  Deterministic ranking prioritizes <strong className="text-white font-semibold">{topCourse.title}</strong> from the MoSPI ACBP 2026-27 schedule to address this operational requirement.
                </>
              )}
              &rdquo;
            </p>
          ) : skillGapReport?.unassessed_count ? (
            <p className="text-sm text-slate-100 leading-relaxed font-normal">
              &ldquo;<strong className="text-amber-300 font-semibold">{skillGapReport.unassessed_count} required competencies</strong> for {userProfile.name} are currently unassessed. Fresh recruitment or missing in-service records require diagnostic assessment without fabricating estimated scores.&rdquo;
            </p>
          ) : (
            <p className="text-sm text-slate-100 leading-relaxed font-normal">
              &ldquo;All required role competencies for <strong className="text-white font-semibold">{userProfile.name}</strong> meet or exceed the prototype cadre benchmark. Continuous learning in advanced statistical modeling is recommended.&rdquo;
            </p>
          )}

          <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap items-center gap-4 text-xs text-slate-300">
            {highestGap && (
              <div className="flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                <span>
                  {highestGap.competency_name}: Level {highestGap.estimated_level ?? 'None'} / Req: Level {highestGap.required_level}
                </span>
              </div>
            )}
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>
                {skillGapReport?.competent_count ?? 0} of {skillGapReport?.total_required_competencies ?? 4} Competencies Met
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-300">
            <Lightbulb className="w-3.5 h-3.5 text-amber-300" />
            <span>Curriculum dynamically mapped from official ACBP schedule</span>
          </div>

          <button
            onClick={onViewRecommendations}
            className="px-4 py-2 text-xs font-bold text-slate-900 bg-amber-400 hover:bg-amber-300 rounded-lg transition-colors shadow flex items-center gap-2"
          >
            <span>View Recommended ACBP Courses</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
