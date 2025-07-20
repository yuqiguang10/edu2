// src/utils/helpers.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO } from 'date-fns';
import { zhCN } from 'date-fns/locale';

/**
 * 合并 Tailwind CSS 类名
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 格式化日期
 */
export function formatDate(date: string | Date, pattern = 'yyyy-MM-dd'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, pattern, { locale: zhCN });
}

/**
 * 格式化日期时间
 */
export function formatDateTime(date: string | Date): string {
  return formatDate(date, 'yyyy-MM-dd HH:mm:ss');
}

/**
 * 格式化相对时间
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const targetDate = typeof date === 'string' ? parseISO(date) : date;
  const diffInMinutes = Math.floor((now.getTime() - targetDate.getTime()) / (1000 * 60));
  
  if (diffInMinutes < 1) return '刚刚';
  if (diffInMinutes < 60) return `${diffInMinutes}分钟前`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}小时前`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) return `${diffInDays}天前`;
  
  return formatDate(targetDate);
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * 生成随机ID
 */
export function generateId(length = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * 深拷贝对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as unknown as T;
  if (typeof obj === 'object') {
    const clonedObj = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
  return obj;
}

/**
 * 验证邮箱格式
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证手机号格式
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

/**
 * 获取用户角色中文名称
 */
export function getRoleLabel(role: UserRole): string {
  const roleLabels = {
    student: '学生',
    teacher: '教师',
    parent: '家长',
    admin: '管理员',
  };
  return roleLabels[role] || role;
}

/**
 * 获取考试状态中文名称
 */
export function getExamStatusLabel(status: ExamStatus): string {
  const statusLabels = {
    draft: '草稿',
    published: '已发布',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消',
  };
  return statusLabels[status] || status;
}

/**
 * 获取作业状态中文名称
 */
export function getHomeworkStatusLabel(status: HomeworkStatus): string {
  const statusLabels = {
    assigned: '已布置',
    submitted: '已提交',
    graded: '已批改',
  };
  return statusLabels[status] || status;
}

/**
 * 计算分数等级
 */
export function getScoreGrade(score: number): { grade: string; color: string } {
  if (score >= 90) return { grade: '优秀', color: 'text-green-600' };
  if (score >= 80) return { grade: '良好', color: 'text-blue-600' };
  if (score >= 70) return { grade: '中等', color: 'text-yellow-600' };
  if (score >= 60) return { grade: '及格', color: 'text-orange-600' };
  return { grade: '不及格', color: 'text-red-600' };
}
