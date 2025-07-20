import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authAPI } from './auth';

// Mock the request module
vi.mock('@/api/request', () => ({
  request: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('authAPI', () => {
  const mockRequest = {
    post: vi.fn(),
    get: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.doMock('@/api/request', () => ({
      request: mockRequest,
    }));
  });

  describe('login', () => {
    it('calls login endpoint with credentials', async () => {
      const credentials = {
        username: 'testuser',
        password: 'password123',
        rememberMe: false,
      };

      const mockResponse = {
        data: {
          user: { id: 1, username: 'testuser' },
          token: 'mock-token',
          refreshToken: 'mock-refresh-token',
        },
      };

      mockRequest.post.mockResolvedValue(mockResponse);

      const result = await authAPI.login(credentials);

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/login', credentials);
      expect(result).toEqual(mockResponse);
    });

    it('handles login error', async () => {
      const credentials = {
        username: 'testuser',
        password: 'wrongpassword',
        rememberMe: false,
      };

      const error = new Error('Invalid credentials');
      mockRequest.post.mockRejectedValue(error);

      await expect(authAPI.login(credentials)).rejects.toThrow('Invalid credentials');
    });
  });

  describe('register', () => {
    it('calls register endpoint with user data', async () => {
      const userData = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123',
        confirmPassword: 'password123',
        realName: 'New User',
        role: 'student',
      };

      const mockResponse = {
        data: {
          user: { id: 2, username: 'newuser' },
        },
      };

      mockRequest.post.mockResolvedValue(mockResponse);

      const result = await authAPI.register(userData);

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/register', userData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('logout', () => {
    it('calls logout endpoint', async () => {
      const mockResponse = { data: null };
      mockRequest.post.mockResolvedValue(mockResponse);

      const result = await authAPI.logout();

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/logout');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getProfile', () => {
    it('calls get profile endpoint', async () => {
      const mockResponse = {
        data: {
          user: { id: 1, username: 'testuser', email: 'test@example.com' },
        },
      };

      mockRequest.get.mockResolvedValue(mockResponse);

      const result = await authAPI.getProfile();

      expect(mockRequest.get).toHaveBeenCalledWith('/auth/profile');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('refreshToken', () => {
    it('calls refresh token endpoint', async () => {
      const refreshToken = 'mock-refresh-token';
      const mockResponse = {
        data: {
          token: 'new-token',
          refreshToken: 'new-refresh-token',
        },
      };

      mockRequest.post.mockResolvedValue(mockResponse);

      const result = await authAPI.refreshToken(refreshToken);

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/refresh', { refreshToken });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('changePassword', () => {
    it('calls change password endpoint', async () => {
      const passwordData = {
        oldPassword: 'oldpassword',
        newPassword: 'newpassword',
      };

      const mockResponse = { data: null };
      mockRequest.post.mockResolvedValue(mockResponse);

      const result = await authAPI.changePassword(passwordData);

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/change-password', passwordData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('forgotPassword', () => {
    it('calls forgot password endpoint', async () => {
      const email = 'test@example.com';
      const mockResponse = { data: null };
      mockRequest.post.mockResolvedValue(mockResponse);

      const result = await authAPI.forgotPassword(email);

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/forgot-password', { email });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('resetPassword', () => {
    it('calls reset password endpoint', async () => {
      const resetData = {
        token: 'reset-token',
        newPassword: 'newpassword',
      };

      const mockResponse = { data: null };
      mockRequest.post.mockResolvedValue(mockResponse);

      const result = await authAPI.resetPassword(resetData);

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/reset-password', resetData);
      expect(result).toEqual(mockResponse);
    });
  });
}); 