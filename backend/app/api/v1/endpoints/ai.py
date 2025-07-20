from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.ai import (
    ChatRequest, ChatResponse, RecommendationRequest, RecommendationResponse,
    AnalysisRequest, AnalysisResponse
)
from app.schemas.common import APIResponse
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/chat", response_model=APIResponse[ChatResponse])
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """AI聊天对话"""
    ai_service = AIService()
    
    # 添加用户信息到上下文
    if request.context is None:
        request.context = {}
    request.context["user_id"] = current_user.id
    request.context["username"] = current_user.username
    
    response = await ai_service.chat(request)
    
    return APIResponse(
        data=response,
        message="对话成功"
    )


@router.post("/recommendations", response_model=APIResponse[RecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取AI推荐"""
    ai_service = AIService()
    
    # 确保用户只能获取自己的推荐
    request.user_id = current_user.id
    
    response = await ai_service.generate_recommendations(request)
    
    return APIResponse(
        data=response,
        message="推荐生成成功"
    )


@router.post("/analysis", response_model=APIResponse[AnalysisResponse])
async def analyze_performance(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """AI学习分析"""
    ai_service = AIService()
    
    # 确保用户只能分析自己的数据
    request.student_id = current_user.id
    
    response = await ai_service.analyze_performance(request)
    
    return APIResponse(
        data=response,
        message="分析完成"
    )


@router.post("/generate-exam", response_model=APIResponse[list])
async def generate_exam_questions(
    subject_id: int,
    difficulty_level: int,
    question_count: int,
    knowledge_point_ids: list = None,
    current_user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db)
) -> Any:
    """AI智能组卷"""
    # 这里可以集成更复杂的AI组卷逻辑
    from app.services.question_service import QuestionService
    
    question_service = QuestionService(db)
    
    # 简单的智能组卷逻辑
    questions = question_service.search_questions(
        subject_id=subject_id,
        difficulty_id=difficulty_level,
        knowledge_point_ids=knowledge_point_ids,
        page=1,
        page_size=question_count
    )
    
    return APIResponse(
        data=questions["questions"],
        message="智能组卷完成"
    )
