import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import ProtectedRoute from '../ProtectedRoute';
import { useAuth } from '@/hooks/useAuth';

vi.mock('@/hooks/useAuth');

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;

describe('ProtectedRoute', () => {
  const TestComponent = () => <div>Protected Content</div>;

  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      hasAnyRole: vi.fn(),
      hasAnyPermission: vi.fn(),
      loading: false,
      user: { 
        id: 1, 
        username: 'test', 
        roles: ['student'], 
        permissions: [] 
      } as any,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshAuth: vi.fn(),
      updateProfile: vi.fn(),
      changePassword: vi.fn(),
      clearError: vi.fn(),
      initializeAuth: vi.fn(),
      hasRole: vi.fn(),
      hasPermission: vi.fn(),
      token: null,
      refreshToken: null,
      error: null,
    });
  });

  const renderProtectedRoute = (props = {}) => {
    return render(
      <BrowserRouter>
        <ProtectedRoute {...props}>
          <TestComponent />
        </ProtectedRoute>
      </BrowserRouter>
    );
  };

  it('renders children when authenticated and no role/permission requirements', () => {
    renderProtectedRoute();
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      isAuthenticated: false,
      user: null,
    });

    renderProtectedRoute();
    
    // Should redirect, so protected content should not be visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('shows access denied when user lacks required role', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      hasAnyRole: vi.fn().mockReturnValue(false),
    });

    renderProtectedRoute({ roles: ['admin'] });
    
    expect(screen.getByText('访问被拒绝')).toBeInTheDocument();
    expect(screen.getByText('需要角色：admin')).toBeInTheDocument();
  });

  it('shows permission denied when user lacks required permission', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      hasAnyRole: vi.fn().mockReturnValue(true),
      hasAnyPermission: vi.fn().mockReturnValue(false),
    });

    renderProtectedRoute({ 
      roles: ['admin'], 
      permissions: ['user:manage'] 
    });
    
    expect(screen.getByText('权限不足')).toBeInTheDocument();
    expect(screen.getByText('需要权限：user:manage')).toBeInTheDocument();
  });

  it('renders children when user has required roles and permissions', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      hasAnyRole: vi.fn().mockReturnValue(true),
      hasAnyPermission: vi.fn().mockReturnValue(true),
    });

    renderProtectedRoute({ 
      roles: ['admin'], 
      permissions: ['user:manage'] 
    });
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('shows loading state when authentication is loading', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      loading: true,
    });

    renderProtectedRoute();
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // Loading component
  });
});