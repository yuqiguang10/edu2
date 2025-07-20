# backend/app/schemas/class_management.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum


class AssignmentType(str, Enum):
    """分配类型枚举"""
    CLASS_TEACHER = "class_teacher"
    SUBJECT_TEACHER = "subject_teacher"


class LearningLevel(str, Enum):
    """学习水平枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"


class LearningStyle(str, Enum):
    """学习风格枚举"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"


class ClassCreateRequest(BaseModel):
    """班级创建请求"""
    name: str = Field(..., max_length=50, description="班级名称")
    grade_name: str = Field(..., max_length=50, description="年级名称")
    study_level_id: int = Field(..., description="学段ID")
    description: Optional[str] = Field(None, description="班级描述")
    academic_year: str = Field(default="2023-2024", description="学年")
    semester: str = Field(default="上学期", description="学期")
    max_students: int = Field(default=50, ge=1, le=100, description="最大学生数")
    class_motto: Optional[str] = Field(None, max_length=200, description="班级口号")
    class_rules: Optional[str] = Field(None, description="班级规则")


class ClassResponse(BaseModel):
    """班级响应"""
    id: int
    name: str
    grade_name: str
    study_level_id: int
    description: Optional[str] = None
    status: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClassTeacherAssignmentRequest(BaseModel):
    """班级教师分配请求"""
    teacher_id: int = Field(..., description="教师ID")
    subject_id: int = Field(..., description="学科ID")
    assignment_type: AssignmentType = Field(..., description="分配类型")


class ClassTeacherAssignmentResponse(BaseModel):
    """班级教师分配响应"""
    id: int
    class_id: int
    teacher_id: int
    subject_id: int
    assignment_type: str
    start_date: date
    end_date: Optional[date] = None
    is_active: bool

    class Config:
        from_attributes = True


class StudentImportResponse(BaseModel):
    """学生导入响应"""
    id: int
    task_name: str
    class_id: int
    total_count: int
    success_count: int
    failed_count: int
    status: str
    error_log: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HomeworkCreateRequest(BaseModel):
    """作业创建请求"""
    title: str = Field(..., max_length=100, description="作业标题")
    description: Optional[str] = Field(None, description="作业描述")
    class_id: int = Field(..., description="班级ID")
    subject_id: int = Field(..., description="学科ID")
    assign_date: date = Field(..., description="布置日期")
    due_date: date = Field(..., description="截止日期")
    student_ids: Optional[List[int]] = Field(None, description="指定学生ID列表")
    
    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'assign_date' in values and v <= values['assign_date']:
            raise ValueError('截止日期必须晚于布置日期')
        return v


class ExamCreateRequest(BaseModel):
    """考试创建请求"""
    title: str = Field(..., max_length=100, description="考试标题")
    description: Optional[str] = Field(None, description="考试描述")
    class_id: int = Field(..., description="班级ID")
    subject_id: Optional[int] = Field(None, description="学科ID")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    duration: Optional[int] = Field(None, description="考试时长(分钟)")
    total_score: float = Field(..., gt=0, description="总分")
    student_ids: Optional[List[int]] = Field(None, description="指定学生ID列表")
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v


class HomeworkAssignmentResponse(BaseModel):
    """作业分配响应"""
    assignment_id: int
    homework_id: int
    title: str
    description: Optional[str] = None
    subject_name: Optional[str] = None
    assign_date: date
    due_date: datetime
    status: str
    submitted: bool
    score: Optional[float] = None
    late_submission: bool


class ExamAssignmentResponse(BaseModel):
    """考试分配响应"""
    assignment_id: int
    exam_id: int
    title: str
    description: Optional[str] = None
    subject_name: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration: Optional[int] = None
    status: str
    submitted: bool
    score: Optional[float] = None
    total_score: float


class StudentAssignmentResponse(BaseModel):
    """学生作业考试响应"""
    homeworks: List[HomeworkAssignmentResponse]
    exams: List[ExamAssignmentResponse]


class GradeHomeworkRequest(BaseModel):
    """作业批改请求"""
    score: float = Field(..., ge=0, description="得分")
    comment: Optional[str] = Field(None, description="评语")


class GradeExamRequest(BaseModel):
    """考试批改请求"""
    score: float = Field(..., ge=0, description="得分")
    comment: Optional[str] = Field(None, description="评语")


class StudentLearningProfileResponse(BaseModel):
    """学生学习画像响应"""
    id: int
    student_id: int
    class_id: int
    learning_level: Optional[str] = None
    learning_style: Optional[str] = None
    attention_span: Optional[int] = None
    study_efficiency: Optional[float] = None
    math_ability: Optional[float] = None
    language_ability: Optional[float] = None
    science_ability: Optional[float] = None
    arts_ability: Optional[float] = None
    homework_completion_rate: Optional[float] = None
    exam_performance_trend: Optional[str] = None
    mistake_pattern: Optional[Dict[str, Any]] = None
    knowledge_gaps: Optional[List[str]] = None
    preferred_difficulty: Optional[str] = None
    preferred_question_types: Optional[List[str]] = None
    optimal_study_time: Optional[Dict[str, Any]] = None
    recommended_resources: Optional[List[Dict[str, Any]]] = None
    recommended_exercises: Optional[List[Dict[str, Any]]] = None
    learning_suggestions: Optional[str] = None
    last_analysis_date: Optional[datetime] = None
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True


class LearningRecommendationResponse(BaseModel):
    """学习推荐响应"""
    id: int
    resource_type: str
    resource_title: str
    resource_url: Optional[str] = None
    subject_name: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_time: Optional[int] = None
    recommendation_reason: Optional[str] = None
    recommendation_score: Optional[float] = None
    clicked: bool
    completed: bool


class TeachingScheduleCreateRequest(BaseModel):
    """教学进度创建请求"""
    subject_id: int = Field(..., description="学科ID")
    chapter_id: Optional[str] = Field(None, description="章节ID")
    title: str = Field(..., max_length=200, description="教学内容标题")
    description: Optional[str] = Field(None, description="内容描述")
    teaching_objectives: Optional[List[str]] = Field(None, description="教学目标")
    key_points: Optional[List[str]] = Field(None, description="重点内容")
    difficult_points: Optional[List[str]] = Field(None, description="难点内容")
    planned_date: date = Field(..., description="计划授课日期")
    duration_minutes: int = Field(default=45, ge=1, le=180, description="课时长度")
    knowledge_point_ids: Optional[List[str]] = Field(None, description="知识点ID列表")


class TeachingScheduleResponse(BaseModel):
    """教学进度响应"""
    id: int
    class_id: int
    subject_id: int
    teacher_id: int
    title: str
    description: Optional[str] = None
    planned_date: date
    actual_date: Optional[date] = None
    