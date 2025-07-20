// frontend/src/components/auth/RoleBasedComponent.tsx
import React from 'react';
import { useAuth } from '@/hooks/useAuth';

interface RoleBasedComponentProps {
  children: React.ReactNode;
  roles?: string[];
  permissions?: string[];
  fallback?: React.ReactNode;
  requireAll?: boolean; // 是否需要同时满足所有角色/权限
}

const RoleBasedComponent: React.FC<RoleBasedComponentProps> = ({
  children,
  roles = [],
  permissions = [],
  fallback = null,
  requireAll = false,
}) => {
  const { hasRole, hasPermission, hasAnyRole, hasAnyPermission } = useAuth();

  let hasAccess = true;

  // 检查角色
  if (roles.length > 0) {
    if (requireAll) {
      hasAccess = roles.every(role => hasRole(role));
    } else {
      hasAccess = hasAnyRole(roles);
    }
  }

  // 检查权限
  if (hasAccess && permissions.length > 0) {
    if (requireAll) {
      hasAccess = permissions.every(permission => hasPermission(permission));
    } else {
      hasAccess = hasAnyPermission(permissions);
    }
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>;
};

export default RoleBasedComponent;