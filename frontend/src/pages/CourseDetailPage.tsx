import React from 'react';
import { useApp } from '../context/AppContext';
import { CourseDetailView } from '../components/course/CourseDetailView';

export const CourseDetailPage: React.FC = () => {
  const {
    courses,
    selectedCourseId,
    toggleModuleCompletion,
    navigateTo,
    setSelectedAssessmentTopicId,
    startDiagnosticAssessment,
  } = useApp();

  const currentCourse =
    courses.find((c) => c.id === selectedCourseId) || courses[0] || null;

  return (
    <div className="space-y-6">
      <CourseDetailView
        course={currentCourse}
        onToggleModule={(moduleId) => {
          if (currentCourse?.id) {
            toggleModuleCompletion(currentCourse.id, moduleId);
          }
        }}
        onGoToQuiz={() => {
          if (currentCourse?.targetCompetencyId) {
            setSelectedAssessmentTopicId(currentCourse.targetCompetencyId);
            startDiagnosticAssessment(currentCourse.targetCompetencyId);
          }
          navigateTo('quiz');
        }}
        onBack={() => navigateTo('recommendations')}
      />
    </div>
  );
};
