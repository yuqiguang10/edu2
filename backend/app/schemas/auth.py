# backend/app/schemas/auth.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class RefreshTokenResponse(BaseModel):
    """刷新令牌响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: EmailStr
    real_name: Optional[str] = None
    student_id: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: int
    last_login: Optional[datetime] = None
    created_at: datetime
    roles: List[str] = []
    permissions: List[str] = []

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    roles: List[str] = []
    permissions: List[str] = []


class UserCreate(BaseModel):
    """用户创建"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, description="手机号")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserUpdate(BaseModel):
    """用户更新"""
    real_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1)


class PasswordChangeRequest(BaseModel):
    """密码修改请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码长度至少6位')
        return v


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, description="新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    permissions: List[str] = []

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """权限响应"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True/profile", response_model=APIResponse[UserResponse])
async def update_profile(
    user_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """更新用户资料"""
    user_service = UserService(db)
    
    # 过滤允许更新的字段
    allowed_fields = ["real_name", "phone", "avatar"]
    update_data = {k: v for k, v in user_update.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有可更新的字段"
        )
    
    # 更新用户信息
    updated_user = user_service.update(current_user, update_data)
    
    return APIResponse(
        data=UserResponse.from_orm(updated_user),
        message="更新成功"
    )


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """修改密码"""
    user_service = UserService(db)
    
    try:
        user_service.change_password(
            current_user.id,
            password_data.old_password,
            password_data.new_password
        )
        
        return APIResponse(message="密码修改成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(
    background_tasks: BackgroundTasks,
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """忘记密码"""
    user_service = UserService(db)
    email_service = EmailService()
    
    # 查找用户
    user = user_service.get_by_email(request_data.email)
    if not user:
        # 为了安全，即使用户不存在也返回成功
        return APIResponse(message="如果邮箱存在，重置链接已发送")
    
    # 生成重置令牌（有效期30分钟）
    reset_token = create_access_token(
        user.username,
        expires_delta=timedelta(minutes=30)
    )
    
    # 发送重置邮件（后台任务）
    background_tasks.add_task(
        email_service.send_password_reset_email,
        user.email,
        user.real_name or user.username,
        reset_token
    )
    
    return APIResponse(message="如果邮箱存在，重置链接已发送")


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """重置密码"""
    # 验证重置令牌
    username = verify_token(reset_data.token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的重置令牌"
        )
    
    user_service = UserService(db)
    user = user_service.get_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 重置密码
    user_service.reset_password(user.id, reset_data.new_password)
    
    return APIResponse(message="密码重置成功")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "auth"}