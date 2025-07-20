# backend/tests/conftest.py
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.core.security import get_password_hash

# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db() -> Generator:
    """创建测试数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    db = TestingSessionLocal()
    
    # 初始化测试数据
    setup_test_data(db)
    
    try:
        yield db
    finally:
        db.close()
        # 清理表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator:
    """创建测试客户端"""
    with TestClient(app) as c:
        yield c


def setup_test_data(db):
    """设置测试数据"""
    # 创建角色
    roles = [
        Role(name="admin", description="系统管理员"),
        Role(name="teacher", description="教师"),
        Role(name="student", description="学生"),
        Role(name="parent", description="家长")
    ]
    
    for role in roles:
        db.add(role)
    
    # 创建权限
    permissions = [
        Permission(name="用户管理", code="user:manage"),
        Permission(name="试题管理", code="question:manage"),
        Permission(name="考试管理", code="exam:manage")
    ]
    
    for permission in permissions:
        db.add(permission)
    
    db.commit()
    
    # 为管理员角色分配权限
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    for permission in permissions:
        role_permission = RolePermission(role_id=admin_role.id, permission_id=permission.id)
        db.add(role_permission)
    
    # 创建测试用户
    users = [
        {
            "username": "admin",
            "email": "admin@test.com",
            "password_hash": get_password_hash("admin123"),
            "real_name": "管理员",
            "status": 1,
            "role": "admin"
        },
        {
            "username": "teacher001",
            "email": "teacher@test.com", 
            "password_hash": get_password_hash("teacher123"),
            "real_name": "测试教师",
            "status": 1,
            "role": "teacher"
        },
        {
            "username": "student001",
            "email": "student@test.com",
            "password_hash": get_password_hash("student123"),
            "real_name": "测试学生",
            "status": 1,
            "role": "student"
        }
    ]
    
    for user_data in users:
        role_name = user_data.pop("role")
        user = User(**user_data)
        db.add(user)
        db.flush()
        
        # 分配角色
        role = db.query(Role).filter(Role.name == role_name).first()
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
    
    db.commit()


# backend/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.services.user_service import UserService
from app.schemas.auth import UserCreate, LoginRequest


class TestAuth:
    """认证相关测试"""
    
    def test_login_success(self, client: TestClient):
        """测试登录成功"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "student123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["username"] == "student001"
        assert "student" in data["data"]["roles"]
    
    def test_login_invalid_credentials(self, client: TestClient):
        """测试登录失败 - 无效凭据"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "wrong_password"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "用户名或密码错误" in data["message"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """测试登录失败 - 用户不存在"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        
        assert response.status_code == 401
    
    def test_register_success(self, client: TestClient):
        """测试注册成功"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newstudent",
                "email": "newstudent@test.com",
                "password": "password123",
                "real_name": "新学生"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "newstudent"
        assert data["data"]["email"] == "newstudent@test.com"
    
    def test_register_duplicate_username(self, client: TestClient):
        """测试注册失败 - 用户名重复"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "student001",  # 已存在的用户名
                "email": "new@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "用户名已存在" in data["detail"]
    
    def test_register_duplicate_email(self, client: TestClient):
        """测试注册失败 - 邮箱重复"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "student@test.com",  # 已存在的邮箱
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "邮箱已存在" in data["detail"]
    
    def test_get_profile_success(self, client: TestClient):
        """测试获取用户资料成功"""
        # 先登录获取token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "student123"}
        )
        token = login_response.json()["data"]["access_token"]
        
        # 获取用户资料
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "student001"
        assert "roles" in data["data"]
        assert "permissions" in data["data"]
    
    def test_get_profile_unauthorized(self, client: TestClient):
        """测试获取用户资料失败 - 未授权"""
        response = client.get("/api/v1/auth/profile")
        
        assert response.status_code == 401
    
    def test_change_password_success(self, client: TestClient):
        """测试修改密码成功"""
        # 先登录获取token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "student123"}
        )
        token = login_response.json()["data"]["access_token"]
        
        # 修改密码
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "student123",
                "new_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证新密码可以登录
        new_login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "newpassword123"}
        )
        assert new_login_response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client: TestClient):
        """测试修改密码失败 - 旧密码错误"""
        # 先登录获取token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "student123"}
        )
        token = login_response.json()["data"]["access_token"]
        
        # 修改密码（旧密码错误）
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "wrong_password",
                "new_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "旧密码错误" in data["detail"]
    
    def test_refresh_token_success(self, client: TestClient):
        """测试刷新令牌成功"""
        # 先登录获取token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "student123"}
        )
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # 刷新令牌
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
    
    def test_refresh_token_invalid(self, client: TestClient):
        """测试刷新令牌失败 - 无效令牌"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "无效的刷新令牌" in data["detail"]


