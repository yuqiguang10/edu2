# backend/app/ai/agents/student_agent.py
"""
学生AI Agent - 实现完整的学生学习支持流程
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.ai.agents.base_agent import BaseAgent
from app.models.question import Question
from app.models.analytics import StudentKnowledgeMastery, MistakeCollection
from app.models.homework import Homework
from app.models.exam import Exam
from app.core.database import get_db


@dataclass
class LearningState:
    """学习状态"""
    is_new_session: bool
    last_activity: Optional[datetime]
    current_focus_level: float
    session_duration: int
    context_type: str  # 'study', 'homework', 'exam', 'review'


@dataclass
class Recommendation:
    """推荐项"""
    type: str  # 'practice_questions', 'video_content', 'mistake_analysis', 'learning_path'
    title: str
    description: str
    priority: int  # 1-5, 5为最高优先级
    knowledge_points: List[str]
    estimated_time: int  # 预估时间（分钟）
    data: Dict[str, Any]


class StudentAIAgent(BaseAgent):
    """学生AI Agent - 实现完整的学生学习支持流程"""
    
    async def on_startup(self) -> Dict[str, Any]:
        """Agent启动流程"""
        # 检测学习状态 - 对应流程图S3
        learning_state = await self.detect_learning_state()
        
        if learning_state.is_new_session:
            # 获取学习进度 - 对应流程图S4
            progress = await self.get_learning_progress()
            context = {"type": "new_session", "progress": progress}
        else:
            # 分析当前行为 - 对应流程图S5
            behavior = await self.analyze_current_behavior()
            context = {"type": "continuing", "behavior": behavior}
        
        # 生成个性化推荐 - 对应流程图S6
        recommendations = await self.generate_personalized_recommendations(context)
        
        return {
            "status": "active",
            "learning_state": learning_state.__dict__,
            "recommendations": [rec.__dict__ for rec in recommendations],
            "actions": await self.prepare_actions(recommendations),
            "context": context
        }
    
    async def on_shutdown(self):
        """关闭时保存会话数据"""
        await self.log_activity("agent_shutdown", {
            "session_duration": (datetime.now() - self.session_context["startup_time"]).total_seconds(),
            "final_state": self.session_context
        })
    
    async def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户行为"""
        action_type = action.get("type")
        
        # 记录用户行为 - 对应流程图S8
        await self.record_learning_data(action_type, action)
        
        # 根据行为类型处理
        if action_type == "start_learning":
            return await self._handle_start_learning(action)
        elif action_type == "answer_question":
            return await self._handle_answer_question(action)
        elif action_type == "view_content":
            return await self._handle_view_content(action)
        elif action_type == "request_help":
            return await self._handle_request_help(action)
        elif action_type == "complete_homework":
            return await self._handle_complete_homework(action)
        else:
            return await self._handle_general_action(action)
    
    async def detect_learning_state(self) -> LearningState:
        """检测学习状态 - 对应流程图S3"""
        # 获取最近活动
        recent_activities = await self.knowledge_base.get_recent_activities(self.user_id, hours=1)
        
        last_activity = None
        if recent_activities:
            last_activity = datetime.fromisoformat(recent_activities[0]['timestamp'])
        
        # 判断是否为新会话
        is_new_session = (
            not last_activity or 
            (datetime.now() - last_activity).total_seconds() > 3600  # 1小时间隔
        )
        
        # 计算专注度
        focus_level = await self._calculate_focus_level(recent_activities)
        
        # 计算会话时长
        session_duration = 0
        if not is_new_session and recent_activities:
            session_duration = sum(
                activity.get('session_duration', 0) 
                for activity in recent_activities
            )
        
        # 推断当前上下文
        context_type = await self._infer_context_type(recent_activities)
        
        return LearningState(
            is_new_session=is_new_session,
            last_activity=last_activity,
            current_focus_level=focus_level,
            session_duration=session_duration,
            context_type=context_type
        )
    
    async def get_learning_progress(self) -> Dict[str, Any]:
        """获取学习进度 - 对应流程图S4"""
        with next(get_db()) as db:
            # 获取知识点掌握情况
            mastery_records = db.query(StudentKnowledgeMastery).filter(
                StudentKnowledgeMastery.student_id == self.user_id
            ).all()
            
            total_points = len(mastery_records) if mastery_records else 1
            mastered_points = len([m for m in mastery_records if m.mastery_level >= 0.8])
            
            progress = {
                "overall_progress": mastered_points / total_points,
                "total_knowledge_points": total_points,
                "mastered_points": mastered_points,
                "weak_points": await self._identify_weak_points(),
                "recent_improvements": await self._get_recent_improvements(),
                "next_goals": await self._suggest_next_goals()
            }
            
            return progress
    
    async def analyze_current_behavior(self) -> Dict[str, Any]:
        """分析当前行为 - 对应流程图S5"""
        recent_activities = await self.knowledge_base.get_recent_activities(self.user_id, hours=24)
        
        if not recent_activities:
            return {"type": "inactive", "patterns": []}
        
        # 分析行为模式
        patterns = await self._analyze_behavior_patterns(recent_activities)
        
        # 分析学习效率
        efficiency = await self._calculate_learning_efficiency(recent_activities)
        
        # 检测学习困难
        difficulties = await self._detect_learning_difficulties(recent_activities)
        
        return {
            "type": "active",
            "patterns": patterns,
            "efficiency": efficiency,
            "difficulties": difficulties,
            "focus_trends": await self._analyze_focus_trends(recent_activities),
            "preferred_times": await self._identify_preferred_learning_times(recent_activities)
        }
    
    async def generate_personalized_recommendations(self, context: Dict[str, Any]) -> List[Recommendation]:
        """生成个性化推荐 - 对应流程图S6"""
        recommendations = []
        
        # 获取学生画像
        profile = await self.knowledge_base.get_user_profile(self.user_id)
        
        # 获取薄弱知识点
        weak_points = await self._identify_weak_points()
        
        # 获取学习偏好
        preferences = await self._get_learning_preferences()
        
        # 基于上下文生成不同类型的推荐
        if context["type"] == "new_session":
            recommendations.extend(await self._generate_session_start_recommendations(context, weak_points))
        else:
            recommendations.extend(await self._generate_continuation_recommendations(context, weak_points))
        
        # 添加错题复习推荐
        mistake_recommendations = await self._generate_mistake_review_recommendations()
        recommendations.extend(mistake_recommendations)
        
        # 添加学习路径推荐
        path_recommendations = await self._generate_learning_path_recommendations(profile, weak_points)
        recommendations.extend(path_recommendations)
        
        # 按优先级排序
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    async def execute_recommendations(self, recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
        """执行推荐动作 - 对应流程图S7"""
        actions = []
        
        for rec in recommendations:
            if rec.type == "practice_questions":
                # 推送练习题 - S7a
                questions = await self._get_recommended_questions(rec.knowledge_points)
                actions.append({
                    "type": "push_questions",
                    "data": questions,
                    "knowledge_points": rec.knowledge_points,
                    "priority": rec.priority
                })
            
            elif rec.type == "video_content":
                # 推荐学习视频 - S7b
                videos = await self._get_recommended_videos(rec.data.get("topic"))
                actions.append({
                    "type": "recommend_video",
                    "data": videos,
                    "topic": rec.data.get("topic"),
                    "priority": rec.priority
                })
            
            elif rec.type == "mistake_analysis":
                # 错题分析 - S7c
                mistakes = await self._get_mistake_analysis()
                actions.append({
                    "type": "mistake_analysis",
                    "data": mistakes,
                    "priority": rec.priority
                })
            
            elif rec.type == "learning_path":
                # 学习路径推荐
                actions.append({
                    "type": "learning_path",
                    "data": rec.data,
                    "priority": rec.priority
                })
        
        return actions
    
    async def record_learning_data(self, action_type: str, data: Dict[str, Any]):
        """记录学习数据 - 对应流程图S8"""
        learning_record = {
            "user_id": self.user_id,
            "action_type": action_type,
            "timestamp": datetime.now(),
            "data": data,
            "session_id": self.session_context.get("session_id")
        }
        
        # 记录到中央知识库
        await self.knowledge_base.update_behavior_log(self.user_id, learning_record)
        
        # 实时更新用户画像 - 对应流程图S9
        await self._update_user_profile_realtime(learning_record)
    
    # ================== 私有辅助方法 ==================
    
    async def _handle_start_learning(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """处理开始学习行为"""
        subject = action.get("subject")
        topic = action.get("topic")
        
        # 生成学习建议
        suggestions = await self._generate_learning_suggestions(subject, topic)
        
        # 推荐相关资源
        resources = await self._recommend_learning_resources(subject, topic)
        
        return {
            "type": "learning_guidance",
            "suggestions": suggestions,
            "resources": resources,
            "estimated_duration": action.get("planned_duration", 30),
            "focus_tips": await self._get_focus_tips()
        }
    
    async def _handle_answer_question(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """处理答题行为"""
        question_id = action.get("question_id")
        answer = action.get("answer")
        is_correct = action.get("is_correct", False)
        time_spent = action.get("time_spent", 0)
        
        # 更新知识点掌握度
        await self._update_knowledge_mastery(question_id, is_correct, time_spent)
        
        # 如果答错，添加到错题集
        if not is_correct:
            await self._add_to_mistake_collection(question_id, answer)
        
        # 生成即时反馈
        feedback = await self._generate_answer_feedback(question_id, is_correct, time_spent)
        
        # 推荐下一题
        next_questions = await self._recommend_next_questions(question_id, is_correct)
        
        return {
            "type": "answer_feedback",
            "feedback": feedback,
            "next_questions": next_questions,
            "knowledge_update": True
        }
    
    async def _handle_view_content(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """处理内容浏览行为"""
        content_type = action.get("content_type")  # video, text, image
        content_id = action.get("content_id")
        duration = action.get("duration", 0)
        
        # 分析内容理解度
        comprehension = await self._analyze_content_comprehension(content_type, duration)
        
        # 推荐相关练习
        related_exercises = await self._recommend_related_exercises(content_id)
        
        return {
            "type": "content_feedback",
            "comprehension_score": comprehension,
            "related_exercises": related_exercises,
            "continue_suggestions": await self._suggest_content_continuation(content_id)
        }
    
    async def _handle_request_help(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """处理求助行为"""
        help_type = action.get("help_type")  # "question", "concept", "method"
        context = action.get("context", {})
        
        # 使用AI生成帮助内容
        help_prompt = await self._build_help_prompt(help_type, context)
        ai_response = await self.llm_client.generate(help_prompt, {
            "role": "student",
            "user_profile": await self.knowledge_base.get_user_profile(self.user_id)
        })
        
        # 推荐相关资源
        resources = await self._recommend_help_resources(help_type, context)
        
        return {
            "type": "ai_help",
            "help_content": ai_response,
            "resources": resources,
            "follow_up_questions": await self._generate_follow_up_questions(help_type, context)
        }
    
    async def _calculate_focus_level(self, activities: List[Dict]) -> float:
        """计算专注度水平"""
        if not activities:
            return 0.5
        
        # 基于活动频率和持续时间计算专注度
        total_time = sum(activity.get('session_duration', 0) for activity in activities)
        activity_count = len(activities)
        
        if total_time == 0:
            return 0.5
        
        # 理想的专注度：较少的切换，较长的持续时间
        avg_duration = total_time / activity_count
        focus_score = min(avg_duration / 1800, 1.0)  # 30分钟为满分
        
        return focus_score
    
    async def _infer_context_type(self, activities: List[Dict]) -> str:
        """推断当前学习上下文"""
        if not activities:
            return "general"
        
        recent_types = [activity.get('action_type', '') for activity in activities[:5]]
        
        if any('homework' in t for t in recent_types):
            return "homework"
        elif any('exam' in t for t in recent_types):
            return "exam"
        elif any('review' in t for t in recent_types):
            return "review"
        else:
            return "study"
    
    async def _identify_weak_points(self) -> List[str]:
        """识别薄弱知识点"""
        with next(get_db()) as db:
            weak_masteries = db.query(StudentKnowledgeMastery).filter(
                StudentKnowledgeMastery.student_id == self.user_id,
                StudentKnowledgeMastery.mastery_level < 0.6
            ).order_by(StudentKnowledgeMastery.mastery_level).limit(5).all()
            
            return [mastery.knowledge_point_id for mastery in weak_masteries]
    
    async def _get_recent_improvements(self) -> List[Dict[str, Any]]:
        """获取最近的进步"""
        # 这里可以实现更复杂的进步检测逻辑
        return []
    
    async def _suggest_next_goals(self) -> List[str]:
        """建议下一步学习目标"""
        weak_points = await self._identify_weak_points()
        
        goals = []
        for point in weak_points[:3]:  # 前3个最薄弱的
            goals.append(f"提高 {point} 的掌握程度")
        
        return goals
    
    async def _analyze_behavior_patterns(self, activities: List[Dict]) -> List[str]:
        """分析行为模式"""
        patterns = []
        
        if len(activities) < 5:
            return patterns
        
        # 检测学习时间模式
        hours = [datetime.fromisoformat(a['timestamp']).hour for a in activities if 'timestamp' in a]
        if hours:
            most_active_hour = max(set(hours), key=hours.count)
            patterns.append(f"最活跃时间: {most_active_hour}:00-{most_active_hour+1}:00")
        
        # 检测学习习惯
        durations = [a.get('session_duration', 0) for a in activities]
        if durations:
            avg_duration = sum(durations) / len(durations)
            if avg_duration > 1800:  # 30分钟
                patterns.append("倾向于长时间学习")
            else:
                patterns.append("倾向于短时间学习")
        
        return patterns
    
    async def _calculate_learning_efficiency(self, activities: List[Dict]) -> float:
        """计算学习效率"""
        if not activities:
            return 0.5
        
        # 简化的效率计算：基于正确率和时间效率
        correct_answers = len([a for a in activities if a.get('action_type') == 'answer_question' and a.get('data', {}).get('is_correct')])
        total_answers = len([a for a in activities if a.get('action_type') == 'answer_question'])
        
        if total_answers == 0:
            return 0.5
        
        accuracy = correct_answers / total_answers
        return min(accuracy * 1.2, 1.0)  # 给准确率一些加权
    
    async def _detect_learning_difficulties(self, activities: List[Dict]) -> List[str]:
        """检测学习困难"""
        difficulties = []
        
        # 检测连续答错
        wrong_answers = [a for a in activities if a.get('action_type') == 'answer_question' and not a.get('data', {}).get('is_correct')]
        if len(wrong_answers) >= 3:
            difficulties.append("连续答错，可能遇到理解困难")
        
        # 检测学习时间异常
        recent_study_time = sum(a.get('session_duration', 0) for a in activities[-5:])
        if recent_study_time > 7200:  # 超过2小时
            difficulties.append("学习时间过长，可能效率不高")
        
        return difficulties
    
    async def _generate_session_start_recommendations(self, context: Dict, weak_points: List[str]) -> List[Recommendation]:
        """生成会话开始推荐"""
        recommendations = []
        
        # 推荐复习薄弱知识点
        if weak_points:
            recommendations.append(Recommendation(
                type="practice_questions",
                title="巩固薄弱知识点",
                description=f"针对 {', '.join(weak_points[:2])} 的专项练习",
                priority=4,
                knowledge_points=weak_points[:2],
                estimated_time=20,
                data={"focus": "weak_points"}
            ))
        
        # 推荐每日练习
        recommendations.append(Recommendation(
            type="practice_questions",
            title="每日练习",
            description="今日推荐练习题，保持学习节奏",
            priority=3,
            knowledge_points=[],
            estimated_time=15,
            data={"focus": "daily_practice"}
        ))
        
        return recommendations
    
    async def _generate_continuation_recommendations(self, context: Dict, weak_points: List[str]) -> List[Recommendation]:
        """生成继续学习推荐"""
        recommendations = []
        
        behavior = context.get("behavior", {})
        difficulties = behavior.get("difficulties", [])
        
        if difficulties:
            # 如果有困难，推荐针对性帮助
            recommendations.append(Recommendation(
                type="video_content",
                title="概念讲解视频",
                description="针对当前困难的概念讲解",
                priority=5,
                knowledge_points=weak_points[:1],
                estimated_time=10,
                data={"topic": "concept_explanation"}
            ))
        
        return recommendations
    
    async def _generate_mistake_review_recommendations(self) -> List[Recommendation]:
        """生成错题复习推荐"""
        with next(get_db()) as db:
            recent_mistakes = db.query(MistakeCollection).filter(
                MistakeCollection.student_id == self.user_id,
                MistakeCollection.status == 1  # 未掌握
            ).limit(5).all()
            
            if recent_mistakes:
                return [Recommendation(
                    type="mistake_analysis",
                    title="错题复习",
                    description=f"复习 {len(recent_mistakes)} 道错题",
                    priority=4,
                    knowledge_points=[],
                    estimated_time=15,
                    data={"mistake_ids": [m.id for m in recent_mistakes]}
                )]
        
        return []
    
    async def _generate_learning_path_recommendations(self, profile: Dict, weak_points: List[str]) -> List[Recommendation]:
        """生成学习路径推荐"""
        if not weak_points:
            return []
        
        return [Recommendation(
            type="learning_path",
            title="个性化学习路径",
            description="基于你的学习情况定制的学习路径",
            priority=3,
            knowledge_points=weak_points,
            estimated_time=30,
            data={"path_type": "personalized", "weak_points": weak_points}
        )]
    
    async def prepare_actions(self, recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
        """准备执行动作"""
        return await self.execute_recommendations(recommendations)
    
    async def _update_user_profile_realtime(self, learning_record: Dict[str, Any]):
        """实时更新用户画像"""
        # 这里可以实现实时的画像更新逻辑
        # 例如：更新学习时间偏好、答题速度、专注度等
        pass