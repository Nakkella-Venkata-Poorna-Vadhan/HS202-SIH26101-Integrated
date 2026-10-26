import React from 'react';
import { useApp } from '../context/AppContext';
import { LearningHistoryTable } from '../components/history/LearningHistoryTable';

export const LearningHistoryPage: React.FC = () => {
  const { history } = useApp();

  return (
    <div className="space-y-6">
      <LearningHistoryTable history={history} />
    </div>
  );
};
