# backend/app/models/homework.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Date, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Homework(Base):
    """作业表"""
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    assign_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    class_ = relationship("Class")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    submissions = relationship("HomeworkSubmission", back_populates="homework")


class HomeworkSubmission(Base):
    """作业提交表"""
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text)
    attachment = Column(String(255))
    score = Column(Float)
    comment = Column(Text)
    submit_date = Column(DateTime)
    status = Column(Integer, default=1)  # 1-未提交, 2-已提交, 3-已批改
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    homework = relationship("Homework", back_populates="submissions")
    student = relationship("User")
