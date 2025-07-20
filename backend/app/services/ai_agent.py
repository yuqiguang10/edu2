# backend/app/api/v1/endpoints/ai_agent.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.ai_service import AIService
from app.schemas.ai import ChatRequest, ChatResponse, RecommendationResponse
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("/chat", response_model=APIResponse[ChatResponse])
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI对话接口"""
    try:
        ai_service = AIService(db)
        
        response = await ai_service.chat(
            message=request.message,
            role=request.role,
            user_id=current_user.id,
            context=request.context
        )
        
        return APIResponse(
            data=ChatResponse(**response),
            message="对话成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=APIResponse[list[RecommendationResponse]])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个性化推荐"""
    try:
        ai_service = AIService(db)
        
        recommendations = await ai_service.get_personalized_recommendations(current_user.id)
        
        return APIResponse(
            data=[RecommendationResponse(**rec) for rec in recommendations],
            message="推荐获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))