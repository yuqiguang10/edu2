# backend/app/ai/knowledge/knowledge_base.py
"""
中央知识库
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.analytics import LearningBehaviorLog, StudentProfile
from app.models.user import User
from app.models.education import Class


class CentralKnowledgeBase:
    """中央知识库"""
    
    def __init__(self):
        self.cache = {}
    
    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """获取用户画像"""
        with next(get_db()) as db:
            profile = db.query(StudentProfile).filter(StudentProfile.student_id == user_id).first()
            
            if profile:
                return {
                    "user_id": user_id,
                    "learning_style": profile.learning_style,
                    "ability_scores": {
                        "visual": profile.ability_visual,
                        "verbal": profile.ability_verbal,
                        "logical": profile.ability_logical,
                        "mathematical": profile.ability_mathematical
                    },
                    "attention_duration": profile.attention_duration,
                    "preferred_content_type": profile.preferred_content_type,
                    "updated_at": profile.updated_at
                }
            else:
                # 创建默认画像
                return await self.create_default_profile(user_id)
    
    async def create_default_profile(self, user_id: int) -> Dict[str, Any]:
        """创建默认用户画像"""
        with next(get_db()) as db:
            default_profile = StudentProfile(
                student_id=user_id,
                learning_style="mixed",
                ability_visual=0.5,
                ability_verbal=0.5,
                ability_logical=0.5,
                ability_mathematical=0.5,
                attention_duration=30,
                preferred_content_type="mixed"
            )
            
            db.add(default_profile)
            db.commit()
            
            return await self.get_user_profile(user_id)
    
    async def update_behavior_log(self, user_id: int, action: Dict[str, Any]):
        """更新用户行为日志"""
        with next(get_db()) as db:
            behavior_log = LearningBehaviorLog(
                student_id=user_id,
                action_type=action.get('type', 'unknown'),
                action_data=action,
                session_duration=action.get('duration', 0),
                timestamp=datetime.now()
            )
            
            db.add(behavior_log)
            db.commit()
    
    async def get_recent_activities(self, user_id: int, hours: int = 24) -> List[Dict[str, Any]]:
        """获取最近活动记录"""
        with next(get_db()) as db:
            since_time = datetime.now() - timedelta(hours=hours)
            
            activities = db.query(LearningBehaviorLog).filter(
                LearningBehaviorLog.student_id == user_id,
                LearningBehaviorLog.timestamp >= since_time
            ).order_by(LearningBehaviorLog.timestamp.desc()).limit(50).all()
            
            return [
                {
                    "id": activity.id,
                    "action_type": activity.action_type,
                    "action_data": activity.action_data,
                    "session_duration": activity.session_duration,
                    "timestamp": activity.timestamp
                }
                for activity in activities
            ]
    
    async def log_agent_activity(
        self, 
        user_id: int, 
        agent_type: str, 
        activity_type: str, 
        data: Dict[str, Any], 
        timestamp: datetime
    ):
        """记录AI代理活动"""
        await self.update_behavior_log(user_id, {
            "type": f"ai_agent_{activity_type}",
            "agent_type": agent_type,
            "data": data,
            "timestamp": timestamp.isoformat()
        })
    
    async def get_learning_stats(self, user_id: int) -> Dict[str, Any]:
        """获取学习统计数据"""
        activities = await self.get_recent_activities(user_id, hours=24*7)  # 最近一周
        
        if not activities:
            return {
                "total_time": 0,
                "session_count": 0,
                "avg_session_duration": 0,
                "most_active_hour": None,
                "learning_consistency": 0
            }
        
        total_time = sum(activity.get('session_duration', 0) for activity in activities)
        session_count = len(activities)
        avg_duration = total_time / session_count if session_count > 0 else 0
        
        return {
            "total_time": total_time,
            "session_count": session_count,
            "avg_session_duration": avg_duration,
            "most_active_hour": self._calculate_most_active_hour(activities),
            "learning_consistency": self._calculate_consistency_score(activities)
        }
    
    def _calculate_most_active_hour(self, activities: List[Dict]) -> int:
        """计算最活跃的小时"""
        hour_counts = {}
        for activity in activities:
            if 'timestamp' in activity:
                hour = datetime.fromisoformat(activity['timestamp']).hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        return max(hour_counts, key=hour_counts.get) if hour_counts else None
    
    def _calculate_consistency_score(self, activities: List[Dict]) -> float:
        """计算学习一致性分数"""
        if len(activities) < 2:
            return 0.0
        
        # 简单的一致性计算：基于活动分布的均匀程度
        days = set()
        for activity in activities:
            if 'timestamp' in activity:
                day = datetime.fromisoformat(activity['timestamp']).date()
                days.add(day)
        
        # 一周内的天数比例
        consistency = len(days) / 7.0
        return min(consistency, 1.0)