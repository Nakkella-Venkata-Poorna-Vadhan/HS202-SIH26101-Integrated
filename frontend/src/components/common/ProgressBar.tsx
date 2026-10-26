import React from 'react';

interface ProgressBarProps {
  value: number; // 0 to 100
  target?: number;
  level?: 'strong' | 'developing' | 'needs-improvement' | 'critical-gap';
  height?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  target,
  level,
  height = 'md',
  showLabel = false,
  className = '',
}) => {
  // Determine color based on level or value
  let barColor = 'bg-blue-600';
  if (level) {
    switch (level) {
      case 'strong':
        barColor = 'bg-emerald-600';
        break;
      case 'developing':
        barColor = 'bg-blue-600';
        break;
      case 'needs-improvement':
        barColor = 'bg-amber-500';
        break;
      case 'critical-gap':
        barColor = 'bg-rose-500';
        break;
    }
  } else {
    if (value >= 75) barColor = 'bg-emerald-600';
    else if (value >= 60) barColor = 'bg-blue-600';
    else if (value >= 50) barColor = 'bg-amber-500';
    else barColor = 'bg-rose-500';
  }

  const heightClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-3.5',
  };

  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between items-center text-xs text-slate-600 mb-1 font-medium">
          <span>{clampedValue}%</span>
          {target && <span>Target: {target}%</span>}
        </div>
      )}
      <div className={`w-full bg-slate-100 rounded-full overflow-hidden ${heightClasses[height]} relative`}>
        <div
          className={`${barColor} ${heightClasses[height]} rounded-full transition-all duration-700 ease-out`}
          style={{ width: `${clampedValue}%` }}
        />
        {target && (
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-slate-800 z-10"
            style={{ left: `${target}%` }}
            title={`Target: ${target}%`}
          />
        )}
      </div>
    </div>
  );
};
