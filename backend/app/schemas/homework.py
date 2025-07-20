# backend/app/schemas/homework.py
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime


class HomeworkCreate(BaseModel):
    """作业创建"""
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    class_id: int
    subject_id: int
    assign_date: date
    due_date: date


class HomeworkResponse(BaseModel):
    """作业响应"""
    id: int
    title: str
    description: Optional[str] = None
    assign_date: date
    due_date: date
    teacher_name: Optional[str] = None
    subject_name: Optional[str] = None
    submission_count: int = 0
    total_students: int = 0

    class Config:
        from_attributes = True


class HomeworkSubmissionCreate(BaseModel):
    """作业提交创建"""
    homework_id: int
    content: Optional[str] = None
    attachment: Optional[str] = None


class HomeworkSubmissionResponse(BaseModel):
    """作业提交响应"""
    id: int
    homework_id: int
    student_id: int
    content: Optional[str] = None
    attachment: Optional[str] = None
    score: Optional[float] = None
    comment: Optional[str] = None
    submit_date: Optional[datetime] = None
    status: int
    student_name: Optional[str] = None
    homework_title: Optional[str] = None

    class Config:
        from_attributes = True