# backend/app/ai/engines/recommendation_engine.py
"""
智能推荐引擎 - 实现个性化推荐算法
"""
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import math

from app.core.database import get_db
from app.models.question import Question, KnowledgePoint
from app.models.analytics import StudentKnowledgeMastery, LearningBehaviorLog
from app.models.content import LearningResource
from app.ai.engines.llm_client import LLMClient


class IntelligentRecommendationEngine:
    """智能推荐引擎 - 实现个性化推荐"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def generate_student_recommendations(self, student_id: int) -> List[Dict[str, Any]]:
        """为学生生成个性化推荐"""
        # 1. 获取学生画像
        profile = await self._get_student_profile(student_id)
        
        # 2. 分析学习行为
        learning_behavior = await self._analyze_learning_behavior(student_id)
        
        # 3. 识别薄弱环节
        weak_points = await self._identify_weak_points(student_id)
        
        # 4. 生成推荐
        recommendations = []
        
        # 知识点强化推荐
        for weak_point in weak_points[:3]:  # 前3个最薄弱的
            questions = await self._recommend_questions_for_knowledge_point(
                weak_point["id"], profile["difficulty_preference"]
            )
            if questions:
                recommendations.append({
                    "type": "knowledge_reinforcement",
                    "knowledge_point": weak_point,
                    "questions": questions,
                    "priority": weak_point["urgency_score"],
                    "estimated_time": len(questions) * 2  # 每题2分钟
                })
        
        # 学习路径推荐
        learning_path = await self._generate_learning_path(student_id, weak_points)
        if learning_path:
            recommendations.append({
                "type": "learning_path",
                "path": learning_path,
                "estimated_time": learning_path["total_time"],
                "priority": 4
            })
        
        # 资源推荐
        resources = await self._recommend_learning_resources(profile, weak_points)
        if resources:
            recommendations.append({
                "type": "learning_resources",
                "resources": resources,
                "priority": 3
            })
        
        # 复习推荐
        review_items = await self._recommend_review_items(student_id, profile)
        if review_items:
            recommendations.append({
                "type": "review_session",
                "items": review_items,
                "priority": 5,
                "estimated_time": len(review_items) * 3
            })
        
        # 按优先级排序
        recommendations.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    async def recommend_questions_for_knowledge_point(
        self, 
        knowledge_point_id: str, 
        difficulty_level: int,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """为特定知识点推荐题目"""
        with next(get_db()) as db:
            # 获取候选题目
            candidate_questions = db.query(Question).filter(
                Question.knowledge_point_ids.contains(knowledge_point_id),
                Question.difficulty_level <= difficulty_level + 1,
                Question.difficulty_level >= difficulty_level - 1,
                Question.status == 1
            ).all()
            
            if not candidate_questions:
                return []
            
            # AI评分算法
            scored_questions = []
            for question in candidate_questions:
                score = await self._calculate_question_score(question, difficulty_level)
                scored_questions.append((question, score))
            
            # 排序并返回top推荐
            scored_questions.sort(key=lambda x: x[1], reverse=True)
            top_questions = scored_questions[:count]
            
            return [
                {
                    "id": q[0].id,
                    "content": q[0].content,
                    "type": q[0].type,
                    "difficulty": q[0].difficulty_level,
                    "score": q[1],
                    "estimated_time": q[0].estimated_time or 120,
                    "knowledge_points": q[0].knowledge_point_ids
                }
                for q in top_questions
            ]
    
    async def _calculate_question_score(self, question: Question, target_difficulty: int) -> float:
        """计算题目推荐分数"""
        score = 0.0
        
        # 难度匹配度 (40%)
        difficulty_diff = abs(question.difficulty_level - target_difficulty)
        difficulty_score = max(0, 1 - difficulty_diff / 5) * 0.4
        score += difficulty_score
        
        # 题目质量 (30%)
        quality_score = (question.quality_score or 0.7) * 0.3
        score += quality_score
        
        # 最近使用频率 (20%) - 降低最近常用的题目权重
        usage_score = await self._calculate_usage_freshness(question.id) * 0.2
        score += usage_score
        
        # 知识点覆盖度 (10%)
        coverage_score = len(question.knowledge_point_ids or []) / 5 * 0.1
        score += min(coverage_score, 0.1)
        
        return min(score, 1.0)
    
    async def _calculate_usage_freshness(self, question_id: int) -> float:
        """计算题目使用新鲜度"""
        with next(get_db()) as db:
            # 查询最近30天内的使用次数
            recent_usage = db.query(LearningBehaviorLog).filter(
                LearningBehaviorLog.action_type == "answer_question",
                LearningBehaviorLog.action_data.contains(str(question_id)),
                LearningBehaviorLog.timestamp >= datetime.now() - timedelta(days=30)
            ).count()
            
            # 使用次数越多，新鲜度越低
            return max(0, 1 - recent_usage / 10)
    
    async def _get_student_profile(self, student_id: int) -> Dict[str, Any]:
        """获取学生画像"""
        with next(get_db()) as db:
            from app.models.analytics import StudentProfile
            profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
            
            if profile:
                return {
                    "learning_style": profile.learning_style,
                    "difficulty_preference": self._infer_difficulty_preference(profile),
                    "attention_span": profile.attention_duration,
                    "preferred_content": profile.preferred_content_type,
                    "abilities": {
                        "visual": profile.ability_visual,
                        "verbal": profile.ability_verbal,
                        "logical": profile.ability_logical,
                        "mathematical": profile.ability_mathematical
                    }
                }
            
            # 默认画像
            return {
                "learning_style": "mixed",
                "difficulty_preference": 3,
                "attention_span": 30,
                "preferred_content": "mixed",
                "abilities": {"visual": 0.5, "verbal": 0.5, "logical": 0.5, "mathematical": 0.5}
            }
    
    def _infer_difficulty_preference(self, profile) -> int:
        """推断难度偏好"""
        # 基于能力水平推断适合的难度
        avg_ability = (profile.ability_visual + profile.ability_verbal + 
                      profile.ability_logical + profile.ability_mathematical) / 4
        
        if avg_ability >= 0.8:
            return 4  # 高难度
        elif avg_ability >= 0.6:
            return 3  # 中高难度
        elif avg_ability >= 0.4:
            return 2  # 中等难度
        else:
            return 1  # 基础难度
    
    async def _analyze_learning_behavior(self, student_id: int) -> Dict[str, Any]:
        """分析学习行为"""
        with next(get_db()) as db:
            # 获取最近30天的学习行为
            recent_behaviors = db.query(LearningBehaviorLog).filter(
                LearningBehaviorLog.student_id == student_id,
                LearningBehaviorLog.timestamp >= datetime.now() - timedelta(days=30)
            ).order_by(LearningBehaviorLog.timestamp.desc()).all()
            
            if not recent_behaviors:
                return {"activity_level": "low", "patterns": []}
            
            # 分析活动水平
            daily_activities = {}
            for behavior in recent_behaviors:
                day = behavior.timestamp.date()
                daily_activities[day] = daily_activities.get(day, 0) + 1
            
            avg_daily_activities = sum(daily_activities.values()) / len(daily_activities)
            
            activity_level = "high" if avg_daily_activities > 10 else "medium" if avg_daily_activities > 5 else "low"
            
            # 分析学习模式
            patterns = await self._identify_learning_patterns(recent_behaviors)
            
            return {
                "activity_level": activity_level,
                "avg_daily_activities": avg_daily_activities,
                "patterns": patterns,
                "total_sessions": len(recent_behaviors),
                "consistency_score": self._calculate_consistency_score(daily_activities)
            }
    
    def _calculate_consistency_score(self, daily_activities: Dict) -> float:
        """计算学习一致性分数"""
        if len(daily_activities) < 7:
            return 0.5
        
        activities_list = list(daily_activities.values())
        mean = sum(activities_list) / len(activities_list)
        
        if mean == 0:
            return 0.0
        
        # 计算变异系数
        variance = sum((x - mean) ** 2 for x in activities_list) / len(activities_list)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean if mean > 0 else 1
        
        # 变异系数越小，一致性越高
        return max(0, 1 - cv)
    
    async def _identify_learning_patterns(self, behaviors: List) -> List[str]:
        """识别学习模式"""
        patterns = []
        
        if len(behaviors) < 10:
            return patterns
        
        # 分析时间模式
        hours = [b.timestamp.hour for b in behaviors]
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        most_active_hour = max(hour_counts, key=hour_counts.get)
        if hour_counts[most_active_hour] > len(behaviors) * 0.3:
            patterns.append(f"prefer_time_{most_active_hour}")
        
        # 分析活动类型模式
        action_types = [b.action_type for b in behaviors]
        type_counts = {}
        for action_type in action_types:
            type_counts[action_type] = type_counts.get(action_type, 0) + 1
        
        most_common_action = max(type_counts, key=type_counts.get)
        if type_counts[most_common_action] > len(behaviors) * 0.4:
            patterns.append(f"prefer_activity_{most_common_action}")
        
        return patterns
    
    async def _identify_weak_points(self, student_id: int) -> List[Dict[str, Any]]:
        """识别薄弱知识点"""
        with next(get_db()) as db:
            weak_masteries = db.query(StudentKnowledgeMastery).filter(
                StudentKnowledgeMastery.student_id == student_id,
                StudentKnowledgeMastery.mastery_level < 0.7
            ).order_by(StudentKnowledgeMastery.mastery_level).limit(10).all()
            
            weak_points = []
            for mastery in weak_masteries:
                # 计算紧急度分数
                urgency = await self._calculate_urgency_score(mastery)
                
                weak_points.append({
                    "id": mastery.knowledge_point_id,
                    "name": mastery.knowledge_point.name if mastery.knowledge_point else mastery.knowledge_point_id,
                    "mastery_level": mastery.mastery_level,
                    "urgency_score": urgency,
                    "last_practice": mastery.last_practice_time
                })
            
            return weak_points
    
    async def _calculate_urgency_score(self, mastery) -> float:
        """计算知识点学习紧急度"""
        urgency = 0.0
        
        # 基于掌握水平 (40%)
        mastery_urgency = (1 - mastery.mastery_level) * 0.4
        urgency += mastery_urgency
        
        # 基于时间间隔 (30%)
        if mastery.last_practice_time:
            days_since_practice = (datetime.now() - mastery.last_practice_time).days
            time_urgency = min(days_since_practice / 30, 1.0) * 0.3
            urgency += time_urgency
        else:
            urgency += 0.3  # 从未练习过，高紧急度
        
        # 基于依赖关系 (30%) - 如果是基础知识点，紧急度更高
        dependency_urgency = await self._calculate_dependency_urgency(mastery.knowledge_point_id)
        urgency += dependency_urgency * 0.3
        
        return min(urgency, 1.0)
    
    async def _calculate_dependency_urgency(self, knowledge_point_id: str) -> float:
        """计算知识点依赖紧急度"""
        # 这里可以实现更复杂的知识图谱依赖分析
        # 简化版本：假设某些知识点是基础知识点
        basic_concepts = ["basic_arithmetic", "algebra_fundamentals", "geometry_basics"]
        
        if knowledge_point_id in basic_concepts:
            return 1.0  # 基础概念优先级最高
        
        return 0.5  # 默认中等优先级
    
    async def _generate_learning_path(self, student_id: int, weak_points: List[Dict]) -> Optional[Dict[str, Any]]:
        """生成学习路径"""
        if not weak_points:
            return None
        
        # 按紧急度和依赖关系排序
        sorted_points = sorted(weak_points, key=lambda x: x["urgency_score"], reverse=True)
        
        path_steps = []
        total_time = 0
        
        for i, point in enumerate(sorted_points[:5]):  # 最多5个步骤
            step_time = await self._estimate_learning_time(point)
            
            path_steps.append({
                "step": i + 1,
                "knowledge_point": point["name"],
                "knowledge_point_id": point["id"],
                "current_mastery": point["mastery_level"],
                "target_mastery": 0.8,
                "estimated_time": step_time,
                "recommended_actions": await self._get_recommended_actions(point)
            })
            
            total_time += step_time
        
        return {
            "total_steps": len(path_steps),
            "total_time": total_time,
            "path_steps": path_steps,
            "completion_target": "2周内完成基础巩固"
        }
    
    async def _estimate_learning_time(self, knowledge_point: Dict) -> int:
        """估算学习时间（分钟）"""
        base_time = 30  # 基础时间30分钟
        
        # 根据掌握水平调整
        mastery_gap = 0.8 - knowledge_point["mastery_level"]
        additional_time = mastery_gap * 60  # 每0.1掌握度差距增加6分钟
        
        return int(base_time + additional_time)
    
    async def _get_recommended_actions(self, knowledge_point: Dict) -> List[str]:
        """获取推荐学习行动"""
        actions = []
        
        if knowledge_point["mastery_level"] < 0.3:
            actions.extend([
                "观看基础概念讲解视频",
                "阅读相关教材章节",
                "完成基础练习题"
            ])
        elif knowledge_point["mastery_level"] < 0.6:
            actions.extend([
                "复习基础概念",
                "完成进阶练习题",
                "总结常见错误"
            ])
        else:
            actions.extend([
                "完成挑战性练习",
                "应用到综合题目中",
                "教授他人巩固理解"
            ])
        
        return actions
    
    async def _recommend_learning_resources(self, profile: Dict, weak_points: List[Dict]) -> List[Dict[str, Any]]:
        """推荐学习资源"""
        resources = []
        
        learning_style = profile.get("learning_style", "mixed")
        preferred_content = profile.get("preferred_content", "mixed")
        
        for point in weak_points[:3]:  # 前3个薄弱点
            point_resources = await self._get_resources_for_knowledge_point(
                point["id"], learning_style, preferred_content
            )
            resources.extend(point_resources)
        
        return resources[:5]  # 最多返回5个资源
    
    async def _get_resources_for_knowledge_point(
        self, 
        knowledge_point_id: str, 
        learning_style: str, 
        preferred_content: str
    ) -> List[Dict[str, Any]]:
        """为知识点获取资源"""
        with next(get_db()) as db:
            query = db.query(LearningResource).filter(
                LearningResource.knowledge_point_ids.contains(knowledge_point_id),
                LearningResource.status == 1
            )
            
            # 根据学习风格筛选
            if learning_style == "visual" and preferred_content != "mixed":
                query = query.filter(LearningResource.content_type.in_(["video", "image", "animation"]))
            elif learning_style == "verbal" and preferred_content != "mixed":
                query = query.filter(LearningResource.content_type.in_(["text", "audio", "document"]))
            
            resources = query.limit(3).all()
            
            return [
                {
                    "id": resource.id,
                    "title": resource.title,
                    "type": resource.content_type,
                    "url": resource.url,
                    "duration": resource.duration,
                    "difficulty": resource.difficulty_level,
                    "rating": resource.rating
                }
                for resource in resources
            ]
    
    async def _recommend_review_items(self, student_id: int, profile: Dict) -> List[Dict[str, Any]]:
        """推荐复习项目"""
        with next(get_db()) as db:
            # 获取需要复习的知识点（掌握度中等，但最近没有练习的）
            review_candidates = db.query(StudentKnowledgeMastery).filter(
                StudentKnowledgeMastery.student_id == student_id,
                StudentKnowledgeMastery.mastery_level.between(0.6, 0.85),
                StudentKnowledgeMastery.last_practice_time < datetime.now() - timedelta(days=7)
            ).order_by(StudentKnowledgeMastery.last_practice_time).limit(5).all()
            
            review_items = []
            for candidate in review_candidates:
                # 计算遗忘风险
                forgetting_risk = await self._calculate_forgetting_risk(candidate)
                
                if forgetting_risk > 0.3:  # 遗忘风险超过30%才推荐复习
                    review_items.append({
                        "knowledge_point_id": candidate.knowledge_point_id,
                        "knowledge_point_name": candidate.knowledge_point.name if candidate.knowledge_point else candidate.knowledge_point_id,
                        "current_mastery": candidate.mastery_level,
                        "forgetting_risk": forgetting_risk,
                        "days_since_practice": (datetime.now() - candidate.last_practice_time).days,
                        "review_priority": forgetting_risk * (1 - candidate.mastery_level)
                    })
            
            # 按复习优先级排序
            review_items.sort(key=lambda x: x["review_priority"], reverse=True)
            
            return review_items
    
    async def _calculate_forgetting_risk(self, mastery_record) -> float:
        """计算遗忘风险"""
        if not mastery_record.last_practice_time:
            return 1.0  # 从未练习，遗忘风险最高
        
        days_since_practice = (datetime.now() - mastery_record.last_practice_time).days
        
        # 简化的遗忘曲线模型
        # 假设遗忘率与掌握水平成反比，与时间间隔成正比
        base_retention = mastery_record.mastery_level
        time_factor = days_since_practice / 30  # 30天为基准
        
        forgetting_risk = 1 - (base_retention * math.exp(-0.1 * time_factor))
        
        return max(0, min(forgetting_risk, 1.0))
    
    async def generate_ai_powered_recommendations(self, student_id: int, context: str = "") -> List[Dict[str, Any]]:
        """使用AI生成更智能的推荐"""
        # 获取学生数据
        profile = await self._get_student_profile(student_id)
        behavior = await self._analyze_learning_behavior(student_id)
        weak_points = await self._identify_weak_points(student_id)
        
        # 构建AI提示词
        prompt = f"""
        基于以下学生学习数据，生成5个个性化学习推荐：
        
        学生画像：
        - 学习风格：{profile['learning_style']}
        - 注意力持续时间：{profile['attention_span']}分钟
        - 偏好内容类型：{profile['preferred_content']}
        
        学习行为分析：
        - 活动水平：{behavior['activity_level']}
        - 学习一致性：{behavior.get('consistency_score', 0.5)}
        
        薄弱知识点：{[p['name'] for p in weak_points[:3]]}
        
        当前上下文：{context}
        
        请生成JSON格式的推荐，包含以下字段：
        - type: 推荐类型（practice/review/concept/resource）
        - title: 推荐标题
        - description: 详细描述
        - priority: 优先级（1-5）
        - estimated_time: 预估时间（分钟）
        - reasoning: 推荐理由
        """
        
        try:
            ai_response = await self.llm_client.analyze_json_response(prompt, {
                "role": "student",
                "context": "recommendation_generation"
            })
            
            if ai_response.get("success", True) and isinstance(ai_response, dict):
                return ai_response.get("recommendations", [])
            
        except Exception as e:
            print(f"AI recommendation generation failed: {e}")
        
        # 如果AI生成失败，回退到基础推荐
        return await self.generate_student_recommendations(student_id)
                