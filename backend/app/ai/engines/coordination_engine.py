# backend/app/ai/engines/coordination_engine.py
"""
AI协调引擎 - 实现流程图中的核心调度功能
"""
import asyncio
from typing import Dict, Any, Optional, Type
from datetime import datetime

from app.ai.agents.base_agent import BaseAgent
from app.ai.knowledge.knowledge_base import CentralKnowledgeBase
from app.models.user import User
from app.core.database import get_db


class AICoordinationEngine:
    """AI协调引擎 - 统一管理所有AI Agent"""
    
    def __init__(self):
        self.knowledge_base = CentralKnowledgeBase()
        self.user_agents: Dict[int, BaseAgent] = {}
        self.agent_registry: Dict[str, Type[BaseAgent]] = {}
        self.context_manager = ContextManager()
        
    def register_agent_type(self, role: str, agent_class: Type[BaseAgent]):
        """注册AI代理类型"""
        self.agent_registry[role] = agent_class
    
    async def initialize_agent(self, user_id: int, role: str) -> Optional[BaseAgent]:
        """根据用户角色初始化对应的AI Agent"""
        try:
            # 检查是否已有活跃的agent
            if user_id in self.user_agents and self.user_agents[user_id].active:
                return self.user_agents[user_id]
            
            # 获取用户信息
            with next(get_db()) as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise ValueError(f"User {user_id} not found")
            
            # 根据角色创建对应的agent
            agent_class = self.agent_registry.get(role)
            if not agent_class:
                raise ValueError(f"No agent registered for role: {role}")
            
            agent = agent_class(user_id, self.knowledge_base)
            
            # 启动agent
            startup_result = await agent.startup()
            
            # 缓存agent
            self.user_agents[user_id] = agent
            
            # 记录启动日志
            await self.knowledge_base.log_agent_activity(
                user_id=user_id,
                agent_type=agent.__class__.__name__,
                activity_type="agent_startup",
                data=startup_result,
                timestamp=datetime.now()
            )
            
            return agent
            
        except Exception as e:
            print(f"Failed to initialize agent for user {user_id}, role {role}: {e}")
            return None
    
    async def process_user_action(self, user_id: int, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理用户行为，触发AI Agent流程"""
        try:
            # 获取或创建agent
            agent = self.user_agents.get(user_id)
            if not agent or not agent.active:
                # 自动推断用户角色
                role = await self._infer_user_role(user_id)
                agent = await self.initialize_agent(user_id, role)
                
                if not agent:
                    return {"error": "Failed to initialize AI agent"}
            
            # 更新用户行为日志
            await self.knowledge_base.update_behavior_log(user_id, action)
            
            # 触发AI Agent处理
            response = await agent.process_action(action)
            
            # 更新中央知识库
            if response and response.get("update_profile"):
                await self._update_user_profile(user_id, response["profile_updates"])
            
            # 检查是否需要跨角色协同
            await self._check_cross_role_coordination(user_id, action, response)
            
            return response
            
        except Exception as e:
            print(f"Error processing user action: {e}")
            return {"error": str(e)}
    
    async def _infer_user_role(self, user_id: int) -> str:
        """推断用户角色"""
        with next(get_db()) as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if user and user.roles:
                # 返回第一个角色
                return user.roles[0].name
            
            return "student"  # 默认为学生
    
    async def _update_user_profile(self, user_id: int, updates: Dict[str, Any]):
        """更新用户画像"""
        try:
            # 这里可以实现更复杂的画像更新逻辑
            await self.knowledge_base.update_behavior_log(user_id, {
                "type": "profile_update",
                "updates": updates,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Failed to update user profile: {e}")
    
    async def _check_cross_role_coordination(
        self, 
        user_id: int, 
        action: Dict[str, Any], 
        response: Dict[str, Any]
    ):
        """检查是否需要跨角色协同"""
        try:
            # 检查是否需要通知教师
            if action.get("type") in ["homework_submit", "exam_complete", "learning_difficulty"]:
                await self._notify_teachers(user_id, action, response)
            
            # 检查是否需要通知家长
            if action.get("type") in ["low_performance", "attendance_issue", "behavioral_concern"]:
                await self._notify_parents(user_id, action, response)
                
        except Exception as e:
            print(f"Cross-role coordination error: {e}")
    
    async def _notify_teachers(self, student_id: int, action: Dict, response: Dict):
        """通知相关教师"""
        # 这里会在后续实现
        pass
    
    async def _notify_parents(self, student_id: int, action: Dict, response: Dict):
        """通知相关家长"""
        # 这里会在后续实现
        pass
    
    async def shutdown_agent(self, user_id: int):
        """关闭用户的AI Agent"""
        if user_id in self.user_agents:
            agent = self.user_agents[user_id]
            await agent.shutdown()
            del self.user_agents[user_id]
    
    async def get_agent_status(self, user_id: int) -> Dict[str, Any]:
        """获取代理状态"""
        if user_id in self.user_agents:
            agent = self.user_agents[user_id]
            return {
                "active": agent.active,
                "agent_type": agent.__class__.__name__,
                "startup_time": agent.session_context.get("startup_time"),
                "session_id": agent.session_context.get("session_id")
            }
        
        return {"active": False, "agent_type": None}
    
    async def bulk_process_actions(self, actions: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """批量处理用户行为"""
        tasks = []
        for action in actions:
            user_id = action.get("user_id")
            if user_id:
                task = self.process_user_action(user_id, action)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) else {"error": str(result)}
            for result in results
        ]


class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.contexts: Dict[int, Dict[str, Any]] = {}
    
    def get_context(self, user_id: int) -> Dict[str, Any]:
        """获取用户上下文"""
        return self.contexts.get(user_id, {})
    
    def update_context(self, user_id: int, context_updates: Dict[str, Any]):
        """更新用户上下文"""
        if user_id not in self.contexts:
            self.contexts[user_id] = {}
        
        self.contexts[user_id].update(context_updates)
    
    def clear_context(self, user_id: int):
        """清除用户上下文"""
        if user_id in self.contexts:
            del self.contexts[user_id]
