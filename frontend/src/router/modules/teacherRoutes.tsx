import React from 'react';
import { Routes, Route } from 'react-router-dom';
import TeacherDashboard from '@/pages/teacher/Dashboard';
import TeacherClasses from '@/pages/teacher/Classes';
import TeacherHomework from '@/pages/teacher/Homework';
import TeacherExams from '@/pages/teacher/Exams';
import TeacherAnalytics from '@/pages/teacher/Analytics';
import TeacherResources from '@/pages/teacher/Resources';
import TeacherAIAssistant from '@/pages/teacher/AIAssistant';

export const teacherRoutes = (
  <Routes>
    <Route path="/dashboard" element={<TeacherDashboard />} />
    <Route path="/classes" element={<TeacherClasses />} />
    <Route path="/homework" element={<TeacherHomework />} />
    <Route path="/exams" element={<TeacherExams />} />
    <Route path="/analytics" element={<TeacherAnalytics />} />
    <Route path="/resources" element={<TeacherResources />} />
    <Route path="/ai-assistant" element={<TeacherAIAssistant />} />
    <Route path="/" element={<TeacherDashboard />} />
  </Routes>
);