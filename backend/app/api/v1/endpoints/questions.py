from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_roles
from app.models.user import User
from app.schemas.exam import QuestionCreate, QuestionResponse
from app.schemas.common import APIResponse, PaginationParams
from app.services.question_service import QuestionService

router = APIRouter()


@router.get("", response_model=APIResponse[dict])
async def search_questions(
    keyword: str = Query(None, description="搜索关键词"),
    subject_id: int = Query(None, description="学科ID"),
    difficulty_id: int = Query(None, description="难度ID"),
    question_type_id: int = Query(None, description="题型ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """搜索题目"""
    question_service = QuestionService(db)
    
    result = question_service.search_questions(
        keyword=keyword,
        subject_id=subject_id,
        difficulty_id=difficulty_id,
        question_type_id=question_type_id,
        page=page,
        page_size=page_size
    )
    
    # 转换为响应模型
    questions = []
    for question in result["questions"]:
        questions.append(QuestionResponse(
            id=question.id,
            question_id=question.question_id,
            question_text=question.question_text,
            options=question.options,
            answer=question.answer,
            explanation=question.explanation,
            is_objective=question.is_objective,
            question_type_id=question.question_type_id,
            subject_id=question.subject_id,
            difficulty_id=question.difficulty_id,
            save_num=question.save_num,
            status=question.status,
            created_at=question.created_at
        ))
    
    return APIResponse(
        data={
            "questions": questions,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"]
        }
    )


@router.get("/{question_id}", response_model=APIResponse[QuestionResponse])
async def get_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取题目详情"""
    question_service = QuestionService(db)
    
    question = question_service.get_question_with_knowledge_points(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    return APIResponse(
        data=QuestionResponse(
            id=question.id,
            question_id=question.question_id,
            question_text=question.question_text,
            options=question.options,
            answer=question.answer,
            explanation=question.explanation,
            is_objective=question.is_objective,
            question_type_id=question.question_type_id,
            subject_id=question.subject_id,
            difficulty_id=question.difficulty_id,
            save_num=question.save_num,
            status=question.status,
            created_at=question.created_at,
            knowledge_points=[kp.knowledge_point.knowledge_id for kp in question.knowledge_points]
        )
    )


@router.post("", response_model=APIResponse[QuestionResponse])
async def create_question(
    question_create: QuestionCreate,
    current_user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db)
) -> Any:
    """创建题目"""
    question_service = QuestionService(db)
    
    question = question_service.create_question(question_create)
    
    return APIResponse(
        data=QuestionResponse(
            id=question.id,
            question_id=question.question_id,
            question_text=question.question_text,
            options=question.options,
            answer=question.answer,
            explanation=question.explanation,
            is_objective=question.is_objective,
            question_type_id=question.question_type_id,
            subject_id=question.subject_id,
            difficulty_id=question.difficulty_id,
            save_num=question.save_num,
            status=question.status,
            created_at=question.created_at
        ),
        message="题目创建成功"
    )


@router.get("/{question_id}/similar", response_model=APIResponse[List[QuestionResponse]])
async def get_similar_questions(
    question_id: int,
    count: int = Query(5, ge=1, le=20, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取相似题目"""
    question_service = QuestionService(db)
    
    questions = question_service.get_similar_questions(question_id, count)
    
    similar_questions = []
    for question in questions:
        similar_questions.append(QuestionResponse(
            id=question.id,
            question_id=question.question_id,
            question_text=question.question_text,
            options=question.options,
            answer=question.answer,
            explanation=question.explanation,
            is_objective=question.is_objective,
            question_type_id=question.question_type_id,
            subject_id=question.subject_id,
            difficulty_id=question.difficulty_id,
            save_num=question.save_num,
            status=question.status,
            created_at=question.created_at
        ))
    
    return APIResponse(data=similar_questions)


@router.get("/recommendations/{student_id}", response_model=APIResponse[List[QuestionResponse]])
async def get_recommended_questions(
    student_id: int,
    subject_id: int = Query(..., description="学科ID"),
    count: int = Query(10, ge=1, le=50, description="推荐数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取推荐题目"""
    # 学生只能获取自己的推荐
    if student_id != current_user.id and "teacher" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    question_service = QuestionService(db)
    
    questions = question_service.get_recommended_questions(student_id, subject_id, count)
    
    recommended_questions = []
    for question in questions:
        recommended_questions.append(QuestionResponse(
            id=question.id,
            question_id=question.question_id,
            question_text=question.question_text,
            options=question.options,
            answer=question.answer,
            explanation=question.explanation,
            is_objective=question.is_objective,
            question_type_id=question.question_type_id,
            subject_id=question.subject_id,
            difficulty_id=question.difficulty_id,
            save_num=question.save_num,
            status=question.status,
            created_at=question.created_at
        ))
    
    return APIResponse(data=recommended_questions)
