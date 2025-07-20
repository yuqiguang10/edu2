import { StateCreator } from 'zustand';
import type { UserRole } from '@/types';

export interface AppState {
  currentRole: UserRole;
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
  loading: boolean;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
  read: boolean;
}

export interface AppActions {
  setCurrentRole: (role: UserRole) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  markNotificationAsRead: (id: string) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  setLoading: (loading: boolean) => void;
}

export type AppSlice = AppState & AppActions;

export const createAppSlice: StateCreator<AppSlice> = (set, get) => ({
  // 初始状态
  currentRole: 'student',
  sidebarCollapsed: false,
  theme: 'light',
  notifications: [],
  loading: false,

  // 设置当前角色
  setCurrentRole: (role) => {
    set({ currentRole: role });
  },

  // 切换侧边栏
  toggleSidebar: () => {
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },

  // 设置侧边栏状态
  setSidebarCollapsed: (collapsed) => {
    set({ sidebarCollapsed: collapsed });
  },

  // 设置主题
  setTheme: (theme) => {
    set({ theme });
    document.documentElement.classList.toggle('dark', theme === 'dark');
  },

  // 添加通知
  addNotification: (notification) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      read: false,
    };
    
    set((state) => ({
      notifications: [newNotification, ...state.notifications],
    }));
  },

  // 标记通知为已读
  markNotificationAsRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      ),
    }));
  },

  // 删除通知
  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter(notification => notification.id !== id),
    }));
  },

  // 清空通知
  clearNotifications: () => {
    set({ notifications: [] });
  },

  // 设置加载状态
  setLoading: (loading) => {
    set({ loading });
  },
});