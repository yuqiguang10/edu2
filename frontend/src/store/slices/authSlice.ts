import { StateCreator } from 'zustand';
import { authAPI } from '@/api/modules/auth';
import { storage } from '@/utils/storage';
import { APP_CONFIG } from '@/utils/constants';
import type { User, LoginCredentials, RegisterData } from '@/types';

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  permissions: string[];
  loading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
  initializeAuth: () => void;
}

export type AuthSlice = AuthState & AuthActions;

export const createAuthSlice: StateCreator<AuthSlice> = (set, get) => ({
  // 初始状态
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  permissions: [],
  loading: false,
  error: null,

  // 登录
  login: async (credentials) => {
    try {
      set({ loading: true, error: null });
      
      const response = await authAPI.login(credentials);
      const { user, token, refreshToken, permissions } = response.data;

      // 保存到本地存储
      storage.set(APP_CONFIG.TOKEN_KEY, token);
      storage.set(APP_CONFIG.REFRESH_TOKEN_KEY, refreshToken);
      storage.set(APP_CONFIG.USER_KEY, user);

      set({
        user,
        token,
        refreshToken,
        permissions,
        isAuthenticated: true,
        loading: false,
        error: null,
      });
    } catch (error: any) {
      set({
        loading: false,
        error: error.message || '登录失败',
      });
      throw error;
    }
  },

  // 注册
  register: async (data) => {
    try {
      set({ loading: true, error: null });
      
      await authAPI.register(data);
      
      set({ loading: false, error: null });
    } catch (error: any) {
      set({
        loading: false,
        error: error.message || '注册失败',
      });
      throw error;
    }
  },

  // 登出
  logout: () => {
    // 清除本地存储
    storage.remove(APP_CONFIG.TOKEN_KEY);
    storage.remove(APP_CONFIG.REFRESH_TOKEN_KEY);
    storage.remove(APP_CONFIG.USER_KEY);

    // 重置状态
    set({
      user: null,
      token: null,
      refreshToken: null,
      permissions: [],
      isAuthenticated: false,
      error: null,
    });

    // 调用API登出（可选，因为token已经清除）
    authAPI.logout().catch(console.error);
  },

  // 刷新认证信息
  refreshAuth: async () => {
    try {
      const refreshToken = get().refreshToken;
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await authAPI.refreshToken(refreshToken);
      const { token } = response.data;

      storage.set(APP_CONFIG.TOKEN_KEY, token);
      set({ token });
    } catch (error) {
      // 刷新失败，清除认证信息
      get().logout();
      throw error;
    }
  },

  // 更新用户信息
  updateProfile: async (data) => {
    try {
      set({ loading: true, error: null });
      
      const response = await authAPI.updateProfile(data);
      const updatedUser = response.data;

      storage.set(APP_CONFIG.USER_KEY, updatedUser);
      set({
        user: updatedUser,
        loading: false,
        error: null,
      });
    } catch (error: any) {
      set({
        loading: false,
        error: error.message || '更新失败',
      });
      throw error;
    }
  },

  // 清除错误
  clearError: () => {
    set({ error: null });
  },

  // 初始化认证状态（从本地存储恢复）
  initializeAuth: () => {
    const token = storage.get(APP_CONFIG.TOKEN_KEY);
    const refreshToken = storage.get(APP_CONFIG.REFRESH_TOKEN_KEY);
    const user = storage.get(APP_CONFIG.USER_KEY);

    if (token && user) {
      set({
        token,
        refreshToken,
        user,
        isAuthenticated: true,
      });
    }
  },
});