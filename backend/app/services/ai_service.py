# backend/app/services/ai_service.py
import json
import httpx
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.models.analytics import StudentPerformance, LearningBehavior
from app.models.question import Question, KnowledgePoint
from app.services.analytics_service import AnalyticsService


class AIService:
    """AI服务类 - 集成LLM进行智能对话和推荐"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def chat(
        self, 
        message: str, 
        role: str, 
        user_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """AI对话主入口"""
        
        # 获取用户信息
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 根据角色构建不同的系统提示词
        system_prompt = self._build_system_prompt(role, user, context)
        
        # 构建用户画像上下文
        user_context = await self._build_user_context(user_id, role)
        
        # 调用LLM API
        response = await self._call_llm(
            system_prompt=system_prompt,
            user_message=message,
            context=user_context
        )
        
        # 处理AI响应，生成建议和资源推荐
        processed_response = await self._process_ai_response(
            response, role, user_id, message
        )
        
        return processed_response
    
    def _build_system_prompt(self, role: str, user: User, context: Dict[str, Any]) -> str:
        """构建角色专属的系统提示词"""
        
        base_info = f"""
你是一个专业的K12教育AI助手。当前用户是{user.real_name}，角色为{role}。
当前时间：{context.get('current_time', '未知')}
"""
        
        role_prompts = {
            'student': f"""
你是{user.real_name}的专属学习助手。你的任务是：
1. 帮助学生解答学习问题，提供清晰易懂的解释
2. 基于学习数据提供个性化学习建议
3. 制定学习计划，推荐适合的学习资源
4. 分析学习情况，指出薄弱环节
5. 鼓励学生，维持学习动力

回答风格：
- 亲切友好，使用学生容易理解的语言
- 多用例子和类比来解释复杂概念
- 适当使用emoji让对话更生动
- 给予积极正面的反馈
""",
            
            'teacher': f"""
你是{user.real_name}老师的教学助手。你的任务是：
1. 协助分析学生学习情况，提供数据洞察
2. 提供备课建议和教学资源推荐
3. 协助制定差异化教学方案
4. 提供作业和考试建议
5. 协助处理班级管理问题

回答风格：
- 专业严谨，基于教育理论和数据
- 提供具体可操作的建议
- 考虑教学实际情况
- 关注学生个体差异
""",
            
            'parent': f"""
你是{user.real_name}的家庭教育助手。你的任务是：
1. 帮助了解孩子的学习情况
2. 提供家庭教育建议
3. 协助家校沟通
4. 解答教育相关问题
5. 提供心理支持

