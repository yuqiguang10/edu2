// frontend/src/components/auth/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Loading } from '@/components/common';

interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: string[];
  permissions?: string[];
  requireAuth?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  roles = [],
  permissions = [],
  requireAuth = true,
}) => {
  const { isAuthenticated, hasAnyRole, hasAnyPermission, loading, user } = useAuth();
  const location = useLocation();

  // 如果正在加载，显示加载状态
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" />
      </div>
    );
  }

  // 如果需要认证但未登录，跳转到登录页
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果已登录但不需要认证，允许访问
  if (!requireAuth) {
    return <>{children}</>;
  }

  // 检查角色权限
  if (roles.length > 0 && !hasAnyRole(roles)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">访问被拒绝</h1>
          <p className="text-gray-600 mb-6">您没有访问此页面的权限。</p>
          <p className="text-sm text-gray-500">
            需要角色：{roles.join(', ')}
          </p>
        </div>
      </div>
    );
  }

  // 检查权限
  if (permissions.length > 0 && !hasAnyPermission(permissions)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">权限不足</h1>
          <p className="text-gray-600 mb-6">您没有执行此操作的权限。</p>
          <p className="text-sm text-gray-500">
            需要权限：{permissions.join(', ')}
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;