# backend/app/schemas/ai.py (更新版本)
"""
AI相关的Pydantic模型
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class AIAgentInitRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None


class AIAgentResponse(BaseModel):
    agent_id: str
    status: str
    agent_type: str
    recommendations: List[Dict[str, Any]]
    initial_context: Dict[str, Any]


class ActionRequest(BaseModel):
    action_type: str
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


class ActionResponse(BaseModel):
    response_type: str
    suggestions: List[str]
    recommendations: List[Dict[str, Any]]
    feedback: str
    next_actions: List[Dict[str, Any]]
    context_updates: Dict[str, Any]


class RecommendationResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    priority: int
    estimated_time: int
    data: Dict[str, Any]
    reasoning: str


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    message: str
    suggestions: List[str]
    actions: List[Dict[str, Any]]
    context: Dict[str, Any]