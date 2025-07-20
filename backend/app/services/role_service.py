# backend/app/services/role_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import Role, Permission, RolePermission
from app.services.base_service import BaseService


class RoleService(BaseService[Role]):
    """角色服务"""
    
    def __init__(self, db: Session):
        super().__init__(db, Role)
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def assign_permission(self, role_id: int, permission_code: str) -> bool:
        """为角色分配权限"""
        # 获取权限
        permission = self.db.query(Permission).filter(
            Permission.code == permission_code
        ).first()
        if not permission:
            raise ValueError(f"权限 '{permission_code}' 不存在")
        
        # 检查是否已分配
        existing = self.db.query(RolePermission).filter(
            and_(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission.id
            )
        ).first()
        
        if existing:
            return False
        
        # 分配权限
        role_permission = RolePermission(role_id=role_id, permission_id=permission.id)
        self.db.add(role_permission)
        self.db.commit()
        
        return True
    
    def remove_permission(self, role_id: int, permission_code: str) -> bool:
        """移除角色权限"""
        permission = self.db.query(Permission).filter(
            Permission.code == permission_code
        ).first()
        if not permission:
            return False
        
        role_permission = self.db.query(RolePermission).filter(
            and_(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission.id
            )
        ).first()
        
        if role_permission:
            self.db.delete(role_permission)
            self.db.commit()
            return True
        
        return False
    
    def get_role_permissions(self, role_id: int) -> List[str]:
        """获取角色权限"""
        permissions = self.db.query(Permission).join(RolePermission).filter(
            RolePermission.role_id == role_id
        ).all()
        
        return [permission.code for permission in permissions]