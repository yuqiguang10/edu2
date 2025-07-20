from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, exams, questions, ai

api_router = APIRouter()

# 包含所有路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(exams.router, prefix="/exams", tags=["考试管理"])
api_router.include_router(questions.router, prefix="/questions", tags=["题库管理"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI功能"])
