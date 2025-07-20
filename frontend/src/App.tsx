import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useWebSocket } from '@/hooks/useWebSocket';
import AuthGuard from '@/components/guards/AuthGuard';
import RoleGuard from '@/components/guards/RoleGuard';
import MainLayout from '@/components/layout/MainLayout';
import LoginPage from '@/pages/auth/Login';
import RegisterPage from '@/pages/auth/Register';
import ForgotPasswordPage from '@/pages/auth/ForgotPassword';
import NotFoundPage from '@/pages/NotFound';
import { studentRoutes } from '@/router/modules/studentRoutes';
import { teacherRoutes } from '@/router/modules/teacherRoutes';
import { parentRoutes } from '@/router/modules/parentRoutes';
import { adminRoutes } from '@/router/modules/adminRoutes';
import { ROUTES } from '@/utils/constants';
import Loading from '@/components/common/Loading';

const App: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  // 建立WebSocket连接
  useWebSocket(import.meta.env.VITE_WS_URL, {
    onMessage: (data) => {
      console.log('WebSocket message received:', data);
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* 公共路由 */}
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
        <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />

        {/* 需要认证的路由 */}
        <Route
          path="/*"
          element={
            <AuthGuard>
              <MainLayout>
                <Routes>
                  {/* 首页重定向 */}
                  <Route
                    path="/"
                    element={<Navigate to={getDefaultRoute(user?.roles?.[0] || 'student')} replace />}
                  />

                  {/* 学生路由 */}
                  <Route
                    path="/student/*"
                    element={
                      <RoleGuard requiredRole="student">
                        {studentRoutes}
                      </RoleGuard>
                    }
                  />

                  {/* 教师路由 */}
                  <Route
                    path="/teacher/*"
                    element={
                      <RoleGuard requiredRole="teacher">
                        {teacherRoutes}
                      </RoleGuard>
                    }
                  />

                  {/* 家长路由 */}
                  <Route
                    path="/parent/*"
                    element={
                      <RoleGuard requiredRole="parent">
                        {parentRoutes}
                      </RoleGuard>
                    }
                  />

                  {/* 管理员路由 */}
                  <Route
                    path="/admin/*"
                    element={
                      <RoleGuard requiredRole="admin">
                        {adminRoutes}
                      </RoleGuard>
                    }
                  />

                  {/* 404页面 */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </MainLayout>
            </AuthGuard>
          }
        />
      </Routes>
    </div>
  );
};

// 根据用户角色获取默认路由
const getDefaultRoute = (role: string): string => {
  switch (role) {
    case 'admin':
      return ROUTES.ADMIN.DASHBOARD;
    case 'teacher':
      return ROUTES.TEACHER.DASHBOARD;
    case 'parent':
      return ROUTES.PARENT.DASHBOARD;
    default:
      return ROUTES.STUDENT.DASHBOARD;
  }
};

export default App;