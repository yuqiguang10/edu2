// src/components/layout/Sidebar.tsx
import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Home, BookOpen, FileText, Award, TrendingUp, AlertCircle,
  Book, Users, BarChart3, Brain, MessageSquare, Calendar,
  Settings
} from 'lucide-react';
import { cn } from '@/utils/helpers';
import { ROUTES } from '@/utils/constants';
import type { UserRole } from '@/types';

interface SidebarProps {
  currentRole: UserRole;
  collapsed: boolean;
}

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ElementType;
  href: string;
  badge?: number;
}

const Sidebar: React.FC<SidebarProps> = ({ currentRole, collapsed }) => {
  const location = useLocation();

  const navigationItems: Record<UserRole, NavigationItem[]> = {
    student: [
      { id: 'dashboard', label: '学习首页', icon: Home, href: ROUTES.STUDENT.DASHBOARD },
      { id: 'courses', label: '我的课程', icon: BookOpen, href: ROUTES.STUDENT.COURSES },
      { id: 'homework', label: '作业练习', icon: FileText, href: ROUTES.STUDENT.HOMEWORK, badge: 3 },
      { id: 'exams', label: '考试测评', icon: Award, href: ROUTES.STUDENT.EXAMS },
      { id: 'progress', label: '学���分析', icon: TrendingUp, href: ROUTES.STUDENT.PROGRESS },
      { id: 'mistakes', label: '错题本', icon: AlertCircle, href: ROUTES.STUDENT.MISTAKES },
      { id: 'resources', label: '学习资源', icon: Book, href: ROUTES.STUDENT.RESOURCES },
    ],
    teacher: [
      { id: 'dashboard', label: '教学首页', icon: Home, href: ROUTES.TEACHER.DASHBOARD },
      { id: 'classes', label: '班级管理', icon: Users, href: ROUTES.TEACHER.CLASSES },
      { id: 'homework', label: '作业管理', icon: FileText, href: ROUTES.TEACHER.HOMEWORK, badge: 5 },
      { id: 'exams', label: '考试管理', icon: Award, href: ROUTES.TEACHER.EXAMS },
      { id: 'analytics', label: '学情分析', icon: BarChart3, href: ROUTES.TEACHER.ANALYTICS },
      { id: 'resources', label: '教学资源', icon: Book, href: ROUTES.TEACHER.RESOURCES },
      { id: 'ai-assistant', label: 'AI助手', icon: Brain, href: ROUTES.TEACHER.AI_ASSISTANT },
    ],
    parent: [
      { id: 'dashboard', label: '监督首页', icon: Home, href: ROUTES.PARENT.DASHBOARD },
      { id: 'child-progress', label: '孩子表现', icon: TrendingUp, href: ROUTES.PARENT.CHILD_PROGRESS },
      { id: 'communication', label: '家校沟通', icon: MessageSquare, href: ROUTES.PARENT.COMMUNICATION, badge: 2 },
      { id: 'schedule', label: '学习计划', icon: Calendar, href: ROUTES.PARENT.SCHEDULE },
      { id: 'reports', label: '学习报告', icon: FileText, href: ROUTES.PARENT.REPORTS },
    ],
    admin: [
      { id: 'dashboard', label: '管理首页', icon: Home, href: ROUTES.ADMIN.DASHBOARD },
      { id: 'users', label: '用户管理', icon: Users, href: ROUTES.ADMIN.USERS },
      { id: 'system', label: '系统管理', icon: Settings, href: ROUTES.ADMIN.SYSTEM },
      { id: 'analytics', label: '数据分析', icon: BarChart3, href: ROUTES.ADMIN.ANALYTICS },
      { id: 'resources', label: '资源管理', icon: Book, href: ROUTES.ADMIN.RESOURCES },
    ],
  };

  const items = navigationItems[currentRole] || [];

  return (
    <aside
      className={cn(
        'fixed left-0 top-16 h-[calc(100vh-64px)] bg-white border-r border-gray-200 transition-all duration-300 z-40',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <nav className="h-full overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {items.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            
            return (
              <li key={item.id}>
                <NavLink
                  to={item.href}
                  className={({ isActive: linkIsActive }) =>
                    cn(
                      'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                      'hover:bg-gray-100 hover:text-gray-900',
                      (isActive || linkIsActive) && 'bg-primary-50 text-primary-700 border-r-2 border-primary-700',
                      !isActive && !linkIsActive && 'text-gray-600',
                      collapsed && 'justify-center'
                    )
                  }
                  title={collapsed ? item.label : undefined}
                >
                  <Icon size={20} className={cn('flex-shrink-0', !collapsed && 'mr-3')} />
                  
                  {!collapsed && (
                    <>
                      <span className="flex-1">{item.label}</span>
                      {item.badge && (
                        <span className="ml-2 bg-red-100 text-red-600 text-xs font-medium px-2 py-1 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                  
                  {collapsed && item.badge && (
                    <span className="absolute left-8 top-1 bg-red-500 text-white text-xs font-medium px-1.5 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
