import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { AdminEmployee } from '../../types';
import { Search, Filter, Shield, User, ArrowUpRight, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';
import { ProgressBar } from '../common/ProgressBar';

interface AdminEmployeeTableProps {
  onInspectEmployee?: (emp: AdminEmployee) => void;
}

export const AdminEmployeeTable: React.FC<AdminEmployeeTableProps> = ({ onInspectEmployee }) => {
  const { adminEmployeesList, selectLearner, navigateTo } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');

  const departments = ['All', ...Array.from(new Set(adminEmployeesList.map((e) => e.department)))];

  const filteredEmployees = adminEmployeesList.filter((emp) => {
    const matchesSearch =
      emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.employeeId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.role.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesDept = selectedDept === 'All' || emp.department === selectedDept;

    return matchesSearch && matchesDept;
  });

  const handleSelectOfficer = (empId: string) => {
    selectLearner(empId);
    navigateTo('dashboard');
  };

  const getStatusBadge = (status: AdminEmployee['status']) => {
    switch (status) {
      case 'Exceeding Target':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
            <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
            Assessed
          </span>
        );
      case 'On Track':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
            Partially Assessed
          </span>
        );
      case 'Needs Attention':
      default:
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
            <HelpCircle className="w-2.5 h-2.5 text-amber-600" />
            Unassessed (Fresh)
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-900">
              Demonstration Cadre Learner Profiles
            </h3>
            <span className="text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full">
              Synthetic Profiles
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Click on any officer to view their live competency radar, skill gaps, and course recommendations
          </p>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700">
          Showing {filteredEmployees.length} of {adminEmployeesList.length} demonstration profiles
        </span>
      </div>

      {/* Filter Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
        {/* Search */}
        <div className="relative sm:col-span-2">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search officer name, designation, or ID (e.g. LEARNER-001)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
          />
        </div>

        {/* Division Filter */}
        <div>
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:border-blue-600 bg-white"
          >
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept === 'All' ? 'All Divisions' : dept}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-slate-200 rounded-xl">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
            <tr>
              <th className="py-3 px-4">Officer Details</th>
              <th className="py-3 px-4">Division & Cadre Role</th>
              <th className="py-3 px-4">Assessment Coverage</th>
              <th className="py-3 px-4">Identified Gaps</th>
              <th className="py-3 px-4">Profile Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredEmployees.map((emp) => (
              <tr
                key={emp.id}
                className="hover:bg-blue-50/40 transition-colors cursor-pointer"
                onClick={() => handleSelectOfficer(emp.id)}
              >
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-900 text-white font-bold text-xs flex items-center justify-center shrink-0">
                      {emp.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-bold text-slate-900 hover:text-blue-700 transition-colors">
                        {emp.name}
                      </p>
                      <span className="text-[10px] text-slate-500 font-mono">{emp.employeeId}</span>
                    </div>
                  </div>
                </td>

                <td className="py-3 px-4">
                  <p className="font-medium text-slate-800">{emp.role}</p>
                  <span className="text-[11px] text-slate-500">{emp.department}</span>
                </td>

                <td className="py-3 px-4">
                  <div className="w-36 space-y-1">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-slate-600">
                        {emp.assessedCount} / {emp.totalRequired} Assessed
                      </span>
                      <span className="font-bold text-slate-900">{emp.competency}%</span>
                    </div>
                    <ProgressBar
                      value={emp.competency}
                      level={emp.competency >= 75 ? 'strong' : 'developing'}
                      height="sm"
                    />
                  </div>
                </td>

                <td className="py-3 px-4">
                  <span className={`font-bold ${emp.skillGapsCount > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                    {emp.skillGapsCount} Gap{emp.skillGapsCount !== 1 ? 's' : ''}
                  </span>
                </td>

                <td className="py-3 px-4">{getStatusBadge(emp.status)}</td>

                <td className="py-3 px-4 text-right">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectOfficer(emp.id);
                    }}
                    className="px-3 py-1 text-xs font-semibold text-blue-700 hover:text-white hover:bg-blue-800 border border-blue-200 rounded-lg transition-colors inline-flex items-center gap-1"
                  >
                    <span>Inspect</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredEmployees.length === 0 && (
          <div className="p-8 text-center text-xs text-slate-500">
            No demonstration officers matched your search criteria.
          </div>
        )}
      </div>
    </div>
  );
};
