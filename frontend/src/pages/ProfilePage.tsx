import React from 'react';
import { useApp } from '../context/AppContext';
import { EmployeeProfileView } from '../components/profile/EmployeeProfileView';

export const ProfilePage: React.FC = () => {
  const {
    userProfile,
    skills,
    overallCompetency,
    updateUserProfile,
  } = useApp();

  return (
    <div className="space-y-6">
      <EmployeeProfileView
        profile={userProfile}
        skills={skills}
        overallCompetency={overallCompetency}
        onUpdateProfile={updateUserProfile}
      />
    </div>
  );
};
