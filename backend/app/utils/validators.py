import re
from typing import Any
from fastapi import HTTPException


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}'
    return bool(re.match(pattern, phone))


def validate_password(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 6:
        return False
    
    # 至少包含字母和数字
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    return has_letter and has_digit


def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if len(username) < 3 or len(username) > 20:
        return False
    
    # 只能包含字母、数字和下划线
    pattern = r'^[a-zA-Z0-9_]+'
    return bool(re.match(pattern, username))


def validate_pagination_params(page: int, page_size: int) -> None:
    """验证分页参数"""
    if page < 1:
        raise HTTPException(status_code=400, detail="��码必须大于0")
    
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页数量必须在1-100之间")


class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)
