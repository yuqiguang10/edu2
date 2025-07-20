from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class Exam(Base):
    """考试表"""
    __tablename__ = "exams"
    
    title = Column(String(100), nullable=False)
    description = Column(Text)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer)  # 分钟
    total_score = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="draft")  # draft, published, ongoing, completed, cancelled
    
    # 关系
    class_obj = relationship("Class", back_populates="exams")
    subject = relationship("Subject", back_populates="exams")
    teacher = relationship("Teacher", back_populates="exams")
    questions = relationship("ExamQuestion", back_populates="exam")
    records = relationship("ExamRecord", back_populates="exam")


class ExamQuestion(Base):
    """考试-题目关联表"""
    __tablename__ = "exam_questions"
    
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    score = Column(Float, nullable=False)
    sequence = Column(Integer, nullable=False, default=0)
    
    # 关系
    exam = relationship("Exam", back_populates="questions")
    question = relationship("Question", back_populates="exam_questions")


class ExamRecord(Base):
    """考试记录表"""
    __tablename__ = "exam_records"
    
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    submit_time = Column(DateTime(timezone=True))
    total_score = Column(Float)
    status = Column(Integer, nullable=False, default=1)  # 1-进行中，2-已提交，3-已批改
    
    # 关系
    student = relationship("User", back_populates="student_records")
    exam = relationship("Exam", back_populates="records")
    answers = relationship("ExamAnswer", back_populates="exam_record")


class ExamAnswer(Base):
    """考试答题记���表"""
    __tablename__ = "exam_answers"
    
    exam_record_id = Column(Integer, ForeignKey("exam_records.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(Text)
    score = Column(Float)
    is_correct = Column(Boolean)
    review_comment = Column(Text)
    
    # 关系
    exam_record = relationship("ExamRecord", back_populates="answers")
    question = relationship("Question")


class Homework(Base):
    """作业表"""
    __tablename__ = "homeworks"
    
    title = Column(String(100), nullable=False)
    description = Column(Text)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    assign_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    max_score = Column(Float, default=100)
    
    # 关系
    class_obj = relationship("Class")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    submissions = relationship("HomeworkSubmission", back_populates="homework")


class HomeworkSubmission(Base):
    """作业提交表"""
    __tablename__ = "homework_submissions"
    
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text)
    attachment = Column(String(255))
    score = Column(Float)
    comment = Column(Text)
    submit_date = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="pending")  # pending, submitted, graded
    
    # 关系
    homework = relationship("Homework", back_populates="submissions")
    student = relationship("User")
