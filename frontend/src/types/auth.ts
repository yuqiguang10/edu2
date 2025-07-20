// frontend/src/types/auth.ts
export interface User {
    id: number;
    username: string;
    email: string;
    real_name?: string;
    student_id?: string;
    phone?: string;
    avatar?: string;
    status: number;
    last_login?: string;
    created_at: string;
    roles: string[];
    permissions: string[];
  }
  
  export interface LoginCredentials {
    username: string;
    password: string;
  }
  
  export interface LoginResponse {
    user: User;
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
    roles: string[];
    permissions: string[];
  }
  
  export interface RegisterData {
    username: string;
    email: string;
    password: string;
    real_name?: string;
    phone?: string;
  }
  
  export interface PasswordChangeData {
    old_password: string;
    new_password: string;
  }
  
  export interface PasswordResetData {
    email: string;
  }
  
  export interface PasswordResetConfirm {
    token: string;
    new_password: string;
  }