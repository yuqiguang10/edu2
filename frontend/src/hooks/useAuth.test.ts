import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useAuth } from './useAuth';

// Mock the store
vi.mock('@/store', () => ({
  useStore: vi.fn(),
}));

// Mock the API
vi.mock('@/api/modules/auth', () => ({
  authAPI: {
    login: vi.fn(),
    logout: vi.fn(),
    getProfile: vi.fn(),
  },
}));

// Mock storage
vi.mock('@/utils/storage', () => ({
  storage: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
    clear: vi.fn(),
  },
}));

describe('useAuth', () => {
  const mockUseStore = vi.fn();
  const mockAuthAPI = {
    login: vi.fn(),
    logout: vi.fn(),
    getProfile: vi.fn(),
  };
  const mockStorage = {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
    clear: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mock values
    mockUseStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    vi.doMock('@/store', () => ({
      useStore: mockUseStore,
    }));
    
    vi.doMock('@/api/modules/auth', () => ({
      authAPI: mockAuthAPI,
    }));
    
    vi.doMock('@/utils/storage', () => ({
      storage: mockStorage,
    }));
  });

  it('should return auth state', () => {
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(typeof result.current.login).toBe('function');
    expect(typeof result.current.logout).toBe('function');
  });

  it('should return authenticated state when user exists', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      roles: ['student'],
    };
    
    mockUseStore.mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
  });

  it('should check if user has specific role', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      roles: ['student', 'teacher'],
    };
    
    mockUseStore.mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.hasRole('student')).toBe(true);
    expect(result.current.hasRole('teacher')).toBe(true);
    expect(result.current.hasRole('admin')).toBe(false);
  });

  it('should check if user has any of the specified roles', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      roles: ['student'],
    };
    
    mockUseStore.mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.hasAnyRole(['student', 'teacher'])).toBe(true);
    expect(result.current.hasAnyRole(['admin', 'teacher'])).toBe(false);
  });

  it('should return loading state', () => {
    mockUseStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      loading: true,
      login: vi.fn(),
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.loading).toBe(true);
  });

  it('should handle login function', async () => {
    const mockLogin = vi.fn();
    mockUseStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: mockLogin,
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    const credentials = {
      username: 'testuser',
      password: 'password123',
    };
    
    await act(async () => {
      await result.current.login(credentials);
    });
    
    expect(mockLogin).toHaveBeenCalledWith(credentials);
  });

  it('should handle logout function', async () => {
    const mockLogout = vi.fn();
    mockUseStore.mockReturnValue({
      user: { id: 1, username: 'testuser' },
      isAuthenticated: true,
      login: vi.fn(),
      logout: mockLogout,
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.logout();
    });
    
    expect(mockLogout).toHaveBeenCalled();
  });

  it('should return user roles', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      roles: ['student', 'teacher'],
    };
    
    mockUseStore.mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.userRoles).toEqual(['student', 'teacher']);
  });

  it('should return empty roles when user is null', () => {
    mockUseStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
      setUser: vi.fn(),
    });
    
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.userRoles).toEqual([]);
  });
}); 