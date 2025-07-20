from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.security import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # 不需要认证的路径
        self.public_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
        }
    
    async def dispatch(self, request: Request, call_next):
        # 检查是否是公开路径
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # 检查是否有认证头
        authorization = request.headers.get("Authorization")
        if not authorization:
            # 如果是API路径但没有认证头，返回401
            if request.url.path.startswith("/api/"):
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "message": "未提供认证令牌",
                        "code": 401
                    }
                )
            return await call_next(request)
        
        # 验证令牌格式
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "message": "无效的认证方案",
                        "code": 401
                    }
                )
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message": "无效的认证格式",
                    "code": 401
                }
            )
        
        # 验证令牌
        username = verify_token(token)
        if not username:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message": "无效或过期的令牌",
                    "code": 401
                }
            )
        
        # 将用户信息添加到请求状态
        request.state.user_id = username
        
        return await call_next(request)