class TestUserService:
    """用户服务测试"""
    
    def test_create_user(self, db):
        """测试创建用户"""
        user_service = UserService(db)
        
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            real_name="测试用户"
        )
        
        user = user_service.create_user(user_data)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.real_name == "测试用户"
        assert user.status == 1
        
        # 验证角色分配
        roles = user_service.get_user_roles(user.id)
        assert "student" in roles
    
    def test_authenticate_success(self, db):
        """测试用户认证成功"""
        user_service = UserService(db)
        
        user = user_service.authenticate("student001", "student123")
        
        assert user is not None
        assert user.username == "student001"
    
    def test_authenticate_failure(self, db):
        """测试用户认证失败"""
        user_service = UserService(db)
        
        # 错误密码
        user = user_service.authenticate("student001", "wrong_password")
        assert user is None
        
        # 不存在的用户
        user = user_service.authenticate("nonexistent", "password")
        assert user is None
    
    def test_get_user_roles(self, db):
        """测试获取用户角色"""
        user_service = UserService(db)
        
        # 获取学生用户
        user = user_service.get_by_username("student001")
        roles = user_service.get_user_roles(user.id)
        
        assert "student" in roles
        assert len(roles) == 1
    
    def test_get_user_permissions(self, db):
        """测试获取用户权限"""
        user_service = UserService(db)
        
        # 获取管理员用户
        user = user_service.get_by_username("admin")
        permissions = user_service.get_user_permissions(user.id)
        
        assert "user:manage" in permissions
        assert "question:manage" in permissions
        assert "exam:manage" in permissions
    
    def test_assign_role(self, db):
        """测试分配角色"""
        user_service = UserService(db)
        
        # 获取学生用户
        user = user_service.get_by_username("student001")
        
        # 分配教师角色
        result = user_service.assign_role(user.id, "teacher")
        assert result is True
        
        # 验证角色分配
        roles = user_service.get_user_roles(user.id)
        assert "teacher" in roles
        assert "student" in roles
    
    def test_remove_role(self, db):
        """测试移除角色"""
        user_service = UserService(db)
        
        # 获取用户并分配多个角色
        user = user_service.get_by_username("student001")
        user_service.assign_role(user.id, "teacher")
        
        # 移除学生角色
        result = user_service.remove_role(user.id, "student")
        assert result is True
        
        # 验证角色移除
        roles = user_service.get_user_roles(user.id)
        assert "student" not in roles
        assert "teacher" in roles


class TestPermissions:
    """权限测试"""
    
    def test_admin_access(self, client: TestClient):
        """测试管理员权限"""
        # 管理员登录
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["data"]["access_token"]
        
        # 访问需要管理权限的接口
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_student_access_denied(self, client: TestClient):
        """测试学生权限被拒绝"""
        # 学生登录
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "student001", "password": "student123"}
        )
        token = login_response.json()["data"]["access_token"]
        
        # 尝试访问需要管理权限的接口
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403


# frontend/src/components/auth/__tests__/LoginForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import LoginForm from '../LoginForm';
import { useAuth } from '@/hooks/useAuth';

// Mock useAuth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: null }),
  };
});

