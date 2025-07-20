import React, { ReactNode, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { ROUTES } from '@/utils/constants';
import Loading from '@/components/common/Loading';

interface AuthGuardProps {
  children: ReactNode;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  // 如果未认证，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
  }

  // 如果已认证但用户信息还在加载
  if (!user) {
    return <Loading fullScreen text="正在加载用户信息..." />;
  }

  return <>{children}</>;
};

export default AuthGuard;