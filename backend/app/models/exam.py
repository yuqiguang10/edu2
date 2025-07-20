# backend/app/models/exam.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Exam(Base):
    """考试表"""
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration = Column(Integer)  # 考试时长(分钟)
    total_score = Column(Float, nullable=False)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    class_ = relationship("Class")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    questions = relationship("ExamQuestion", back_populates="exam")
    records = relationship("ExamRecord", back_populates="exam")


class ExamQuestion(Base):
    """考试题目关联表"""
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    score = Column(Float, nullable=False)
    sequence = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    exam = relationship("Exam", back_populates="questions")
    question = relationship("Question")


class ExamRecord(Base):
    """考试记录表"""
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("homeworks.id"))
    start_time = Column(DateTime, nullable=False)
    submit_time = Column(DateTime)
    total_score = Column(Float)
    status = Column(Integer, default=1)  # 1-进行中, 2-已提交, 3-已批改
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    student = relationship("User")
    exam = relationship("Exam", back_populates="records")
    homework = relationship("Homework")
    answers = relationship("ExamAnswerRecord", back_populates="exam_record")


class ExamAnswerRecord(Base):
    """考试答题记录表"""
    __tablename__ = "exam_answer_records"

    id = Column(Integer, primary_key=True, index=True)
    exam_record_id = Column(Integer, ForeignKey("exam_records.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(Text)
    score = Column(Float)
    is_correct = Column(Boolean)
    review_comment = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    exam_record = relationship("ExamRecord", back_populates="answers")
    question = relationship("Question")