回答风格：
- 温和耐心，理解家长的关切
- 提供实用的家庭教育方法
- 平衡期望与现实
- 重视孩子的身心健康
"""
        }
        
        return base_info + role_prompts.get(role, "")
    
    async def _build_user_context(self, user_id: int, role: str) -> Dict[str, Any]:
        """构建用户上下文信息"""
        
        context = {"user_id": user_id, "role": role}
        
        if role == 'student':
            # 学生上下文
            context.update(await self._get_student_context(user_id))
        elif role == 'teacher':
            # 教师上下文
            context.update(await self._get_teacher_context(user_id))
        elif role == 'parent':
            # 家长上下文
            context.update(await self._get_parent_context(user_id))
        
        return context
    
    async def _get_student_context(self, student_id: int) -> Dict[str, Any]:
        """获取学生学习上下文"""
        
        # 获取学习表现数据
        performances = self.db.query(StudentPerformance)\
            .filter(StudentPerformance.student_id == student_id)\
            .order_by(StudentPerformance.created_at.desc())\
            .limit(5).all()
        
        # 获取最近学习行为
        behaviors = self.db.query(LearningBehavior)\
            .filter(LearningBehavior.student_id == student_id)\
            .order_by(LearningBehavior.date.desc())\
            .limit(10).all()
        
        # 获取薄弱知识点
        weak_points = await self.analytics_service.get_weak_knowledge_points(student_id)
        
        return {
            "recent_performance": [
                {
                    "subject": p.subject.name if p.subject else "未知",
                    "average_score": p.average_score,
                    "ranking": p.ranking,
                    "progress_rate": p.progress_rate
                } for p in performances
            ],
            "learning_behaviors": [
                {
                    "date": b.date.strftime("%Y-%m-%d"),
                    "study_duration": b.study_duration,
                    "correct_rate": b.correct_rate,
                    "activity_type": b.activity_type
                } for b in behaviors
            ],
            "weak_knowledge_points": weak_points[:5]  # 前5个薄弱点
        }
    
    async def _get_teacher_context(self, teacher_id: int) -> Dict[str, Any]:
        """获取教师教学上下文"""
        # 这里可以添加教师相关的上下文信息
        # 比如负责的班级、学科、学生表现统计等
        return {
            "teacher_subjects": [],  # TODO: 实现教师学科信息
            "class_performance": {},  # TODO: 实现班级表现统计
        }
    
    async def _get_parent_context(self, parent_id: int) -> Dict[str, Any]:
        """获取家长上下文"""
        # 这里可以添加家长孩子的学习情况
        return {
            "children_performance": {},  # TODO: 实现孩子表现信息
        }
    
    async def _call_llm(
        self, 
        system_prompt: str, 
        user_message: str, 
        context: Dict[str, Any]
    ) -> str:
        """调用LLM API"""
        
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
用户问题: {user_message}

用户上下文: {json.dumps(context, ensure_ascii=False, indent=2)}

请基于以上信息回答用户问题。
"""}
            ]
            
            # 调用OpenAI API (或其他LLM API)
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return "抱歉，AI服务暂时不可用，请稍后再试。"
                
        except Exception as e:
            print(f"LLM API调用失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"
    
    async def _process_ai_response(
        self, 
        ai_response: str, 
        role: str, 
        user_id: int, 
        original_question: str
    ) -> Dict[str, Any]:
        """处理AI响应，添加建议和资源"""
        
        # 生成相关建议
        suggestions = await self._generate_suggestions(
            ai_response, role, user_id, original_question
        )
        
        # 推荐相关资源
        resources = await self._recommend_resources(
            ai_response, role, user_id, original_question
        )
        
        return {
            "content": ai_response,
            "suggestions": suggestions,
            "resources": resources,
            "timestamp": "now"
        }
    
    async def _generate_suggestions(
        self, 
        ai_response: str, 
        role: str, 
        user_id: int, 
        original_question: str
    ) -> List[str]:
        """生成相关建议"""
        
        suggestions = []
        
        if role == 'student':
            # 学生建议
            if "数学" in original_question or "math" in original_question.lower():
                suggestions.extend([
                    "推荐一些数学练习题",
                    "制定数学学习计划",
                    "分析我的数学薄弱点"
                ])
            if "学习计划" in original_question:
                suggestions.extend([
                    "制定本周学习计划",
                    "分析我的学习效率",
                    "推荐学习方法"
                ])
        elif role == 'teacher':
            # 教师建议
            suggestions.extend([
                "分析班级整体表现",
                "推荐教学资源",
                "制定差异化教学方案"
            ])
        elif role == 'parent':
            # 家长建议
            suggestions.extend([
                "查看孩子学习报告",
                "获取家庭教育建议",
                "了解孩子学习状态"
            ])
        
        return suggestions[:3]  # 限制建议数量
    
    async def _recommend_resources(
        self, 
        ai_response: str, 
        role: str, 
        user_id: int, 
        original_question: str
    ) -> List[Dict[str, str]]:
        """推荐相关资源"""
        
        resources = []
        
        # 根据问题内容推荐资源
        if "数学" in original_question:
            resources.append({
                "title": "数学基础练习题库",
                "url": "/resources/math-basics",
                "type": "exercise"
            })
        
        if "语文" in original_question:
            resources.append({
                "title": "语文阅读理解训练",
                "url": "/resources/chinese-reading",
                "type": "exercise"
            })
        
        # 根据角色推荐不同资源
        if role == 'teacher':
            resources.append({
                "title": "教学资源库",
                "url": "/teacher/resources",
                "type": "resource"
            })
        
        return resources[:3]  # 限制资源数量
    
    async def get_personalized_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """获取个性化推荐"""
        
        # 分析用户学习数据
        weak_points = await self.analytics_service.get_weak_knowledge_points(user_id)
        
        # 生成推荐
        recommendations = []
        
        for point in weak_points[:5]:  # 前5个薄弱点
            # 查找相关题目
            questions = self.db.query(Question)\
                .join(Question.knowledge_points)\
                .filter(Question.knowledge_points.any(knowledge_id=point['id']))\
                .limit(3).all()
            
            if questions:
                recommendations.append({
                    "id": f"rec_{point['id']}",
                    "title": f"强化 {point['name']} 练习",
                    "description": f"根据你的学习情况，建议重点练习{point['name']}相关题目",
                    "subject": point.get('subject', '未知'),
                    "difficulty": "适中",
                    "url": f"/practice/{point['id']}",
                    "type": "knowledge_point",
                    "questions_count": len(questions)
                })
        
        return recommendations