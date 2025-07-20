from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException, status
from app.models.user import User, Role, UserRole, RolePermission, Permission
from app.core.security import get_password_hash, verify_password
from app.schemas.auth import UserCreate, UserUpdate
from app.services.base_service import BaseService


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
    
    def get_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """根据用户名或邮箱获取用户"""
        return self.db.query(User).filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()
    
    def create_user(self, user_create: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if self.get_by_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if self.get_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 创建用户
        user_data = user_create.dict(exclude={"password", "role"})
        user_data["password_hash"] = get_password_hash(user_create.password)
        
        user = self.create(user_data)
        
        # 分配角色
        self.assign_role(user.id, user_create.role)
        
        return user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """更新用户"""
        user = self.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        update_data = user_update.dict(exclude_unset=True)
        return self.update(user, update_data)
    
    def authenticate(self, username_or_email: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_by_username_or_email(username_or_email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # 更新最后登录时间
        from datetime import datetime
        user.last_login = datetime.now()
        self.db.commit()
        
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = self.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True
    
    def reset_password(self, email: str, new_password: str) -> bool:
        """重置密码"""
        user = self.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True
    
    def assign_role(self, user_id: int, role_name: str) -> bool:
        """分配角色"""
        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色 {role_name} 不存在"
            )
        
        # 检查是否已有该角色
        existing = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role.id
        ).first()
        
        if existing:
            return True
        
        user_role = UserRole(user_id=user_id, role_id=role.id)
        self.db.add(user_role)
        self.db.commit()
        return True
    
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
