import React, { useState } from 'react';
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
import { Clock, Info, CheckCircle2 } from 'lucide-react';

interface DailyProgressChartProps {
  days: DayProgress[];
  targetDailyHours?: number;
}

export const DailyProgressChart: React.FC<DailyProgressChartProps> = ({
  days,
  targetDailyHours = 1.0,
}) => {
  const [selectedDay, setSelectedDay] = useState<DayProgress | null>(days[days.length - 1]);

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Daily Learning Hours Distribution</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Click on any day bar to inspect specific competencies and activities completed
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 font-medium text-slate-600">
            <span className="w-3 h-3 rounded bg-blue-700 inline-block"></span>
            <span>Met Target (≥1.0h)</span>
          </div>
          <div className="flex items-center gap-1.5 font-medium text-slate-600">
            <span className="w-3 h-3 rounded bg-blue-300 inline-block"></span>
            <span>Partial Day (&lt;1.0h)</span>
          </div>
          <div className="flex items-center gap-1.5 font-medium text-amber-700">
            <span className="w-3 h-0.5 bg-amber-500 inline-block"></span>
            <span>Daily Benchmark (1.0h)</span>
          </div>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={days}
            margin={{ top: 20, right: 20, left: -15, bottom: 5 }}
            onClick={(state) => {
              if (state && state.activePayload && state.activePayload.length) {
                setSelectedDay(state.activePayload[0].payload as DayProgress);
              }
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis
              dataKey="day"
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              tick={{ fill: '#475569', fontSize: 12, fontWeight: 500 }}
            />
            <YAxis
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              tick={{ fill: '#64748b', fontSize: 11 }}
              domain={[0, 2.0]}
              ticks={[0, 0.5, 1.0, 1.5, 2.0]}
              unit="h"
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload as DayProgress;
                  return (
                    <div className="bg-slate-900 text-white p-3 rounded-lg shadow-xl text-xs space-y-1.5 border border-slate-700">
                      <div className="flex items-center justify-between gap-4">
                        <span className="font-bold text-amber-300">{data.day}</span>
                        <span className="text-slate-400">{data.date}</span>
                      </div>
                      <p className="text-white">
                        Completed Time: <span className="font-bold text-emerald-400">{data.hours} hrs</span>
                      </p>
                      <p className="text-slate-300">Daily Target: {targetDailyHours} hr</p>
                      {data.completedTasks?.length > 0 && (
                        <div className="pt-1.5 border-t border-slate-700">
                          <span className="text-[10px] text-slate-400 font-semibold block mb-0.5">Tasks:</span>
                          {data.completedTasks.map((task, i) => (
                            <p key={i} className="text-[11px] text-slate-200 leading-snug">
                              • {task}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine
              y={targetDailyHours}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              strokeWidth={2}
              label={{
                value: 'Target: 1.0 hr/day',
                position: 'top',
                fill: '#b45309',
                fontSize: 11,
                fontWeight: 600
              }}
            />
            <Bar dataKey="hours" radius={[6, 6, 0, 0]} maxBarSize={52}>
              {days.map((entry, index) => {
                const isSelected = selectedDay?.day === entry.day;
                const meetsTarget = entry.hours >= targetDailyHours;
                return (
                  <Cell
                    key={`cell-${index}`}
                    cursor="pointer"
                    fill={isSelected ? '#1e3a8a' : meetsTarget ? '#2563eb' : '#93c5fd'}
                    stroke={isSelected ? '#1d4ed8' : 'none'}
                    strokeWidth={isSelected ? 2 : 0}
                  />
                );
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Selected Day Details Panel */}
      {selectedDay && (
        <div className="mt-4 p-3 bg-blue-50/60 rounded-xl border border-blue-100 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-700 text-white flex items-center justify-center font-bold text-xs">
              {selectedDay.shortDay}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-900">{selectedDay.day} ({selectedDay.date})</span>
                <span className="text-[11px] font-semibold text-blue-700 bg-white px-2 py-0.5 rounded border border-blue-200">
                  {selectedDay.hours} hours logged
                </span>
              </div>
              <p className="text-xs text-slate-600 mt-0.5">
                {selectedDay.completedTasks.length > 0
                  ? selectedDay.completedTasks.join(' • ')
                  : 'No active module logged on this day.'}
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs font-semibold text-slate-700">Daily Target: 1.0h</span>
            <p className="text-[11px] font-medium text-emerald-700">
              {selectedDay.hours >= 1.0 ? '✓ Target achieved' : 'Partial completion'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
