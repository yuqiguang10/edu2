# backend/app/ai/engines/llm_client.py
"""
大语言模型客户端
"""
import os
import json
import openai
from typing import Dict, Any, List, Optional
from app.core.config import settings


class LLMClient:
    """大语言模型客户端"""
    
    def __init__(self):
        self.provider = settings.AI_MODEL_PROVIDER  # 'openai' or 'anthropic'
        self.setup_client()
    
    def setup_client(self):
        """设置客户端"""
        if self.provider == 'openai':
            openai.api_key = settings.OPENAI_API_KEY
        elif self.provider == 'anthropic':
            # 这里可以添加Anthropic客户端设置
            pass
    
    async def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """生成文本响应"""
        if self.provider == 'openai':
            return await self._generate_openai(prompt, context)
        elif self.provider == 'anthropic':
            return await self._generate_anthropic(prompt, context)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    async def _generate_openai(self, prompt: str, context: Optional[Dict] = None) -> str:
        """使用OpenAI生成响应"""
        try:
            messages = []
            
            if context:
                system_prompt = self._build_system_prompt(context)
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return "抱歉，AI服务暂时不可用。"
    
    async def _generate_anthropic(self, prompt: str, context: Optional[Dict] = None) -> str:
        """使用Anthropic生成响应"""
        # 这里可以实现Anthropic API调用
        return "Anthropic integration coming soon..."
    
    def _build_system_prompt(self, context: Dict) -> str:
        """构建系统提示词"""
        role = context.get('role', 'student')
        
        system_prompts = {
            'student': "你是一个专业的K12教育AI助手，专门为学生提供个性化学习指导。",
            'teacher': "你是一个专业的K12教育AI助手，专门为教师提供教学支持和学情分析。",
            'parent': "你是一个专业的K12教育AI助手，专门为家长提供孩子学习情况分析和建议。",
            'admin': "你是一个专业的K12教育AI助手，专门为管理员提供数据分析和系统优化建议。"
        }
        
        return system_prompts.get(role, system_prompts['student'])
    
    async def analyze_json_response(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """生成结构化JSON响应"""
        json_prompt = f"""
        {prompt}
        
        请以JSON格式回复，确保返回的内容是有效的JSON格式。
        """
        
        response = await self.generate(json_prompt, context)
        
        try:
            # 清理可能的markdown格式
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3].strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            # 如果解析失败，返回错误信息
            return {
                "error": "JSON解析失败",
                "raw_response": response,
                "success": False
            }
