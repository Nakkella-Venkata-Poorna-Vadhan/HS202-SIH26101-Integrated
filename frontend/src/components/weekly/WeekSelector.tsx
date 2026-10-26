import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar, Download } from 'lucide-react';

interface WeekSelectorProps {
  onExport?: () => void;
}

export const WeekSelector: React.FC<WeekSelectorProps> = ({ onExport }) => {
  const [currentWeekIndex, setCurrentWeekIndex] = useState(0);

  const weeks = [
    { label: 'October 1 – October 7, 2026', tag: 'Current Week', isCurrent: true },
    { label: 'September 24 – September 30, 2026', tag: 'Week 39', isCurrent: false },
    { label: 'September 17 – September 23, 2026', tag: 'Week 38', isCurrent: false },
    { label: 'September 10 – September 16, 2026', tag: 'Week 37', isCurrent: false },
  ];

  const handlePrev = () => {
    if (currentWeekIndex < weeks.length - 1) {
      setCurrentWeekIndex(currentWeekIndex + 1);
    }
  };

  const handleNext = () => {
    if (currentWeekIndex > 0) {
      setCurrentWeekIndex(currentWeekIndex - 1);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-sm flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-blue-50 text-blue-800">
          <Calendar className="w-5 h-5" />
        </div>
        <div>
          <span className="text-xs text-slate-500 font-medium">Reporting Cycle</span>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-slate-900">
              {weeks[currentWeekIndex].label}
            </h2>
            <span
              className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                weeks[currentWeekIndex].isCurrent
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-slate-100 text-slate-600 border-slate-200'
              }`}
            >
              {weeks[currentWeekIndex].tag}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <div className="flex items-center border border-slate-200 rounded-lg overflow-hidden bg-slate-50">
          <button
            onClick={handlePrev}
            disabled={currentWeekIndex === weeks.length - 1}
            className="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 border-r border-slate-200 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous Week</span>
          </button>
          <button
            onClick={handleNext}
            disabled={currentWeekIndex === 0}
            className="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
          >
            <span>Next Week</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {onExport && (
          <button
            onClick={onExport}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            <span>Export Report</span>
          </button>
        )}
      </div>
    </div>
  );
};
