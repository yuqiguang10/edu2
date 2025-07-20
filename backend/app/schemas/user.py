# backend/app/schemas/user.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserUpdate(BaseModel):
    """用户更新"""
    real_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class StudentProfileResponse(BaseModel):
    """学生画像响应"""
    id: int
    student_id: int
    learning_style: Optional[str] = None
    ability_visual: Optional[float] = None
    ability_verbal: Optional[float] = None
    ability_logical: Optional[float] = None
    ability_mathematical: Optional[float] = None
    attention_duration: Optional[int] = None
    preferred_content_type: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class ClassResponse(BaseModel):
    """班级响应"""
    id: int
    name: str
    grade_name: str
    study_level_name: Optional[str] = None
    class_teacher_name: Optional[str] = None
    student_count: int = 0
    status: int

    class Config:
        from_attributes = True


class SubjectResponse(BaseModel):
    """学科响应"""
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class KnowledgePointResponse(BaseModel):
    """知识点响应"""
    id: str
    title: str
    upid: Optional[str] = None
    displayorder: int
    hasChild: bool
    subject_name: Optional[str] = None
    chapter_title: Optional[str] = None

    class Config:
        from_attributes = True