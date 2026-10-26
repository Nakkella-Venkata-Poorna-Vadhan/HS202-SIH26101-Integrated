import React from 'react';
import {
  LayoutDashboard,
  BookOpen,
  Award,
  TrendingDown,
  ClipboardCheck,
  CalendarCheck,
  History,
  UserCheck,
  BarChart2,
  Users,
  BrainCircuit,
  RotateCcw,
  Sparkles,
  ChevronRight,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { PageRoute } from '../../types';

interface SidebarProps {
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onCloseMobile }) => {
  const { currentRoute, navigateTo, userRole, adminTab, resetDemoData, overallCompetency, weeklyHours } = useApp();

  const handleNav = (route: PageRoute) => {
    navigateTo(route);
    onCloseMobile();
  };

  const employeeNavItems: {
    route: PageRoute;
    label: string;
    icon: React.ElementType;
    badge?: string;
    badgeColor?: string;
  }[] = [
    { route: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { route: 'weekly-progress', label: 'Weekly Progress', icon: CalendarCheck, badge: 'Core Demo', badgeColor: 'bg-blue-100 text-blue-800' },
    { route: 'competency-assessment', label: 'Competency', icon: Award },
    { route: 'skill-gap', label: 'Skill Gap Analysis', icon: TrendingDown },
    { route: 'recommendations', label: 'AI Recommendations', icon: Sparkles, badge: 'AI', badgeColor: 'bg-purple-100 text-purple-800' },
    { route: 'course-details', label: 'My Learning & Courses', icon: BookOpen },
    { route: 'quiz', label: 'Assessments / Quiz', icon: ClipboardCheck },
    { route: 'history', label: 'Learning History', icon: History },
    { route: 'profile', label: 'Officer Profile', icon: UserCheck },
  ];

  const adminNavItems: {
    tab: 'analytics' | 'trainer-studio';
    label: string;
    icon: React.ElementType;
  }[] = [
    { tab: 'analytics', label: 'Organization Analytics', icon: BarChart2 },
    { tab: 'analytics', label: 'Employee Progress', icon: Users },
    { tab: 'trainer-studio', label: 'Trainer Studio (MCQ Generator)', icon: BrainCircuit },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs md:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform duration-300 ease-in-out md:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        } md:static md:z-20`}
      >
        {/* Brand in Sidebar (for mobile or collapse) */}
        <div className="h-16 px-5 border-b border-slate-200 flex items-center justify-between md:hidden">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-900 flex items-center justify-center text-white font-bold text-sm">
              S<span className="text-amber-400">AI</span>
            </div>
            <span className="font-bold text-base text-slate-900">StatSkill AI</span>
          </div>
          <button
            onClick={onCloseMobile}
            className="p-1 rounded-md text-slate-500 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>

        {/* Scrollable Navigation Area */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {/* Employee Section */}
          <div>
            <div className="px-3 mb-2 flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Officer Portal
              </span>
              <span className="text-[10px] font-medium bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded border border-emerald-200">
                Active
              </span>
            </div>
            <nav className="space-y-1">
              {employeeNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentRoute === item.route;
                return (
                  <button
                    key={item.route}
                    onClick={() => handleNav(item.route)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-blue-900 text-white shadow-sm font-semibold'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${
                          isActive ? 'bg-blue-800 text-amber-300' : item.badgeColor
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Admin Section */}
          <div>
            <div className="px-3 mb-2 flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Admin Management
              </span>
              <span className="text-[10px] font-medium bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                Prototype
              </span>
            </div>
            <nav className="space-y-1">
              {adminNavItems.map((item, idx) => {
                const Icon = item.icon;
                const isActive = currentRoute === 'admin' && adminTab === item.tab;
                return (
                  <button
                    key={`${item.tab}-${idx}`}
                    onClick={() => {
                      navigateTo('admin', undefined, { tab: item.tab });
                      onCloseMobile();
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-blue-900 text-white shadow-sm font-semibold'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
                      <span>{item.label}</span>
                    </div>
                    <ChevronRight className={`w-3 h-3 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Live Mini Progress Tracker Widget in Sidebar */}
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold text-slate-700">Weekly Target</span>
              <span className="text-xs font-bold text-blue-900">{weeklyHours} / 8.0h</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden mb-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, (weeklyHours / 8.0) * 100)}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-500">
              <span>Overall Competency:</span>
              <span className="font-bold text-emerald-700">{overallCompetency}%</span>
            </div>
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="p-3 border-t border-slate-200 space-y-2 bg-slate-50/50">
          <button
            onClick={resetDemoData}
            className="w-full py-2 px-3 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-slate-900 flex items-center justify-center gap-2 transition-colors shadow-2xs"
            title="Reset to default mock values"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
            Reset Prototype State
          </button>

          <div className="text-[10px] text-slate-600 text-center font-medium py-1">
            Smart India Hackathon 2026 • MoSPI
          </div>
        </div>
      </aside>
    </>
  );
};
