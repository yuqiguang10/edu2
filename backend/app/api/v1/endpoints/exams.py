from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.schemas.exam import (
    ExamCreate, ExamUpdate, ExamResponse, ExamSubmission,
    ExamRecordResponse, QuestionResponse
)
from app.schemas.common import APIResponse, PaginationParams, PaginationResponse
from app.services.exam_service import ExamService
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=APIResponse[PaginationResponse[ExamResponse]])
async def get_exams(
    pagination: PaginationParams = Depends(),
    class_id: int = Query(None, description="班级ID"),
    status: str = Query(None, description="考试状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取考试列表"""
    exam_service = ExamService(db)
    user_service = UserService(db)
    
    # 获取用户角色
    roles = user_service.get_user_roles(current_user.id)
    
    filters = {}
    if status:
        filters["status"] = status
    
    # 根据角色过滤数据
    if "student" in roles:
        # 学生只能看到自己班级的已发布考试
        if not class_id:
            # 这里需要获取学生的班级ID
            class_id = 1  # 简化处理
        exams = exam_service.get_exams_by_class(class_id, current_user.id)
    elif "teacher" in roles:
        # 教师可以看到自己创建的考试
        filters["teacher_id"] = current_user.id
        exams = exam_service.get_multi(
            skip=(pagination.page - 1) * pagination.page_size,
            limit=pagination.page_size,
            filters=filters
        )
    else:
        # 管理员可以看到所有考试
        exams = exam_service.get_multi(
            skip=(pagination.page - 1) * pagination.page_size,
            limit=pagination.page_size,
            filters=filters
        )
    
    total = exam_service.count(filters)
    
    # 转换为响应模型
    exam_responses = []
    for exam in exams:
        exam_responses.append(ExamResponse(
            id=exam.id,
            title=exam.title,
            description=exam.description,
            class_id=exam.class_id,
            subject_id=exam.subject_id,
            teacher_id=exam.teacher_id,
            start_time=exam.start_time,
            end_time=exam.end_time,
            duration=exam.duration,
            total_score=exam.total_score,
            status=exam.status,
            created_at=exam.created_at,
            question_count=len(exam.questions) if exam.questions else 0
        )),
        message="考试更新成功"
    )


@router.post("/{exam_id}/start", response_model=APIResponse[ExamRecordResponse])
async def start_exam(
    exam_id: int,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db)
) -> Any:
    """开始考试"""
    exam_service = ExamService(db)
    
    exam_record = exam_service.start_exam(exam_id, current_user.id)
    
    return APIResponse(
        data=ExamRecordResponse(
            id=exam_record.id,
            exam_id=exam_record.exam_id,
            student_id=exam_record.student_id,
            start_time=exam_record.start_time,
            submit_time=exam_record.submit_time,
            total_score=exam_record.total_score,
            status=exam_record.status
        ),
        message="考试开始成功"
    )


@router.post("/{exam_id}/submit", response_model=APIResponse[ExamRecordResponse])
async def submit_exam(
    exam_id: int,
    submission: ExamSubmission,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db)
) -> Any:
    """提交考试"""
    exam_service = ExamService(db)
    
    exam_record = exam_service.submit_exam(exam_id, current_user.id, submission)
    
    return APIResponse(
        data=ExamRecordResponse(
            id=exam_record.id,
            exam_id=exam_record.exam_id,
            student_id=exam_record.student_id,
            start_time=exam_record.start_time,
            submit_time=exam_record.submit_time,
            total_score=exam_record.total_score,
            status=exam_record.status
        ),
        message="考试提交成功"
    )


@router.get("/{exam_id}/questions", response_model=APIResponse[List[QuestionResponse]])
async def get_exam_questions(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取考试题目"""
    exam_service = ExamService(db)
    
    exam = exam_service.get_exam_with_questions(exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )
    
    questions = []
    for exam_question in exam.questions:
        question = exam_question.question
        questions.append(QuestionResponse(
            id=question.id,
            question_id=question.question_id,
            question_text=question.question_text,
            options=question.options,
            answer=question.answer if current_user.id == exam.teacher_id else None,  # 学生不能看到答案
            explanation=question.explanation,
            is_objective=question.is_objective,
            question_type_id=question.question_type_id,
            subject_id=question.subject_id,
            difficulty_id=question.difficulty_id,
            save_num=question.save_num,
            status=question.status,
            created_at=question.created_at
        ))
    
    return APIResponse(data=questions)


@router.get("/{exam_id}/statistics", response_model=APIResponse[dict])
async def get_exam_statistics(
    exam_id: int,
    current_user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db)
) -> Any:
    """获取考试统计"""
    exam_service = ExamService(db)
    
    statistics = exam_service.get_exam_statistics(exam_id)
    
    return APIResponse(
        data=statistics,
        message="获取统计信息成功"
    )