describe('LoginForm', () => {
  const mockLogin = vi.fn();
  const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;

  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      login: mockLogin,
      loading: false,
      error: null,
      user: null,
      isAuthenticated: false,
      permissions: [],
      roles: [],
      token: null,
      refreshToken: null,
      register: vi.fn(),
      logout: vi.fn(),
      refreshAuth: vi.fn(),
      updateProfile: vi.fn(),
      changePassword: vi.fn(),
      clearError: vi.fn(),
      initializeAuth: vi.fn(),
      hasRole: vi.fn(),
      hasPermission: vi.fn(),
      hasAnyRole: vi.fn(),
      hasAnyPermission: vi.fn(),
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  const renderLoginForm = () => {
    return render(
      <BrowserRouter>
        <LoginForm />
      </BrowserRouter>
    );
  };

  it('renders login form correctly', () => {
    renderLoginForm();
    
    expect(screen.getByText('登录您的账户')).toBeInTheDocument();
    expect(screen.getByLabelText('用户名')).toBeInTheDocument();
    expect(screen.getByLabelText('密码')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    renderLoginForm();
    
    const submitButton = screen.getByRole('button', { name: '登录' });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('请输入用户名')).toBeInTheDocument();
      expect(screen.getByText('请输入密码')).toBeInTheDocument();
    });
  });

  it('calls login function with correct credentials', async () => {
    renderLoginForm();
    
    const usernameInput = screen.getByLabelText('用户名');
    const passwordInput = screen.getByLabelText('密码');
    const submitButton = screen.getByRole('button', { name: '登录' });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('shows loading state during login', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      loading: true,
    });
    
    renderLoginForm();
    
    expect(screen.getByText('登录中...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录中...' })).toBeDisabled();
  });

  it('displays error message when login fails', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      error: '用户名或密码错误',
    });
    
    renderLoginForm();
    
    expect(screen.getByText('用户名或密码错误')).toBeInTheDocument();
  });

  it('toggles password visibility', () => {
    renderLoginForm();
    
    const passwordInput = screen.getByLabelText('密码');
    const toggleButton = screen.getByRole('button', { name: '' }); // Eye icon button
    
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
});

// frontend/src/hooks/__tests__/useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';
import { useAuth } from '../useAuth';
import { authAPI } from '@/api/modules/auth';
import { storage } from '@/utils/storage';

// Mock dependencies
vi.mock('@/api/modules/auth');
vi.mock('@/utils/storage');
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock zustand store
const mockStore = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  permissions: [],
  roles: [],
  loading: false,
  error: null,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  refreshAuth: vi.fn(),
  updateProfile: vi.fn(),
  changePassword: vi.fn(),
  clearError: vi.fn(),
  initializeAuth: vi.fn(),
  hasRole: vi.fn(),
  hasPermission: vi.fn(),
  hasAnyRole: vi.fn(),
  hasAnyPermission: vi.fn(),
};

vi.mock('@/store', () => ({
  useStore: vi.fn(() => mockStore),
}));

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes auth state correctly', () => {
    const { result } = renderHook(() => useAuth());
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.loading).toBe(false);
  });

  it('calls login with correct credentials', async () => {
    const mockLoginResponse = {
      data: {
        user: { id: 1, username: 'testuser' },
        access_token: 'token123',
        refresh_token: 'refresh123',
        roles: ['student'],
        permissions: [],
      },
    };

    (authAPI.login as vi.Mock).mockResolvedValue(mockLoginResponse);
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login({
        username: 'testuser',
        password: 'password123',
      });
    });

    expect(authAPI.login).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });
  });

  it('handles login error correctly', async () => {
    const error = new Error('Login failed');
    (authAPI.login as vi.Mock).mockRejectedValue(error);
    
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      try {
        await result.current.login({
          username: 'testuser',
          password: 'wrongpassword',
        });
      } catch (e) {
        // Expected to throw
      }
    });

    expect(mockStore.login).toHaveBeenCalled();
  });

  it('checks roles correctly', () => {
    mockStore.hasRole.mockReturnValue(true);
    
    const { result } = renderHook(() => useAuth());
    
    const hasStudentRole = result.current.hasRole('student');
    expect(hasStudentRole).toBe(true);
    expect(mockStore.hasRole).toHaveBeenCalledWith('student');
  });

  it('checks permissions correctly', () => {
    mockStore.hasPermission.mockReturnValue(false);
    
    const { result } = renderHook(() => useAuth());
    
    const hasManagePermission = result.current.hasPermission('user:manage');
    expect(hasManagePermission).toBe(false);
    expect(mockStore.hasPermission).toHaveBeenCalledWith('user:manage');
  });
});

