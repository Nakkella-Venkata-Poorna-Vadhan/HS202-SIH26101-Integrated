import React, { useState } from 'react';
import { LearningHistoryRecord } from '../../types';
import { Search, Filter, Download, Calendar, CheckCircle2, Clock, Award } from 'lucide-react';

interface LearningHistoryTableProps {
  history: LearningHistoryRecord[];
}

export const LearningHistoryTable: React.FC<LearningHistoryTableProps> = ({ history }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCourse, setSelectedCourse] = useState('All');
  const [selectedSkill, setSelectedSkill] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');

  // Extract unique courses, skills, statuses for dropdowns
  const uniqueCourses = ['All', ...Array.from(new Set(history.map((h) => h.course)))];
  const uniqueSkills = ['All', ...Array.from(new Set(history.map((h) => h.skill)))];
  const uniqueStatuses = ['All', ...Array.from(new Set(history.map((h) => h.status)))];

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      item.course.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.activity.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.skill.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCourse = selectedCourse === 'All' || item.course === selectedCourse;
    const matchesSkill = selectedSkill === 'All' || item.skill === selectedSkill;
    const matchesStatus = selectedStatus === 'All' || item.status === selectedStatus;

    return matchesSearch && matchesCourse && matchesSkill && matchesStatus;
  });

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden space-y-4 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Official Learning & Assessment History</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit trail of completed modules, quizzes, and continuous learning hours
          </p>
        </div>

        <button
          onClick={() => window.print()}
          title="Opens browser print dialog to print or save transcript as PDF"
          className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-1.5 shadow-2xs cursor-pointer"
        >
          <Download className="w-3.5 h-3.5 text-slate-500" />
          <span>Print / Export Transcript (PDF)</span>
        </button>
      </div>

      {/* Filter Controls Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2">
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search activities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Course Filter */}
        <div>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="w-full py-2 px-3 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none"
          >
            {uniqueCourses.map((c) => (
              <option key={c} value={c}>
                Course: {c}
              </option>
            ))}
          </select>
        </div>

        {/* Skill Filter */}
        <div>
          <select
            value={selectedSkill}
            onChange={(e) => setSelectedSkill(e.target.value)}
            className="w-full py-2 px-3 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none"
          >
            {uniqueSkills.map((s) => (
              <option key={s} value={s}>
                Skill: {s}
              </option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full py-2 px-3 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none"
          >
            {uniqueStatuses.map((st) => (
              <option key={st} value={st}>
                Status: {st}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-slate-200 rounded-lg">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              <th className="py-3 px-4">Date</th>
              <th className="py-3 px-4">Course</th>
              <th className="py-3 px-4">Activity Type</th>
              <th className="py-3 px-4">Skill Category</th>
              <th className="py-3 px-4">Duration</th>
              <th className="py-3 px-4">Score</th>
              <th className="py-3 px-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs">
            {filteredHistory.length > 0 ? (
              filteredHistory.map((row) => (
                <tr key={row.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4 font-medium text-slate-600 whitespace-nowrap">
                    {row.date}
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-900">
                    {row.course}
                  </td>
                  <td className="py-3 px-4 text-slate-700">
                    <span className="inline-flex items-center gap-1">
                      {row.activity === 'Quiz' ? (
                        <Award className="w-3.5 h-3.5 text-purple-600" />
                      ) : (
                        <Clock className="w-3.5 h-3.5 text-blue-600" />
                      )}
                      {row.activity}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-600">
                    <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[11px]">
                      {row.skill}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-700">
                    {row.duration}
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-900">
                    {row.score !== '—' ? (
                      <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {row.score}
                      </span>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="w-3 h-3" />
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="py-8 text-center text-xs text-slate-500">
                  No learning activities match the selected filter criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-xs text-slate-500 pt-2">
        <span>Showing {filteredHistory.length} of {history.length} learning records</span>
        <span>Certified by Cadre Records Authority</span>
      </div>
    </div>
  );
};
