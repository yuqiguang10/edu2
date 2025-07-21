# backend/app/ai/agents/base_agent.py
"""
AI代理基类
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.analytics import StudentProfile, LearningBehaviorLog
from app.ai.engines.llm_client import LLMClient


class BaseAgent(ABC):
    """AI代理基类"""
    
    def __init__(self, user_id: int, knowledge_base: 'CentralKnowledgeBase'):
        self.user_id = user_id
        self.knowledge_base = knowledge_base
        self.llm_client = LLMClient()
        self.session_context = {}
        self.active = False
        
    async def startup(self) -> Dict[str, Any]:
        """启动AI代理"""
        self.active = True
        self.session_context = await self.initialize_context()
        return await self.on_startup()
    
    async def shutdown(self):
        """关闭AI代理"""
        self.active = False
        await self.on_shutdown()
    
    async def initialize_context(self) -> Dict[str, Any]:
        """初始化上下文信息"""
        context = {
            "user_id": self.user_id,
            "startup_time": datetime.now(),
            "session_id": f"{self.user_id}_{datetime.now().timestamp()}"
        }
        return context
    
    @abstractmethod
    async def on_startup(self) -> Dict[str, Any]:
        """启动时的具体逻辑"""
        pass
    
    @abstractmethod
    async def on_shutdown(self):
        """关闭时的具体逻辑"""
        pass
    
    @abstractmethod
    async def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户行为"""
        pass
    
    async def log_activity(self, activity_type: str, data: Dict[str, Any]):
        """记录活动日志"""
        await self.knowledge_base.log_agent_activity(
            user_id=self.user_id,
            agent_type=self.__class__.__name__,
            activity_type=activity_type,
            data=data,
            timestamp=datetime.now()
        )
