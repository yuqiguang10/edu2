# backend/app/models/question.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Chapter(Base):
    """章节表"""
    __tablename__ = "chapters"

    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    upid = Column(String(50), ForeignKey("chapters.id"))
    displayorder = Column(Integer, nullable=False)
    parentpath = Column(Text, nullable=False)
    hasChild = Column(Boolean, nullable=False)
    xd = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    chid = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade_id = Column(String(50), ForeignKey("grades.id"))
    version_id = Column(String(50), ForeignKey("textbook_versions.id"))

    # 关联关系
    parent = relationship("Chapter", remote_side="Chapter.id")
    study_level = relationship("StudyLevel")
    subject = relationship("Subject")
    grade = relationship("Grade", back_populates="chapters")
    version = relationship("TextbookVersion")
    knowledge_points = relationship("KnowledgePoint", back_populates="chapter")


class KnowledgePoint(Base):
    """知识点表"""
    __tablename__ = "knowledge_points"

    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    upid = Column(String(50), ForeignKey("knowledge_points.id"))
    displayorder = Column(Integer, nullable=False)
    parentpath = Column(Text, nullable=False)
    hasChild = Column(Boolean, nullable=False)
    xd = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    chid = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    chapter_id = Column(String(50), ForeignKey("chapters.id"))

    # 关联关系
    parent = relationship("KnowledgePoint", remote_side="KnowledgePoint.id")
    study_level = relationship("StudyLevel")
    subject = relationship("Subject")
    chapter = relationship("Chapter", back_populates="knowledge_points")
    questions = relationship("QuestionKnowledge", back_populates="knowledge_point")


class QuestionType(Base):
    """题型表"""
    __tablename__ = "question_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("question_types.id"))
    is_district_question = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    parent = relationship("QuestionType", remote_side="QuestionType.id")
    questions = relationship("Question", back_populates="question_type")


class DifficultyLevel(Base):
    """难度级别表"""
    __tablename__ = "difficulty_levels"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    level = Column(Integer, nullable=False)
    description = Column(Text)

    # 关联关系
    questions = relationship("Question", back_populates="difficulty")


class Question(Base):
    """试题表"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(50), unique=True, nullable=False)
    question_type_id = Column(Integer, ForeignKey("question_types.id"), nullable=False)
    question_channel_type = Column(String(50))
    channel_type_name = Column(String(50))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    xd = Column(String(10), nullable=False)
    chid = Column(String(10), nullable=False)
    difficulty_id = Column(Integer, ForeignKey("difficulty_levels.id"), nullable=False)
    difficult_index = Column(String(10), nullable=False)
    difficult_name = Column(String(50))
    title = Column(Text)
    question_text = Column(Text, nullable=False)
    options = Column(Text)
    answer = Column(Text)
    explanation = Column(Text)
    is_objective = Column(Boolean, default=True)
    knowledge_info = Column(Text)
    save_num = Column(Integer, default=0)
    create_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    paper_source = Column(Text)
    parent_id = Column(String(50))
    paperid = Column(String(50))
    paper_title = Column(String(255))
    exam_type = Column(String(50))
    exam_name = Column(String(100))
    is_collect = Column(Boolean, default=False)
    extra_file = Column(Text)
    new_flag = Column(Boolean, default=False)
    link_paper = Column(Boolean, default=False)
    exit_paper = Column(Boolean, default=False)
    explain_sort_need = Column(Boolean, default=False)
    sub_explanation = Column(Text)
    answer_json = Column(Text)
    is_use = Column(Boolean, default=True)
    status = Column(Integer, default=1)
    terms = Column(Text)
    is_explain = Column(Boolean, default=False)
    is_on_sale = Column(Boolean, default=True)
    audio_translate = Column(Text)
    paper_type = Column(String(50))
    district_question_type_name = Column(String(100))
    xdName = Column(String(50))
    xkName = Column(String(50))
    propositional_feature_attributes = Column(Text)
    academic_ability_attributes = Column(Text)
    list = Column(Text)  # 子题目列表数据

    # 关联关系
    question_type = relationship("QuestionType", back_populates="questions")
    subject = relationship("Subject")
    difficulty = relationship("DifficultyLevel", back_populates="questions")
    knowledge_points = relationship("QuestionKnowledge", back_populates="question")
    chapters = relationship("QuestionChapter", back_populates="question")


class QuestionKnowledge(Base):
    """试题知识点关联表"""
    __tablename__ = "question_knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question_external_id = Column(String(50), nullable=False)
    knowledge_id = Column(String(50), ForeignKey("knowledge_points.id"), nullable=False)

    # 关联关系
    question = relationship("Question", back_populates="knowledge_points")
    knowledge_point = relationship("KnowledgePoint", back_populates="questions")


class QuestionChapter(Base):
    """试题章节关联表"""
    __tablename__ = "question_chapter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question_external_id = Column(String(50), nullable=False)
    chapter_id = Column(String(50), ForeignKey("chapters.id"), nullable=False)

    # 关联关系
    question = relationship("Question", back_populates="chapters")
    chapter = relationship("Chapter")

