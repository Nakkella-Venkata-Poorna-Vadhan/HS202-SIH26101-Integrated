import React, { useState, useEffect } from 'react';
import { UserProfile, CompetencyScore } from '../../types';
import { ProgressBar } from '../common/ProgressBar';
import {
  User,
  Building,
  Briefcase,
  GraduationCap,
  Calendar,
  Mail,
  Phone,
  MapPin,
  Edit3,
  CheckCircle,
  Target,
  Sparkles,
  BookOpen
} from 'lucide-react';

interface EmployeeProfileViewProps {
  profile: UserProfile;
  skills: CompetencyScore[];
  overallCompetency: number;
  onUpdateProfile: (updated: Partial<UserProfile>) => void;
}

export const EmployeeProfileView: React.FC<EmployeeProfileViewProps> = ({
  profile,
  skills,
  overallCompetency,
  onUpdateProfile
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState(profile);
  const [showSuccessToast, setShowSuccessToast] = useState(false);

  useEffect(() => {
    setFormData(profile);
  }, [profile]);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdateProfile(formData);
    setIsEditing(false);
    setShowSuccessToast(true);
    setTimeout(() => setShowSuccessToast(false), 3000);
  };

  const getInitials = (name: string) => {
    const parts = name.trim().split(' ').filter(p => !p.toLowerCase().startsWith('dr.'));
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {showSuccessToast && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-semibold flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>Profile records updated locally in current demonstration session!</span>
        </div>
      )}

      {/* Main Profile Header Card */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-start space-x-4">
            {/* Avatar Pill */}
            <div className="w-16 h-16 rounded-xl bg-blue-900 text-white font-extrabold text-2xl flex items-center justify-center shadow-md">
              {getInitials(profile.name)}
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h1 className="text-2xl font-extrabold text-slate-900">{profile.name}</h1>
                <span className="text-xs font-bold bg-blue-100 text-blue-900 px-2 py-0.5 rounded border border-blue-200">
                  ID: {profile.employeeId}
                </span>
                <span className="text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full">
                  Synthetic Demonstration Profile
                </span>
              </div>

              <p className="text-sm font-semibold text-slate-700">{profile.designation}</p>
              <p className="text-xs text-slate-500">{profile.department}</p>

              <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-600">
                <span className="flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  {profile.email}
                </span>
                <span className="flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  {profile.phone}
                </span>
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  {profile.location}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={() => setIsEditing(!isEditing)}
            className="px-4 py-2 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center gap-1.5 transition-colors"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>{isEditing ? 'Cancel Editing' : 'Edit Profile'}</span>
          </button>
        </div>

        {/* Edit Form Modal/Panel */}
        {isEditing && (
          <form onSubmit={handleSave} className="mt-6 pt-6 border-t border-slate-200 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Edit Officer Profile Details</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-slate-600 font-semibold mb-1">Full Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-slate-600 font-semibold mb-1">Designation</label>
                <input
                  type="text"
                  value={formData.designation}
                  onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-slate-600 font-semibold mb-1">Department</label>
                <input
                  type="text"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-slate-600 font-semibold mb-1">Job Role Description</label>
                <input
                  type="text"
                  value={formData.jobRole}
                  onChange={(e) => setFormData({ ...formData, jobRole: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-slate-600 font-semibold mb-1">Experience</label>
                <input
                  type="text"
                  value={formData.experience}
                  onChange={(e) => setFormData({ ...formData, experience: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-slate-600 font-semibold mb-1">Education</label>
                <input
                  type="text"
                  value={formData.education}
                  onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-md"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 rounded-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 text-xs font-bold text-white bg-blue-900 rounded-md hover:bg-blue-800"
              >
                Save Changes
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Grid: Qualifications & Official Mandates */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Education & Experience Details */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-blue-800" />
            <span>Qualifications & Cadre Role</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-500 font-medium block">Educational Credentials</span>
              <p className="font-bold text-slate-900 mt-0.5">{profile.education}</p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-500 font-medium block">Cadre Experience</span>
              <p className="font-bold text-slate-900 mt-0.5">{profile.experience}</p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-slate-500 font-medium block">Current Assignment / Job Role</span>
              <p className="font-bold text-slate-900 mt-0.5">{profile.jobRole}</p>
            </div>
          </div>
        </div>

        {/* Competency Profile Summary */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-purple-600" />
              <span>Assessed Competency Summary</span>
            </h3>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Overall: {overallCompetency}%
            </span>
          </div>

          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {skills.map((s) => (
              <div key={s.name} className="text-xs">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-semibold text-slate-800 truncate mr-2">{s.name}</span>
                  <span className="font-bold text-slate-900 shrink-0">
                    {s.level === 'unassessed' ? 'Unassessed' : `${s.current}%`}
                  </span>
                </div>
                <ProgressBar
                  value={s.level === 'unassessed' ? 0 : s.current}
                  target={s.required}
                  level={s.level === 'unassessed' ? 'developing' : s.level}
                  height="sm"
                />
              </div>
            ))}
            {skills.length === 0 && (
              <p className="text-xs text-slate-500 text-center py-4">
                No competency scores recorded.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Preferences & Goals */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Learning Preferences */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-amber-600" />
            <span>Learning Preferences</span>
          </h3>
          <p className="text-xs text-slate-500">
            Cadre capacity building aligns training delivery with official preferences:
          </p>
          <ul className="space-y-2 text-xs">
            {profile.learningPreferences.map((pref, i) => (
              <li key={i} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-center gap-2 font-medium text-slate-700">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                <span>{pref}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Current Learning Goals */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm space-y-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-700" />
            <span>Target Learning Objectives (ACBP Schedule)</span>
          </h3>
          <p className="text-xs text-slate-500">
            Priorities derived directly from identified competency deficits:
          </p>
          <ul className="space-y-2 text-xs">
            {profile.currentGoals.map((goal, i) => (
              <li key={i} className="p-2.5 rounded-lg bg-blue-50/50 border border-blue-100 flex items-start gap-2 font-medium text-blue-950">
                <CheckCircle className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <span>{goal}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