// frontend/src/components/auth/__tests__/ProtectedRoute.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import ProtectedRoute from '../ProtectedRoute';
import { useAuth } from '@/hooks/useAuth';

vi.mock('@/hooks/useAuth');

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;

describe('ProtectedRoute', () => {
  const TestComponent = () => <div>Protected Content</div>;

  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      hasAnyRole: vi.fn(),
      hasAnyPermission: vi.fn(),
      loading: false,
      user: { 
        id: 1, 
        username: 'test', 
        roles: ['student'], 
        permissions: [] 
      } as any,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshAuth: vi.fn(),
      updateProfile: vi.fn(),
      changePassword: vi.fn(),
      clearError: vi.fn(),
      initializeAuth: vi.fn(),
      hasRole: vi.fn(),
      hasPermission: vi.fn(),
      token: null,
      refreshToken: null,
      error: null,
    });
  });

  const renderProtectedRoute = (props = {}) => {
    return render(
      <BrowserRouter>
        <ProtectedRoute {...props}>
          <TestComponent />
        </ProtectedRoute>
      </BrowserRouter>
    );
  };

  it('renders children when authenticated and no role/permission requirements', () => {
    renderProtectedRoute();
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      isAuthenticated: false,
      user: null,
    });

    renderProtectedRoute();
    
    // Should redirect, so protected content should not be visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('shows access denied when user lacks required role', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      hasAnyRole: vi.fn().mockReturnValue(false),
    });

    renderProtectedRoute({ roles: ['admin'] });
    
    expect(screen.getByText('访问被拒绝')).toBeInTheDocument();
    expect(screen.getByText('需要角色：admin')).toBeInTheDocument();
  });

  it('shows permission denied when user lacks required permission', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      hasAnyRole: vi.fn().mockReturnValue(true),
      hasAnyPermission: vi.fn().mockReturnValue(false),
    });

    renderProtectedRoute({ 
      roles: ['admin'], 
      permissions: ['user:manage'] 
    });
    
    expect(screen.getByText('权限不足')).toBeInTheDocument();
    expect(screen.getByText('需要权限：user:manage')).toBeInTheDocument();
  });

  it('renders children when user has required roles and permissions', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      hasAnyRole: vi.fn().mockReturnValue(true),
      hasAnyPermission: vi.fn().mockReturnValue(true),
    });

    renderProtectedRoute({ 
      roles: ['admin'], 
      permissions: ['user:manage'] 
    });
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('shows loading state when authentication is loading', () => {
    mockUseAuth.mockReturnValue({
      ...mockUseAuth(),
      loading: true,
    });

    renderProtectedRoute();
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // Loading component
  });
});

// 运行测试的脚本
// backend/scripts/run_tests.py
#!/usr/bin/env python3
"""
运行所有测试的脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def run_backend_tests():
    """运行后端测试"""
    print("🧪 运行后端测试...")
    
    # 进入后端目录
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # 运行测试
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--cov=app", 
        "--cov-report=html",
        "--cov-report=term"
    ], capture_output=False)
    
    return result.returncode == 0

def run_frontend_tests():
    """运行前端测试"""
    print("🧪 运行前端测试...")
    
    # 进入前端目录
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    os.chdir(frontend_dir)
    
    # 运行测试
    result = subprocess.run([
        "npm", "run", "test", "--", "--coverage"
    ], capture_output=False)
    
    return result.returncode == 0

def main():
    """主函数"""
    print("🚀 开始运行测试套件...")
    
    backend_success = run_backend_tests()
    frontend_success = run_frontend_tests()
    
    print("\n📊 测试结果:")
    print(f"后端测试: {'✅ 通过' if backend_success else '❌ 失败'}")
    print(f"前端测试: {'✅ 通过' if frontend_success else '❌ 失败'}")
    
    if backend_success and frontend_success:
        print("\n🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("\n💥 部分测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
        