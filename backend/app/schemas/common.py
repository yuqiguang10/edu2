from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataType = TypeVar("DataType")


class APIResponse(BaseModel, Generic[DataType]):
    """API响应基类"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[DataType] = None
    code: int = 200


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class PaginationResponse(BaseModel, Generic[DataType]):
    """分页响应"""
    data: List[DataType]
    total: int
    page: int
    page_size: int
    total_pages: int
