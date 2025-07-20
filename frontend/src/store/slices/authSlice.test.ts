import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createAuthSlice } from './authSlice';
import { authAPI } from '@/api/modules/auth';

// Mock the auth API
vi.mock('@/api/modules/auth', () => ({
  authAPI: {
    login: vi.fn(),
    logout: vi.fn(),
    getProfile: vi.fn(),
    refreshToken: vi.fn(),
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

describe('authSlice', () => {
  const mockAuthAPI = {
    login: vi.fn(),
    logout: vi.fn(),
    getProfile: vi.fn(),
    refreshToken: vi.fn(),
  };

  const mockStorage = {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
    clear: vi.fn(),
  };

  let set: any;
  let get: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    set = vi.fn();
    get = vi.fn();
    
    vi.doMock('@/api/modules/auth', () => ({
      authAPI: mockAuthAPI,
    }));
    
    vi.doMock('@/utils/storage', () => ({
      storage: mockStorage,
    }));
  });

  describe('initial state', () => {
    it('has correct initial state', () => {
      const slice = createAuthSlice(set, get);
      
      expect(slice.user).toBe(null);
      expect(slice.isAuthenticated).toBe(false);
      expect(slice.token).toBe(null);
      expect(slice.refreshToken).toBe(null);
      expect(slice.loading).toBe(false);
      expect(slice.permissions).toEqual([]);
    });
  });

  describe('login', () => {
    it('successfully logs in user', async () => {
      const credentials = {
        username: 'testuser',
        password: 'password123',
        rememberMe: false,
      };

      const mockResponse = {
        data: {
          user: { id: 1, username: 'testuser', roles: ['student'] },
          token: 'mock-token',
          refreshToken: 'mock-refresh-token',
          permissions: ['read', 'write'],
        },
      };

      mockAuthAPI.login.mockResolvedValue(mockResponse);

      const slice = createAuthSlice(set, get);
      await slice.login(credentials);

      expect(mockAuthAPI.login).toHaveBeenCalledWith(credentials);
      expect(mockStorage.set).toHaveBeenCalledWith('token', 'mock-token');
      expect(mockStorage.set).toHaveBeenCalledWith('refreshToken', 'mock-refresh-token');
      expect(set).toHaveBeenCalledWith({
        user: mockResponse.data.user,
        isAuthenticated: true,
        token: 'mock-token',
        refreshToken: 'mock-refresh-token',
        permissions: ['read', 'write'],
        loading: false,
      });
    });

    it('handles login error', async () => {
      const credentials = {
        username: 'testuser',
        password: 'wrongpassword',
        rememberMe: false,
      };

      const error = new Error('Invalid credentials');
      mockAuthAPI.login.mockRejectedValue(error);

      const slice = createAuthSlice(set, get);
      
      await expect(slice.login(credentials)).rejects.toThrow('Invalid credentials');
      
      expect(set).toHaveBeenCalledWith({ loading: false });
    });

    it('sets loading state during login', async () => {
      const credentials = {
        username: 'testuser',
        password: 'password123',
        rememberMe: false,
      };

      mockAuthAPI.login.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      const slice = createAuthSlice(set, get);
      const loginPromise = slice.login(credentials);

      expect(set).toHaveBeenCalledWith({ loading: true });

      await loginPromise;
    });
  });

  describe('logout', () => {
    it('successfully logs out user', async () => {
      mockAuthAPI.logout.mockResolvedValue({ data: null });

      const slice = createAuthSlice(set, get);
      await slice.logout();

      expect(mockAuthAPI.logout).toHaveBeenCalled();
      expect(mockStorage.clear).toHaveBeenCalled();
      expect(set).toHaveBeenCalledWith({
        user: null,
        isAuthenticated: false,
        token: null,
        refreshToken: null,
        permissions: [],
        loading: false,
      });
    });

    it('handles logout error gracefully', async () => {
      const error = new Error('Logout failed');
      mockAuthAPI.logout.mockRejectedValue(error);

      const slice = createAuthSlice(set, get);
      await slice.logout();

      // Should still clear local state even if API call fails
      expect(mockStorage.clear).toHaveBeenCalled();
      expect(set).toHaveBeenCalledWith({
        user: null,
        isAuthenticated: false,
        token: null,
        refreshToken: null,
        permissions: [],
        loading: false,
      });
    });
  });

  describe('getProfile', () => {
    it('successfully gets user profile', async () => {
      const mockResponse = {
        data: {
          user: { id: 1, username: 'testuser', roles: ['student'] },
        },
      };

      mockAuthAPI.getProfile.mockResolvedValue(mockResponse);

      const slice = createAuthSlice(set, get);
      await slice.getProfile();

      expect(mockAuthAPI.getProfile).toHaveBeenCalled();
      expect(set).toHaveBeenCalledWith({
        user: mockResponse.data.user,
        loading: false,
      });
    });

    it('handles get profile error', async () => {
      const error = new Error('Profile fetch failed');
      mockAuthAPI.getProfile.mockRejectedValue(error);

      const slice = createAuthSlice(set, get);
      
      await expect(slice.getProfile()).rejects.toThrow('Profile fetch failed');
      
      expect(set).toHaveBeenCalledWith({ loading: false });
    });
  });

  describe('refreshToken', () => {
    it('successfully refreshes token', async () => {
      const refreshToken = 'old-refresh-token';
      const mockResponse = {
        data: {
          token: 'new-token',
          refreshToken: 'new-refresh-token',
        },
      };

      mockAuthAPI.refreshToken.mockResolvedValue(mockResponse);

      const slice = createAuthSlice(set, get);
      await slice.refreshToken(refreshToken);

      expect(mockAuthAPI.refreshToken).toHaveBeenCalledWith(refreshToken);
      expect(mockStorage.set).toHaveBeenCalledWith('token', 'new-token');
      expect(mockStorage.set).toHaveBeenCalledWith('refreshToken', 'new-refresh-token');
      expect(set).toHaveBeenCalledWith({
        token: 'new-token',
        refreshToken: 'new-refresh-token',
        loading: false,
      });
    });

    it('handles refresh token error', async () => {
      const refreshToken = 'invalid-refresh-token';
      const error = new Error('Token refresh failed');
      mockAuthAPI.refreshToken.mockRejectedValue(error);

      const slice = createAuthSlice(set, get);
      
      await expect(slice.refreshToken(refreshToken)).rejects.toThrow('Token refresh failed');
      
      expect(set).toHaveBeenCalledWith({ loading: false });
    });
  });

  describe('initializeAuth', () => {
    it('initializes auth from storage', async () => {
      const storedToken = 'stored-token';
      const storedRefreshToken = 'stored-refresh-token';
      
      mockStorage.get.mockImplementation((key: string) => {
        if (key === 'token') return storedToken;
        if (key === 'refreshToken') return storedRefreshToken;
        return null;
      });

      const mockResponse = {
        data: {
          user: { id: 1, username: 'testuser', roles: ['student'] },
        },
      };

      mockAuthAPI.getProfile.mockResolvedValue(mockResponse);

      const slice = createAuthSlice(set, get);
      await slice.initializeAuth();

      expect(mockStorage.get).toHaveBeenCalledWith('token');
      expect(mockStorage.get).toHaveBeenCalledWith('refreshToken');
      expect(mockAuthAPI.getProfile).toHaveBeenCalled();
      expect(set).toHaveBeenCalledWith({
        user: mockResponse.data.user,
        isAuthenticated: true,
        token: storedToken,
        refreshToken: storedRefreshToken,
        loading: false,
      });
    });

    it('handles initialization when no token exists', async () => {
      mockStorage.get.mockReturnValue(null);

      const slice = createAuthSlice(set, get);
      await slice.initializeAuth();

      expect(mockAuthAPI.getProfile).not.toHaveBeenCalled();
      expect(set).toHaveBeenCalledWith({ loading: false });
    });

    it('handles profile fetch error during initialization', async () => {
      const storedToken = 'stored-token';
      mockStorage.get.mockReturnValue(storedToken);

      const error = new Error('Profile fetch failed');
      mockAuthAPI.getProfile.mockRejectedValue(error);

      const slice = createAuthSlice(set, get);
      await slice.initializeAuth();

      // Should clear invalid tokens
      expect(mockStorage.clear).toHaveBeenCalled();
      expect(set).toHaveBeenCalledWith({
        user: null,
        isAuthenticated: false,
        token: null,
        refreshToken: null,
        permissions: [],
        loading: false,
      });
    });
  });
}); 