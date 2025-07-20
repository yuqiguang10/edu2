import React, { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import type { UserRole } from '@/types';

interface RoleGuardProps {
  children: ReactNode;
  requiredRole: UserRole;
}

const RoleGuard: React.FC<RoleGuardProps> = ({ children, requiredRole }) => {
  const { user, hasRole } = useAuth();

  if (!user || !hasRole(requiredRole)) {
    // 重定向到默认页面或403页面
    return <Navigate to="/403" replace />;
  }

  return <>{children}</>;
};

export default RoleGuard;