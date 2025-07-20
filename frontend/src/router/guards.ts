// frontend/src/router/guards.ts
import type { User } from '@/types/auth';

export interface RouteGuard {
  requireAuth?: boolean;
  roles?: string[];
  permissions?: string[];
  requireAll?: boolean;
  redirect?: string;
}

export const checkRouteAccess = (
  user: User | null,
  guard: RouteGuard
): { hasAccess: boolean; redirect?: string } => {
  const {
    requireAuth = true,
    roles = [],
    permissions = [],
    requireAll = false,
    redirect = '/login'
  } = guard;

  // 检查是否需要认证
  if (requireAuth && !user) {
    return { hasAccess: false, redirect };
  }

  // 如果不需要认证，直接允许访问
  if (!requireAuth) {
    return { hasAccess: true };
  }

  // 检查角色
  if (roles.length > 0) {
    const hasRole = requireAll
      ? roles.every(role => user?.roles.includes(role))
      : roles.some(role => user?.roles.includes(role));
    
    if (!hasRole) {
      return { hasAccess: false, redirect: '/403' };
    }
  }

  // 检查权限
  if (permissions.length > 0) {
    const hasPermission = requireAll
      ? permissions.every(permission => user?.permissions.includes(permission))
      : permissions.some(permission => user?.permissions.includes(permission));
    
    if (!hasPermission) {
      return { hasAccess: false, redirect: '/403' };
    }
  }

  return { hasAccess: true };
};