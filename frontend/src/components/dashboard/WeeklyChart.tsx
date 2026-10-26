import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from 'recharts';
import { DayProgress } from '../../types';
import { ArrowUpRight, Clock, Target } from 'lucide-react';

interface WeeklyChartProps {
  days: DayProgress[];
  totalHours: number;
  targetHours: number;
  onViewDetailed: () => void;
}

export const WeeklyChart: React.FC<WeeklyChartProps> = ({
  days,
  totalHours,
  targetHours,
  onViewDetailed,
}) => {
  const percentage = Math.round((totalHours / targetHours) * 100);

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base font-bold text-slate-900">Weekly Learning Activity</h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
              Demonstration Telemetry (LMS Pending)
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              01 Oct – 07 Oct 2026
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            {totalHours === 0 
              ? 'No study sessions recorded for this officer profile this week.'
              : 'Daily continuous learning hours recorded against the 1.0 hr/day target.'}
          </p>
        </div>

        <button
          onClick={onViewDetailed}
          className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1 hover:underline"
        >
          View Full Breakdown
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Target summary bar */}
      <div className="mb-5 p-3 bg-slate-50 rounded-lg border border-slate-200/80 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center font-bold">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs text-slate-500 font-medium block">Weekly Target Progress</span>
            <div className="flex items-baseline gap-1.5">
              <span className="text-lg font-bold text-slate-900">{totalHours} / {targetHours} hours</span>
              <span className="text-xs font-semibold text-blue-700">({percentage}% completed)</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-blue-600 inline-block"></span>
            <span>Completed Hours</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-amber-500 inline-block"></span>
            <span>Target Line (1.0h/day)</span>
          </div>
        </div>
      </div>

      {/* Chart container */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={days} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis
              dataKey="shortDay"
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }}
            />
            <YAxis
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              tick={{ fill: '#64748b', fontSize: 11 }}
              domain={[0, 2]}
              ticks={[0, 0.5, 1.0, 1.5, 2.0]}
              unit="h"
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload as DayProgress;
                  return (
                    <div className="bg-slate-900 text-white p-3 rounded-lg shadow-xl text-xs space-y-1">
                      <p className="font-bold text-amber-300">{data.day} ({data.date})</p>
                      <p className="text-white">
                        Learning time: <span className="font-bold text-emerald-400">{data.hours} hrs</span>
                      </p>
                      <p className="text-slate-300">Target: {data.targetHours} hr</p>
                      {data.completedTasks?.length > 0 && (
                        <div className="pt-1 border-t border-slate-700">
                          <p className="text-[10px] text-slate-400 font-medium">Activity:</p>
                          <p className="text-[11px] text-slate-200">{data.completedTasks[0]}</p>
                        </div>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine
              y={1.0}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              label={{ value: 'Daily Target (1.0h)', position: 'insideTopRight', fill: '#d97706', fontSize: 11, fontWeight: 600 }}
            />
            <Bar dataKey="hours" radius={[4, 4, 0, 0]} maxBarSize={48}>
              {days.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.hours >= entry.targetHours ? '#1e40af' : '#60a5fa'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100">
        <span>Mon: 0.8h • Tue: 1.2h • Wed: 0.6h • Thu: 1.5h • Fri: 1.0h • Sat: 0.9h • Sun: 0.5h</span>
        <span className="font-semibold text-emerald-700">On Track this Week</span>
      </div>
    </div>
  );
};
