import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';
import { useAuth } from '../useAuth';
import { authAPI } from '@/api/modules/auth';
import { storage } from '@/utils/storage';

// Mock dependencies
vi.mock('@/api/modules/auth');
vi.mock('@/utils/storage');
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock zustand store
const mockStore = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  permissions: [],
  roles: [],
  loading: false,
  error: null,
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
  hasAnyRole: vi.fn(),
  hasAnyPermission: vi.fn(),
};

vi.mock('@/store', () => ({
  useStore: vi.fn(() => mockStore),
}));

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes auth state correctly', () => {
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.loading).toBe(false);
  });

  it('calls login with correct credentials', async () => {
    const mockLoginResponse = {
      data: {
        user: { id: 1, username: 'testuser' },
        access_token: 'token123',
        refresh_token: 'refresh123',
        roles: ['student'],
        permissions: [],
      },
    };

    (authAPI.login as vi.Mock).mockResolvedValue(mockLoginResponse);
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login({
        username: 'testuser',
        password: 'password123',
      });
    });

    expect(authAPI.login).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });
  });

  it('handles login error correctly', async () => {
    const error = new Error('Login failed');
    (authAPI.login as vi.Mock).mockRejectedValue(error);
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      try {
        await result.current.login({
          username: 'testuser',
          password: 'wrongpassword',
        });
      } catch (e) {
        // Expected to throw
      }
    });

    expect(mockStore.login).toHaveBeenCalled();
  });

  it('checks roles correctly', () => {
    mockStore.hasRole.mockReturnValue(true);
    
    const { result } = renderHook(() => useAuth());
    
    const hasStudentRole = result.current.hasRole('student');
    expect(hasStudentRole).toBe(true);
    expect(mockStore.hasRole).toHaveBeenCalledWith('student');
  });

  it('checks permissions correctly', () => {
    mockStore.hasPermission.mockReturnValue(false);
    
    const { result } = renderHook(() => useAuth());
    
    const hasManagePermission = result.current.hasPermission('user:manage');
    expect(hasManagePermission).toBe(false);
    expect(mockStore.hasPermission).toHaveBeenCalledWith('user:manage');
  });
});