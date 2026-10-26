import React, { useState } from 'react';
import {
  ChevronRight,
  Sparkles,
  CheckCircle2,
  PlayCircle,
  HelpCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { PageRoute } from '../../types';

export const DemoFlowBanner: React.FC = () => {
  const { currentRoute, navigateTo, quizSubmission } = useApp();
  const [collapsed, setCollapsed] = useState(false);

  const demoSteps: {
    id: number;
    title: string;
    route: PageRoute;
    hint: string;
  }[] = [
    { id: 1, title: 'Dashboard', route: 'dashboard', hint: 'Overview KPI cards, skills, 6.5h learning' },
    { id: 2, title: 'Weekly Progress', route: 'weekly-progress', hint: 'Daily hours chart & activity timeline' },
    { id: 3, title: 'Competency Gap', route: 'skill-gap', hint: 'Radar chart: Current vs Required' },
    { id: 4, title: 'AI Recommendations', route: 'recommendations', hint: 'AI Roadmap: Step 1 → Step 4' },
    { id: 5, title: 'Course Details', route: 'course-details', hint: 'Python course curriculum & modules' },
    { id: 6, title: 'Assessment Quiz', route: 'quiz', hint: 'Interactive MCQ with live scoring' },
  ];

  // Helper to determine active step
  const getActiveStepIndex = () => {
    switch (currentRoute) {
      case 'dashboard':
        return 0;
      case 'weekly-progress':
        return 1;
      case 'competency-assessment':
      case 'skill-gap':
        return 2;
      case 'recommendations':
        return 3;
      case 'course-details':
        return 4;
      case 'quiz':
        return 5;
      default:
        return 0;
    }
  };

  const activeIndex = getActiveStepIndex();

  const handleNextStep = () => {
    const nextIdx = (activeIndex + 1) % demoSteps.length;
    navigateTo(demoSteps[nextIdx].route);
  };

  return (
    <div className="bg-slate-900 border-b border-slate-800 text-white transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2.5">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-400"></span>
            </span>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-300">
                SIH Hackathon Demonstration Walkthrough:
              </span>
              <span className="text-xs text-slate-300 hidden md:inline">
                Follow the recommended end-to-end competency loop
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleNextStep}
              className="text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded-md flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <span>Next Step: {demoSteps[(activeIndex + 1) % demoSteps.length].title}</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-1 rounded text-slate-400 hover:text-white"
              title="Toggle flow bar"
            >
              {collapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Stepper bar */}
        {!collapsed && (
          <div className="mt-2.5 pt-2 border-t border-slate-800 flex items-center overflow-x-auto pb-1 gap-1 sm:gap-2">
            {demoSteps.map((step, idx) => {
              const isActive = activeIndex === idx;
              const isPast = activeIndex > idx || (step.id === 6 && quizSubmission?.completed);

              return (
                <button
                  key={step.id}
                  onClick={() => navigateTo(step.route)}
                  className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs whitespace-nowrap transition-all ${
                    isActive
                      ? 'bg-blue-700 text-white font-bold ring-1 ring-blue-400'
                      : isPast
                      ? 'bg-slate-800 text-emerald-300 hover:bg-slate-700'
                      : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                  }`}
                  title={step.hint}
                >
                  <span
                    className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      isActive
                        ? 'bg-white text-blue-900'
                        : isPast
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {isPast ? '✓' : step.id}
                  </span>
                  <span>{step.title}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
