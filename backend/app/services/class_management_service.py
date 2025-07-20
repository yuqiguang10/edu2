# backend/app/services/class_management_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, UploadFile
from datetime import datetime, date
import pandas as pd
import json

from app.models.education import Class, StudyLevel, Subject
from app.models.user import User, Teacher, Student, Role
from app.models.class_management import (
    ClassInfo, ClassTeacherAssignment, StudentClassHistory, 
    StudentImportTask, HomeworkAssignment, ExamAssignment,
    TeachingSchedule, HomeworkSubmissionDetail, ExamSubmissionDetail
)
from app.models.homework import Homework, HomeworkSubmission
from app.models.exam import Exam, ExamRecord
from app.models.analytics import StudentProfile, LearningRecommendation
from app.core.security import get_password_hash
from app.utils.excel_parser import parse_student_excel
from app.services.ai_service import AIService


class ClassManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    # ==================== 管理员功能 ====================
    
    def create_class(self, class_data: Dict[str, Any], creator_id: int) -> Class:
        """创建班级"""
        # 检查班级名称是否重复
        existing_class = self.db.query(Class).filter(
            and_(
                Class.name == class_data["name"],
                Class.grade_name == class_data["grade_name"]
            )
        ).first()
        
        if existing_class:
            raise HTTPException(status_code=400, detail="班级名称已存在")
        
        # 创建班级基础信息
        new_class = Class(
            name=class_data["name"],
            grade_name=class_data["grade_name"],
            study_level_id=class_data["study_level_id"],
            description=class_data.get("description"),
            status=1
        )
        
        self.db.add(new_class)
        self.db.flush()  # 获取班级ID
        
        # 创建班级详细信息
        class_info = ClassInfo(
            class_id=new_class.id,
            academic_year=class_data.get("academic_year", "2023-2024"),
            semester=class_data.get("semester", "上学期"),
            max_students=class_data.get("max_students", 50),
            student_count=0,
            class_motto=class_data.get("class_motto"),
            class_rules=class_data.get("class_rules"),
            created_by=creator_id
        )
        
        self.db.add(class_info)
        self.db.commit()
        
        return new_class

    def assign_teacher_to_class(
        self, 
        class_id: int, 
        teacher_id: int, 
        subject_id: int, 
        assignment_type: str
    ) -> ClassTeacherAssignment:
        """分配教师到班级"""
        # 验证班级和教师存在
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")
        
        # 检查是否已有班主任（如果分配的是班主任）
        if assignment_type == "class_teacher":
            existing_class_teacher = self.db.query(ClassTeacherAssignment).filter(
                and_(
                    ClassTeacherAssignment.class_id == class_id,
                    ClassTeacherAssignment.assignment_type == "class_teacher",
                    ClassTeacherAssignment.is_active == True
                )
            ).first()
            
            if existing_class_teacher:
                raise HTTPException(status_code=400, detail="该班级已有班主任")
        
        # 检查教师是否已分配同一科目
        existing_assignment = self.db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == class_id,
                ClassTeacherAssignment.teacher_id == teacher_id,
                ClassTeacherAssignment.subject_id == subject_id,
                ClassTeacherAssignment.is_active == True
            )
        ).first()
        
        if existing_assignment:
            raise HTTPException(status_code=400, detail="教师已分配该科目")
        
        # 创建分配记录
        assignment = ClassTeacherAssignment(
            class_id=class_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            assignment_type=assignment_type,
            is_active=True
        )
        
        self.db.add(assignment)
        
        # 如果是班主任，更新班级信息
        if assignment_type == "class_teacher":
            class_obj.class_teacher_id = teacher_id
            
        self.db.commit()
        return assignment

    def get_all_classes(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取所有班级列表"""
        offset = (page - 1) * page_size
        
        query = self.db.query(Class).filter(Class.status == 1)
        total = query.count()
        
        classes = query.offset(offset).limit(page_size).all()
        
        result = []
        for class_obj in classes:
            class_info = self.db.query(ClassInfo).filter(
                ClassInfo.class_id == class_obj.id
            ).first()
            
            # 获取班主任信息
            class_teacher = None
            if class_obj.class_teacher_id:
                teacher = self.db.query(Teacher).filter(
                    Teacher.id == class_obj.class_teacher_id
                ).first()
                if teacher:
                    teacher_user = self.db.query(User).filter(
                        User.id == teacher.user_id
                    ).first()
                    class_teacher = {
                        "id": teacher.id,
                        "name": teacher_user.real_name or teacher_user.username
                    }
            
            result.append({
                "id": class_obj.id,
                "name": class_obj.name,
                "grade_name": class_obj.grade_name,
                "student_count": class_info.student_count if class_info else 0,
                "max_students": class_info.max_students if class_info else 50,
                "class_teacher": class_teacher,
                "academic_year": class_info.academic_year if class_info else None,
                "created_at": class_obj.created_at
            })
        
        return {
            "items": result,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    def get_class_detail(self, class_id: int) -> Dict[str, Any]:
        """获取班级详细信息"""
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        class_info = self.db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id
        ).first()
        
        # 获取教师分配情况
        teacher_assignments = self.db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == class_id,
                ClassTeacherAssignment.is_active == True
            )
        ).all()
        
        teachers = []
        for assignment in teacher_assignments:
            teacher = self.db.query(Teacher).filter(
                Teacher.id == assignment.teacher_id
            ).first()
            teacher_user = self.db.query(User).filter(
                User.id == teacher.user_id
            ).first()
            subject = self.db.query(Subject).filter(
                Subject.id == assignment.subject_id
            ).first()
            
            teachers.append({
                "teacher_id": teacher.id,
                "teacher_name": teacher_user.real_name or teacher_user.username,
                "subject_name": subject.name,
                "assignment_type": assignment.assignment_type,
                "assigned_at": assignment.assigned_at
            })
        
        # 获取学生列表
        students = self.get_class_students(class_id)
        
        return {
            "id": class_obj.id,
            "name": class_obj.name,
            "grade_name": class_obj.grade_name,
            "description": class_obj.description,
            "class_info": class_info.__dict__ if class_info else None,
            "teachers": teachers,
            "students": students[:10],  # 只返回前10个学生，详细列表另外获取
            "total_students": len(students)
        }

    # ==================== 学生管理功能 ====================
    
    def add_student_to_class(
        self, 
        student_id: int, 
        class_id: int, 
        join_reason: str = None
    ) -> bool:
        """添加学生到班级"""
        # 验证学生和班级存在
        student = self.db.query(User).filter(
            and_(User.id == student_id, User.status == 1)
        ).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        # 检查学生是否已在该班级
        existing_record = self.db.query(StudentClassHistory).filter(
            and_(
                StudentClassHistory.student_id == student_id,
                StudentClassHistory.class_id == class_id,
                StudentClassHistory.status == "active"
            )
        ).first()
        
        if existing_record:
            raise HTTPException(status_code=400, detail="学生已在该班级")
        
        # 检查班级人数限制
        class_info = self.db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id
        ).first()
        
        if class_info and class_info.student_count >= class_info.max_students:
            raise HTTPException(status_code=400, detail="班级人数已满")
        
        # 创建学生班级历史记录
        history = StudentClassHistory(
            student_id=student_id,
            class_id=class_id,
            join_date=date.today(),
            join_reason=join_reason,
            status="active"
        )
        
        self.db.add(history)
        
        # 更新班级学生数量
        if class_info:
            class_info.student_count += 1
        
        self.db.commit()
        return True

    def remove_student_from_class(
        self, 
        student_id: int, 
        class_id: int, 
        leave_reason: str = None
    ) -> bool:
        """从班级移除学生"""
        history = self.db.query(StudentClassHistory).filter(
            and_(
                StudentClassHistory.student_id == student_id,
                StudentClassHistory.class_id == class_id,
                StudentClassHistory.status == "active"
            )
        ).first()
        
        if not history:
            return False
        
        # 更新记录状态
        history.status = "transferred"
        history.leave_date = date.today()
        history.leave_reason = leave_reason
        
        # 更新班级学生数量
        class_info = self.db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id
        ).first()
        
        if class_info and class_info.student_count > 0:
            class_info.student_count -= 1
        
        self.db.commit()
        return True

    def get_class_students(self, class_id: int) -> List[Dict[str, Any]]:
        """获取班级学生列表"""
        histories = self.db.query(StudentClassHistory).filter(
            and_(
                StudentClassHistory.class_id == class_id,
                StudentClassHistory.status == "active"
            )
        ).all()
        
        result = []
        for history in histories:
            student = self.db.query(User).filter(
                User.id == history.student_id
            ).first()
            
            if student:
                # 获取学生画像
                profile = self.db.query(StudentProfile).filter(
                    StudentProfile.student_id == student.id
                ).first()
                
                result.append({
                    "student_id": student.id,
                    "username": student.username,
                    "real_name": student.real_name,
                    "student_id_number": student.student_id,
                    "email": student.email,
                    "phone": student.phone,
                    "join_date": history.join_date,
                    "learning_style": profile.learning_style if profile else None,
                    "last_login": student.last_login
                })
        
        return result

    async def import_students_from_excel(
        self, 
        class_id: int, 
        file: UploadFile, 
        creator_id: int
    ) -> StudentImportTask:
        """批量导入学生"""
        # 创建导入任务
        task = StudentImportTask(
            task_name=f"批量导入_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            class_id=class_id,
            imported_by=creator_id,
            file_path=file.filename,
            status="processing"
        )
        
        self.db.add(task)
        self.db.flush()
        
        try:
            # 解析Excel文件
            file_content = await file.read()
            students_data = parse_student_excel(file_content)
            
            task.total_count = len(students_data)
            success_count = 0
            failed_count = 0
            error_log = []
            
            for idx, student_data in enumerate(students_data):
                try:
                    # 创建用户账号
                    existing_user = self.db.query(User).filter(
                        or_(
                            User.username == student_data["username"],
                            User.email == student_data["email"]
                        )
                    ).first()
                    
                    if existing_user:
                        error_log.append(f"第{idx+1}行: 用户名或邮箱已存在")
                        failed_count += 1
                        continue
                    
                    # 创建学生用户
                    new_user = User(
                        username=student_data["username"],
                        email=student_data["email"],
                        password_hash=get_password_hash(student_data.get("password", "123456")),
                        real_name=student_data.get("real_name"),
                        student_id=student_data.get("student_id_number"),
                        phone=student_data.get("phone"),
                        status=1
                    )
                    
                    self.db.add(new_user)
                    self.db.flush()
                    
                    # 分配学生角色
                    student_role = self.db.query(Role).filter(Role.name == "student").first()
                    if student_role:
                        from app.models.user import UserRole
                        user_role = UserRole(user_id=new_user.id, role_id=student_role.id)
                        self.db.add(user_role)
                    
                    # 添加到班级
                    self.add_student_to_class(
                        new_user.id, 
                        class_id, 
                        "批量导入"
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    error_log.append(f"第{idx+1}行: {str(e)}")
                    failed_count += 1
            
            # 更新任务状态
            task.success_count = success_count
            task.failed_count = failed_count
            task.error_log = "\n".join(error_log)
            task.status = "completed"
            task.completed_at = datetime.now()
            
        except Exception as e:
            task.status = "failed"
            task.error_log = str(e)
            task.completed_at = datetime.now()
        
        self.db.commit()
        return task

    # ==================== 教师功能 ====================
    
    def get_teacher_classes(self, teacher_user_id: int) -> List[Dict[str, Any]]:
        """获取教师负责的班级"""
        teacher = self.db.query(Teacher).filter(
            Teacher.user_id == teacher_user_id
        ).first()
        
        if not teacher:
            return []
        
        assignments = self.db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.teacher_id == teacher.id,
                ClassTeacherAssignment.is_active == True
            )
        ).all()
        
        result = []
        for assignment in assignments:
            class_obj = self.db.query(Class).filter(
                Class.id == assignment.class_id
            ).first()
            
            class_info = self.db.query(ClassInfo).filter(
                ClassInfo.class_id == assignment.class_id
            ).first()
            
            subject = self.db.query(Subject).filter(
                Subject.id == assignment.subject_id
            ).first()
            
            result.append({
                "class_id": class_obj.id,
                "class_name": class_obj.name,
                "grade_name": class_obj.grade_name,
                "subject_name": subject.name,
                "assignment_type": assignment.assignment_type,
                "student_count": class_info.student_count if class_info else 0,
                "is_class_teacher": assignment.assignment_type == "class_teacher"
            })
        
        return result

    def create_homework_assignment(
        self, 
        homework_data: Dict[str, Any], 
        teacher_id: int,
        student_ids: List[int] = None
    ) -> Homework:
        """创建作业并分配给学生"""
        # 创建作业
        homework = Homework(
            title=homework_data["title"],
            description=homework_data["description"],
            class_id=homework_data["class_id"],
            subject_id=homework_data["subject_id"],
            teacher_id=teacher_id,
            assign_date=homework_data.get("assign_date", date.today()),
            due_date=homework_data["due_date"]
        )
        
        self.db.add(homework)
        self.db.flush()
        
        # 分配给学生
        if student_ids:
            for student_id in student_ids:
                assignment = HomeworkAssignment(
                    homework_id=homework.id,
                    student_id=student_id,
                    due_date=homework_data["due_date"],
                    status="assigned"
                )
                self.db.add(assignment)
        else:
            # 分配给班级所有学生
            students = self.get_class_students(homework_data["class_id"])
            for student in students:
                assignment = HomeworkAssignment(
                    homework_id=homework.id,
                    student_id=student["student_id"],
                    due_date=homework_data["due_date"],
                    status="assigned"
                )
                self.db.add(assignment)
        
        self.db.commit()
        return homework

    def create_exam_assignment(
        self, 
        exam_data: Dict[str, Any], 
        teacher_id: int,
        student_ids: List[int] = None
    ) -> Exam:
        """创建考试并分配给学生"""
        # 创建考试
        exam = Exam(
            title=exam_data["title"],
            description=exam_data["description"],
            class_id=exam_data["class_id"],
            subject_id=exam_data["subject_id"],
            teacher_id=teacher_id,
            start_time=exam_data["start_time"],
            end_time=exam_data["end_time"],
            duration=exam_data.get("duration"),
            total_score=exam_data["total_score"]
        )
        
        self.db.add(exam)
        self.db.flush()
        
        # 分配给学生
        if student_ids:
            for student_id in student_ids:
                assignment = ExamAssignment(
                    exam_id=exam.id,
                    student_id=student_id,
                    start_time=exam_data["start_time"],
                    end_time=exam_data["end_time"],
                    duration_minutes=exam_data.get("duration"),
                    status="assigned"
                )
                self.db.add(assignment)
        else:
            # 分配给班级所有学生
            students = self.get_class_students(exam_data["class_id"])
            for student in students:
                assignment = ExamAssignment(
                    exam_id=exam.id,
                    student_id=student["student_id"],
                    start_time=exam_data["start_time"],
                    end_time=exam_data["end_time"],
                    duration_minutes=exam_data.get("duration"),
                    status="assigned"
                )
                self.db.add(assignment)
        
        self.db.commit()
        return exam

    def grade_homework(
        self, 
        submission_id: int, 
        grader_id: int, 
        grade_data: Dict[str, Any]
    ) -> bool:
        """批改作业"""
        submission = self.db.query(HomeworkSubmission).filter(
            HomeworkSubmission.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="作业提交不存在")
        
        # 更新作业成绩和评语
        submission.score = grade_data.get("score")
        submission.comment = grade_data.get("comment")
        submission.status = 3  # 已批改
        
        # 更新作业分配状态
        assignment = self.db.query(HomeworkAssignment).filter(
            and_(
                HomeworkAssignment.homework_id == submission.homework_id,
                HomeworkAssignment.student_id == submission.student_id
            )
        ).first()
        
        if assignment:
            assignment.status = "graded"
            assignment.final_score = grade_data.get("score")
        
        self.db.commit()
        return True

    # ==================== 学生功能 ====================
    
    def get_student_assignments(self, student_id: int) -> Dict[str, Any]:
        """获取学生的作业和考试安排"""
        # 获取作业
        homework_assignments = self.db.query(HomeworkAssignment).filter(
            HomeworkAssignment.student_id == student_id
        ).all()
        
        homeworks = []
        for assignment in homework_assignments:
            homework = self.db.query(Homework).filter(
                Homework.id == assignment.homework_id
            ).first()
            
            if homework:
                submission = self.db.query(HomeworkSubmission).filter(
                    and_(
                        HomeworkSubmission.homework_id == homework.id,
                        HomeworkSubmission.student_id == student_id
                    )
                ).first()
                
                homeworks.append({
                    "id": homework.id,
                    "title": homework.title,
                    "description": homework.description,
                    "due_date": assignment.due_date,
                    "status": assignment.status,
                    "score": assignment.final_score,
                    "submitted": submission is not None,
                    "submit_time": submission.submit_date if submission else None
                })
        
        # 获取考试
        exam_assignments = self.db.query(ExamAssignment).filter(
            ExamAssignment.student_id == student_id
        ).all()
        
        exams = []
        for assignment in exam_assignments:
            exam = self.db.query(Exam).filter(
                Exam.id == assignment.exam_id
            ).first()
            
            if exam:
                record = self.db.query(ExamRecord).filter(
                    and_(
                        ExamRecord.exam_id == exam.id,
                        ExamRecord.student_id == student_id
                    )
                ).first()
                
                exams.append({
                    "id": exam.id,
                    "title": exam.title,
                    "description": exam.description,
                    "start_time": assignment.start_time,
                    "end_time": assignment.end_time,
                    "duration": assignment.duration_minutes,
                    "total_score": exam.total_score,
                    "status": assignment.status,
                    "score": assignment.final_score,
                    "submitted": record is not None,
                    "submit_time": record.submit_time if record else None
                })
        
        return {
            "homeworks": homeworks,
            "exams": exams
        }

    async def generate_student_learning_profile(self, student_id: int) -> StudentProfile:
        """生成学生学习画像"""
        # 获取现有画像
        profile = self.db.query(StudentProfile).filter(
            StudentProfile.student_id == student_id
        ).first()
        
        if not profile:
            profile = StudentProfile(student_id=student_id)
            self.db.add(profile)
        
        # 使用AI分析学生学习数据
        learning_data = self._collect_student_learning_data(student_id)
        ai_analysis = await self.ai_service.analyze_student_profile(learning_data)
        
        # 更新画像信息
        profile.learning_style = ai_analysis.get("learning_style")
        profile.ability_visual = ai_analysis.get("visual_ability")
        profile.ability_verbal = ai_analysis.get("verbal_ability")
        profile.ability_logical = ai_analysis.get("logical_ability")
        profile.ability_mathematical = ai_analysis.get("mathematical_ability")
        profile.attention_duration = ai_analysis.get("attention_duration")
        profile.preferred_content_type = ai_analysis.get("preferred_content_type")
        
        self.db.commit()
        return profile

    def get_student_recommendations(self, student_id: int) -> List[Dict[str, Any]]:
        """获取学生学习推荐"""
        recommendations = self.db.query(LearningRecommendation).filter(
            and_(
                LearningRecommendation.student_id == student_id,
                LearningRecommendation.status == 1
            )
        ).order_by(LearningRecommendation.priority.desc()).limit(10).all()
        
        result = []
        for rec in recommendations:
            result.append({
                "id": rec.id,
                "knowledge_point": rec.knowledge_point,
                "difficulty_level": rec.difficulty_level,
                "resource_type": rec.resource_type,
                "resource_id": rec.resource_id,
                "reason": rec.reason,
                "priority": rec.priority,
                "created_at": rec.created_at
            })
        
        return result

    # ==================== 教学进度管理 ====================
    
    def create_teaching_schedule(
        self, 
        schedule_data: Dict[str, Any], 
        teacher_id: int
    ) -> TeachingSchedule:
        """创建教学进度安排"""
        schedule = TeachingSchedule(
            class_id=schedule_data["class_id"],
            subject_id=schedule_data["subject_id"],
            teacher_id=teacher_id,
            chapter_id=schedule_data.get("chapter_id"),
            knowledge_point_ids=schedule_data.get("knowledge_point_ids"),
            title=schedule_data["title"],
            description=schedule_data.get("description"),
            teaching_objectives=schedule_data.get("teaching_objectives"),
            key_points=schedule_data.get("key_points"),
            difficult_points=schedule_data.get("difficult_points"),
            planned_date=schedule_data["planned_date"],
            duration_minutes=schedule_data.get("duration_minutes", 45),
            status="planned"
        )
        
        self.db.add(schedule)
        self.db.commit()
        return schedule

    def get_teaching_schedules(
        self, 
        class_id: int = None, 
        subject_id: int = None,
        teacher_id: int = None
    ) -> List[Dict[str, Any]]:
        """获取教学进度列表"""
        query = self.db.query(TeachingSchedule)
        
        if class_id:
            query = query.filter(TeachingSchedule.class_id == class_id)
        if subject_id:
            query = query.filter(TeachingSchedule.subject_id == subject_id)
        if teacher_id:
            query = query.filter(TeachingSchedule.teacher_id == teacher_id)
        
        schedules = query.order_by(TeachingSchedule.planned_date).all()
        
        result = []
        for schedule in schedules:
            # 获取关联信息
            class_obj = self.db.query(Class).filter(Class.id == schedule.class_id).first()
            subject = self.db.query(Subject).filter(Subject.id == schedule.subject_id).first()
            teacher = self.db.query(Teacher).filter(Teacher.id == schedule.teacher_id).first()
            teacher_user = self.db.query(User).filter(User.id == teacher.user_id).first() if teacher else None
            
            result.append({
                "id": schedule.id,
                "title": schedule.title,
                "description": schedule.description,
                "class_name": class_obj.name if class_obj else None,
                "subject_name": subject.name if subject else None,
                "teacher_name": teacher_user.real_name if teacher_user else None,
                "planned_date": schedule.planned_date,
                "actual_date": schedule.actual_date,
                "duration_minutes": schedule.duration_minutes,
                "status": schedule.status,
                "completion_rate": schedule.completion_rate,
                "student_understanding": schedule.student_understanding,
                "created_at": schedule.created_at
            })
        
        return result

    # ==================== 数据分析和统计 ====================
    
    def get_class_statistics(self, class_id: int) -> Dict[str, Any]:
        """获取班级统计信息"""
        # 基础信息
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()
        class_info = self.db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
        
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        # 学生统计
        students = self.get_class_students(class_id)
        student_count = len(students)
        
        # 作业统计
        homeworks = self.db.query(Homework).filter(Homework.class_id == class_id).all()
        homework_count = len(homeworks)
        
        # 考试统计
        exams = self.db.query(Exam).filter(Exam.class_id == class_id).all()
        exam_count = len(exams)
        
        # 最近活动统计
        recent_homework = self.db.query(Homework).filter(
            Homework.class_id == class_id
        ).order_by(Homework.created_at.desc()).limit(5).all()
        
        recent_exams = self.db.query(Exam).filter(
            Exam.class_id == class_id
        ).order_by(Exam.created_at.desc()).limit(5).all()
        
        return {
            "class_info": {
                "id": class_obj.id,
                "name": class_obj.name,
                "grade_name": class_obj.grade_name,
                "description": class_obj.description,
                "academic_year": class_info.academic_year if class_info else None,
                "max_students": class_info.max_students if class_info else 50
            },
            "statistics": {
                "student_count": student_count,
                "homework_count": homework_count,
                "exam_count": exam_count,
                "avg_score": self._calculate_class_avg_score(class_id),
                "attendance_rate": self._calculate_attendance_rate(class_id)
            },
            "recent_activities": {
                "homeworks": [{"id": h.id, "title": h.title, "created_at": h.created_at} for h in recent_homework],
                "exams": [{"id": e.id, "title": e.title, "created_at": e.created_at} for e in recent_exams]
            }
        }

    def get_student_learning_analytics(self, student_id: int) -> Dict[str, Any]:
        """获取学生学习分析"""
        # 基础信息
        student = self.db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        # 学习数据
        homework_submissions = self.db.query(HomeworkSubmission).filter(
            HomeworkSubmission.student_id == student_id
        ).all()
        
        exam_records = self.db.query(ExamRecord).filter(
            ExamRecord.student_id == student_id
        ).all()
        
        # 计算统计数据
        total_homeworks = len(homework_submissions)
        completed_homeworks = len([h for h in homework_submissions if h.status == 3])
        homework_completion_rate = completed_homeworks / total_homeworks if total_homeworks > 0 else 0
        
        homework_scores = [h.score for h in homework_submissions if h.score is not None]
        avg_homework_score = sum(homework_scores) / len(homework_scores) if homework_scores else 0
        
        total_exams = len(exam_records)
        completed_exams = len([e for e in exam_records if e.status == 2])
        exam_completion_rate = completed_exams / total_exams if total_exams > 0 else 0
        
        exam_scores = [e.total_score for e in exam_records if e.total_score is not None]
        avg_exam_score = sum(exam_scores) / len(exam_scores) if exam_scores else 0
        
        return {
            "student_info": {
                "id": student.id,
                "username": student.username,
                "real_name": student.real_name,
                "student_id": student.student_id
            },
            "learning_statistics": {
                "homework_completion_rate": homework_completion_rate,
                "exam_completion_rate": exam_completion_rate,
                "avg_homework_score": avg_homework_score,
                "avg_exam_score": avg_exam_score,
                "total_homeworks": total_homeworks,
                "total_exams": total_exams
            },
            "recent_performance": {
                "recent_homework_scores": homework_scores[-10:],
                "recent_exam_scores": exam_scores[-10:]
            }
        }

    # ==================== 辅助方法 ====================
    
    def _collect_student_learning_data(self, student_id: int) -> Dict[str, Any]:
        """收集学生学习数据用于AI分析"""
        # 获取作业数据
        homework_submissions = self.db.query(HomeworkSubmission).filter(
            HomeworkSubmission.student_id == student_id
        ).all()
        
        # 获取考试数据
        exam_records = self.db.query(ExamRecord).filter(
            ExamRecord.student_id == student_id
        ).all()
        
        # 获取学习行为数据
        from app.models.analytics import LearningBehavior
        behaviors = self.db.query(LearningBehavior).filter(
            LearningBehavior.student_id == student_id
        ).all()
        
        return {
            "homework_data": [
                {
                    "score": h.score,
                    "submit_time": h.submit_date,
                    "content_length": len(h.content) if h.content else 0
                } for h in homework_submissions
            ],
            "exam_data": [
                {
                    "score": e.total_score,
                    "duration": (e.submit_time - e.start_time).total_seconds() / 60 if e.submit_time and e.start_time else None
                } for e in exam_records
            ],
            "behavior_data": [
                {
                    "study_duration": b.study_duration,
                    "focus_duration": b.focus_duration,
                    "correct_rate": b.correct_rate
                } for b in behaviors
            ]
        }
    
    def _calculate_class_avg_score(self, class_id: int) -> float:
        """计算班级平均分"""
        # 获取班级所有学生
        students = self.get_class_students(class_id)
        if not students:
            return 0.0
        
        # 计算所有学生的平均分
        total_score = 0
        score_count = 0
        
        for student in students:
            student_id = student["student_id"]
            
            # 获取作业成绩
            homework_submissions = self.db.query(HomeworkSubmission).filter(
                HomeworkSubmission.student_id == student_id
            ).all()
            
            for submission in homework_submissions:
                if submission.score is not None:
                    total_score += submission.score
                    score_count += 1
            
            # 获取考试成绩
            exam_records = self.db.query(ExamRecord).filter(
                ExamRecord.student_id == student_id
            ).all()
            
            for record in exam_records:
                if record.total_score is not None:
                    total_score += record.total_score
                    score_count += 1
        
        return total_score / score_count if score_count > 0 else 0.0
    
    def _calculate_attendance_rate(self, class_id: int) -> float:
        """计算班级出勤率"""
        from app.models.education import Attendance
        
        # 获取最近30天的考勤记录
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        attendance_records = self.db.query(Attendance).filter(
            and_(
                Attendance.class_id == class_id,
                Attendance.date >= thirty_days_ago.date()
            )
        ).all()
        
        if not attendance_records:
            return 100.0  # 没有考勤记录默认100%
        
        present_count = len([a for a in attendance_records if a.status == "present"])
        total_count = len(attendance_records)
        
        return (present_count / total_count) * 100 if total_count > 0 else 100.0