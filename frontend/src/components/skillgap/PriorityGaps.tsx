import React from 'react';
import { AlertTriangle, Sparkles, ArrowRight, ShieldAlert, CheckCircle2, HelpCircle } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { BackendSkillGap } from '../../types';

interface PriorityGapsProps {
  onGeneratePath: () => void;
  onSelectGapCourse: (competencyId: string, competencyName: string) => void;
}

export const PriorityGaps: React.FC<PriorityGapsProps> = ({
  onGeneratePath,
  onSelectGapCourse
}) => {
  const { skillGapReport, courses, startDiagnosticAssessment, navigateTo } = useApp();

  const gaps = skillGapReport?.gaps || [];

  const highPriorityGaps = gaps.filter(
    (g) => g.status === 'gap_identified' && (g.priority === 'critical' || g.priority === 'high')
  );

  const mediumLowGaps = gaps.filter(
    (g) => g.status === 'gap_identified' && g.priority !== 'critical' && g.priority !== 'high'
  );

  const unassessedGaps = gaps.filter((g) => g.status === 'unassessed');

  const competentList = gaps.filter((g) => g.status === 'competent');

  const findMatchingCourse = (competencyId: string) => {
    return courses.find((c) => c.targetCompetencyId === competencyId);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-600" />
            <h3 className="text-base font-bold text-slate-900">Priority Competency Deficits</h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Role requirement deficits computed deterministically: <code className="font-mono text-slate-700">gap = max(0, Required - Estimated)</code>
          </p>
        </div>

        <button
          onClick={onGeneratePath}
          className="px-4 py-2 text-xs font-bold text-slate-950 bg-amber-400 hover:bg-amber-300 rounded-lg shadow-sm transition-all flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4 fill-slate-950" />
          <span>View Recommended Courses</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Critical & High Priority Section */}
      {highPriorityGaps.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
            <h4 className="text-xs font-bold uppercase tracking-wider text-rose-700">
              Critical & High Priority Gaps ({highPriorityGaps.length})
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {highPriorityGaps.map((item) => {
              const matched = findMatchingCourse(item.competency_id);
              return (
                <div
                  key={item.competency_id}
                  className="border border-rose-200 bg-rose-50/40 rounded-xl p-4 flex flex-col justify-between hover:bg-rose-50/80 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-bold text-slate-900">
                        {item.competency_name}
                      </span>
                      <span className="text-xs font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded-full border border-rose-200">
                        Gap: {item.gap} Level{item.gap && item.gap > 1 ? 's' : ''} ({item.priority.toUpperCase()})
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs text-slate-700 mb-2 font-medium">
                      <div>
                        <span className="text-slate-500 block text-[11px]">Current Estimated Level:</span>
                        <span className="font-bold text-slate-900">
                          Level {item.estimated_level} / 5
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[11px]">Required Benchmark:</span>
                        <span className="font-bold text-blue-900">
                          Level {item.required_level} / 5
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-rose-100 mb-3 leading-relaxed">
                      <strong className="text-slate-900">Audit Diagnosis: </strong>
                      {item.explanation}
                    </p>

                    {item.evidence_sources.length > 0 && (
                      <div className="text-[10px] text-slate-500 mb-3">
                        <span className="font-semibold text-slate-700">Assessment Evidence: </span>
                        {item.evidence_sources.join(', ')}
                      </div>
                    )}
                  </div>

                  <div className="pt-3 border-t border-rose-200/60 flex items-center justify-between gap-2">
                    <span className="text-[11px] font-mono text-slate-500">
                      ID: {item.competency_id}
                    </span>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          startDiagnosticAssessment(item.competency_id);
                          navigateTo('quiz');
                        }}
                        className="text-xs font-bold text-blue-900 bg-blue-100 hover:bg-blue-200 px-2.5 py-1 rounded-md flex items-center gap-1 transition-colors"
                      >
                        <Sparkles className="w-3 h-3 text-blue-700" />
                        <span>Re-assess</span>
                      </button>

                      <button
                        onClick={() => onSelectGapCourse(item.competency_id, item.competency_name)}
                        className="text-xs font-bold text-blue-700 hover:text-blue-900 flex items-center gap-1 hover:underline"
                      >
                        <span>
                          {matched ? `View Course: ${matched.id}` : 'Inspect ACBP Curriculum'}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Medium & Low Priority Section */}
      {mediumLowGaps.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-700">
              Medium / Developing Gaps ({mediumLowGaps.length})
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {mediumLowGaps.map((item) => {
              const matched = findMatchingCourse(item.competency_id);
              return (
                <div
                  key={item.competency_id}
                  className="border border-amber-200 bg-amber-50/30 rounded-xl p-4 flex flex-col justify-between hover:bg-amber-50/60 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-bold text-slate-900">
                        {item.competency_name}
                      </span>
                      <span className="text-xs font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full border border-amber-200">
                        Gap: {item.gap} Level ({item.priority.toUpperCase()})
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs text-slate-700 mb-2 font-medium">
                      <div>
                        <span className="text-slate-500 block text-[11px]">Current Estimated Level:</span>
                        <span className="font-bold text-slate-900">Level {item.estimated_level} / 5</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[11px]">Required Level:</span>
                        <span className="font-bold text-blue-900">Level {item.required_level} / 5</span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-amber-100 mb-3 leading-relaxed">
                      {item.explanation}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-amber-200/60 flex items-center justify-between gap-2">
                    <span className="text-[11px] font-mono text-slate-500">
                      ID: {item.competency_id}
                    </span>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          startDiagnosticAssessment(item.competency_id);
                          navigateTo('quiz');
                        }}
                        className="text-xs font-bold text-blue-900 bg-blue-100 hover:bg-blue-200 px-2.5 py-1 rounded-md flex items-center gap-1 transition-colors"
                      >
                        <Sparkles className="w-3 h-3 text-blue-700" />
                        <span>Re-assess</span>
                      </button>

                      <button
                        onClick={() => onSelectGapCourse(item.competency_id, item.competency_name)}
                        className="text-xs font-bold text-blue-700 hover:text-blue-900 flex items-center gap-1 hover:underline"
                      >
                        <span>{matched ? `View Course: ${matched.id}` : 'Inspect ACBP Curriculum'}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Unassessed Competencies Section */}
      {unassessedGaps.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Unassessed Role Competencies ({unassessedGaps.length}) — No Fabricated Scores
            </h4>
          </div>

          <div className="border border-slate-200 bg-slate-50 rounded-xl p-4 divide-y divide-slate-200/70">
            {unassessedGaps.map((item) => (
              <div key={item.competency_id} className="py-2.5 first:pt-0 last:pb-0 flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <HelpCircle className="w-4 h-4 text-slate-400" />
                    <span className="text-xs font-bold text-slate-800">{item.competency_name}</span>
                    <span className="text-[10px] font-mono text-slate-500">({item.competency_id})</span>
                    <span className="text-[10px] font-semibold bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded">
                      Required: Level {item.required_level}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5 ml-6">
                    {item.explanation}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-semibold text-slate-500 bg-white border border-slate-200 px-2 py-0.5 rounded">
                    Status: Unassessed
                  </span>
                  <button
                    onClick={() => {
                      startDiagnosticAssessment(item.competency_id);
                      navigateTo('quiz');
                    }}
                    className="text-xs font-bold text-blue-900 bg-blue-100 hover:bg-blue-200 px-2.5 py-1 rounded-md flex items-center gap-1 transition-colors shadow-2xs"
                  >
                    <span>Assess Competency</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Competent Section */}
      {competentList.length > 0 && (
        <div className="pt-2">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              Satisfied Role Competencies ({competentList.length})
            </h4>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            {competentList.map((c) => (
              <div
                key={c.competency_id}
                className="p-2.5 bg-emerald-50/60 border border-emerald-200 rounded-lg flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-slate-800">{c.competency_name}</span>
                  <span className="text-[10px] text-slate-500 block">
                    Level {c.estimated_level} meets required Level {c.required_level}
                  </span>
                </div>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                  ✓ Competent
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
