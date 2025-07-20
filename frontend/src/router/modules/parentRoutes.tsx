import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ParentDashboard from '@/pages/parent/Dashboard';
import ParentChildProgress from '@/pages/parent/ChildProgress';
import ParentCommunication from '@/pages/parent/Communication';
import ParentSchedule from '@/pages/parent/Schedule';
import ParentReports from '@/pages/parent/Reports';

export const parentRoutes = (
  <Routes>
    <Route path="/dashboard" element={<ParentDashboard />} />
    <Route path="/child-progress" element={<ParentChildProgress />} />
    <Route path="/communication" element={<ParentCommunication />} />
    <Route path="/schedule" element={<ParentSchedule />} />
    <Route path="/reports" element={<ParentReports />} />
    <Route path="/" element={<ParentDashboard />} />
  </Routes>
);