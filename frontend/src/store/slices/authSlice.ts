// frontend/src/store/slices/authSlice.ts
import { StateCreator } from 'zustand';
import { authAPI } from '@/api/modules/auth';
import { storage } from '@/utils/storage';
import { APP_CONFIG } from '@/utils/constants';
import toast from 'react-hot-toast';
import type { 
  User, 
  LoginCredentials, 
  RegisterData, 
  PasswordChangeData 
} from '@/types/auth';

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  permissions: string[];
  roles: string[];
  loading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  changePassword: (data: PasswordChangeData) => Promise<void>;
  clearError: () => void;
  initializeAuth: () => void;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
}

export type AuthSlice = AuthState & AuthActions;

export const createAuthSlice: StateCreator<AuthSlice> = (set, get) => ({
  // 初始状态
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  permissions: [],
  roles: [],
  loading: false,
  error: null,

  // 登录
  login: async (credentials) => {
    try {
      set({ loading: true, error: null });
      
      const response = await authAPI.login(credentials);
      const { user, access_token, refresh_token, permissions, roles } = response.data;

      // 保存到本地存储
      storage.set(APP_CONFIG.TOKEN_KEY, access_token);
      storage.set(APP_CONFIG.REFRESH_TOKEN_KEY, refresh_token);
      storage.set(APP_CONFIG.USER_KEY, user);

      set({
        user,
        token: access_token,
        refreshToken: refresh_token,
        permissions,
        roles,
        isAuthenticated: true,
        loading: false,
        error: null,
      });

      toast.success('登录成功');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '登录失败';
      set({
        loading: false,
        error: errorMessage,
      });
      toast.error(errorMessage);
      throw error;
    }
  },

  // 注册
  register: async (data) => {
    try {
      set({ loading: true, error: null });
      
      await authAPI.register(data);
      
      set({ loading: false, error: null });
      toast.success('注册成功，请登录');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '注册失败';
      set({
        loading: false,
        error: errorMessage,
      });
      toast.error(errorMessage);
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
      roles: [],
      isAuthenticated: false,
      error: null,
    });

    // 调用API登出
    authAPI.logout().catch(console.error);
    
    toast.success('已退出登录');
  },

  // 刷新认证信息
  refreshAuth: async () => {
    try {
      const refreshToken = get().refreshToken;
      if (!refreshToken) {
        throw new Error('No refresh token');
      }

      const response = await authAPI.refreshToken(refreshToken);
      const { access_token } = response.data;

      // 更新token
      storage.set(APP_CONFIG.TOKEN_KEY, access_token);
      set({ token: access_token });

      // 获取最新用户信息
      const profileResponse = await authAPI.getProfile();
      const user = profileResponse.data;

      storage.set(APP_CONFIG.USER_KEY, user);
      set({
        user,
        permissions: user.permissions,
        roles: user.roles,
        isAuthenticated: true,
      });
    } catch (error) {
      console.error('Token refresh failed:', error);
      get().logout();
    }
  },

  // 更新用户资料
  updateProfile: async (data) => {
    try {
      set({ loading: true, error: null });
      
      const response = await authAPI.updateProfile(data);
      const updatedUser = response.data;

      // 更新本地存储和状态
      storage.set(APP_CONFIG.USER_KEY, updatedUser);
      set({
        user: updatedUser,
        loading: false,
        error: null,
      });

      toast.success('资料更新成功');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '更新失败';
      set({
        loading: false,
        error: errorMessage,
      });
      toast.error(errorMessage);
      throw error;
    }
  },

  // 修改密码
  changePassword: async (data) => {
    try {
      set({ loading: true, error: null });
      
      await authAPI.changePassword(data);
      
      set({ loading: false, error: null });
      toast.success('密码修改成功');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '密码修改失败';
      set({
        loading: false,
        error: errorMessage,
      });
      toast.error(errorMessage);
      throw error;
    }
  },

  // 清除错误
  clearError: () => {
    set({ error: null });
  },

  // 初始化认证状态
  initializeAuth: () => {
    const token = storage.get(APP_CONFIG.TOKEN_KEY);
    const refreshToken = storage.get(APP_CONFIG.REFRESH_TOKEN_KEY);
    const user = storage.get(APP_CONFIG.USER_KEY);

    if (token && user) {
      set({
        user,
        token,
        refreshToken,
        permissions: user.permissions || [],
        roles: user.roles || [],
        isAuthenticated: true,
      });
    }
  },

  // 权限检查方法
  hasRole: (role: string) => {
    const { user } = get();
    return user?.roles.includes(role) || false;
  },

  hasPermission: (permission: string) => {
    const { user } = get();
    return user?.permissions.includes(permission) || false;
  },

  hasAnyRole: (roles: string[]) => {
    const { user } = get();
    if (!user) return false;
    return roles.some(role => user.roles.includes(role));
  },

  hasAnyPermission: (permissions: string[]) => {
    const { user } = get();
    if (!user) return false;
    return permissions.some(permission => user.permissions.includes(permission));
  },
});