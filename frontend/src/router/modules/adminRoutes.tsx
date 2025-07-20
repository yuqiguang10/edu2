import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AdminDashboard from '@/pages/admin/Dashboard';
import AdminUsers from '@/pages/admin/Users';
import AdminSystem from '@/pages/admin/System';
import AdminAnalytics from '@/pages/admin/Analytics';
import AdminResources from '@/pages/admin/Resources';

export const adminRoutes = (
  <Routes>
    <Route path="/dashboard" element={<AdminDashboard />} />
    <Route path="/users" element={<AdminUsers />} />
    <Route path="/system" element={<AdminSystem />} />
    <Route path="/analytics" element={<AdminAnalytics />} />
    <Route path="/resources" element={<AdminResources />} />
    <Route path="/" element={<AdminDashboard />} />
  </Routes>
);