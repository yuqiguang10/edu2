import { request } from '../request';
import { API_ENDPOINTS } from '@/utils/constants';
import type { 
  LoginCredentials, 
  RegisterData, 
  User, 
  ApiResponse 
} from '@/types';

export interface LoginResponse {
  user: User;
  token: string;
  refreshToken: string;
  permissions: string[];
}

export const authAPI = {
  // 用户登录
  login: (credentials: LoginCredentials): Promise<ApiResponse<LoginResponse>> =>
    request.post(API_ENDPOINTS.AUTH.LOGIN, credentials),

  // 用户注册
  register: (data: RegisterData): Promise<ApiResponse<User>> =>
    request.post(API_ENDPOINTS.AUTH.REGISTER, data),

  // 登出
  logout: (): Promise<ApiResponse<void>> =>
    request.post(API_ENDPOINTS.AUTH.LOGOUT),

  // 刷新token
  refreshToken: (refreshToken: string): Promise<ApiResponse<{ token: string }>> =>
    request.post(API_ENDPOINTS.AUTH.REFRESH, { refreshToken }),

  // 获取用户信息
  getProfile: (): Promise<ApiResponse<User>> =>
    request.get(API_ENDPOINTS.AUTH.PROFILE),

  // 更新用户信息
  updateProfile: (data: Partial<User>): Promise<ApiResponse<User>> =>
    request.patch(API_ENDPOINTS.AUTH.PROFILE, data),
};