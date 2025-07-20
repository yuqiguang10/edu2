# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class User(Base):
    """用户基础表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50))
    student_id = Column(String(50), unique=True, index=True)
    phone = Column(String(20))
    avatar = Column(String(255))
    status = Column(SmallInteger, default=1)  # 1-正常, 0-禁用
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    user_roles = relationship("UserRole", back_populates="user")
    teacher = relationship("Teacher", back_populates="user", uselist=False)
    parent_relations = relationship("ParentStudentRelation", 
                                  foreign_keys="ParentStudentRelation.parent_id",
                                  back_populates="parent")
    student_relations = relationship("ParentStudentRelation",
                                   foreign_keys="ParentStudentRelation.student_id", 
                                   back_populates="student")


class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    user_roles = relationship("UserRole", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role")


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    role_permissions = relationship("RolePermission", back_populates="permission")


class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    # 关联关系
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class RolePermission(Base):
    """角色权限关联表"""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


class Teacher(Base):
    """教师表"""
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    title = Column(String(50))  # 职称
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    education = Column(String(50))  # 学历
    experience = Column(Integer)  # 教龄
    bio = Column(Text)  # 个人简介
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="teacher")
    department = relationship("Department", back_populates="teachers")
    subject = relationship("Subject", back_populates="teachers")
    class_teachers = relationship("ClassTeacher", back_populates="teacher")


class ParentStudentRelation(Base):
    """家长学生关系表"""
    __tablename__ = "parent_student_relations"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    relation_type = Column(String(20), nullable=False)  # 父亲、母亲、监护人等
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    parent = relationship("User", foreign_keys=[parent_id], back_populates="parent_relations")
    student = relationship("User", foreign_keys=[student_id], back_populates="student_relations")
