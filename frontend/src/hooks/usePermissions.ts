// frontend/src/hooks/usePermissions.ts
import { useAuth } from './useAuth';

/**
 * 权限管理Hook
 */
export const usePermissions = () => {
  const { user, hasRole, hasPermission, hasAnyRole, hasAnyPermission } = useAuth();

  /**
   * 检查是否可以访问路由
   */
  const canAccessRoute = (path: string): boolean => {
    // 这里可以根据路径匹配对应的权限要求
    const routePermissions: Record<string, { roles?: string[]; permissions?: string[] }> = {
      '/admin': { roles: ['admin'] },
      '/admin/users': { permissions: ['user:manage'] },
      '/admin/system': { permissions: ['system:config'] },
      '/teacher': { roles: ['teacher'] },
      '/student': { roles: ['student'] },
      '/parent': { roles: ['parent'] },
    };

    const requirement = routePermissions[path];
    if (!requirement) return true;

    if (requirement.roles && !hasAnyRole(requirement.roles)) {
      return false;
    }

    if (requirement.permissions && !hasAnyPermission(requirement.permissions)) {
      return false;
    }

    return true;
  };

  /**
   * 获取用户可访问的菜单项
   */
  const getAccessibleMenus = () => {
    const allMenus = [
      {
        key: 'dashboard',
        label: '仪表盘',
        path: '/dashboard',
        icon: 'Dashboard',
      },
      {
        key: 'student',
        label: '学生功能',
        roles: ['student'],
        children: [
          { key: 'student-courses', label: '我的课程', path: '/student/courses' },
          { key: 'student-homework', label: '作业管理', path: '/student/homework' },
          { key: 'student-exams', label: '考试管理', path: '/student/exams' },
          { key: 'student-progress', label: '学习进度', path: '/student/progress' },
        ],
      },
      {
        key: 'teacher',
        label: '教师功能',
        roles: ['teacher'],
        children: [
          { key: 'teacher-classes', label: '班级管理', path: '/teacher/classes' },
          { key: 'teacher-homework', label: '作业管理', path: '/teacher/homework' },
          { key: 'teacher-exams', label: '考试管理', path: '/teacher/exams' },
          { key: 'teacher-analytics', label: '学情分析', path: '/teacher/analytics' },
        ],
      },
      {
        key: 'parent',
        label: '家长功能',
        roles: ['parent'],
        children: [
          { key: 'parent-children', label: '孩子管理', path: '/parent/children' },
          { key: 'parent-communication', label: '家校沟通', path: '/parent/communication' },
        ],
      },
      {
        key: 'admin',
        label: '系统管理',
        roles: ['admin'],
        children: [
          { 
            key: 'admin-users', 
            label: '用户管理', 
            path: '/admin/users',
            permissions: ['user:manage']
          },
          { 
            key: 'admin-system', 
            label: '系统配置', 
            path: '/admin/system',
            permissions: ['system:config']
          },
        ],
      },
    ];

    // 过滤用户可访问的菜单
    const filterMenus = (menus: any[]): any[] => {
      return menus.filter(menu => {
        // 检查角色权限
        if (menu.roles && !hasAnyRole(menu.roles)) {
          return false;
        }

        // 检查权限
        if (menu.permissions && !hasAnyPermission(menu.permissions)) {
          return false;
        }

        // 递归过滤子菜单
        if (menu.children) {
          menu.children = filterMenus(menu.children);
        }

        return true;
      });
    };

    return filterMenus(allMenus);
  };

  return {
    hasRole,
    hasPermission,
    hasAnyRole,
    hasAnyPermission,
    canAccessRoute,
    getAccessibleMenus,
    user,
  };
};