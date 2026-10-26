import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { BackendCompetency } from '../../types';
import {
  Award,
  Database,
  ShieldCheck,
  Users2,
  Play,
  ArrowRight,
  TrendingDown,
  Sparkles,
  Search,
  BookOpen,
  CheckCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface CompetencyCategoriesProps {
  onStartAssessment: (categoryName: string, skillName?: string) => void;
  onViewSkillGaps: () => void;
}

export const CompetencyCategories: React.FC<CompetencyCategoriesProps> = ({
  onStartAssessment,
  onViewSkillGaps,
}) => {
  const { allCompetencies, skillGapReport, userProfile, navigateTo } = useApp();
  const [activeTab, setActiveTab] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Filter competencies by tab and search
  const filtered = allCompetencies.filter((comp) => {
    const matchesTab =
      activeTab === 'All' ||
      (activeTab === 'Functional' && comp.competency_type === 'functional') ||
      (activeTab === 'Behavioural' && comp.competency_type === 'behavioural');

    const matchesSearch =
      !searchTerm ||
      comp.competency_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      comp.competency_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      comp.description.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesTab && matchesSearch;
  });

  const functionalCount = allCompetencies.filter((c) => c.competency_type === 'functional').length;
  const behaviouralCount = allCompetencies.filter((c) => c.competency_type === 'behavioural').length;

  // Check if a competency is in the active learner's gap report
  const getRoleRequirement = (competencyId: string) => {
    return skillGapReport?.gaps.find((g) => g.competency_id === competencyId);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Explanation Card */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="max-w-2xl">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
              Karmayogi Competency Model (KCM)
            </span>
            <span className="text-xs text-slate-500">• Official Source: SRC-CBC-KCM-2024</span>
            <span className="text-[10px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded-full">
              {allCompetencies.length} Official Competencies
            </span>
          </div>

          <h2 className="text-xl font-bold text-slate-900">
            KCM Official Competency Dictionary
          </h2>
          <p className="text-xs text-slate-600 mt-1 leading-relaxed">
            Curated civil service and statistical competencies extracted from the Capacity Building Commission
            Karmayogi Competency Model. Sub-themes and behavioural indicators define proficiency across cadres.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onViewSkillGaps}
            className="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <TrendingDown className="w-4 h-4 text-slate-500" />
            <span>View Active Gaps</span>
          </button>

          <button
            onClick={() => onStartAssessment('Functional', 'Data Analytics')}
            className="px-5 py-2.5 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-sm transition-all flex items-center gap-2"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Launch Sandbox Quiz</span>
          </button>
        </div>
      </div>

      {/* Search & Tabs Strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
        {/* Tabs */}
        <div className="flex items-center space-x-2 overflow-x-auto">
          {[
            { id: 'All', label: `All Competencies (${allCompetencies.length})` },
            { id: 'Functional', label: `Functional (${functionalCount})` },
            { id: 'Behavioural', label: `Behavioural (${behaviouralCount})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-900 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search KCM ID, title, keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
          />
        </div>
      </div>

      {/* Competencies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((comp) => {
          const req = getRoleRequirement(comp.competency_id);
          const isExpanded = expandedId === comp.competency_id;

          return (
            <div
              key={comp.competency_id}
              className={`bg-white rounded-xl border transition-all p-5 flex flex-col justify-between ${
                req
                  ? 'border-blue-300 shadow-sm bg-blue-50/10'
                  : 'border-slate-200/90 shadow-2xs hover:border-slate-300'
              }`}
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-extrabold text-blue-900 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
                      {comp.competency_id}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                      {comp.competency_type}
                    </span>
                  </div>

                  {req && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-900 border border-blue-200">
                      Required for {userProfile.name}
                    </span>
                  )}
                </div>

                <h3 className="text-base font-bold text-slate-900 mb-1 leading-snug">
                  {comp.competency_name}
                </h3>

                <p className="text-xs text-slate-600 leading-relaxed mb-3 line-clamp-3">
                  {comp.description}
                </p>

                {/* Role Requirement Callout if required */}
                {req && (
                  <div className="p-2.5 rounded-lg bg-blue-50/70 border border-blue-200 mb-3 text-xs">
                    <div className="flex items-center justify-between text-[11px] font-bold text-blue-950 mb-1">
                      <span>Target Role Requirement: Level {req.required_level} / 5</span>
                      <span>
                        Status:{' '}
                        {req.status === 'unassessed'
                          ? 'Unassessed'
                          : req.gap && req.gap > 0
                          ? `${req.gap} Level Gap`
                          : 'Competent'}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 leading-snug">{req.explanation}</p>
                  </div>
                )}

                {/* Sub-themes / Behaviours toggle */}
                {comp.behaviours && comp.behaviours.length > 0 && (
                  <div>
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : comp.competency_id)}
                      className="text-[11px] font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1 mb-2"
                    >
                      <span>
                        {isExpanded ? 'Hide' : 'Show'} {comp.behaviours.length} Sub-themes / Indicators
                      </span>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {isExpanded && (
                      <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80 mb-3 space-y-1.5 text-xs">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                          Official Sub-themes (SRC-CBC-KCM-2024):
                        </span>
                        {comp.behaviours.map((b, idx) => (
                          <div key={idx} className="flex items-start gap-1.5 text-slate-700 text-[11px]">
                            <span className="text-blue-600 font-bold shrink-0">•</span>
                            <span>{b}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Source Page Citation Footer */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-600 font-medium">
                <span>
                  Source: KCM-2024 (Pages: {comp.source_page.join(', ')})
                </span>
                <span className="capitalize text-slate-600">
                  Status: {comp.validation_status.replace(/_/g, ' ')}
                </span>
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="col-span-2 text-center py-12 bg-white rounded-xl border border-slate-200 text-xs text-slate-500">
            No official competencies matched &ldquo;{searchTerm}&rdquo;.
          </div>
        )}
      </div>
    </div>
  );
};
