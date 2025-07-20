/ frontend/src/utils/auth.ts
import { User } from '@/types/auth';

/**
 * 检查用户是否有指定角色
 */
export const hasRole = (user: User | null, role: string): boolean => {
  if (!user) return false;
  return user.roles.includes(role);
};

/**
 * 检查用户是否有指定权限
 */
export const hasPermission = (user: User | null, permission: string): boolean => {
  if (!user) return false;
  return user.permissions.includes(permission);
};

/**
 * 检查用户是否有任一角色
 */
export const hasAnyRole = (user: User | null, roles: string[]): boolean => {
  if (!user) return false;
  return roles.some(role => user.roles.includes(role));
};

/**
 * 检查用户是否有任一权限
 */
export const hasAnyPermission = (user: User | null, permissions: string[]): boolean => {
  if (!user) return false;
  return permissions.some(permission => user.permissions.includes(permission));
};

/**
 * 获取用户主要角色（用于界面显示）
 */
export const getPrimaryRole = (user: User | null): string => {
  if (!user || user.roles.length === 0) return 'guest';
  
  // 按优先级返回角色
  const rolePriority = ['admin', 'teacher', 'parent', 'student'];
  for (const role of rolePriority) {
    if (user.roles.includes(role)) {
      return role;
    }
  }
  
  return user.roles[0];
};

/**
 * 获取角色显示名称
 */
export const getRoleDisplayName = (role: string): string => {
  const roleNames: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
    parent: '家长',
  };
  
  return roleNames[role] || role;
};