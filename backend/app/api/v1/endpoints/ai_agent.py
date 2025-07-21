# backend/app/api/v1/endpoints/ai_agent.py
"""
AI Agent API端点 - 更新版本
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.ai import (
    AIAgentInitRequest, AIAgentResponse, ActionRequest, ActionResponse,
    RecommendationResponse, ChatRequest, ChatResponse
)
from app.schemas.common import APIResponse
from app.ai import get_ai_coordinator
from app.ai.engines.recommendation_engine import IntelligentRecommendationEngine

router = APIRouter()


@router.post("/agent/initialize", response_model=APIResponse[AIAgentResponse])
async def initialize_ai_agent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """初始化用户的AI Agent"""
    try:
        ai_coordinator = get_ai_coordinator()
        
        # 推断用户角色
        user_role = current_user.roles[0].name if current_user.roles else "student"
        
        # 初始化AI Agent
        agent = await ai_coordinator.initialize_agent(current_user.id, user_role)
        
        if not agent:
            raise HTTPException(status_code=500, detail="AI Agent初始化失败")
        
        # 获取启动结果
        startup_result = agent.session_context
        
        return APIResponse(
            data=AIAgentResponse(
                agent_id=startup_result.get("session_id"),
                status="active",
                agent_type=agent.__class__.__name__,
                recommendations=startup_result.get("recommendations", []),
                initial_context=startup_result.get("context", {})
            ),
            message="AI助手已成功启动"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent启动失败: {str(e)}")


@router.post("/agent/action", response_model=APIResponse[ActionResponse])
async def process_user_action(
    request: ActionRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
) -> Any:
    """处理用户行为并获取AI响应"""
    try:
        ai_coordinator = get_ai_coordinator()
        
        # 处理用户行为
        action_data = {
            "type": request.action_type,
            "data": request.data,
            "timestamp": request.timestamp or datetime.now().isoformat(),
            "context": request.context or {}
        }
        
        # 获取AI响应
        response = await ai_coordinator.process_user_action(current_user.id, action_data)
        
        if not response:
            raise HTTPException(status_code=500, detail="AI处理失败")
        
        # 异步更新用户画像
        background_tasks.add_task(
            _update_user_profile_async, 
            current_user.id, 
            action_data, 
            response
        )
        
        return APIResponse(
            data=ActionResponse(
                response_type=response.get("type", "general"),
                suggestions=response.get("suggestions", []),
                recommendations=response.get("recommendations", []),
                feedback=response.get("feedback", ""),
                next_actions=response.get("actions", []),
                context_updates=response.get("context", {})
            ),
            message="AI响应生成成功"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"行为处理失败: {str(e)}")


@router.get("/recommendations", response_model=APIResponse[List[RecommendationResponse]])
async def get_personalized_recommendations(
    context: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取个性化推荐"""
    try:
        recommendation_engine = IntelligentRecommendationEngine()
        
        # 生成推荐
        if context:
            recommendations = await recommendation_engine.generate_ai_powered_recommendations(
                current_user.id, context
            )
        else:
            recommendations = await recommendation_engine.generate_student_recommendations(
                current_user.id
            )
        
        # 转换为响应格式
        recommendation_responses = [
            RecommendationResponse(
                id=f"rec_{i}",
                type=rec.get("type", "general"),
                title=rec.get("title", ""),
                description=rec.get("description", ""),
                priority=rec.get("priority", 3),
                estimated_time=rec.get("estimated_time", 30),
                data=rec.get("data", {}),
                reasoning=rec.get("reasoning", "基于你的学习情况生成")
            )
            for i, rec in enumerate(recommendations)
        ]
        
        return APIResponse(
            data=recommendation_responses,
            message="推荐生成成功"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐生成失败: {str(e)}")


@router.post("/chat", response_model=APIResponse[ChatResponse])
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """AI对话接口"""
    try:
        ai_coordinator = get_ai_coordinator()
        
        # 处理对话请求
        chat_action = {
            "type": "ai_chat",
            "data": {
                "message": request.message,
                "context": request.context,
                "history": request.history
            }
        }
        
        response = await ai_coordinator.process_user_action(current_user.id, chat_action)
        
        if not response:
            raise HTTPException(status_code=500, detail="AI对话失败")
        
        return APIResponse(
            data=ChatResponse(
                message=response.get("ai_response", "抱歉，我现在无法回答这个问题。"),
                suggestions=response.get("suggestions", []),
                actions=response.get("actions", []),
                context=response.get("context", {})
            ),
            message="对话成功"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI对话失败: {str(e)}")


@router.get("/agent/status", response_model=APIResponse[Dict[str, Any]])
async def get_agent_status(
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取AI Agent状态"""
    try:
        ai_coordinator = get_ai_coordinator()
        status = await ai_coordinator.get_agent_status(current_user.id)
        
        return APIResponse(
            data=status,
            message="状态获取成功"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"状态获取失败: {str(e)}")


@router.post("/agent/shutdown")
async def shutdown_agent(
    current_user: User = Depends(get_current_user)
) -> Any:
    """关闭AI Agent"""
    try:
        ai_coordinator = get_ai_coordinator()
        await ai_coordinator.shutdown_agent(current_user.id)
        
        return APIResponse(
            data={"status": "shutdown"},
            message="AI助手已关闭"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"关闭失败: {str(e)}")


@router.get("/learning-analysis", response_model=APIResponse[Dict[str, Any]])
async def get_learning_analysis(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取学习分析报告"""
    try:
        from app.ai.knowledge.knowledge_base import CentralKnowledgeBase
        
        knowledge_base = CentralKnowledgeBase()
        
        # 获取学习统计
        stats = await knowledge_base.get_learning_stats(current_user.id)
        
        # 获取最近活动
        activities = await knowledge_base.get_recent_activities(current_user.id, hours=days*24)
        
        # 生成分析报告
        analysis = {
            "period_days": days,
            "total_learning_time": stats["total_time"],
            "session_count": stats["session_count"],
            "average_session_duration": stats["avg_session_duration"],
            "most_active_hour": stats["most_active_hour"],
            "consistency_score": stats["learning_consistency"],
            "recent_activities": len(activities),
            "activity_trend": await _calculate_activity_trend(activities, days)
        }
        
        return APIResponse(
            data=analysis,
            message="学习分析生成成功"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析生成失败: {str(e)}")


# 辅助函数
async def _update_user_profile_async(user_id: int, action_data: Dict, response: Dict):
    """异步更新用户画像"""
    try:
        # 这里可以实现复杂的画像更新逻辑
        # 例如：更新学习偏好、能力评估等
        pass
    except Exception as e:
        print(f"Profile update failed for user {user_id}: {e}")


async def _calculate_activity_trend(activities: List[Dict], days: int) -> str:
    """计算活动趋势"""
    if len(activities) < 2:
        return "insufficient_data"
    
    # 简单的趋势计算
    mid_point = len(activities) // 2
    recent_half = activities[:mid_point]
    earlier_half = activities[mid_point:]
    
    recent_avg = len(recent_half) / (days / 2) if days > 1 else len(recent_half)
    earlier_avg = len(earlier_half) / (days / 2) if days > 1 else len(earlier_half)
    
    if recent_avg > earlier_avg * 1.2:
        return "increasing"
    elif recent_avg < earlier_avg * 0.8:
        return "decreasing"
    else:
        return "stable"