// src/types/user.ts
export interface User extends BaseEntity {
  username: string;
  email: string;
  realName?: string;
  studentId?: string;
  phone?: string;
  avatar?: string;
  status: number;
  lastLogin?: string;
  roles: UserRole[];
}

export interface LoginCredentials {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  realName: string;
  phone?: string;
  role: UserRole;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  permissions: string[];
}
