import React from 'react';
import { useApp } from '../context/AppContext';
import { InteractiveQuiz } from '../components/quiz/InteractiveQuiz';

export const QuizPage: React.FC = () => {
  const { navigateTo } = useApp();

  return (
    <div className="space-y-6">
      <InteractiveQuiz
        onReturnToDashboard={() => navigateTo('dashboard')}
        onViewWeeklyProgress={() => navigateTo('weekly-progress')}
      />
    </div>
  );
};
