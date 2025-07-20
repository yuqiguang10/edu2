# backend/app/api/v1/endpoints/auth.py
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_active_user
from app.core.config import settings
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_token,
    verify_password,
    get_password_hash
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserCreate, UserResponse,
    PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm,
    RefreshTokenRequest, RefreshTokenResponse
)
from app.schemas.common import APIResponse
from app.services.user_service import UserService
from app.services.email_service import EmailService

router = APIRouter()


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    background_tasks: BackgroundTasks,
    user_credentials: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    user_service = UserService(db)
    
    # 认证用户
    user = user_service.authenticate(
        user_credentials.username,
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # 生成令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username, expires_delta=access_token_expires)
    
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(user.username, expires_delta=refresh_token_expires)
    
    # 获取用户角色和权限
    roles = user_service.get_user_roles(user.id)
    permissions = user_service.get_user_permissions(user.id)
    
    # 更新最后登录时间（后台任务）
    background_tasks.add_task(user_service.update_last_login, user.id)
    
    return APIResponse(
        data=LoginResponse(
            user=UserResponse.from_orm(user),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            roles=roles,
            permissions=permissions
        ),
        message="登录成功"
    )


@router.post("/register", response_model=APIResponse[UserResponse])
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """用户注册"""
    user_service = UserService(db)
    
    try:
        # 创建用户（默认为学生角色）
        user = user_service.create_user(user_data, role_name="student")
        
        return APIResponse(
            data=UserResponse.from_orm(user),
            message="注册成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh", response_model=APIResponse[RefreshTokenResponse])
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """刷新访问令牌"""
    # 验证刷新令牌
    username = verify_token(token_data.refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 获取用户
    user_service = UserService(db)
    user = user_service.get_by_username(username)
    if not user or user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username, expires_delta=access_token_expires)
    
    return APIResponse(
        data=RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        message="令牌刷新成功"
    )


@router.post("/logout", response_model=APIResponse)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """用户登出"""
    # 在实际项目中，这里可以将token加入黑名单
    # 由于JWT是无状态的，简单实现只返回成功
    return APIResponse(message="登出成功")


@router.get("/profile", response_model=APIResponse[UserResponse])
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取用户资料"""
    user_service = UserService(db)
    
    # 获取用户角色
    roles = user_service.get_user_roles(current_user.id)
    permissions = user_service.get_user_permissions(current_user.id)
    
    user_data = UserResponse.from_orm(current_user)
    user_data.roles = roles
    user_data.permissions = permissions
    
    return APIResponse(
        data=user_data,
        message="获取成功"
    )


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: int,
    user_update: dict,
    current_user: User = Depends(require_permissions("user:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """更新用户信息"""
    user_service = UserService(db)
    
    user = user_service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 过滤允许更新的字段
    allowed_fields = ["real_name", "phone", "avatar", "status"]
    update_data = {k: v for k, v in user_update.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有可更新的字段"
        )
    
    updated_user = user_service.update(user, update_data)
    
    user_response = UserResponse.from_orm(updated_user)
    user_response.roles = user_service.get_user_roles(updated_user.id)
    
    return APIResponse(
        data=user_response,
        message="用户更新成功"
    )


@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permissions("user:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """删除用户"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user_service = UserService(db)
    
    if not user_service.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return APIResponse(message="用户删除成功")


@router.post("/{user_id}/roles/{role_name}", response_model=APIResponse)
async def assign_role(
    user_id: int,
    role_name: str,
    current_user: User = Depends(require_permissions("user:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """分配角色"""
    user_service = UserService(db)
    
    if not user_service.get(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        if user_service.assign_role(user_id, role_name):
            return APIResponse(message=f"角色 '{role_name}' 分配成功")
        else:
            return APIResponse(message=f"用户已拥有角色 '{role_name}'")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}/roles/{role_name}", response_model=APIResponse)
async def remove_role(
    user_id: int,
    role_name: str,
    current_user: User = Depends(require_permissions("user:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """移除角色"""
    user_service = UserService(db)
    
    if user_service.remove_role(user_id, role_name):
        return APIResponse(message=f"角色 '{role_name}' 移除成功")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在或用户未拥有该角色"
        )


@router.post("/{user_id}/reset-password", response_model=APIResponse)
async def admin_reset_password(
    user_id: int,
    new_password: str,
    current_user: User = Depends(require_permissions("user:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """管理员重置用户密码"""
    user_service = UserService(db)
    
    if not user_service.reset_password(user_id, new_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return APIResponse(message="密码重置成功")
