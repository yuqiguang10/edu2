import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Login from './Login';

// Mock the auth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

describe('Login', () => {
  const mockUseAuth = vi.fn();
  const mockNavigate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mocks
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: vi.fn(),
      loading: false,
    });
    
    vi.doMock('@/hooks/useAuth', () => ({
      useAuth: mockUseAuth,
    }));
    
    vi.doMock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
      };
    });
  });

  it('renders login form', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    expect(screen.getByText('登录')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('用户名或邮箱')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('密码')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /登录/i })).toBeInTheDocument();
  });

  it('allows user to input credentials', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const usernameInput = screen.getByPlaceholderText('用户名或邮箱');
    const passwordInput = screen.getByPlaceholderText('密码');
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(usernameInput).toHaveValue('testuser');
    expect(passwordInput).toHaveValue('password123');
  });

  it('shows validation errors for empty fields', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const loginButton = screen.getByRole('button', { name: /登录/i });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText('请输入用户名或邮箱')).toBeInTheDocument();
      expect(screen.getByText('请输入密码')).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid email', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const usernameInput = screen.getByPlaceholderText('用户名或邮箱');
    fireEvent.change(usernameInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(usernameInput);
    
    await waitFor(() => {
      expect(screen.getByText('请输入有效的邮箱地址')).toBeInTheDocument();
    });
  });

  it('calls login function with valid credentials', async () => {
    const mockLogin = vi.fn();
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: mockLogin,
      loading: false,
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const usernameInput = screen.getByPlaceholderText('用户名或邮箱');
    const passwordInput = screen.getByPlaceholderText('密码');
    const loginButton = screen.getByRole('button', { name: /登录/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
        rememberMe: false,
      });
    });
  });

  it('shows loading state during login', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: vi.fn(),
      loading: true,
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    expect(screen.getByText('登录中...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /登录中.../i })).toBeDisabled();
  });

  it('redirects to dashboard when already authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 1, username: 'testuser', roles: ['student'] },
      isAuthenticated: true,
      login: vi.fn(),
      loading: false,
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    expect(mockNavigate).toHaveBeenCalledWith('/student/dashboard');
  });

  it('toggles password visibility', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const passwordInput = screen.getByPlaceholderText('密码');
    const toggleButton = screen.getByRole('button', { name: /toggle password/i });
    
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('handles remember me checkbox', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const rememberMeCheckbox = screen.getByRole('checkbox', { name: /记住我/i });
    expect(rememberMeCheckbox).not.toBeChecked();
    
    fireEvent.click(rememberMeCheckbox);
    expect(rememberMeCheckbox).toBeChecked();
  });

  it('navigates to register page', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const registerLink = screen.getByText('还没有账号？立即注册');
    fireEvent.click(registerLink);
    
    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  it('navigates to forgot password page', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const forgotPasswordLink = screen.getByText('忘记密码？');
    fireEvent.click(forgotPasswordLink);
    
    expect(mockNavigate).toHaveBeenCalledWith('/forgot-password');
  });

  it('displays error message from login failure', async () => {
    const mockLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'));
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: mockLogin,
      loading: false,
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    const usernameInput = screen.getByPlaceholderText('用户名或邮箱');
    const passwordInput = screen.getByPlaceholderText('密码');
    const loginButton = screen.getByRole('button', { name: /登录/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText('用户名或密码错误')).toBeInTheDocument();
    });
  });
}); 