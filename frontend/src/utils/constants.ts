// src/utils/constants.ts
export const APP_CONFIG = {
  APP_NAME: 'K12智能教育平台',
  VERSION: '1.0.0',
  API_TIMEOUT: 30000,
  TOKEN_KEY: 'edu_token',
  REFRESH_TOKEN_KEY: 'edu_refresh_token',
  USER_KEY: 'edu_user',
} as const;

export const ROUTES = {
  // 公共路由
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  
  // 学生路由
  STUDENT: {
    DASHBOARD: '/student/dashboard',
    COURSES: '/student/courses',
    HOMEWORK: '/student/homework',
    EXAMS: '/student/exams',
    PROGRESS: '/student/progress',
    MISTAKES: '/student/mistakes',
    RESOURCES: '/student/resources',
  },
  
  // 教师路由
  TEACHER: {
    DASHBOARD: '/teacher/dashboard',
    CLASSES: '/teacher/classes',
    HOMEWORK: '/teacher/homework',
    EXAMS: '/teacher/exams',
    ANALYTICS: '/teacher/analytics',
    RESOURCES: '/teacher/resources',
    AI_ASSISTANT: '/teacher/ai-assistant',
  },
  
  // 家长路由
  PARENT: {
    DASHBOARD: '/parent/dashboard',
    CHILD_PROGRESS: '/parent/child-progress',
    COMMUNICATION: '/parent/communication',
    SCHEDULE: '/parent/schedule',
    REPORTS: '/parent/reports',
  },
  
  // 管理员路由
  ADMIN: {
    DASHBOARD: '/admin/dashboard',
    USERS: '/admin/users',
    SYSTEM: '/admin/system',
    ANALYTICS: '/admin/analytics',
    RESOURCES: '/admin/resources',
  },
} as const;

export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    LOGOUT: '/api/v1/auth/logout',
    REGISTER: '/api/v1/auth/register',
    REFRESH: '/api/v1/auth/refresh',
    PROFILE: '/api/v1/auth/profile',
  },
  
  // 用户相关
  USERS: {
    LIST: '/api/v1/users',
    DETAIL: (id: number) => `/api/v1/users/${id}`,
    UPDATE: (id: number) => `/api/v1/users/${id}`,
    DELETE: (id: number) => `/api/v1/users/${id}`,
  },
  
  // 考试相关
  EXAMS: {
    LIST: '/api/v1/exams',
    CREATE: '/api/v1/exams',
    DETAIL: (id: number) => `/api/v1/exams/${id}`,
    UPDATE: (id: number) => `/api/v1/exams/${id}`,
    DELETE: (id: number) => `/api/v1/exams/${id}`,
    START: (id: number) => `/api/v1/exams/${id}/start`,
    SUBMIT: (id: number) => `/api/v1/exams/${id}/submit`,
    QUESTIONS: (id: number) => `/api/v1/exams/${id}/questions`,
  },
  
  // 题库相关
  QUESTIONS: {
    LIST: '/api/v1/questions',
    SEARCH: '/api/v1/questions/search',
    DETAIL: (id: number) => `/api/v1/questions/${id}`,
    RECOMMENDATIONS: '/api/v1/questions/recommendations',
  },
  
  // AI相关
  AI: {
    CHAT: '/api/v1/ai/chat',
    RECOMMENDATIONS: '/api/v1/ai/recommendations',
    ANALYSIS: '/api/v1/ai/analysis',
    GENERATE_EXAM: '/api/v1/ai/generate-exam',
  },
} as const;

export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT_ERROR: '请求超时，请稍后重试',
  SERVER_ERROR: '服务器错误，请稍后重试',
  UNAUTHORIZED: '登录已过期，请重新登录',
  FORBIDDEN: '权限不足，无法执行此操作',
  NOT_FOUND: '请求的资源不存在',
  VALIDATION_ERROR: '数据验证失败',
  UNKNOWN_ERROR: '未知错误，请联系管理员',
} as const;
