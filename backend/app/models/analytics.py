# backend/app/models/analytics.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class StudentProfile(Base):
    """学生画像表"""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    learning_style = Column(String(50))
    ability_visual = Column(Float)
    ability_verbal = Column(Float)
    ability_logical = Column(Float)
    ability_mathematical = Column(Float)
    attention_duration = Column(Integer)  # 注意力持续时间（分钟）
    preferred_content_type = Column(String(50))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")


class StudentKnowledgeMastery(Base):
    """学生知识点掌握表"""
    __tablename__ = "student_knowledge_mastery"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    knowledge_point_id = Column(String(50), ForeignKey("knowledge_points.id"), nullable=False)
    mastery_level = Column(Float, nullable=False)  # 掌握程度：0-1
    last_practice_time = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    knowledge_point = relationship("KnowledgePoint")


class MistakeCollection(Base):
    """错题集表"""
    __tablename__ = "mistake_collections"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    exam_record_id = Column(Integer, ForeignKey("exam_records.id"))
    wrong_answer = Column(Text)
    mistake_type = Column(String(50))
    mistake_analysis = Column(Text)
    review_count = Column(Integer, default=0)
    status = Column(Integer, default=1)  # 1-未掌握, 2-已掌握
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    question = relationship("Question")
    exam_record = relationship("ExamRecord")


class Note(Base):
    """笔记表"""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    knowledge_point_id = Column(String(50), ForeignKey("knowledge_points.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    subject = relationship("Subject")
    knowledge_point = relationship("KnowledgePoint")


class LearningPath(Base):
    """学习路径表"""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    subject = relationship("Subject")
    nodes = relationship("LearningPathNode", back_populates="path")


class LearningPathNode(Base):
    """学习路径节点表"""
    __tablename__ = "learning_path_nodes"

    id = Column(Integer, primary_key=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    knowledge_point_id = Column(String(50), ForeignKey("knowledge_points.id"), nullable=False)
    sequence = Column(Integer, nullable=False)
    status = Column(Integer, default=0)  # 0-未开始, 1-学习中, 2-已完成
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    path = relationship("LearningPath", back_populates="nodes")
    knowledge_point = relationship("KnowledgePoint")


class StudentPerformance(Base):
    """学生表现分析表"""
    __tablename__ = "student_performances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    semester = Column(String(20), nullable=False)
    average_score = Column(Float)
    ranking = Column(Integer)
    progress_rate = Column(Float)
    study_time = Column(Integer)  # 学习时长（分钟）
    assignment_completion_rate = Column(Float)
    exam_pass_rate = Column(Float)
    knowledge_mastery = Column(JSON)  # 知识点掌握情况
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    subject = relationship("Subject")
    class_ = relationship("Class")


class LearningBehavior(Base):
    """学习行为分析表"""
    __tablename__ = "learning_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    study_duration = Column(Integer)  # 学习时长（分钟）
    resource_views = Column(Integer)  # 资源查看次数
    question_attempts = Column(Integer)  # 题目尝试次数
    correct_rate = Column(Float)  # 正确率
    focus_duration = Column(Integer)  # 专注时长（分钟）
    activity_type = Column(String(50))  # 活动类型
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    student = relationship("User")


class LearningPathAnalysis(Base):
    """学习路径分析表"""
    __tablename__ = "learning_path_analyses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    target_score = Column(Float)
    current_level = Column(String(20))
    weak_points = Column(JSON)  # 薄弱环节
    recommended_resources = Column(JSON)  # 推荐资源
    study_plan = Column(JSON)  # 学习计划
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(Integer, default=1)  # 1-进行中, 2-已完成, 3-已放弃
    completion_rate = Column(Float, default=0)
    path_data = Column(JSON)  # 路径数据
    analysis_result = Column(JSON)  # 分析结果
    recommendations = Column(JSON)  # 推荐建议
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    subject = relationship("Subject")


class TeachingAnalysis(Base):
    """教学分析表"""
    __tablename__ = "teaching_analyses"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    semester = Column(String(20), nullable=False)
    average_score = Column(Float)
    pass_rate = Column(Float)
    excellent_rate = Column(Float)
    score_distribution = Column(JSON)  # 分数分布
    knowledge_points_analysis = Column(JSON)  # 知识点掌握分析
    improvement_suggestions = Column(Text)  # 改进建议
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    teacher = relationship("Teacher")
    class_ = relationship("Class")
    subject = relationship("Subject")


class LearningRecommendation(Base):
    """学习推荐表"""
    __tablename__ = "learning_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    knowledge_point = Column(String(100))
    difficulty_level = Column(Integer)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    reason = Column(Text)
    priority = Column(Integer)
    status = Column(Integer, default=1)  # 1-未开始, 2-进行中, 3-已完成
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    subject = relationship("Subject")