import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  ShieldAlert,
  Clock,
  CheckCircle2,
  RefreshCw,
  LogOut,
  Building2,
  UserCheck,
  FileText,
  AlertCircle,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export const PendingApprovalPage: React.FC = () => {
  const { authUser, employeeStatus, refreshApplicationStatus, logout, loginAs } = useApp();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState<string | null>(null);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshMessage(null);
    try {
      await refreshApplicationStatus();
      setRefreshMessage('Application status checked. Current status: ' + (employeeStatus?.approval_status || 'UNAPPROVED'));
    } catch {
      setRefreshMessage('Could not retrieve updated status. Please try again.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const currentStatus = employeeStatus?.approval_status || authUser?.profile?.approval_status || 'UNAPPROVED';
  const appStatus = employeeStatus?.application_status || 'SUBMITTED';
  const assignedAdmin = employeeStatus?.assigned_admin_name || 'Cadre Review Queue (Pending Assignment)';
  const submissionNumber = employeeStatus?.submission_number ?? 1;

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
        {/* Banner Header */}
        <div className="bg-linear-to-r from-amber-600 to-amber-700 p-6 text-white relative">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-white/10 rounded-xl backdrop-blur-xs border border-white/20">
              <Clock className="w-7 h-7 text-amber-200 animate-pulse" />
            </div>
            <div>
              <div className="inline-block bg-amber-900/40 text-amber-100 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider mb-1">
                MoSPI Civil Service Competency Framework v2.7
              </div>
              <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white">
                Application Submitted & Pending Jurisdictional Review
              </h1>
              <p className="text-xs text-amber-100 mt-0.5">
                Official employee registration received. Awaiting administrative verification.
              </p>
            </div>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 sm:p-8 space-y-6">
          {/* Progress Timeline */}
          <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
            <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-4">
              Onboarding & Activation Progress
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
              <div className="flex items-start gap-2.5 p-3 rounded-lg bg-emerald-50 border border-emerald-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-emerald-950">1. Registration</p>
                  <p className="text-[11px] text-emerald-700">Account Created</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 p-3 rounded-lg bg-emerald-50 border border-emerald-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-emerald-950">2. Verification</p>
                  <p className="text-[11px] text-emerald-700">Email Confirmed</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-100 border border-amber-300 ring-2 ring-amber-400/50">
                <Clock className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-amber-950">3. Admin Review</p>
                  <p className="text-[11px] text-amber-800 font-semibold">{appStatus}</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-100 border border-slate-200 opacity-60">
                <div className="w-4 h-4 rounded-full border-2 border-slate-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-slate-700">4. Activation</p>
                  <p className="text-[11px] text-slate-500">Workspace Access</p>
                </div>
              </div>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-slate-200 rounded-xl p-4 bg-white space-y-2.5">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <UserCheck className="w-3.5 h-3.5 text-blue-600" />
                <span>Employee Particulars</span>
              </h3>
              <div className="text-xs space-y-1.5 text-slate-600">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Official Name:</span>
                  <span className="font-semibold text-slate-900">{employeeStatus?.full_name || authUser?.profile?.full_name || 'Registered Officer'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Employee Code:</span>
                  <span className="font-mono font-bold text-blue-900">{employeeStatus?.employee_code || authUser?.profile?.employee_code || 'PENDING'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Registered Email:</span>
                  <span className="font-medium text-slate-900">{authUser?.email}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Account Status:</span>
                  <span className="inline-block px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                    {authUser?.account_status || 'ACTIVE'}
                  </span>
                </div>
              </div>
            </div>

            <div className="border border-slate-200 rounded-xl p-4 bg-white space-y-2.5">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-amber-600" />
                <span>Jurisdictional Routing</span>
              </h3>
              <div className="text-xs space-y-1.5 text-slate-600">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Submission Number:</span>
                  <span className="font-mono font-bold text-slate-900">#{submissionNumber}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Application Status:</span>
                  <span className="inline-block px-2 py-0.5 rounded bg-amber-100 text-amber-900 font-bold text-[10px]">
                    {appStatus}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Approval State:</span>
                  <span className="font-bold text-rose-700">{currentStatus}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Assigned Reviewer:</span>
                  <span className="font-semibold text-slate-800">{assignedAdmin}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Architecture Rule Explanation Alert */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-950 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-700 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold">Role-Based Access Control Notice (Architecture v2.7)</p>
              <p className="text-blue-900 leading-relaxed">
                Public self-registration creates an active user account with a verified email address, but under Section 3 & Section 6 of the architecture plan, access to protected learning features, diagnostic assessments, and individual training plans strictly requires approval by an Administrator holding jurisdiction over your Cadre/Department.
              </p>
              <p className="text-blue-800 text-[11px]">
                Attempts to access protected employee endpoints without approval return <code className="bg-blue-100 px-1 py-0.5 rounded font-mono font-bold">403 Forbidden: Unapproved employee account</code>.
              </p>
            </div>
          </div>

          {refreshMessage && (
            <div className="p-3 rounded-lg bg-slate-100 text-xs text-slate-700 font-medium border border-slate-200 text-center">
              {refreshMessage}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-200">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="px-4 py-2 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-sm transition-all flex items-center gap-2 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>{isRefreshing ? 'Checking Status...' : 'Refresh Application Status'}</span>
            </button>

            <button
              onClick={() => logout()}
              className="px-4 py-2 text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>

          {/* Evaluator Quick Access Helper */}
          <div className="bg-slate-50 border border-dashed border-slate-300 rounded-xl p-4">
            <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-2">
              Demonstration & Evaluation Switching:
            </span>
            <p className="text-[11px] text-slate-500 mb-3">
              To evaluate the active competency assessment, skill gap analytics, and ACBP recommendation engines without waiting for administrative review, you can switch to one of the approved demonstration officer personas:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                onClick={() => loginAs('employee', 'LEARNER-001')}
                className="p-2 text-left text-xs font-bold text-blue-950 bg-white hover:bg-blue-50 border border-slate-200 rounded-lg transition-colors flex items-center justify-between cursor-pointer"
              >
                <span>Arun Kumar (SSO, FOD - Approved)</span>
                <ChevronRight className="w-3.5 h-3.5 text-blue-600" />
              </button>
              <button
                onClick={() => loginAs('employee', 'LEARNER-003')}
                className="p-2 text-left text-xs font-bold text-blue-950 bg-white hover:bg-blue-50 border border-slate-200 rounded-lg transition-colors flex items-center justify-between cursor-pointer"
              >
                <span>Pooja Verma (JSO, SDRD - Baseline)</span>
                <ChevronRight className="w-3.5 h-3.5 text-blue-600" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

