from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    """聊天消息模式"""
    role: str = Field(..., description="消息角色: user 或 assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """聊天请求模式"""
    message: str = Field(..., description="用户消息")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    history: List[ChatMessage] = Field(default=[], description="聊天历史")


class ChatResponse(BaseModel):
    """聊天响应模式"""
    message: str = Field(..., description="AI回复")
    suggestions: List[str] = Field(default=[], description="建议问题")
    actions: List[Dict[str, Any]] = Field(default=[], description="推荐操作")


class RecommendationRequest(BaseModel):
    """推荐请求模式"""
    user_id: int
    subject_id: int
    context: Optional[Dict[str, Any]] = None


class LearningPathStep(BaseModel):
    """学习路径步骤"""
    step: int
    title: str
    progress: float
    resources: List[Dict[str, Any]] = []


class RecommendationResponse(BaseModel):
    """推荐响应模式"""
    questions: List[QuestionResponse] = []
    learning_path: List[LearningPathStep] = []
    weak_points: List[str] = []
    next_goal: str = ""


class AnalysisRequest(BaseModel):
    """分析请求模式"""
    student_id: int
    time_range: Optional[Dict[str, str]] = None
    subjects: List[int] = []


class TrendData(BaseModel):
    """趋势数据"""
    date: str
    score: float
    subject: str


class AnalysisResponse(BaseModel):
    """分析响应模式"""
    overall_score: float
    improvement: float
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendation: str = ""
    trend_data: List[TrendData] = []
