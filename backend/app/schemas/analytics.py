# backend/app/schemas/analytics.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class StudentPerformanceResponse(BaseModel):
    """学生表现响应"""
    id: int
    student_id: int
    subject_id: int
    semester: str
    average_score: Optional[float] = None
    ranking: Optional[int] = None
    progress_rate: Optional[float] = None
    study_time: Optional[int] = None
    assignment_completion_rate: Optional[float] = None
    exam_pass_rate: Optional[float] = None
    knowledge_mastery: Optional[Dict[str, Any]] = None
    subject_name: Optional[str] = None
    student_name: Optional[str] = None

    class Config:
        from_attributes = True


class LearningBehaviorResponse(BaseModel):
    """学习行为响应"""
    id: int
    student_id: int
    date: datetime
    study_duration: Optional[int] = None
    resource_views: Optional[int] = None
    question_attempts: Optional[int] = None
    correct_rate: Optional[float] = None
    focus_duration: Optional[int] = None
    activity_type: Optional[str] = None

    class Config:
        from_attributes = True


class StudentDashboardData(BaseModel):
    """学生仪表盘数据"""
    today_study_time: int = 0
    weekly_homework_count: int = 0
    accuracy_rate: float = 0.0
    total_points: int = 0
    subject_progress: List[Dict[str, Any]] = []
    weekly_stats: List[Dict[str, Any]] = []
    recent_mistakes: List[Dict[str, Any]] = []
    today_tasks: List[Dict[str, Any]] = []


class TeachingAnalysisResponse(BaseModel):
    """教学分析响应"""
    id: int
    teacher_id: int
    class_id: int
    subject_id: int
    semester: str
    average_score: Optional[float] = None
    pass_rate: Optional[float] = None
    excellent_rate: Optional[float] = None
    score_distribution: Optional[Dict[str, Any]] = None
    knowledge_points_analysis: Optional[Dict[str, Any]] = None
    improvement_suggestions: Optional[str] = None
    teacher_name: Optional[str] = None
    class_name: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True


class LearningRecommendationResponse(BaseModel):
    """学习推荐响应"""
    id: int
    student_id: int
    subject_id: int
    knowledge_point: Optional[str] = None
    difficulty_level: Optional[int] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    reason: Optional[str] = None
    priority: Optional[int] = None
    status: int
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True