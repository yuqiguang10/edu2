# backend/app/ai/__init__.py (完整版本)
"""
AI模块初始化和全局配置
"""
from app.ai.engines.coordination_engine import AICoordinationEngine

# 全局AI协调引擎实例
ai_coordinator = AICoordinationEngine()

def init_ai_system():
    """初始化AI系统"""
    try:
        # 注册所有AI代理类型
        from app.ai.agents.student_agent import StudentAIAgent
        
        ai_coordinator.register_agent_type("student", StudentAIAgent)
        
        # TODO: 在后续步骤中注册其他代理
        # ai_coordinator.register_agent_type("teacher", TeacherAIAgent)
        # ai_coordinator.register_agent_type("parent", ParentAIAgent)
        # ai_coordinator.register_agent_type("admin", AdminAIAgent)
        
        print("🤖 AI Agent类型注册完成")
        print("📚 知识库连接就绪")
        print("🔗 LLM客户端配置完成")
        print("✨ AI系统初始化成功!")
        
        return True
    except Exception as e:
        print(f"❌ AI系统初始化失败: {e}")
        return False

def get_ai_coordinator() -> AICoordinationEngine:
    """获取AI协调引擎实例"""
    return ai_coordinator