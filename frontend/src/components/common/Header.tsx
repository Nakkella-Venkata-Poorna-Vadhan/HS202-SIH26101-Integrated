import React, { useState, useRef, useEffect } from 'react';
import {
  Bell,
  CheckCircle2,
  ChevronDown,
  LogOut,
  Menu,
  Shield,
  User,
  Sparkles,
  BarChart3,
  Award,
  Layers,
  BookOpen,
  Users2
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface HeaderProps {
  onToggleMobileSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileSidebar }) => {
  const {
    userRole,
    userProfile,
    unreadNotifications,
    notificationCount,
    markNotificationRead,
    navigateTo,
    logout,
    loginAs,
    currentRoute,
    availableLearners,
    selectedLearnerId,
    selectLearner
  } = useApp();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLearnerSwitcher, setShowLearnerSwitcher] = useState(false);

  const notifRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const learnerSwitcherRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
      if (learnerSwitcherRef.current && !learnerSwitcherRef.current.contains(event.target as Node)) {
        setShowLearnerSwitcher(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getInitials = (name: string) => {
    const parts = name.trim().split(' ').filter(p => !p.toLowerCase().startsWith('dr.'));
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-subtle">
      {/* Top micro-bar for Government Identity */}
      <div className="bg-slate-900 text-slate-300 text-[11px] px-4 py-1 flex items-center justify-between font-medium">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Official Statistical System of India • MoSPI Initiative</span>
          <span className="hidden md:inline text-slate-500">|</span>
          <span className="hidden md:inline text-slate-400">
            KCM & ACBP Competency Intelligence Engine
          </span>
          <span className="hidden md:inline text-slate-500">|</span>
          <span className="text-amber-300 text-[10px] bg-amber-950/60 px-1.5 py-0.2 rounded border border-amber-800">
            Synthetic Demonstration Data
          </span>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <button
            onClick={() => loginAs(userRole === 'admin' ? 'employee' : 'admin')}
            className="flex items-center gap-1.5 text-blue-300 hover:text-white transition-colors bg-slate-800 px-2 py-0.5 rounded border border-slate-700"
          >
            <Shield className="w-3 h-3 text-amber-400" />
            Switch to {userRole === 'admin' ? 'Officer View' : 'Admin View'}
          </button>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Mobile hamburger & Logo */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleMobileSidebar}
            className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none"
            aria-label="Toggle menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div
            onClick={() => navigateTo('dashboard')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-lg bg-blue-900 flex items-center justify-center text-white shadow-sm font-bold text-lg group-hover:bg-blue-800 transition-colors">
              <span className="tracking-tighter">S</span>
              <span className="text-amber-400 font-extrabold text-sm">AI</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg tracking-tight text-slate-900">
                  StatSkill<span className="text-blue-700">AI</span>
                </span>
                <span className="text-[10px] font-semibold tracking-wider uppercase bg-blue-50 text-blue-800 px-1.5 py-0.5 rounded border border-blue-200">
                  Govt of India
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium hidden sm:block">
                Mission Karmayogi Competency & ACBP Course Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Center: Quick navigation links for desktop */}
        <nav className="hidden lg:flex items-center space-x-1">
          <button
            onClick={() => navigateTo('dashboard')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              currentRoute === 'dashboard'
                ? 'bg-blue-50 text-blue-800 border border-blue-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Dashboard
          </button>

          <button
            onClick={() => navigateTo('weekly-progress')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              currentRoute === 'weekly-progress'
                ? 'bg-blue-50 text-blue-800 border border-blue-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5 text-blue-600" />
            Weekly Progress
          </button>

          <button
            onClick={() => navigateTo('competency-assessment')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              currentRoute === 'competency-assessment'
                ? 'bg-blue-50 text-blue-800 border border-blue-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Award className="w-3.5 h-3.5 text-amber-600" />
            KCM Competencies
          </button>

          <button
            onClick={() => navigateTo('skill-gap')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              currentRoute === 'skill-gap'
                ? 'bg-blue-50 text-blue-800 border border-blue-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            Skill Gaps
          </button>

          <button
            onClick={() => navigateTo('recommendations')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              currentRoute === 'recommendations'
                ? 'bg-blue-50 text-blue-800 border border-blue-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            ACBP Recommendations
          </button>

          <button
            onClick={() => navigateTo('course-details')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              currentRoute === 'course-details'
                ? 'bg-blue-50 text-blue-800 border border-blue-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-slate-500" />
            Courses
          </button>
        </nav>

        {/* Right: Learner Switcher, Notifications, & Profile */}
        <div className="flex items-center space-x-2.5">
          {/* Active Learner Switcher Dropdown */}
          <div className="relative" ref={learnerSwitcherRef}>
            <button
              onClick={() => setShowLearnerSwitcher(!showLearnerSwitcher)}
              className="px-2.5 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 flex items-center gap-1.5 transition-colors"
              title="Switch Demonstration Learner Profile"
            >
              <Users2 className="w-3.5 h-3.5 text-blue-700" />
              <span className="hidden sm:inline font-bold text-slate-900">
                {userProfile.name}
              </span>
              <span className="text-[10px] bg-blue-100 text-blue-800 font-bold px-1.5 py-0.2 rounded">
                {selectedLearnerId}
              </span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {showLearnerSwitcher && (
              <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50">
                <div className="px-3 py-2 border-b border-slate-100">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Synthetic Demonstration Profiles
                  </span>
                  <p className="text-[11px] text-slate-500">
                    Switching recomputes skill gaps & ACBP recommendations
                  </p>
                </div>
                <div className="py-1">
                  {availableLearners.map((learner) => (
                    <button
                      key={learner.learner_id}
                      onClick={() => {
                        selectLearner(learner.learner_id);
                        setShowLearnerSwitcher(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-xs flex items-start gap-2.5 hover:bg-blue-50 transition-colors ${
                        learner.learner_id === selectedLearnerId
                          ? 'bg-blue-50/80 font-bold text-blue-900'
                          : 'text-slate-700'
                      }`}
                    >
                      <div className="w-7 h-7 rounded-md bg-blue-900 text-white font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">
                        {getInitials(learner.name)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="font-bold truncate">{learner.name}</span>
                          <span className="text-[10px] text-slate-400">{learner.learner_id}</span>
                        </div>
                        <p className="text-[10px] text-slate-500 truncate">{learner.department}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Notifications Dropdown */}
          <div className="relative" ref={notifRef}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none transition-colors"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
              {notificationCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-rose-600 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                  {notificationCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="px-4 py-2 border-b border-slate-100 flex items-center justify-between">
                  <span className="font-semibold text-xs text-slate-900 uppercase tracking-wider">
                    Official Notifications ({unreadNotifications.length})
                  </span>
                  <span className="text-[11px] text-blue-600 font-medium">Auto AI alerts</span>
                </div>
                <div className="max-h-72 overflow-y-auto divide-y divide-slate-100">
                  {unreadNotifications.map(notif => (
                    <div
                      key={notif.id}
                      onClick={() => markNotificationRead(notif.id)}
                      className={`p-3.5 hover:bg-slate-50 cursor-pointer transition-colors flex items-start gap-3 ${
                        !notif.read ? 'bg-blue-50/40' : ''
                      }`}
                    >
                      <div className="mt-0.5">
                        <CheckCircle2 className={`w-4 h-4 ${notif.read ? 'text-slate-400' : 'text-blue-600'}`} />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-slate-800 font-medium leading-relaxed">{notif.title}</p>
                        <span className="text-[10px] text-slate-500 mt-1 block">{notif.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="px-4 py-2 border-t border-slate-100 bg-slate-50/70 text-center">
                  <button
                    onClick={() => {
                      setShowNotifications(false);
                      navigateTo('recommendations');
                    }}
                    className="text-xs font-semibold text-blue-700 hover:text-blue-900"
                  >
                    View Recommendation Report →
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User Profile Pill */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 p-1.5 pl-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors focus:outline-none"
            >
              <div className="w-8 h-8 rounded-md bg-blue-900 text-white font-bold text-xs flex items-center justify-center">
                {userRole === 'admin' ? 'AD' : getInitials(userProfile.name)}
              </div>
              <div className="text-left hidden xl:block">
                <p className="text-xs font-bold text-slate-900 leading-tight">
                  {userRole === 'admin' ? 'Administrator' : userProfile.name}
                </p>
                <p className="text-[10px] text-slate-500 font-medium truncate max-w-[140px]">
                  {userRole === 'admin' ? 'MoSPI Oversight' : userProfile.designation}
                </p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50">
                <div className="px-4 py-3 border-b border-slate-100">
                  <p className="text-xs font-bold text-slate-900">{userProfile.name}</p>
                  <p className="text-[11px] text-slate-500">{userProfile.email}</p>
                  <div className="mt-2 flex items-center gap-1.5">
                    <span className="text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded">
                      ID: {userProfile.employeeId}
                    </span>
                    <span className="text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded">
                      {userRole === 'admin' ? 'Admin Role' : 'Demonstration Profile'}
                    </span>
                  </div>
                </div>

                <div className="py-1">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      navigateTo('profile');
                    }}
                    className="w-full text-left px-4 py-2 text-xs text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                  >
                    <User className="w-4 h-4 text-slate-500" />
                    Officer Profile & Assessment
                  </button>

                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      navigateTo('admin');
                    }}
                    className="w-full text-left px-4 py-2 text-xs text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                  >
                    <Shield className="w-4 h-4 text-slate-500" />
                    Administrator Dashboard
                  </button>
                </div>

                <div className="border-t border-slate-100 pt-1">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      logout();
                    }}
                    className="w-full text-left px-4 py-2 text-xs text-rose-600 hover:bg-rose-50 flex items-center gap-2 font-medium"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
