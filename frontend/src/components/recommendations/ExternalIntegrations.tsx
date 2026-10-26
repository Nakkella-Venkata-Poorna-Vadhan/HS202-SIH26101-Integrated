import React from 'react';
import { mockTrainingPrograms } from '../../data/mockData';
import { ExternalLink, Building2, Calendar, Award, Info } from 'lucide-react';

export const ExternalIntegrations: React.FC = () => {
  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-800" />
            <h3 className="text-base font-bold text-slate-900">
              National Training Academy Programmes & Portal References
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Reference directories for iGOT Karmayogi Bharat, NSSTA Academy, and NITI Aayog (External Portals)
          </p>
        </div>

        <span className="text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-1 rounded-full flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-blue-600" />
          External Platform Links • Live iGOT API Pending Production Integration
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {mockTrainingPrograms.map((prog) => (
          <div
            key={prog.id}
            className="border border-slate-200 rounded-xl p-4 bg-slate-50/40 hover:bg-slate-50 hover:border-blue-300 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between gap-1 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-900 bg-blue-100 px-2 py-0.5 rounded">
                  {prog.provider}
                </span>
                <span className="text-[10px] font-medium text-slate-500">
                  {prog.badge}
                </span>
              </div>

              <h4 className="text-xs font-bold text-slate-900 mb-2 leading-snug">
                {prog.title}
              </h4>

              <div className="space-y-1 text-xs text-slate-600 mb-3">
                <p className="flex items-center gap-1 text-[11px]">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  <span>Duration: {prog.duration}</span>
                </p>
                <p className="flex items-center gap-1 text-[11px]">
                  <Award className="w-3 h-3 text-slate-400" />
                  <span>Cadre: {prog.enrollment}</span>
                </p>
              </div>

              <div className="flex flex-wrap gap-1 mb-3">
                {prog.skills.map((s, i) => (
                  <span
                    key={i}
                    className="text-[10px] bg-white text-slate-700 px-1.5 py-0.5 rounded border border-slate-200 font-medium"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200/80 flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-700">
                {prog.status}
              </span>
              <a
                href={prog.url}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-bold text-blue-700 hover:text-blue-900 flex items-center gap-1 hover:underline"
              >
                <span>Portal Link</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
