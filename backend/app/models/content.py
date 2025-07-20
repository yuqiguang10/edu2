from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class TextbookVersion(Base):
    """教材版本表"""
    __tablename__ = "textbook_versions"
    
    version_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    study_level_id = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    publisher = Column(String(100))
    
    # 关系
    subject = relationship("Subject")
    study_level = relationship("StudyLevel")
    chapters = relationship("Chapter", back_populates="textbook_version")


class Chapter(Base):
    """章节表"""
    __tablename__ = "chapters"
    
    chapter_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    parent_id = Column(String(50), ForeignKey("chapters.chapter_id"))
    display_order = Column(Integer, nullable=False)
    parent_path = Column(Text, nullable=False)
    has_child = Column(Boolean, nullable=False)
    study_level_id = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    textbook_version_id = Column(String(50), ForeignKey("textbook_versions.version_id"))
    
    # 关系
    parent = relationship("Chapter", remote_side=[chapter_id])
    textbook_version = relationship("TextbookVersion", back_populates="chapters")
    knowledge_points = relationship("KnowledgePoint", back_populates="chapter")


class KnowledgePoint(Base):
    """知识点表"""
    __tablename__ = "knowledge_points"
    
    knowledge_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    parent_id = Column(String(50), ForeignKey("knowledge_points.knowledge_id"))
    display_order = Column(Integer, nullable=False)
    parent_path = Column(Text, nullable=False)
    has_child = Column(Boolean, nullable=False)
    study_level_id = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    chapter_id = Column(String(50), ForeignKey("chapters.chapter_id"))
    
    # 关系
    parent = relationship("KnowledgePoint", remote_side=[knowledge_id])
    chapter = relationship("Chapter", back_populates="knowledge_points")
    questions = relationship("QuestionKnowledge", back_populates="knowledge_point")


class QuestionType(Base):
    """题型表"""
    __tablename__ = "question_types"
    
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("question_types.id"))
    is_district_question = Column(Boolean, nullable=False, default=False)
    display_order = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=1)
    
    # 关系
    parent = relationship("QuestionType", remote_side=[Base.id])
    questions = relationship("Question", back_populates="question_type")


class DifficultyLevel(Base):
    """难度级别表"""
    __tablename__ = "difficulty_levels"
    
    name = Column(String(50), nullable=False)
    level = Column(Integer, nullable=False)
    description = Column(Text)
    
    # 关系
    questions = relationship("Question", back_populates="difficulty_level")


class Question(Base):
    """试题表"""
    __tablename__ = "questions"
    
    question_id = Column(String(50), unique=True, nullable=False)
    question_type_id = Column(Integer, ForeignKey("question_types.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    difficulty_id = Column(Integer, ForeignKey("difficulty_levels.id"), nullable=False)
    title = Column(Text)
    question_text = Column(Text, nullable=False)
    options = Column(Text)
    answer = Column(Text, nullable=False)
    explanation = Column(Text)
    is_objective = Column(Boolean, default=True)
    save_num = Column(Integer, default=0)
    paper_source = Column(Text)
    exam_type = Column(String(50))
    exam_name = Column(String(100))
    status = Column(Integer, default=1)
    
    # 关系
    question_type = relationship("QuestionType", back_populates="questions")
    difficulty_level = relationship("DifficultyLevel", back_populates="questions")
    knowledge_points = relationship("QuestionKnowledge", back_populates="question")
    exam_questions = relationship("ExamQuestion", back_populates="question")


class QuestionKnowledge(Base):
    """试题-知识点关联表"""
    __tablename__ = "question_knowledge"
    
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    knowledge_id = Column(String(50), ForeignKey("knowledge_points.knowledge_id"), nullable=False)
    
    # 关系
    question = relationship("Question", back_populates="knowledge_points")
    knowledge_point = relationship("KnowledgePoint", back_populates="questions")
