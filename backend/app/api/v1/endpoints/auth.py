from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserCreate, UserResponse,
    PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm
)
from app.schemas.common import APIResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    user_credentials: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    user_service = UserService(db)
    
    user = user_service.authenticate(
        user_credentials.username,
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成令牌
    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username)
    
    # 获取用户角色和权限
    roles = user_service.get_user_roles(user.id)
    permissions = user_service.get_user_permissions(user.id)
    
    return APIResponse(
        data=LoginResponse(
            user=UserResponse(
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
            token=access_token,
            refresh_token=refresh_token,
            permissions=permissions
        ),
        message="登录成功"
    )


@router.post("/register", response_model=APIResponse[UserResponse])
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """用户注册"""
    user_service = UserService(db)
    
    user = user_service.create_user(user_create)
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
        message="注册成功"
    )


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """用户登出"""
    # 这里可以实现令牌黑名单功能
    return APIResponse(
        data=None,
        message="登出成功"
    )


@router.get("/profile", response_model=APIResponse[UserResponse])
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取用户信息"""
    user_service = UserService(db)
    roles = user_service.get_user_roles(current_user.id)
    
    return APIResponse(
        data=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            real_name=current_user.real_name,
            phone=current_user.phone,
            avatar=current_user.avatar,
            status=current_user.status,
            last_login=current_user.last_login,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            roles=roles
        )
    )


@router.post("/change-password", response_model=APIResponse[None])
async def change_password(
    password_change: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """修改密码"""
    user_service = UserService(db)
    
    success = user_service.change_password(
        current_user.id,
        password_change.old_password,
        password_change.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码修改失败"
        )
    
    return APIResponse(
        data=None,
        message="密码修改成功"
    )
