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
