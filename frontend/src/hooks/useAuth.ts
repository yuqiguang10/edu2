// src/hooks/useAuth.ts
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useStore } from '@/store';
import { ROUTES } from '@/utils/constants';
import type { UserRole } from '@/types';

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
    clearError,
    initializeAuth,
  } = useStore();

  const navigate = useNavigate();
  const location = useLocation();

  // 初始化认证状态
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // 检查用户权限
  const hasRole = (role: UserRole): boolean => {
    return user?.roles?.includes(role) || false;
  };

  // 检查是否有权限访问路由
  const canAccessRoute = (route: string): boolean => {
    if (!isAuthenticated) return false;
    
    // 根据路由前缀判断权限
    if (route.startsWith('/student') && !hasRole('student')) return false;
    if (route.startsWith('/teacher') && !hasRole('teacher')) return false;
    if (route.startsWith('/parent') && !hasRole('parent')) return false;
    if (route.startsWith('/admin') && !hasRole('admin')) return false;
    
    return true;
  };

  // 登录并重定向
  const loginAndRedirect = async (credentials: any) => {
    try {
      await login(credentials);
      
      // 根据用户角色重定向到对应的首页
      const from = location.state?.from?.pathname || '/';
      if (from !== '/') {
        navigate(from, { replace: true });
      } else {
        // 默认重定向逻辑
        if (hasRole('admin')) {
          navigate(ROUTES.ADMIN.DASHBOARD);
        } else if (hasRole('teacher')) {
          navigate(ROUTES.TEACHER.DASHBOARD);
        } else if (hasRole('parent')) {
          navigate(ROUTES.PARENT.DASHBOARD);
        } else {
          navigate(ROUTES.STUDENT.DASHBOARD);
        }
      }
    } catch (error) {
      // 错误处理已在store中完成
      throw error;
    }
  };

  // 登出并重定向
  const logoutAndRedirect = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  return {
    user,
    isAuthenticated,
    loading,
    error,
    hasRole,
    canAccessRoute,
    login: loginAndRedirect,
    register,
    logout: logoutAndRedirect,
    updateProfile,
    clearError,
  };
};
