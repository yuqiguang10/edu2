# backend/app/api/v1/endpoints/class_management.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_permissions, require_roles
from app.models.user import User
from app.schemas.class_management import (
    ClassCreateRequest, ClassResponse, ClassTeacherAssignmentRequest,
    ClassTeacherAssignmentResponse, StudentImportResponse, HomeworkCreateRequest,
    ExamCreateRequest, StudentAssignmentResponse, GradeHomeworkRequest,
    GradeExamRequest, StudentLearningProfileResponse, LearningRecommendationResponse,
    TeachingScheduleCreateRequest, TeachingScheduleResponse
)
from app.schemas.common import APIResponse, PaginationParams, PaginationResponse
from app.services.class_management_service import ClassManagementService

router = APIRouter()


@router.post("/classes", response_model=APIResponse[ClassResponse])
async def create_class(
    class_data: ClassCreateRequest,
    current_user: User = Depends(require_permissions("class:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """创建班级（需要班级管理权限）"""
    service = ClassManagementService(db)
    
    class_obj = service.create_class_with_info(
        class_data.dict(),
        current_user.id
    )
    
    return APIResponse(
        data=ClassResponse.from_orm(class_obj),
        message="班级创建成功"
    )


@router.get("/classes", response_model=APIResponse[PaginationResponse[ClassResponse]])
async def get_classes(
    pagination: PaginationParams = Depends(),
    study_level_id: Optional[int] = Query(None, description="学段筛选"),
    status: Optional[int] = Query(None, description="状态筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取班级列表"""
    service = ClassManagementService(db)
    
    filters = {}
    if study_level_id:
        filters["study_level_id"] = study_level_id
    if status is not None:
        filters["status"] = status
    
    classes = service.get_multi(
        skip=(pagination.page - 1) * pagination.page_size,
        limit=pagination.page_size,
        filters=filters
    )
    
    total = service.count(filters)
    
    return APIResponse(
        data=PaginationResponse(
            items=[ClassResponse.from_orm(cls) for cls in classes],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=(total + pagination.page_size - 1) // pagination.page_size
        )
    )


@router.post("/classes/{class_id}/teachers", response_model=APIResponse[ClassTeacherAssignmentResponse])
async def assign_teacher_to_class(
    class_id: int,
    assignment_data: ClassTeacherAssignmentRequest,
    current_user: User = Depends(require_permissions("class:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """分配教师到班级"""
    service = ClassManagementService(db)
    
    assignment = service.assign_teacher_to_class(
        class_id=class_id,
        teacher_id=assignment_data.teacher_id,
        subject_id=assignment_data.subject_id,
        assignment_type=assignment_data.assignment_type,
        creator_id=current_user.id
    )
    
    return APIResponse(
        data=ClassTeacherAssignmentResponse.from_orm(assignment),
        message="教师分配成功"
    )


@router.delete("/classes/{class_id}/teachers/{assignment_id}", response_model=APIResponse)
async def remove_teacher_from_class(
    class_id: int,
    assignment_id: int,
    current_user: User = Depends(require_permissions("class:manage")),
    db: Session = Depends(get_db)
) -> Any:
    """移除教师班级分配"""
    service = ClassManagementService(db)
    
    if service.remove_teacher_from_class(assignment_id):
        return APIResponse(message="教师分配移除成功")
    else:
        raise HTTPException(status_code=404, detail="分配记录不存在")


@router.get("/classes/{class_id}/teachers", response_model=APIResponse[List[dict]])
async def get_class_teachers(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取班级教师列表"""
    service = ClassManagementService(db)
    
    teachers = service.get_class_teachers(class_id)
    
    return APIResponse(data=teachers)


@router.get("/teachers/{teacher_id}/classes", response_model=APIResponse[List[dict]])
async def get_teacher_classes(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取教师负责的班级列表"""
    service = ClassManagementService(db)
    
    classes = service.get_teacher_classes(teacher_id)
    
    return APIResponse(data=classes)


@router.post("/classes/{class_id}/students/{student_id}", response_model=APIResponse)
async def add_student_to_class(
    class_id: int,
    student_id: int,
    join_reason: Optional[str] = Form(None),
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """添加学生到班级"""
    service = ClassManagementService(db)
    
    service.add_student_to_class(student_id, class_id, join_reason)
    
    return APIResponse(message="学生添加成功")


@router.delete("/classes/{class_id}/students/{student_id}", response_model=APIResponse)
async def remove_student_from_class(
    class_id: int,
    student_id: int,
    leave_reason: Optional[str] = Form(None),
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """从班级移除学生"""
    service = ClassManagementService(db)
    
    if service.remove_student_from_class(student_id, class_id, leave_reason):
        return APIResponse(message="学生移除成功")
    else:
        raise HTTPException(status_code=404, detail="学生不在该班级中")


@router.get("/classes/{class_id}/students", response_model=APIResponse[List[dict]])
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取班级学生列表"""
    service = ClassManagementService(db)
    
    students = service.get_class_students(class_id)
    
    return APIResponse(data=students)


@router.post("/classes/{class_id}/import-students", response_model=APIResponse[StudentImportResponse])
async def import_students(
    class_id: int,
    file: UploadFile = File(..., description="Excel文件"),
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """批量导入学生"""
    service = ClassManagementService(db)
    
    task = await service.import_students_from_excel(
        class_id=class_id,
        file=file,
        creator_id=current_user.id
    )
    
    return APIResponse(
        data=StudentImportResponse.from_orm(task),
        message="学生导入任务创建成功"
    )


@router.post("/homeworks", response_model=APIResponse[dict])
async def create_homework(
    homework_data: HomeworkCreateRequest,
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """创建作业"""
    service = ClassManagementService(db)
    
    # 获取教师ID
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="当前用户不是教师")
    
    homework = service.create_homework_assignment(
        homework_data.dict(),
        teacher.id,
        homework_data.student_ids
    )
    
    return APIResponse(
        data={"homework_id": homework.id},
        message="作业创建成功"
    )


@router.post("/exams", response_model=APIResponse[dict])
async def create_exam(
    exam_data: ExamCreateRequest,
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """创建考试"""
    service = ClassManagementService(db)
    
    # 获取教师ID
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="当前用户不是教师")
    
    exam = service.create_exam_assignment(
        exam_data.dict(),
        teacher.id,
        exam_data.student_ids
    )
    
    return APIResponse(
        data={"exam_id": exam.id},
        message="考试创建成功"
    )


@router.get("/students/{student_id}/assignments", response_model=APIResponse[StudentAssignmentResponse])
async def get_student_assignments(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取学生的作业和考试安排"""
    # 权限检查：学生只能查看自己的，教师和管理员可以查看所有
    if current_user.id != student_id:
        user_roles = [role.name for role in current_user.user_roles]
        if not any(role in user_roles for role in ["teacher", "admin"]):
            raise HTTPException(status_code=403, detail="权限不足")
    
    service = ClassManagementService(db)
    assignments = service.get_student_assignments(student_id)
    
    return APIResponse(
        data=StudentAssignmentResponse(**assignments)
    )


@router.post("/homework-submissions/{submission_id}/grade", response_model=APIResponse)
async def grade_homework(
    submission_id: int,
    grade_data: GradeHomeworkRequest,
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """批改作业"""
    service = ClassManagementService(db)
    
    service.grade_homework(
        submission_id=submission_id,
        grader_id=current_user.id,
        grade_data=grade_data.dict()
    )
    
    return APIResponse(message="作业批改成功")


@router.post("/exam-records/{record_id}/grade", response_model=APIResponse)
async def grade_exam(
    record_id: int,
    grade_data: GradeExamRequest,
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """批改考试"""
    service = ClassManagementService(db)
    
    service.grade_exam(
        exam_record_id=record_id,
        grader_id=current_user.id,
        grade_data=grade_data.dict()
    )
    
    return APIResponse(message="考试批改成功")


@router.get("/students/{student_id}/profile", response_model=APIResponse[StudentLearningProfileResponse])
async def get_student_learning_profile(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取学生学习画像"""
    # 权限检查
    if current_user.id != student_id:
        user_roles = [role.name for role in current_user.user_roles]
        if not any(role in user_roles for role in ["teacher", "admin", "parent"]):
            raise HTTPException(status_code=403, detail="权限不足")
    
    service = ClassManagementService(db)
    profile = await service.generate_student_learning_profile(student_id)
    
    return APIResponse(
        data=StudentLearningProfileResponse.from_orm(profile)
    )


@router.get("/students/{student_id}/recommendations", response_model=APIResponse[List[LearningRecommendationResponse]])
async def get_student_recommendations(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取学生学习推荐"""
    # 权限检查
    if current_user.id != student_id:
        user_roles = [role.name for role in current_user.user_roles]
        if not any(role in user_roles for role in ["teacher", "admin"]):
            raise HTTPException(status_code=403, detail="权限不足")
    
    service = ClassManagementService(db)
    recommendations = service.get_student_recommendations(student_id)
    
    return APIResponse(
        data=[LearningRecommendationResponse(**rec) for rec in recommendations]
    )


@router.post("/recommendations/{recommendation_id}/click", response_model=APIResponse)
async def click_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """点击推荐资源"""
    recommendation = db.query(LearningResourceRecommendation).filter(
        LearningResourceRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="推荐不存在")
    
    if recommendation.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    recommendation.clicked = True
    db.commit()
    
    return APIResponse(message="已记录点击")


@router.post("/recommendations/{recommendation_id}/complete", response_model=APIResponse)
async def complete_recommendation(
    recommendation_id: int,
    rating: Optional[int] = Form(None, ge=1, le=5),
    feedback: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """完成推荐资源"""
    recommendation = db.query(LearningResourceRecommendation).filter(
        LearningResourceRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="推荐不存在")
    
    if recommendation.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    recommendation.completed = True
    if rating:
        recommendation.rating = rating
    if feedback:
        recommendation.feedback = feedback
    
    db.commit()
    
    return APIResponse(message="已标记完成")


@router.post("/classes/{class_id}/teaching-schedule", response_model=APIResponse[TeachingScheduleResponse])
async def create_teaching_schedule(
    class_id: int,
    schedule_data: TeachingScheduleCreateRequest,
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """创建教学进度"""
    # 获取教师ID
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="当前用户不是教师")
    
    service = ClassManagementService(db)
    
    schedule_data_dict = schedule_data.dict()
    schedule_data_dict["class_id"] = class_id
    
    schedule = service.create_teaching_schedule(schedule_data_dict, teacher.id)
    
    return APIResponse(
        data=TeachingScheduleResponse.from_orm(schedule),
        message="教学进度创建成功"
    )


@router.get("/classes/{class_id}/teaching-schedule", response_model=APIResponse[List[dict]])
async def get_teaching_schedules(
    class_id: int,
    subject_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取教学进度列表"""
    service = ClassManagementService(db)
    
    schedules = service.get_teaching_schedules(class_id, subject_id)
    
    return APIResponse(data=schedules)


@router.put("/teaching-schedule/{schedule_id}", response_model=APIResponse)
async def update_teaching_schedule(
    schedule_id: int,
    update_data: dict,
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """更新教学进度"""
    schedule = db.query(TeachingSchedule).filter(
        TeachingSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="教学进度不存在")
    
    # 检查权限：只有创建者可以修改
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher or schedule.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 更新字段
    for key, value in update_data.items():
        if hasattr(schedule, key):
            setattr(schedule, key, value)
    
    db.commit()
    
    return APIResponse(message="教学进度更新成功")


# 学生端API
@router.get("/my-classes", response_model=APIResponse[List[dict]])
async def get_my_classes(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db)
) -> Any:
    """获取我的班级信息（学生用）"""
    histories = db.query(StudentClassHistory).filter(
        and_(
            StudentClassHistory.student_id == current_user.id,
            StudentClassHistory.status == "active"
        )
    ).all()
    
    result = []
    for history in histories:
        class_info = db.query(ClassInfo).filter(
            ClassInfo.class_id == history.class_id
        ).first()
        
        # 获取班主任信息
        class_teacher_assignment = db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == history.class_id,
                ClassTeacherAssignment.assignment_type == "class_teacher",
                ClassTeacherAssignment.is_active == True
            )
        ).first()
        
        class_teacher_name = None
        if class_teacher_assignment:
            teacher_user = db.query(User).filter(
                User.id == class_teacher_assignment.teacher.user_id
            ).first()
            class_teacher_name = teacher_user.real_name or teacher_user.username
        
        result.append({
            "class_id": history.class_id,
            "class_name": history.class_.name,
            "grade_name": history.class_.grade_name,
            "class_teacher_name": class_teacher_name,
            "student_count": class_info.student_count if class_info else 0,
            "join_date": history.join_date,
            "class_motto": class_info.class_motto if class_info else None
        })
    
    return APIResponse(data=result)


@router.get("/my-assignments", response_model=APIResponse[StudentAssignmentResponse])
async def get_my_assignments(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db)
) -> Any:
    """获取我的作业和考试安排"""
    service = ClassManagementService(db)
    assignments = service.get_student_assignments(current_user.id)
    
    return APIResponse(
        data=StudentAssignmentResponse(**assignments)
    )


@router.get("/my-profile", response_model=APIResponse[StudentLearningProfileResponse])
async def get_my_learning_profile(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db)
) -> Any:
    """获取我的学习画像"""
    service = ClassManagementService(db)
    profile = await service.generate_student_learning_profile(current_user.id)
    
    return APIResponse(
        data=StudentLearningProfileResponse.from_orm(profile)
    )


@router.get("/my-recommendations", response_model=APIResponse[List[LearningRecommendationResponse]])
async def get_my_recommendations(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db)
) -> Any:
    """获取我的学习推荐"""
    service = ClassManagementService(db)
    recommendations = service.get_student_recommendations(current_user.id)
    
    return APIResponse(
        data=[LearningRecommendationResponse(**rec) for rec in recommendations]
    )


# 教师端API
@router.get("/my-teaching-classes", response_model=APIResponse[List[dict]])
async def get_my_teaching_classes(
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """获取我负责的班级"""
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="当前用户不是教师")
    
    service = ClassManagementService(db)
    classes = service.get_teacher_classes(teacher.id)
    
    return APIResponse(data=classes)


@router.get("/classes/{class_id}/analysis", response_model=APIResponse[dict])
async def get_class_learning_analysis(
    class_id: int,
    current_user: User = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db)
) -> Any:
    """获取班级学习分析报告"""
    service = ClassManagementService(db)
    
    # 获取班级学生
    students = service.get_class_students(class_id)
    
    # 统计分析
    total_students = len(students)
    if total_students == 0:
        return APIResponse(data={"message": "班级暂无学生"})
    
    # 学习水平分布
    level_distribution = {"excellent": 0, "good": 0, "average": 0, "below_average": 0}
    completion_rates = []
    
    for student in students:
        if student["learning_level"]:
            level_distribution[student["learning_level"]] += 1
        if student["homework_completion_rate"]:
            completion_rates.append(student["homework_completion_rate"])
    
    # 计算平均完成率
    avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    
    # 获取近期作业和考试统计
    recent_homeworks = db.query(Homework).filter(
        and_(
            Homework.class_id == class_id,
            Homework.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    ).count()
    
    recent_exams = db.query(Exam).filter(
        and_(
            Exam.class_id == class_id,
            Exam.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    ).count()
    
    analysis_data = {
        "class_overview": {
            "total_students": total_students,
            "avg_homework_completion_rate": round(avg_completion_rate, 2),
            "recent_homeworks": recent_homeworks,
            "recent_exams": recent_exams
        },
        "learning_level_distribution": level_distribution,
        "performance_trends": {
            "improving": len([s for s in students if s.get("exam_performance_trend") == "improving"]),
            "stable": len([s for s in students if s.get("exam_performance_trend") == "stable"]),
            "declining": len([s for s in students if s.get("exam_performance_trend") == "declining"])
        }
    }
    
    return APIResponse(data=analysis_data)


# 批量操作API
@router.post("/classes/{class_id}/batch-assign-homework", response_model=APIResponse)
async def batch_assign_homework(
    class_id: int,
    homework_id: int = Form(...),
    student_ids: Optional[List[int]] = Form(None),
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """批量分配作业给学生"""
    service = ClassManagementService(db)
    
    # 如果没有指定学生，分配给班级所有学生
    if not student_ids:
        students = service.get_class_students(class_id)
        student_ids = [s["student_id"] for s in students]
    
    # 获取作业信息
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 创建分配记录
    for student_id in student_ids:
        existing = db.query(HomeworkAssignment).filter(
            and_(
                HomeworkAssignment.homework_id == homework_id,
                HomeworkAssignment.student_id == student_id
            )
        ).first()
        
        if not existing:
            assignment = HomeworkAssignment(
                homework_id=homework_id,
                student_id=student_id,
                due_date=homework.due_date
            )
            db.add(assignment)
    
    db.commit()
    
    return APIResponse(message=f"作业已分配给{len(student_ids)}名学生")


@router.post("/classes/{class_id}/batch-assign-exam", response_model=APIResponse)
async def batch_assign_exam(
    class_id: int,
    exam_id: int = Form(...),
    student_ids: Optional[List[int]] = Form(None),
    current_user: User = Depends(require_roles("teacher")),
    db: Session = Depends(get_db)
) -> Any:
    """批量分配考试给学生"""
    service = ClassManagementService(db)
    
    # 如果没有指定学生，分配给班级所有学生
    if not student_ids:
        students = service.get_class_students(class_id)
        student_ids = [s["student_id"] for s in students]
    
    # 创建分配记录
    for student_id in student_ids:
        existing = db.query(ExamAssignment).filter(
            and_(
                ExamAssignment.exam_id == exam_id,
                ExamAssignment.student_id == student_id
            )
        ).first()
        
        if not existing:
            assignment = ExamAssignment(
                exam_id=exam_id,
                student_id=student_id
            )
            db.add(assignment)
    
    db.commit()
    
    return APIResponse(message=f"考试已分配给{len(student_ids)}名学生")