import React from 'react';
import { Routes, Route } from 'react-router-dom';
import StudentDashboard from '@/pages/student/Dashboard';
import StudentCourses from '@/pages/student/Courses';
import StudentHomework from '@/pages/student/Homework';
import StudentExams from '@/pages/student/Exams';
import StudentProgress from '@/pages/student/Progress';
import StudentMistakes from '@/pages/student/Mistakes';
import StudentResources from '@/pages/student/Resources';

export const studentRoutes = (
  <Routes>
    <Route path="/dashboard" element={<StudentDashboard />} />
    <Route path="/courses" element={<StudentCourses />} />
    <Route path="/homework" element={<StudentHomework />} />
    <Route path="/exams" element={<StudentExams />} />
    <Route path="/progress" element={<StudentProgress />} />
    <Route path="/mistakes" element={<StudentMistakes />} />
    <Route path="/resources" element={<StudentResources />} />
    <Route path="/" element={<StudentDashboard />} />
  </Routes>
);