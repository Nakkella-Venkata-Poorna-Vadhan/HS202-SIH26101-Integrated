import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  Shield,
  Lock,
  Mail,
  ArrowRight,
  UserCheck,
  Building2,
  Sparkles,
  CheckCircle2,
  KeyRound,
  Users2
} from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { loginAs, availableLearners } = useApp();
  const [identifier, setIdentifier] = useState('LEARNER-001');
  const [password, setPassword] = useState('••••••••••••');
  const [rememberMe, setRememberMe] = useState(true);

  const resolveLearnerId = (input: string): string => {
    const trimmed = input.trim().toLowerCase();
    if (trimmed.includes('002') || trimmed.includes('meenakshi') || trimmed.includes('director')) {
      return 'LEARNER-002';
    }
    if (trimmed.includes('003') || trimmed.includes('pooja') || trimmed.includes('jso') || trimmed.includes('recruit')) {
      return 'LEARNER-003';
    }
    if (trimmed.includes('004') || trimmed.includes('rajesh') || trimmed.includes('ddg') || trimmed.includes('joint')) {
      return 'LEARNER-004';
    }
    if (trimmed.includes('001') || trimmed.includes('arun') || trimmed.includes('sso')) {
      return 'LEARNER-001';
    }
    const matched = availableLearners.find(
      (l) =>
        l.learner_id.toLowerCase() === trimmed ||
        l.name.toLowerCase().includes(trimmed)
    );
    if (matched) return matched.learner_id;
    return 'LEARNER-001';
  };

  const handleOfficerLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const resolvedId = resolveLearnerId(identifier);
    loginAs('employee', resolvedId);
  };

  const handleSelectProfile = (learnerId: string) => {
    setIdentifier(learnerId);
    loginAs('employee', learnerId);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-between">
      {/* Top Gov Header */}
      <header className="bg-slate-900 text-slate-300 text-xs py-2 px-6 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span className="font-semibold text-white">Government of India</span>
          <span className="text-slate-500">•</span>
          <span>Ministry of Statistics and Programme Implementation (MoSPI)</span>
        </div>
        <div className="text-[11px] font-medium text-slate-400 hidden sm:block">
          Official Statistical System Learning Portal • Smart India Hackathon Integrated Prototype
        </div>
      </header>

      {/* Main Login Card */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-lg bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
          {/* Brand header */}
          <div className="bg-linear-to-b from-blue-900 to-indigo-950 p-7 text-white text-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-xl pointer-events-none" />

            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 mb-3 shadow-inner">
              <span className="text-2xl font-black tracking-tight text-white">
                S<span className="text-amber-400">AI</span>
              </span>
            </div>

            <h1 className="text-2xl font-extrabold tracking-tight">StatSkill AI</h1>
            <p className="text-xs text-blue-200 mt-1 font-medium">
              Competency Intelligence & Training Plan Engine
            </p>
            <div className="mt-2.5 inline-block bg-amber-400/20 text-amber-300 text-[10px] font-bold px-2.5 py-0.5 rounded-full border border-amber-400/30 uppercase tracking-wider">
              KCM & MoSPI ACBP Integrated Catalogue
            </div>
          </div>

          {/* Form */}
          <div className="p-6 sm:p-8 space-y-5">
            <form onSubmit={handleOfficerLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Email / Demonstration Learner ID
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    required
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder="e.g. LEARNER-001 or arun.kumar@mospi.gov.in"
                    className="w-full pl-9 pr-3 py-2.5 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 focus:outline-none bg-slate-50 focus:bg-white text-slate-900 font-medium"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Password
                  </label>
                  <span className="text-[11px] text-slate-500">
                    Prototype terminal
                  </span>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter password"
                    className="w-full pl-9 pr-3 py-2.5 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 focus:outline-none bg-slate-50 focus:bg-white text-slate-900 font-medium"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center gap-2 cursor-pointer text-slate-600">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Remember this terminal</span>
                </label>
                <span className="text-[11px] text-slate-500">Simulated Gov Auth</span>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 px-4 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-md transition-all flex items-center justify-center gap-2"
              >
                <span>Login to Officer Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            {/* Quick Demonstration Access Profiles */}
            <div className="pt-4 border-t border-slate-200">
              <span className="text-[11px] font-bold text-slate-600 block text-center uppercase tracking-wider mb-2.5">
                Quick Demonstration Access (Synthetic Profiles):
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleSelectProfile('LEARNER-001')}
                  className="p-2 text-left text-xs font-bold text-blue-950 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                    <span className="truncate">Arun Kumar</span>
                  </div>
                  <span className="text-[10px] text-slate-500 block font-normal">
                    Senior Statistical Officer (FOD)
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => handleSelectProfile('LEARNER-002')}
                  className="p-2 text-left text-xs font-bold text-blue-950 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                    <span className="truncate">Dr. Meenakshi</span>
                  </div>
                  <span className="text-[10px] text-slate-500 block font-normal">
                    Director, National Accounts (NAD)
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => handleSelectProfile('LEARNER-003')}
                  className="p-2 text-left text-xs font-bold text-blue-950 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                    <span className="truncate">Pooja Verma</span>
                  </div>
                  <span className="text-[10px] text-amber-700 block font-normal">
                    JSO (Fresh Recruit • Unassessed)
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => handleSelectProfile('LEARNER-004')}
                  className="p-2 text-left text-xs font-bold text-blue-950 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                    <span className="truncate">Rajesh Sharma</span>
                  </div>
                  <span className="text-[10px] text-slate-500 block font-normal">
                    Deputy Director General (ESD)
                  </span>
                </button>
              </div>

              <div className="mt-2.5">
                <button
                  type="button"
                  onClick={() => loginAs('admin')}
                  className="w-full py-2 px-3 text-xs font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-lg transition-colors flex items-center justify-center gap-1.5"
                >
                  <Shield className="w-3.5 h-3.5 text-amber-600" />
                  <span>Cadre Administrator View (Macro Analytics)</span>
                </button>
              </div>

              <p className="text-[10px] text-slate-500 text-center mt-3 leading-relaxed">
                Powered by official KCM (34 competencies) & ACBP (226 courses) datasets. Learner profiles are synthetic demonstration fixtures.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-4 text-xs text-slate-500 border-t border-slate-200 bg-white">
        Official Statistical Cadre Competency Intelligence System • MoSPI • Smart India Hackathon 2026
      </footer>
    </div>
  );
};
