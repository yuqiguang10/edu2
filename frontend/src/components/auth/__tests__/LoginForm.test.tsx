# frontend/src/components/auth/__tests__/LoginForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import LoginForm from '../LoginForm';
import { useAuth } from '@/hooks/useAuth';

// Mock useAuth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: null }),
  };
});

describe('LoginForm', () => {
  const mockLogin = vi.fn();
  const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;

  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      login: mockLogin,
      loading: false,
      error: null,
      user: null,
      isAuthenticated: false,
      permissions: [],
      roles: [],
      token: null,
      refreshToken: null,
      register: vi.fn(),
      logout: vi.fn(),
      refreshAuth: vi.fn(),
      updateProfile: vi.fn(),
      changePassword: vi.fn(),
      clearError: vi.fn(),
      initializeAuth: vi.fn(),
      hasRole: vi.fn(),
      hasPermission: vi.fn(),
      hasAnyRole: vi.fn(),
      hasAnyPermission: vi.fn(),
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  const renderLoginForm = () => {
    return render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );
  };

  it('renders login form correctly', () => {
    renderLoginForm();
    
    expect(screen.getByText('登录您的账户')).toBeInTheDocument();
    expect(screen.getByLabelText('用户名')).toBeInTheDocument();
    expect(screen.getByLabelText('密码')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    renderLoginForm();
    
    const submitButton = screen.getByRole('button', { name: '登录' });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('请输入用户名')).toBeInTheDocument();
      expect(screen.getByText('请输入密码')).toBeInTheDocument();
    });
  });

  it('calls login function with correct credentials', async () => {
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText('用户名');
    const passwordInput = screen.getByLabelText('密码');
    const submitButton = screen.getByRole('button', { name: '登录' });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('shows loading state during login', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      loading: true,
    });
    
    renderLoginForm();
    
    expect(screen.getByText('登录中...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录中...' })).toBeDisabled();
  });

  it('displays error message when login fails', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      error: '用户名或密码错误',
    });
    
    renderLoginForm();
    
    expect(screen.getByText('用户名或密码错误')).toBeInTheDocument();
  });

  it('toggles password visibility', () => {
    renderLoginForm();
    
    const passwordInput = screen.getByLabelText('密码');
    const toggleButton = screen.getByRole('button', { name: '' }); // Eye icon button
    
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
});