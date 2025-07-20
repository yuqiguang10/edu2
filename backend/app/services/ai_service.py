import json
import openai
import anthropic
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.ai import ChatRequest, ChatResponse, RecommendationRequest, RecommendationResponse, AnalysisRequest, AnalysisResponse


class AIService:
    """AI服务"""
    
    def __init__(self):
        self.provider = settings.AI_MODEL_PROVIDER
        
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.client = openai
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            self.client = None
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """AI聊天对话"""
        if not self.client:
            # 返回模拟响应
            return self._mock_chat_response(request)
        
        try:
            # 构建对话历史
            messages = []
            for msg in request.history[-10:]:  # 只保留最近10条消息
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": request.message
            })
            
            # 添加系统提示
            system_prompt = self._build_system_prompt(request.context)
            
            if self.provider == "openai":
                response = await self._openai_chat(messages, system_prompt)
            else:
                response = await self._anthropic_chat(messages, system_prompt)
            
            return response
            
        except Exception as e:
            return self._mock_chat_response(request)
    
    async def generate_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """生成个性化推荐"""
        if not self.client:
            return self._mock_recommendation_response(request)
        
        try:
            prompt = self._build_recommendation_prompt(request)
            
            if self.provider == "openai":
                response = await self._openai_generate(prompt)
            else:
                response = await self._anthropic_generate(prompt)
            
            return self._parse_recommendation_response(response)
            
        except Exception as e:
            return self._mock_recommendation_response(request)
    
    async def analyze_performance(self, request: AnalysisRequest) -> AnalysisResponse:
        """分析学习表现"""
        if not self.client:
            return self._mock_analysis_response(request)
        
        try:
            prompt = self._build_analysis_prompt(request)
            
            if self.provider == "openai":
                response = await self._openai_generate(prompt)
            else:
                response = await self._anthropic_generate(prompt)
            
            return self._parse_analysis_response(response)
            
        except Exception as e:
            return self._mock_analysis_response(request)
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]]) -> str:
        """构建系统提示"""
        if not context:
            return "你是一个智能教育助手，请用中文回答问题。"
        
        role = context.get("role", "student")
        
        role_prompts = {
            "student": """你是一个专门为学生设计的AI学习助手。你的主要职责是：
1. 帮助学生理解学习内容和概念
2. 提供个性化的学习建议和学习方法
3. 解答学生的学科问题
4. 鼓励学生保持学习动力
5. 分析学习进度并给出改进建议

请用友善、耐心、鼓励的语气与学生交流，用中文回答。""",
            
            "teacher": """你是一个专门为教师设计的AI教学助手。你的主要职责是：
1. 协助教师进行教学设计和课程规划
2. 提供教学资源和教学方法建议
3. 帮助分析学生学情和班级表现
4. 协助批改作业和生成教学报告
5. 提供教育教学的最新趋势和方法

请用专业、实用的语气与教师交流，用中文回答。""",
            
            "parent": """你是一个专门为家长设计的AI教育顾问。你的主要职责是：
1. 帮助家长了解孩子的学习状况
2. 提供家庭教育建议和亲子沟通技巧
3. 解答家长关于教育的疑问
4. 提供学习监督和辅导建议
5. 帮助家长与学校进行有效沟通

请用理解、支持的语气与家长交流，用中文回答。""",
            
            "admin": """你是一个专门为教育管理者设计的AI管理助手。你的主要职责是：
1. 协助进行教育数据分析和系统管理
2. 提供教育管理决策支持
3. 帮助优化教育资源配置
4. 分析教学质量和效果
5. 提供教育政策和管理建议

请用专业、客观的语气与管理者交流，用中文回答。"""
        }
        
        return role_prompts.get(role, role_prompts["student"])
    
    async def _openai_chat(self, messages: List[Dict], system_prompt: str) -> ChatResponse:
        """OpenAI聊天"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            return ChatResponse(
                message=content,
                suggestions=self._extract_suggestions(content)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API错误: {str(e)}")
    
    async def _anthropic_chat(self, messages: List[Dict], system_prompt: str) -> ChatResponse:
        """Anthropic聊天"""
        try:
            # 构建对话文本
            conversation = f"{system_prompt}\n\n"
            for msg in messages:
                role_prefix = "Human:" if msg["role"] == "user" else "Assistant:"
                conversation += f"{role_prefix} {msg['content']}\n\n"
            
            conversation += "Assistant:"
            
            response = await self.client.completions.create(
                model="claude-3-sonnet-20240229",
                prompt=conversation,
                max_tokens_to_sample=1000,
                temperature=0.7
            )
            
            content = response.completion
            
            return ChatResponse(
                message=content,
                suggestions=self._extract_suggestions(content)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Anthropic API错误: {str(e)}")
    
    def _extract_suggestions(self, content: str) -> List[str]:
        """从回复中提取建议问题"""
        # 简单的建议提取逻辑
        suggestions = [
            "我想了解更多相关内容",
            "有什么练习题推荐吗？",
            "这个知识点有什么应用？"
        ]
        return suggestions[:3]
    
    def _mock_chat_response(self, request: ChatRequest) -> ChatResponse:
        """模拟聊天响应"""
        context = request.context or {}
        role = context.get("role", "student")
        
        responses = {
            "student": [
                "我理解你的问题。让我为你详细解释一下这个知识点。",
                "这是一个很好的问题！我建议你从基础概念开始学习。",
                "根据你的学习情况，我推荐你做一些相关的练习题来巩固理解。"
            ],
            "teacher": [
                "根据学生的表现数据，我建议调整教学策略。",
                "这个班级的整体水平不错，可以适当增加难度。",
                "我为你准备了一些教学资源和练习题。"
            ],
            "parent": [
                "您的孩子学习进步很大，请继续鼓励。",
                "建议您多关注孩子的学习习惯养成。",
                "可以适当给孩子一些学习上的帮助和指导。"
            ],
            "admin": [
                "系统数据显示学生参与度有所提升。",
                "建议优化教学资源的分配策略。",
                "可以考虑引入更多的个性化学习功能。"
            ]
        }
        
        import random
        message = random.choice(responses.get(role, responses["student"]))
        
        return ChatResponse(
            message=message,
            suggestions=[
                "能详细说明一下吗？",
                "有什么具体建议吗？",
                "接下来应该怎么做？"
            ]
        )
    
    def _mock_recommendation_response(self, request: RecommendationRequest) -> RecommendationResponse:
        """模拟推荐响应"""
        from app.schemas.exam import QuestionResponse
        from app.schemas.ai import LearningPathStep
        
        # 模拟推荐题目
        questions = [
            QuestionResponse(
                id=1,
                question_id="Q001",
                question_text="解方程：2x + 5 = 13",
                answer="x = 4",
                explanation="将5移到等号右边，得到2x = 8，然后除以2得到x = 4",
                is_objective=True,
                question_type_id=1,
                subject_id=request.subject_id,
                difficulty_id=2,
                save_num=100,
                status=1,
                created_at="2024-01-01T00:00:00"
            ),
            QuestionResponse(
                id=2,
                question_id="Q002",
                question_text="计算函数f(x) = x² + 2x - 3的最小值",
                answer="f(x)最小值为-4，当x=-1时取得",
                explanation="通过求导或配方法可得到最小值",
                is_objective=False,
                question_type_id=2,
                subject_id=request.subject_id,
                difficulty_id=3,
                save_num=80,
                status=1,
                created_at="2024-01-01T00:00:00"
            )
        ]
        
        # 模拟学习路径
        learning_path = [
            LearningPathStep(
                step=1,
                title="基础概念复习",
                progress=100.0,
                resources=[]
            ),
            LearningPathStep(
                step=2,
                title="例题练习",
                progress=60.0,
                resources=[]
            ),
            LearningPathStep(
                step=3,
                title="综合应用",
                progress=0.0,
                resources=[]
            )
        ]
        
        return RecommendationResponse(
            questions=questions,
            learning_path=learning_path,
            weak_points=["函数图像", "几何证明"],
            next_goal="完成二次函数单元练习"
        )
    
    def _mock_analysis_response(self, request: AnalysisRequest) -> AnalysisResponse:
        """模拟分析响应"""
        from app.schemas.ai import TrendData
        
        trend_data = [
            TrendData(date="2024-01-01", score=75.0, subject="数学"),
            TrendData(date="2024-01-08", score=78.0, subject="数学"),
            TrendData(date="2024-01-15", score=82.0, subject="数学"),
            TrendData(date="2024-01-22", score=85.0, subject="数学"),
            TrendData(date="2024-01-29", score=88.0, subject="数学")
        ]
        
        return AnalysisResponse(
            overall_score=85.0,
            improvement=12.0,
            strengths=["逻辑推理", "计算能力", "问题分析"],
            weaknesses=["空间想象", "应用题理解"],
            recommendation="建议加强几何直观训练，多做应用题练习",
            trend_data=trend_data
        )
