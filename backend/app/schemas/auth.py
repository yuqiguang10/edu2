from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    real_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, regex=r'^1[3-9]\d{9}$')


class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(..., description="用户角色")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['student', 'teacher', 'parent', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'角色必须是 {allowed_roles} 中的一个')
        return v


class UserUpdate(BaseModel):
    """更新用户模式"""
    real_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class UserInDB(UserBase):
    """数据库中的用户模式"""
    id: int
    student_id: Optional[str] = None
    avatar: Optional[str] = None
    status: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """用户响应模式"""
    roles: List[str] = []


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = False


class LoginResponse(BaseModel):
    """登录响应"""
    user: UserResponse
    token: str
    refresh_token: str
    permissions: List[str] = []


class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=6)


class PasswordResetRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """确认重置密码"""
    token: str
    new_password: str = Field(..., min_length=6)
