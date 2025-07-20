# backend/app/services/user_service.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.core.security import verify_password, get_password_hash
from app.services.base_service import BaseService
from app.schemas.auth import UserCreate


class UserService(BaseService[User]):
    """用户服务"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_create: UserCreate, role_name: str = "student") -> User:
        """创建用户"""
        # 检查用户名和邮箱是否已存在
        if self.get_by_username(user_create.username):
            raise ValueError("用户名已存在")
        
        if self.get_by_email(user_create.email):
            raise ValueError("邮箱已存在")
        
        # 创建用户
        user_data = user_create.dict()
        user_data["password_hash"] = get_password_hash(user_create.password)
        del user_data["password"]
        
        user = self.create(user_data)
        
        # 分配默认角色
        self.assign_role(user.id, role_name)
        
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def assign_role(self, user_id: int, role_name: str) -> bool:
        """分配角色"""
        # 获取角色
        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise ValueError(f"角色 '{role_name}' 不存在")
        
        # 检查是否已分配
        existing = self.db.query(UserRole).filter(
            and_(UserRole.user_id == user_id, UserRole.role_id == role.id)
        ).first()
        
        if existing:
            return False
        
        # 分配角色
        user_role = UserRole(user_id=user_id, role_id=role.id)
        self.db.add(user_role)
        self.db.commit()
        
        return True
    
    def remove_role(self, user_id: int, role_name: str) -> bool:
        """移除角色"""
        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            return False
        
        user_role = self.db.query(UserRole).filter(
            and_(UserRole.user_id == user_id, UserRole.role_id == role.id)
        ).first()
        
        if user_role:
            self.db.delete(user_role)
            self.db.commit()
            return True
        
        return False
    
    def get_user_roles(self, user_id: int) -> List[str]:
        """获取用户角色"""
        roles = self.db.query(Role).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        
        return [role.name for role in roles]
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户权限"""
        permissions = self.db.query(Permission).join(RolePermission).join(Role).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
        
        return [permission.code for permission in permissions]
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = self.get(user_id)
        if not user:
            return False
        
        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise ValueError("旧密码错误")
        
        # 更新密码
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """重置密码（管理员功能）"""
        user = self.get(user_id)
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def update_last_login(self, user_id: int) -> bool:
        """更新最后登录时间"""
        from datetime import datetime
        
        user = self.get(user_id)
        if not user:
            return False
        
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return True