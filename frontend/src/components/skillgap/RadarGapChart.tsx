import React from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip
} from 'recharts';
import { CompetencyScore } from '../../types';

interface RadarGapChartProps {
  skills: CompetencyScore[];
}

export const RadarGapChart: React.FC<RadarGapChartProps> = ({ skills }) => {
  // Format for radar chart on the prototype 1-5 level scale
  const radarData = skills.map((skill) => ({
    subject: skill.name.length > 20 ? `${skill.name.slice(0, 18)}...` : skill.name,
    fullName: skill.name,
    Current: +(skill.current / 20).toFixed(1),
    Required: +(skill.required / 20).toFixed(1),
    gap: +(skill.gap / 20).toFixed(1),
    isUnassessed: skill.level === 'unassessed'
  }));

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Competency Radar: Assessed vs. Role Requirements
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Mission Karmayogi Prototype 5-Level Scale: Level 1 (Awareness) to Level 5 (Expert)
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-semibold">
          <div className="flex items-center gap-1.5 text-blue-700">
            <span className="w-3 h-3 rounded-full bg-blue-600 inline-block"></span>
            <span>Assessed Level</span>
          </div>
          <div className="flex items-center gap-1.5 text-amber-700">
            <span className="w-3 h-3 rounded-full bg-amber-500 inline-block"></span>
            <span>Required Role Level</span>
          </div>
        </div>
      </div>

      <div className="h-80 w-full">
        {radarData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
              <PolarGrid stroke="#e2e8f0" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: '#334155', fontSize: 11, fontWeight: 600 }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 5]}
                tick={{ fill: '#64748b', fontSize: 10 }}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-slate-900 text-white p-3 rounded-lg shadow-xl text-xs space-y-1">
                        <p className="font-bold text-amber-300">{data.fullName}</p>
                        <p className="text-blue-300">
                          Assessed: <span className="font-bold">{data.isUnassessed ? 'Unassessed' : `Level ${data.Current} / 5`}</span>
                        </p>
                        <p className="text-amber-200">
                          Required Role Benchmark: <span className="font-bold">Level {data.Required} / 5</span>
                        </p>
                        <p className="text-rose-300 pt-1 border-t border-slate-700">
                          Identified Deficit: <span className="font-bold">{data.isUnassessed ? 'Assessment Pending' : `${data.gap} Level(s)`}</span>
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Radar
                name="Assessed Level"
                dataKey="Current"
                stroke="#2563eb"
                fill="#3b82f6"
                fillOpacity={0.45}
              />
              <Radar
                name="Required Role Level"
                dataKey="Required"
                stroke="#f59e0b"
                fill="#f59e0b"
                fillOpacity={0.2}
              />
              <Legend
                wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                iconSize={10}
              />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-xs text-slate-500">
            No competency requirements loaded for this role.
          </div>
        )}
      </div>
    </div>
  );
};
