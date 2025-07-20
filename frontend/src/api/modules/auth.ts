// frontend/src/api/modules/auth.ts
import { request } from '@/api/request';
import type {
  LoginCredentials,
  LoginResponse,
  RegisterData,
  User,
  PasswordChangeData,
  PasswordResetData,
  PasswordResetConfirm,
} from '@/types/auth';

export const authAPI = {
  /**
   * 用户登录
   */
  login: (credentials: LoginCredentials) =>
    request.post<LoginResponse>('/auth/login', credentials),

  /**
   * 用户注册
   */
  register: (data: RegisterData) =>
    request.post<User>('/auth/register', data),

  /**
   * 刷新令牌
   */
  refreshToken: (refreshToken: string) =>
    request.post<{ access_token: string; expires_in: number }>('/auth/refresh', {
      refresh_token: refreshToken,
    }),

  /**
   * 用户登出
   */
  logout: () => request.post('/auth/logout'),

  /**
   * 获取用户资料
   */
  getProfile: () => request.get<User>('/auth/profile'),

  /**
   * 更新用户资料
   */
  updateProfile: (data: Partial<User>) =>
    request.put<User>('/auth/profile', data),

  /**
   * 修改密码
   */
  changePassword: (data: PasswordChangeData) =>
    request.post('/auth/change-password', data),

  /**
   * 忘记密码
   */
  forgotPassword: (data: PasswordResetData) =>
    request.post('/auth/forgot-password', data),

  /**
   * 重置密码
   */
  resetPassword: (data: PasswordResetConfirm) =>
    request.post('/auth/reset-password', data),
};