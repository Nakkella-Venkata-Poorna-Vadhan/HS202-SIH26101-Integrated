import React from 'react';
import { WeeklyBreakdownItem } from '../../types';
import { ProgressBar } from '../common/ProgressBar';
import { BookOpen, ArrowUpRight } from 'lucide-react';

interface LearningBreakdownTableProps {
  items: WeeklyBreakdownItem[];
  onOpenCourse: (courseName: string) => void;
}

export const LearningBreakdownTable: React.FC<LearningBreakdownTableProps> = ({
  items,
  onOpenCourse
}) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
      <div className="p-5 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-900">Weekly Learning Breakdown</h3>
          <p className="text-xs text-slate-500 mt-0.5">Subject-wise time allocated and course progress</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700">
          Total: 6.5 Hours
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              <th className="py-3 px-5">Course</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Time Invested</th>
              <th className="py-3 px-5">Curriculum Progress</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                <td className="py-3.5 px-5 font-bold text-slate-900 flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded bg-blue-50 text-blue-800 flex items-center justify-center shrink-0">
                    <BookOpen className="w-3.5 h-3.5" />
                  </div>
                  <span>{item.course}</span>
                </td>
                <td className="py-3.5 px-4 text-slate-600 font-medium">
                  <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[11px]">
                    {item.category}
                  </span>
                </td>
                <td className="py-3.5 px-4 font-bold text-slate-800">
                  {item.timeSpent}
                </td>
                <td className="py-3.5 px-5 min-w-[180px]">
                  <div className="flex items-center gap-3">
                    <div className="flex-1">
                      <ProgressBar
                        value={item.progress}
                        height="sm"
                        level={item.progress >= 80 ? 'strong' : 'developing'}
                      />
                    </div>
                    <span className="text-xs font-bold text-slate-700 w-10 text-right">{item.progress}%</span>
                  </div>
                </td>
                <td className="py-3.5 px-4 text-right">
                  <button
                    onClick={() => onOpenCourse(item.course)}
                    className="text-xs font-semibold text-blue-700 hover:text-blue-900 hover:underline inline-flex items-center gap-1"
                  >
                    <span>View</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
