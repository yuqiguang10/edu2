// frontend/src/router/routes.ts
import { lazy } from 'react';
import type { RouteGuard } from './guards';

// 懒加载组件
const LoginForm = lazy(() => import('@/pages/auth/Login'));
const RegisterForm = lazy(() => import('@/pages/auth/Register'));
const ForgotPassword = lazy(() => import('@/pages/auth/ForgotPassword'));
const ResetPassword = lazy(() => import('@/pages/auth/ResetPassword'));

const StudentDashboard = lazy(() => import('@/pages/student/Dashboard'));
const StudentCourses = lazy(() => import('@/pages/student/Courses'));
const StudentHomework = lazy(() => import('@/pages/student/Homework'));
const StudentExams = lazy(() => import('@/pages/student/Exams'));
const StudentProgress = lazy(() => import('@/pages/student/Progress'));

const TeacherDashboard = lazy(() => import('@/pages/teacher/Dashboard'));
const TeacherClasses = lazy(() => import('@/pages/teacher/Classes'));
const TeacherHomework = lazy(() => import('@/pages/teacher/Homework'));
const TeacherExams = lazy(() => import('@/pages/teacher/Exams'));
const TeacherAnalytics = lazy(() => import('@/pages/teacher/Analytics'));

const ParentDashboard = lazy(() => import('@/pages/parent/Dashboard'));
const ParentChildren = lazy(() => import('@/pages/parent/Children'));
const ParentCommunication = lazy(() => import('@/pages/parent/Communication'));

const AdminDashboard = lazy(() => import('@/pages/admin/Dashboard'));
const AdminUsers = lazy(() => import('@/pages/admin/Users'));
const AdminSystem = lazy(() => import('@/pages/admin/System'));

const Profile = lazy(() => import('@/pages/common/Profile'));
const Settings = lazy(() => import('@/pages/common/Settings'));
const NotFound = lazy(() => import('@/pages/common/NotFound'));
const Forbidden = lazy(() => import('@/pages/common/Forbidden'));

export interface RouteConfig {
  path: string;
  component: React.ComponentType<any>;
  guard?: RouteGuard;
  children?: RouteConfig[];
}

export const routes: RouteConfig[] = [
  // 认证相关路由（不需要登录）
  {
    path: '/login',
    component: LoginForm,
    guard: { requireAuth: false }
  },
  {
    path: '/register',
    component: RegisterForm,
    guard: { requireAuth: false }
  },
  {
    path: '/forgot-password',
    component: ForgotPassword,
    guard: { requireAuth: false }
  },
  {
    path: '/reset-password',
    component: ResetPassword,
    guard: { requireAuth: false }
  },

  // 学生路由
  {
    path: '/student',
    component: StudentDashboard,
    guard: { roles: ['student'] },
    children: [
      {
        path: '/student/dashboard',
        component: StudentDashboard,
        guard: { roles: ['student'] }
      },
      {
        path: '/student/courses',
        component: StudentCourses,
        guard: { roles: ['student'] }
      },
      {
        path: '/student/homework',
        component: StudentHomework,
        guard: { roles: ['student'] }
      },
      {
        path: '/student/exams',
        component: StudentExams,
        guard: { roles: ['student'] }
      },
      {
        path: '/student/progress',
        component: StudentProgress,
        guard: { roles: ['student'] }
      }
    ]
  },

  // 教师路由
  {
    path: '/teacher',
    component: TeacherDashboard,
    guard: { roles: ['teacher'] },
    children: [
      {
        path: '/teacher/dashboard',
        component: TeacherDashboard,
        guard: { roles: ['teacher'] }
      },
      {
        path: '/teacher/classes',
        component: TeacherClasses,
        guard: { roles: ['teacher'] }
      },
      {
        path: '/teacher/homework',
        component: TeacherHomework,
        guard: { roles: ['teacher'] }
      },
      {
        path: '/teacher/exams',
        component: TeacherExams,
        guard: { roles: ['teacher'] }
      },
      {
        path: '/teacher/analytics',
        component: TeacherAnalytics,
        guard: { roles: ['teacher'] }
      }
    ]
  },

  // 家长路由
  {
    path: '/parent',
    component: ParentDashboard,
    guard: { roles: ['parent'] },
    children: [
      {
        path: '/parent/dashboard',
        component: ParentDashboard,
        guard: { roles: ['parent'] }
      },
      {
        path: '/parent/children',
        component: ParentChildren,
        guard: { roles: ['parent'] }
      },
      {
        path: '/parent/communication',
        component: ParentCommunication,
        guard: { roles: ['parent'] }
      }
    ]
  },

  // 管理员路由
  {
    path: '/admin',
    component: AdminDashboard,
    guard: { roles: ['admin'] },
    children: [
      {
        path: '/admin/dashboard',
        component: AdminDashboard,
        guard: { roles: ['admin'] }
      },
      {
        path: '/admin/users',
        component: AdminUsers,
        guard: { permissions: ['user:manage'] }
      },
      {
        path: '/admin/system',
        component: AdminSystem,
        guard: { permissions: ['system:config'] }
      }
    ]
  },

  // 公共路由
  {
    path: '/profile',
    component: Profile,
    guard: { requireAuth: true }
  },
  {
    path: '/settings',
    component: Settings,
    guard: { requireAuth: true }
  },

  // 错误页面
  {
    path: '/403',
    component: Forbidden,
    guard: { requireAuth: false }
  },
  {
    path: '*',
    component: NotFound,
    guard: { requireAuth: false }
  }
];