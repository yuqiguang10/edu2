from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate
from app.schemas.common import APIResponse, PaginationParams, PaginationResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=APIResponse[PaginationResponse[UserResponse]])
async def get_users(
    pagination: PaginationParams = Depends(),
    role: str = Query(None, description="角色筛选"),
    status: int = Query(None, description="状态筛选"),
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
) -> Any:
    """获取用户列表（仅管理员）"""
    user_service = UserService(db)
    
    filters = {}
    if status is not None:
        filters["status"] = status
    
    users = user_service.get_multi(
        skip=(pagination.page - 1) * pagination.page_size,
        limit=pagination.page_size,
        filters=filters
    )
    
    total = user_service.count(filters)
    
    user_responses = []
    for user in users:
        roles = user_service.get_user_roles(user.id)
        
        # 角色筛选
        if role and role not in roles:
            continue
            
        user_responses.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            real_name=user.real_name,
            phone=user.phone,
            avatar=user.avatar,
            status=user.status,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=roles
        ))
    
    return APIResponse(
        data=PaginationResponse(
            data=user_responses,
            total=len(user_responses),
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(len(user_responses) + pagination.page_size - 1) // pagination.page_size
        )
    )


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取用户详情"""
    # 用户只能查看自己的信息，或者管理员可以查看所有用户
    if user_id != current_user.id:
        user_service = UserService(db)
        roles = user_service.get_user_roles(current_user.id)
        if "admin" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    user_service = UserService(db)
    user = user_service.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    roles = user_service.get_user_roles(user.id)
    
    return APIResponse(
        data=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            real_name=user.real_name,
            phone=user.phone,
            avatar=user.avatar,
            status=user.status,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=roles
        )
    )


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """更新用户信息"""
    # 用户只能更新自己的信息，或者管理员可以更新所有用户
    if user_id != current_user.id:
        user_service = UserService(db)
        roles = user_service.get_user_roles(current_user.id)
        if "admin" not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_update)
    roles = user_service.get_user_roles(user.id)
    
    return APIResponse(
        data=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            real_name=user.real_name,
            phone=user.phone,
            avatar=user.avatar,
            status=user.status,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=roles
        ),
        message="用户信息更新成功"
    )
