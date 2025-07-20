// frontend/src/router/index.tsx
import React, { Suspense } from 'react';
import { 
  createBrowserRouter, 
  RouterProvider, 
  Navigate,
  Outlet 
} from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { checkRouteAccess } from './guards';
import { routes } from './routes';
import { Loading } from '@/components/common';
import { MainLayout } from '@/components/layout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

// 路由守卫组件
const GuardedRoute: React.FC<{
  component: React.ComponentType<any>;
  guard?: any;
}> = ({ component: Component, guard }) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!guard) {
    return <Component />;
  }

  const { hasAccess, redirect } = checkRouteAccess(user, guard);
  
  if (!hasAccess && redirect) {
    return <Navigate to={redirect} replace />;
  }

  return (
    <ProtectedRoute
      roles={guard.roles}
      permissions={guard.permissions}
      requireAuth={guard.requireAuth}
    >
      <Component />
    </ProtectedRoute>
  );
};

// 创建路由配置
const createAppRouter = () => {
  return createBrowserRouter([
    // 认证路由（不需要布局）
    {
      path: '/login',
      element: (
        <Suspense fallback={<Loading />}>
          <GuardedRoute 
            component={routes.find(r => r.path === '/login')!.component}
            guard={routes.find(r => r.path === '/login')!.guard}
          />
        </Suspense>
      )
    },
    {
      path: '/register',
      element: (
        <Suspense fallback={<Loading />}>
          <GuardedRoute 
            component={routes.find(r => r.path === '/register')!.component}
            guard={routes.find(r => r.path === '/register')!.guard}
          />
        </Suspense>
      )
    },
    {
      path: '/forgot-password',
      element: (
        <Suspense fallback={<Loading />}>
          <GuardedRoute 
            component={routes.find(r => r.path === '/forgot-password')!.component}
            guard={routes.find(r => r.path === '/forgot-password')!.guard}
          />
        </Suspense>
      )
    },
    {
      path: '/reset-password',
      element: (
        <Suspense fallback={<Loading />}>
          <GuardedRoute 
            component={routes.find(r => r.path === '/reset-password')!.component}
            guard={routes.find(r => r.path === '/reset-password')!.guard}
          />
        </Suspense>
      )
    },

    // 主应用路由（需要布局）
    {
      path: '/',
      element: <MainLayout />,
      children: [
        // 根路径重定向
        {
          path: '',
          element: <Navigate to="/dashboard" replace />
        },
        
        // 仪表盘重定向
        {
          path: 'dashboard',
          element: <DashboardRedirect />
        },

        // 教师路由
        {
          path: 'teacher/*',
          element: (
            <ProtectedRoute roles={['teacher']}>
              <Outlet />
            </ProtectedRoute>
          ),
          children: [
            {
              path: 'dashboard',
              element: (
                <Suspense fallback={<Loading />}>
                  <GuardedRoute 
                    component={routes.find(r => r.path === '/teacher')!.component}
                    guard={routes.find(r => r.path === '/teacher')!.guard}
                  />
                </Suspense>
              )
            }
            // ... 其他教师路由
          ]
        },

        // 家长路由
        {
          path: 'parent/*',
          element: (
            <ProtectedRoute roles={['parent']}>
              <Outlet />
            </ProtectedRoute>
          ),
          children: [
            {
              path: 'dashboard',
              element: (
                <Suspense fallback={<Loading />}>
                  <GuardedRoute 
                    component={routes.find(r => r.path === '/parent')!.component}
                    guard={routes.find(r => r.path === '/parent')!.guard}
                  />
                </Suspense>
              )
            }
            // ... 其他家长路由
          ]
        },

        // 管理员路由
        {
          path: 'admin/*',
          element: (
            <ProtectedRoute roles={['admin']}>
              <Outlet />
            </ProtectedRoute>
          ),
          children: [
            {
              path: 'dashboard',
              element: (
                <Suspense fallback={<Loading />}>
                  <GuardedRoute 
                    component={routes.find(r => r.path === '/admin')!.component}
                    guard={routes.find(r => r.path === '/admin')!.guard}
                  />
                </Suspense>
              )
            },
            {
              path: 'users',
              element: (
                <Suspense fallback={<Loading />}>
                  <ProtectedRoute permissions={['user:manage']}>
                    <GuardedRoute 
                      component={routes.find(r => r.path === '/admin/users')!.component}
                    />
                  </ProtectedRoute>
                </Suspense>
              )
            }
            // ... 其他管理员路由
          ]
        },

        // 公共路由
        {
          path: 'profile',
          element: (
            <Suspense fallback={<Loading />}>
              <ProtectedRoute>
                <GuardedRoute 
                  component={routes.find(r => r.path === '/profile')!.component}
                />
              </ProtectedRoute>
            </Suspense>
          )
        },
        {
          path: 'settings',
          element: (
            <Suspense fallback={<Loading />}>
              <ProtectedRoute>
                <GuardedRoute 
                  component={routes.find(r => r.path === '/settings')!.component}
                />
              </ProtectedRoute>
            </Suspense>
          )
        }
      ]
    },

    // 错误页面
    {
      path: '/403',
      element: (
        <Suspense fallback={<Loading />}>
          <GuardedRoute 
            component={routes.find(r => r.path === '/403')!.component}
            guard={routes.find(r => r.path === '/403')!.guard}
          />
        </Suspense>
      )
    },
    {
      path: '*',
      element: (
        <Suspense fallback={<Loading />}>
          <GuardedRoute 
            component={routes.find(r => r.path === '*')!.component}
            guard={routes.find(r => r.path === '*')!.guard}
          />
        </Suspense>
      )
    }
  ]);
};

// 仪表盘重定向组件
const DashboardRedirect: React.FC = () => {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // 根据用户角色重定向到对应的仪表盘
  const primaryRole = user.roles[0];
  const dashboardMap: Record<string, string> = {
    admin: '/admin/dashboard',
    teacher: '/teacher/dashboard',
    student: '/student/dashboard',
    parent: '/parent/dashboard',
  };

  const redirectPath = dashboardMap[primaryRole] || '/student/dashboard';
  return <Navigate to={redirectPath} replace />;
};

// 路由提供者组件
const AppRouter: React.FC = () => {
  const router = createAppRouter();
  return <RouterProvider router={router} />;
};

export default AppRouter;