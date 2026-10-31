import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import { OrgTaxonomy } from '../types';
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
  Users2,
  AlertCircle,
  RefreshCw,
  UserPlus,
  Key,
  ShieldCheck,
  ChevronRight,
  Briefcase,
  MapPin
} from 'lucide-react';

type AuthMode = 'login' | 'register' | 'verify-email' | 'reset-password' | 'accept-admin';

export const LoginPage: React.FC = () => {
  const {
    loginAs,
    availableLearners,
    loginWithCredentials,
    registerEmployee,
    verifyEmailToken,
    requestPasswordReset,
    confirmPasswordReset,
    acceptAdminInvite,
    isAuthenticating
  } = useApp();

  const [authMode, setAuthMode] = useState<AuthMode>('login');

  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);

  // Taxonomy data for registration
  const [taxonomy, setTaxonomy] = useState<OrgTaxonomy | null>(null);
  const [loadingTaxonomy, setLoadingTaxonomy] = useState(false);

  // Registration form state
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regPasswordConfirm, setRegPasswordConfirm] = useState('');
  const [regEmployeeCode, setRegEmployeeCode] = useState('');
  const [regMinistryId, setRegMinistryId] = useState('MIN_MOSPI');
  const [regDepartmentId, setRegDepartmentId] = useState('DEP_FOD');
  const [regCadreId, setRegCadreId] = useState('CADRE_SSS');
  const [regDesignationId, setRegDesignationId] = useState('DES_SSO');
  const [regLocationId, setRegLocationId] = useState('LOC_DEL_HQ');
  const [regExperience, setRegExperience] = useState('5.0');
  const [regSkills, setRegSkills] = useState('Statistical Sampling, Survey Design, Data Scrutiny');

  // Verify email form state
  const [verifyToken, setVerifyToken] = useState('');

  // Password reset state
  const [resetStep, setResetStep] = useState<'request' | 'confirm'>('request');
  const [resetEmail, setResetEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [resetNewPassword, setResetNewPassword] = useState('');

  // Accept admin invite state
  const [adminInviteToken, setAdminInviteToken] = useState('');
  const [adminFullName, setAdminFullName] = useState('');
  const [adminPassword, setAdminPassword] = useState('');

  // Fetch taxonomy when registering
  useEffect(() => {
    if (authMode === 'register' && !taxonomy) {
      setLoadingTaxonomy(true);
      api.getOrgTaxonomy()
        .then((data) => {
          setTaxonomy(data);
          if (data.ministries?.length) setRegMinistryId(data.ministries[0].id);
          if (data.departments?.length) setRegDepartmentId(data.departments[0].id);
          if (data.cadres?.length) setRegCadreId(data.cadres[0].id);
          if (data.designations?.length) setRegDesignationId(data.designations[0].id);
          if (data.locations?.length) setRegLocationId(data.locations[0].id);
        })
        .catch((err) => {
          console.error('Failed to load taxonomy:', err);
        })
        .finally(() => setLoadingTaxonomy(false));
    }
  }, [authMode, taxonomy]);

  // Handle standard credentials login
  const handleCredentialsLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSuccess(null);

    // If identifier matches synthetic profile format, allow direct fallback
    if (email.startsWith('LEARNER-') || !email.includes('@')) {
      const resolved = resolveLearnerId(email);
      loginAs('employee', resolved);
      return;
    }

    const res = await loginWithCredentials(email.trim(), password);
    if (!res.success) {
      setAuthError(res.error || 'Authentication failed. Please verify your credentials.');
    }
  };

  // Handle employee registration
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSuccess(null);

    if (regPassword !== regPasswordConfirm) {
      setAuthError('Passwords do not match.');
      return;
    }

    if (regPassword.length < 8) {
      setAuthError('Password must be at least 8 characters long.');
      return;
    }

    const skillsArray = regSkills
      .split(',')
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    const payload = {
      email: regEmail.trim(),
      password: regPassword,
      full_name: regFullName.trim(),
      employee_code: regEmployeeCode.trim().toUpperCase(),
      ministry_id: regMinistryId,
      department_id: regDepartmentId,
      cadre_id: regCadreId,
      designation_id: regDesignationId,
      location_id: regLocationId,
      experience_years: parseFloat(regExperience) || 0,
      self_declared_skills: skillsArray,
    };

    const res = await registerEmployee(payload);
    if (res.success) {
      setAuthSuccess('Registration successful! Please verify your email with the token sent to your email.');
      setAuthMode('verify-email');
    } else {
      setAuthError(res.error || 'Registration failed.');
    }
  };

  // Handle email verification
  const handleVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSuccess(null);

    if (!verifyToken.trim()) {
      setAuthError('Please enter the verification token.');
      return;
    }

    const res = await verifyEmailToken(verifyToken.trim());
    if (res.success) {
      setAuthSuccess('Email verified successfully! You may now log in to check your approval status.');
      setAuthMode('login');
      setEmail(res.user?.email || '');
      setVerifyToken('');
    } else {
      setAuthError(res.error || 'Email verification failed. The token may be expired or invalid.');
    }
  };

  // Handle password reset request
  const handleResetRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSuccess(null);

    const res = await requestPasswordReset(resetEmail.trim());
    if (res.success) {
      setAuthSuccess(res.message || 'If an account exists, password reset instructions have been sent.');
      setResetStep('confirm');
    } else {
      setAuthError(res.error || 'Failed to request password reset.');
    }
  };

  // Handle password reset confirm
  const handleResetConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSuccess(null);

    if (resetNewPassword.length < 8) {
      setAuthError('New password must be at least 8 characters long.');
      return;
    }

    const res = await confirmPasswordReset(resetToken.trim(), resetNewPassword);
    if (res.success) {
      setAuthSuccess('Password reset successfully. You may now log in with your new password.');
      setAuthMode('login');
      setEmail(resetEmail);
      setResetStep('request');
      setResetToken('');
      setResetNewPassword('');
    } else {
      setAuthError(res.error || 'Failed to reset password. The token may be invalid or expired.');
    }
  };

  // Handle administrator invite acceptance
  const handleAcceptAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSuccess(null);

    if (!adminInviteToken.trim() || !adminFullName.trim() || !adminPassword) {
      setAuthError('All fields are required.');
      return;
    }

    if (adminPassword.length < 8) {
      setAuthError('Password must be at least 8 characters long.');
      return;
    }

    const res = await acceptAdminInvite({
      token: adminInviteToken.trim(),
      fullName: adminFullName.trim(),
      password: adminPassword,
    });

    if (!res.success) {
      setAuthError(res.error || 'Failed to accept invitation.');
    }
  };

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

  const handleSelectProfile = (learnerId: string) => {
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
          Official Statistical System Learning Portal • Phase 2 Auth & Access Control
        </div>
      </header>

      {/* Main Container */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-xl bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
          {/* Brand header */}
          <div className="bg-linear-to-b from-blue-900 to-indigo-950 p-6 text-white text-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-xl pointer-events-none" />

            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 mb-2 shadow-inner">
              <span className="text-2xl font-black tracking-tight text-white">
                S<span className="text-amber-400">AI</span>
              </span>
            </div>

            <h1 className="text-2xl font-extrabold tracking-tight">StatSkill AI</h1>
            <p className="text-xs text-blue-200 mt-1 font-medium">
              MoSPI Competency Intelligence & Capacity Building Platform
            </p>

            {/* Auth Navigation Tabs */}
            <div className="mt-4 flex flex-wrap items-center justify-center gap-1 bg-black/20 p-1 rounded-xl border border-white/10 text-xs">
              <button
                type="button"
                onClick={() => { setAuthMode('login'); setAuthError(null); }}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                  authMode === 'login' ? 'bg-white text-blue-950 shadow-sm' : 'text-blue-200 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => { setAuthMode('register'); setAuthError(null); }}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                  authMode === 'register' ? 'bg-white text-blue-950 shadow-sm' : 'text-blue-200 hover:text-white'
                }`}
              >
                Employee Registration
              </button>
              <button
                type="button"
                onClick={() => { setAuthMode('verify-email'); setAuthError(null); }}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                  authMode === 'verify-email' ? 'bg-white text-blue-950 shadow-sm' : 'text-blue-200 hover:text-white'
                }`}
              >
                Verify Email
              </button>
              <button
                type="button"
                onClick={() => { setAuthMode('reset-password'); setAuthError(null); }}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                  authMode === 'reset-password' ? 'bg-white text-blue-950 shadow-sm' : 'text-blue-200 hover:text-white'
                }`}
              >
                Password Reset
              </button>
              <button
                type="button"
                onClick={() => { setAuthMode('accept-admin'); setAuthError(null); }}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                  authMode === 'accept-admin' ? 'bg-white text-blue-950 shadow-sm' : 'text-blue-200 hover:text-white'
                }`}
              >
                Admin Invite
              </button>
            </div>
          </div>

          {/* Form Card Content */}
          <div className="p-6 sm:p-8 space-y-4">
            {/* Feedback Alerts */}
            {authError && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <span className="font-medium leading-relaxed">{authError}</span>
              </div>
            )}
            {authSuccess && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span className="font-medium leading-relaxed">{authSuccess}</span>
              </div>
            )}

            {/* TAB 1: SIGN IN */}
            {authMode === 'login' && (
              <>
                <form onSubmit={handleCredentialsLogin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                      Official Email / Username
                    </label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                      <input
                        type="text"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="e.g. officer@mospi.gov.in or LEARNER-001"
                        className="w-full pl-9 pr-3 py-2.5 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 focus:outline-none bg-slate-50 focus:bg-white text-slate-900 font-medium"
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Password
                      </label>
                      <button
                        type="button"
                        onClick={() => setAuthMode('reset-password')}
                        className="text-[11px] font-semibold text-blue-700 hover:text-blue-900 cursor-pointer"
                      >
                        Forgot password?
                      </button>
                    </div>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                      <input
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter official password"
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
                    <span className="text-[11px] text-slate-500">Argon2id & JWT Auth</span>
                  </div>

                  <button
                    type="submit"
                    disabled={isAuthenticating}
                    className="w-full py-2.5 px-4 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <ArrowRight className="w-4 h-4" />
                    <span>{isAuthenticating ? 'Authenticating...' : 'Sign In with Credentials'}</span>
                  </button>
                </form>

                {/* Quick Demonstration Access Profiles */}
                <div className="pt-4 border-t border-slate-200">
                  <span className="text-[11px] font-bold text-slate-600 block text-center uppercase tracking-wider mb-2.5">
                    Quick Demonstration Access (Pre-Configured Personas):
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
                        Senior Statistical Officer (Approved)
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
                        Director, National Accounts (Approved)
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
                        JSO (Fresh Recruit • Baseline)
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
                        DDG / Joint Secretary (Approved)
                      </span>
                    </button>
                  </div>

                  <div className="mt-2.5">
                    <button
                      type="button"
                      onClick={() => loginAs('admin')}
                      className="w-full py-2 px-3 text-xs font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-lg transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                    >
                      <Shield className="w-3.5 h-3.5 text-amber-600" />
                      <span>Cadre Administrator View (Macro Analytics)</span>
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* TAB 2: EMPLOYEE SELF-REGISTRATION */}
            {authMode === 'register' && (
              <form onSubmit={handleRegister} className="space-y-3.5">
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900 space-y-1">
                  <p className="font-bold">MoSPI Civil Service Public Registration</p>
                  <p className="text-[11px] text-blue-800">
                    Creates an official user account and submits an onboarding application. Verification token will be sent to your email.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={regFullName}
                      onChange={(e) => setRegFullName(e.target.value)}
                      placeholder="e.g. Suresh Chand"
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Official Email *
                    </label>
                    <input
                      type="email"
                      required
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      placeholder="e.g. schand@mospi.gov.in"
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Password (min 8 chars) *
                    </label>
                    <input
                      type="password"
                      required
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Confirm Password *
                    </label>
                    <input
                      type="password"
                      required
                      value={regPasswordConfirm}
                      onChange={(e) => setRegPasswordConfirm(e.target.value)}
                      placeholder="••••••••"
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Employee Code *
                    </label>
                    <input
                      type="text"
                      required
                      value={regEmployeeCode}
                      onChange={(e) => setRegEmployeeCode(e.target.value)}
                      placeholder="e.g. EMP-2026-901"
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white uppercase font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Years of Experience
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      max="50"
                      value={regExperience}
                      onChange={(e) => setRegExperience(e.target.value)}
                      placeholder="e.g. 5.5"
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                    />
                  </div>
                </div>

                {/* Organizational Taxonomy Selectors */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                  <div>
                    <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">
                      Ministry
                    </label>
                    <select
                      value={regMinistryId}
                      onChange={(e) => setRegMinistryId(e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 bg-white"
                    >
                      {taxonomy?.ministries?.map((m) => (
                        <option key={m.id} value={m.id}>{m.name} ({m.code})</option>
                      )) || <option value="MIN_MOSPI">Ministry of Statistics and Programme Implementation</option>}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">
                      Department / Division
                    </label>
                    <select
                      value={regDepartmentId}
                      onChange={(e) => setRegDepartmentId(e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 bg-white"
                    >
                      {taxonomy?.departments?.map((d) => (
                        <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
                      )) || <option value="DEP_FOD">Field Operations Division (FOD)</option>}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">
                      Cadre
                    </label>
                    <select
                      value={regCadreId}
                      onChange={(e) => setRegCadreId(e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 bg-white"
                    >
                      {taxonomy?.cadres?.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      )) || <option value="CADRE_SSS">Subordinate Statistical Service (SSS)</option>}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">
                      Designation
                    </label>
                    <select
                      value={regDesignationId}
                      onChange={(e) => setRegDesignationId(e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 bg-white"
                    >
                      {taxonomy?.designations?.map((des) => (
                        <option key={des.id} value={des.id}>{des.name}</option>
                      )) || <option value="DES_SSO">Senior Statistical Officer</option>}
                    </select>
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-[11px] font-bold text-slate-600 uppercase mb-1">
                      Posting Location
                    </label>
                    <select
                      value={regLocationId}
                      onChange={(e) => setRegLocationId(e.target.value)}
                      className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 bg-white"
                    >
                      {taxonomy?.locations?.map((loc) => (
                        <option key={loc.id} value={loc.id}>{loc.city} - {loc.building_name}</option>
                      )) || <option value="LOC_DEL_HQ">New Delhi - Sardar Patel Bhawan</option>}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Self-Declared Skills (Comma separated)
                  </label>
                  <input
                    type="text"
                    value={regSkills}
                    onChange={(e) => setRegSkills(e.target.value)}
                    placeholder="e.g. Sampling, Data Analytics, Python"
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isAuthenticating}
                  className="w-full py-2.5 px-4 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 mt-2"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>{isAuthenticating ? 'Submitting Registration...' : 'Complete Self-Registration'}</span>
                </button>
              </form>
            )}

            {/* TAB 3: VERIFY EMAIL */}
            {authMode === 'verify-email' && (
              <form onSubmit={handleVerifyEmail} className="space-y-4">
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1">
                  <p className="font-bold">Email Verification (Single-Use Token)</p>
                  <p className="text-[11px] text-amber-800 leading-relaxed">
                    Enter the 32-character hexadecimal verification token dispatched to your email address. In the development test environment, tokens are captured in server logs.
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Verification Token (32-character Hex) *
                  </label>
                  <div className="relative">
                    <Key className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      required
                      value={verifyToken}
                      onChange={(e) => setVerifyToken(e.target.value)}
                      placeholder="e.g. 4a8b1c9f2d3e5a7b8c0d1e2f3a4b5c6d"
                      className="w-full pl-9 pr-3 py-2.5 text-xs font-mono rounded-lg border border-slate-300 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 focus:outline-none bg-slate-50 focus:bg-white text-slate-900"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isAuthenticating}
                  className="w-full py-2.5 px-4 text-xs font-bold text-white bg-emerald-800 hover:bg-emerald-700 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{isAuthenticating ? 'Verifying...' : 'Verify Token & Activate Account'}</span>
                </button>
              </form>
            )}

            {/* TAB 4: PASSWORD RESET */}
            {authMode === 'reset-password' && (
              <div>
                {resetStep === 'request' ? (
                  <form onSubmit={handleResetRequest} className="space-y-4">
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900 space-y-1">
                      <p className="font-bold">Password Reset Instructions</p>
                      <p className="text-[11px] text-blue-800">
                        Enter your registered official email address. If the account exists, an expiring single-use reset token will be issued.
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        Registered Email *
                      </label>
                      <div className="relative">
                        <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                        <input
                          type="email"
                          required
                          value={resetEmail}
                          onChange={(e) => setResetEmail(e.target.value)}
                          placeholder="officer@mospi.gov.in"
                          className="w-full pl-9 pr-3 py-2.5 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={isAuthenticating}
                      className="w-full py-2.5 px-4 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      <KeyRound className="w-4 h-4" />
                      <span>{isAuthenticating ? 'Submitting Request...' : 'Send Password Reset Token'}</span>
                    </button>
                  </form>
                ) : (
                  <form onSubmit={handleResetConfirm} className="space-y-4">
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1">
                      <p className="font-bold">Enter Reset Token & New Password</p>
                      <p className="text-[11px] text-amber-800">
                        Enter the single-use reset token received and choose your new password.
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        Reset Token *
                      </label>
                      <input
                        type="text"
                        required
                        value={resetToken}
                        onChange={(e) => setResetToken(e.target.value)}
                        placeholder="32-character reset token"
                        className="w-full px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        New Password (min 8 chars) *
                      </label>
                      <input
                        type="password"
                        required
                        value={resetNewPassword}
                        onChange={(e) => setResetNewPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isAuthenticating}
                      className="w-full py-2.5 px-4 text-xs font-bold text-white bg-emerald-800 hover:bg-emerald-700 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{isAuthenticating ? 'Updating...' : 'Set New Password'}</span>
                    </button>
                  </form>
                )}
              </div>
            )}

            {/* TAB 5: ACCEPT ADMINISTRATOR INVITATION */}
            {authMode === 'accept-admin' && (
              <form onSubmit={handleAcceptAdmin} className="space-y-4">
                <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-xl text-xs text-indigo-950 space-y-1">
                  <p className="font-bold">Administrator Invitation Activation</p>
                  <p className="text-[11px] text-indigo-800 leading-relaxed">
                    Administrators cannot register publicly. If you have been invited by Project Staff, provide the invitation token to activate your administrative credentials.
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Invitation Token *
                  </label>
                  <input
                    type="text"
                    required
                    value={adminInviteToken}
                    onChange={(e) => setAdminInviteToken(e.target.value)}
                    placeholder="32-character invitation token"
                    className="w-full px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Official Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={adminFullName}
                    onChange={(e) => setAdminFullName(e.target.value)}
                    placeholder="e.g. Dr. K. Venkataraman"
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Set Administrator Password *
                  </label>
                  <input
                    type="password"
                    required
                    value={adminPassword}
                    onChange={(e) => setAdminPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:border-blue-600 focus:outline-none bg-slate-50 focus:bg-white"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isAuthenticating}
                  className="w-full py-2.5 px-4 text-xs font-bold text-white bg-indigo-900 hover:bg-indigo-800 rounded-lg shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>{isAuthenticating ? 'Activating...' : 'Activate Administrator Account'}</span>
                </button>
              </form>
            )}
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
