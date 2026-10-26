import React from 'react';
import { useApp } from '../context/AppContext';
import { CompetencyCategories } from '../components/competency/CompetencyCategories';

export const CompetencyAssessmentPage: React.FC = () => {
  const {
    navigateTo,
    startDiagnosticAssessment,
    setSelectedAssessmentTopicId,
    assessmentTopics
  } = useApp();

  const handleStartAssessment = (cat: string, skill?: string) => {
    let topicId = 'KCM-FUNC-11';
    if (skill) {
      const match = assessmentTopics.find((t) =>
        t.competency_name.toLowerCase().includes(skill.toLowerCase()) ||
        t.competency_id.toLowerCase().includes(skill.toLowerCase())
      );
      if (match) topicId = match.competency_id;
    } else if (assessmentTopics.length > 0) {
      topicId = assessmentTopics[0].competency_id;
    }

    setSelectedAssessmentTopicId(topicId);
    startDiagnosticAssessment(topicId);
    navigateTo('quiz');
  };

  return (
    <div className="space-y-6">
      <CompetencyCategories
        onStartAssessment={handleStartAssessment}
        onViewSkillGaps={() => navigateTo('skill-gap')}
      />
    </div>
  );
};
