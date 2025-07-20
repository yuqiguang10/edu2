from sqlalchemy import Column, Integer, String, Text, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class StudentProfile(Base):
    """学生画像表"""
    __tablename__ = "student_profiles"
    
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    learning_style = Column(String(50))
    ability_visual = Column(Float)
    ability_verbal = Column(Float)
    ability_logical = Column(Float)
    ability_mathematical = Column(Float)
    attention_duration = Column(Integer)  # 分钟
    preferred_content_type = Column(String(50))
    
    # 关系
    student = relationship("User")


class StudentKnowledgeMastery(Base):
    """学生知识点掌握表"""
    __tablename__ = "student_knowledge_mastery"
    
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_point_id = Column(String(50), ForeignKey("knowledge_points.knowledge_id"), nullable=False)
    mastery_level = Column(Float, nullable=False)  # 0-1
    last_practice_time = Column(DateTime(timezone=True))
    
    # 关系
    student = relationship("User")
    knowledge_point = relationship("KnowledgePoint")


class LearningBehavior(Base):
    """学习行为分析表"""
    __tablename__ = "learning_behaviors"
    
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    study_duration = Column(Integer)  # 分钟
    resource_views = Column(Integer)
    question_attempts = Column(Integer)
    correct_rate = Column(Float)
    focus_duration = Column(Integer)  # 分钟
    activity_type = Column(String(50))
    
    # 关系
    student = relationship("User")


class LearningRecommendation(Base):
    """学习推荐表"""
    __tablename__ = "learning_recommendations"
    
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    knowledge_point = Column(String(100))
    difficulty_level = Column(Integer)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    reason = Column(Text)
    priority = Column(Integer)
    status = Column(Integer, default=1)  # 1-未开始 2-进行中 3-已完成
    
    # 关系
    student = relationship("User")
    subject = relationship("Subject")
