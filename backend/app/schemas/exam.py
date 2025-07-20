from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ExamStatus(str, Enum):
    """考试状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published" 
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionBase(BaseModel):
    """题目基础模式"""
    question_text: str
    options: Optional[str] = None
    answer: str
    explanation: Optional[str] = None
    is_objective: bool = True


class QuestionCreate(QuestionBase):
    """创建题目模式"""
    question_type_id: int
    subject_id: int
    difficulty_id: int
    knowledge_point_ids: List[str] = []


class QuestionInDB(QuestionBase):
    """数据库中的题目模式"""
    id: int
    question_id: str
    question_type_id: int
    subject_id: int
    difficulty_id: int
    save_num: int = 0
    status: int = 1
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionResponse(QuestionInDB):
    """题目响应模式"""
    knowledge_points: List[str] = []
    difficulty_name: Optional[str] = None
    subject_name: Optional[str] = None


class ExamQuestionCreate(BaseModel):
    """考试题目创建模式"""
    question_id: int
    score: float
    sequence: int = 0


class ExamBase(BaseModel):
    """考试基础模式"""
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    duration: int = Field(..., gt=0, description="考试时长(分钟)")
    total_score: float = Field(..., gt=0)


class ExamCreate(ExamBase):
    """创建考试模式"""
    class_id: int
    subject_id: int
    start_time: datetime
    end_time: datetime
    questions: List[ExamQuestionCreate] = []


class ExamUpdate(BaseModel):
    """更新考试模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[ExamStatus] = None


class ExamInDB(ExamBase):
    """数据库中的考试模式"""
    id: int
    class_id: int
    subject_id: int
    teacher_id: int
    start_time: datetime
    end_time: datetime
    status: ExamStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExamResponse(ExamInDB):
    """考试响应模式"""
    subject_name: Optional[str] = None
    class_name: Optional[str] = None
    teacher_name: Optional[str] = None
    question_count: int = 0


class AnswerSubmission(BaseModel):
    """答案提交模式"""
    question_id: int
    answer: str


class ExamSubmission(BaseModel):
    """考试提交模式"""
    answers: List[AnswerSubmission]


class ExamRecordResponse(BaseModel):
    """考试记录响应"""
    id: int
    exam_id: int
    student_id: int
    start_time: datetime
    submit_time: Optional[datetime] = None
    total_score: Optional[float] = None
    status: int
    exam_title: Optional[str] = None
    
    class Config:
        from_attributes = True
