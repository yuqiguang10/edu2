import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';
import { storage } from '@/utils/storage';
import { APP_CONFIG, ERROR_MESSAGES } from '@/utils/constants';

// 创建axios实例
const createAxiosInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: APP_CONFIG.API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器
  instance.interceptors.request.use(
    (config) => {
      // 添加认证token
      const token = storage.get(APP_CONFIG.TOKEN_KEY);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // 添加请求时间戳
      config.metadata = { startTime: Date.now() };
      
      // 开发环境下打印请求信息
      if (import.meta.env.DEV) {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
      }

      return config;
    },
    (error) => {
      console.error('请求拦截器错误:', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      // 计算请求耗时
      const duration = Date.now() - response.config.metadata?.startTime;
      
      // 开发环境下打印响应信息
      if (import.meta.env.DEV) {
        console.log(`✅ API Response: ${response.config.url} (${duration}ms)`, response.data);
      }

      // 处理业务错误
      if (response.data && !response.data.success) {
        const errorMessage = response.data.message || ERROR_MESSAGES.UNKNOWN_ERROR;
        toast.error(errorMessage);
        return Promise.reject(new Error(errorMessage));
      }

      return response.data;
    },
    (error) => {
      // 网络错误或HTTP错误
      let errorMessage = ERROR_MESSAGES.UNKNOWN_ERROR;

      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage = ERROR_MESSAGES.TIMEOUT_ERROR;
      } else if (!error.response) {
        errorMessage = ERROR_MESSAGES.NETWORK_ERROR;
      } else {
        const { status, data } = error.response;
        
        switch (status) {
          case 401:
            errorMessage = ERROR_MESSAGES.UNAUTHORIZED;
            // 清除本地认证信息并跳转到登录页
            storage.remove(APP_CONFIG.TOKEN_KEY);
            storage.remove(APP_CONFIG.USER_KEY);
            window.location.href = '/login';
            break;
          case 403:
            errorMessage = ERROR_MESSAGES.FORBIDDEN;
            break;
          case 404:
            errorMessage = ERROR_MESSAGES.NOT_FOUND;
            break;
          case 422:
            errorMessage = data?.message || ERROR_MESSAGES.VALIDATION_ERROR;
            break;
          case 500:
            errorMessage = ERROR_MESSAGES.SERVER_ERROR;
            break;
          default:
            errorMessage = data?.message || ERROR_MESSAGES.UNKNOWN_ERROR;
        }
      }

      console.error('API错误:', error);
      toast.error(errorMessage);
      return Promise.reject(error);
    }
  );

  return instance;
};

export const apiClient = createAxiosInstance();

// 请求方法封装
export const request = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) => 
    apiClient.get<T>(url, config),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.post<T>(url, data, config),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.put<T>(url, data, config),
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.patch<T>(url, data, config),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig) => 
    apiClient.delete<T>(url, config),
};