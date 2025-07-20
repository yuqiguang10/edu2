from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50))
    student_id = Column(String(50), unique=True, index=True)
    phone = Column(String(20))
    avatar = Column(String(255))
    status = Column(SmallInteger, nullable=False, default=1)
    last_login = Column(DateTime(timezone=True))
    
    # 关系
    user_roles = relationship("UserRole", back_populates="user")
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    student_records = relationship("ExamRecord", back_populates="student")


class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # 关系
    user_roles = relationship("UserRole", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role")


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"
    
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # 关系
    role_permissions = relationship("RolePermission", back_populates="permission")


class UserRole(Base):
    """用户-角色关联表"""
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, nullable=False, index=True)
    role_id = Column(Integer, nullable=False, index=True)
    
    # 关系
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class RolePermission(Base):
    """角色-权限关联表"""
    __tablename__ = "role_permissions"
    
    role_id = Column(Integer, nullable=False, index=True)
    permission_id = Column(Integer, nullable=False, index=True)
    
    # 关系
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
