import React from 'react';
import { AdminOverview } from '../components/admin/AdminOverview';
import { AdminEmployeeTable } from '../components/admin/AdminEmployeeTable';
import { TrainerStudio } from '../components/admin/TrainerStudio';
import { Shield, ArrowLeft, BarChart3, Sparkles } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const AdminDashboardPage: React.FC = () => {
  const { loginAs, userProfile, resetDemoState, adminTab, setAdminTab } = useApp();
  const activeTab = adminTab;

  return (
    <div className="space-y-6">
      {/* Top Admin Header */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider bg-slate-900 text-amber-300 px-2.5 py-0.5 rounded">
              Cadre Administration
            </span>
            <span className="text-xs text-slate-500">• MoSPI Statistical HQ Oversight</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Administrator & Trainer Hub
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
            Macro-level organizational analytics, competency gap monitoring, learning material ingestion, and AI question generation.
          </p>
        </div>

        <button
          onClick={() => loginAs('employee')}
          className="px-4 py-2.5 text-xs font-bold text-blue-900 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors flex items-center gap-1.5 shadow-2xs"
        >
          <ArrowLeft className="w-4 h-4 text-blue-700" />
          <span>Switch Back to Officer View ({userProfile.name.split(' ')[0]})</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 bg-slate-200/70 p-1.5 rounded-xl border border-slate-300/80 w-fit">
        <button
          onClick={() => setAdminTab('trainer-studio')}
          className={`px-4 py-2 text-xs font-extrabold rounded-lg transition-all flex items-center gap-2 ${
            activeTab === 'trainer-studio'
              ? 'bg-white text-indigo-950 shadow-sm'
              : 'text-slate-700 hover:text-slate-900'
          }`}
        >
          <Sparkles className="w-4 h-4 text-amber-500" />
          <span>Trainer Studio (Material Upload & MCQ Generator)</span>
        </button>

        <button
          onClick={() => setAdminTab('analytics')}
          className={`px-4 py-2 text-xs font-extrabold rounded-lg transition-all flex items-center gap-2 ${
            activeTab === 'analytics'
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-700 hover:text-slate-900'
          }`}
        >
          <BarChart3 className="w-4 h-4 text-blue-600" />
          <span>Cadre Analytics & Skill Gaps</span>
        </button>
      </div>

      {/* Demonstration Controls & Environment Management */}
      <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-extrabold uppercase tracking-wider text-amber-900 bg-amber-200/80 px-2.5 py-0.5 rounded">
              SIH Evaluator Demonstration Controls
            </span>
            <span className="text-xs text-amber-800 font-semibold">• Local Demo State Management</span>
          </div>
          <p className="text-xs text-amber-900 leading-relaxed max-w-2xl">
            Reset diagnostic quiz attempts and provisional estimates for synthetic learners back to clean baseline (Pooja Verma unassessed). Official KCM catalogue, ACBP courses, and mapping registries remain strictly unaltered.
          </p>
        </div>

        <button
          onClick={async () => {
            if (window.confirm('Reset all demo attempts and provisional estimates to clean initial baseline? Official source datasets will not be affected.')) {
              await resetDemoState();
              alert('Demonstration state successfully reset! Pooja Verma (LEARNER-003) is now in a clean unassessed state.');
            }
          }}
          className="px-4 py-2 text-xs font-extrabold text-amber-950 bg-amber-300 hover:bg-amber-400 border border-amber-400 rounded-lg shadow-2xs transition-all flex items-center gap-1.5"
        >
          <span>↺ Reset Demonstration State</span>
        </button>
      </div>

      {/* Active Tab Content */}
      {activeTab === 'trainer-studio' ? (
        <TrainerStudio />
      ) : (
        <>
          {/* Admin KPIs and 4 Charts */}
          <AdminOverview />

          {/* Cadre Employee Table with 4 filter criteria */}
          <AdminEmployeeTable />
        </>
      )}
    </div>
  );
};
