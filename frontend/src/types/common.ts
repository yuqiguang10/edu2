// src/types/common.ts
export interface BaseEntity {
  id: number | string;
  createdAt: string;
  updatedAt?: string;
}

export interface PaginationParams {
  page: number;
  pageSize: number;
}

export interface PaginationResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  code?: number;
}

export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

export type UserRole = 'student' | 'teacher' | 'parent' | 'admin';
export type ExamStatus = 'draft' | 'published' | 'ongoing' | 'completed' | 'cancelled';
export type HomeworkStatus = 'assigned' | 'submitted' | 'graded';

// 表格列定义
export interface Column<T = any> {
  key: string;
  title: string;
  dataIndex?: keyof T;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, record: T, index: number) => any;
  sorter?: boolean | ((a: T, b: T) => number);
  filterable?: boolean;
  fixed?: 'left' | 'right';
  ellipsis?: boolean;
}
