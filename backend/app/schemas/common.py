# backend/app/schemas/common.py
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    success: bool = Field(default=True, description="请求是否成功")
    data: Optional[T] = Field(default=None, description="返回数据")
    message: str = Field(default="操作成功", description="响应消息")
    code: int = Field(default=200, description="响应状态码")


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页大小")


class PaginationResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: list[T] = Field(description="数据列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页")
    page_size: int = Field(description="每页大小")
    pages: int = Field(description="总页数")
