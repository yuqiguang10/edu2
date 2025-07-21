# backend/app/api/v1/api.py (更新版本)
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, class_management, 
    homework, exam, analytics, ai_agent  # 新增ai_agent
)

api_router = APIRouter()

# 包含所有路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(class_management.router, prefix="/class-management", tags=["班级管理"])
api_router.include_router(homework.router, prefix="/homework", tags=["作业管理"])
api_router.include_router(exam.router, prefix="/exam", tags=["考试管理"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["数据分析"])
api_router.include_router(ai_agent.router, prefix="/ai", tags=["AI智能助手"])  # 新增AI路由
