# backend/app/services/class_management_service.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, UploadFile
import json
import uuid
import os

from app.models.education import Class, Subject
from app.models.user import User, Teacher
from app.models.class_management import (
    ClassInfo, ClassTeacherAssignment, StudentClassHistory,
    StudentImportTask, HomeworkAssignment, ExamAssignment,
    StudentLearningProfile, LearningResourceRecommendation,
    TeachingSchedule
)
from app.models.homework import Homework, HomeworkSubmission
from app.models.exam import Exam, ExamRecord
from app.services.base_service import BaseService
from app.services.user_service import UserService
from app.services.ai_service import AIService
from app.core.security import get_password_hash


class ClassManagementService(BaseService[Class]):
    """班级管理服务"""
    
    def __init__(self, db: Session):
        super().__init__(db, Class)
        self.user_service = UserService(db)
        self.ai_service = AIService(db)
    
    def create_class_with_info(self, class_data: Dict[str, Any], creator_id: int) -> Class:
        """创建班级并初始化班级信息"""
        try:
            # 创建班级
            class_obj = self.create(class_data)
            
            # 创建班级信息
            class_info_data = {
                "class_id": class_obj.id,
                "academic_year": class_data.get("academic_year", "2023-2024"),
                "semester": class_data.get("semester", "上学期"),
                "max_students": class_data.get("max_students", 50),
                "class_motto": class_data.get("class_motto", ""),
                "class_rules": class_data.get("class_rules", ""),
            }
            
            class_info = ClassInfo(**class_info_data)
            self.db.add(class_info)
            self.db.commit()
            
            return class_obj
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"创建班级失败: {str(e)}")
    
    def assign_teacher_to_class(
        self, 
        class_id: int, 
        teacher_id: int, 
        subject_id: int,
        assignment_type: str,
        creator_id: int
    ) -> ClassTeacherAssignment:
        """分配教师到班级"""
        # 验证班级、教师、学科是否存在
        class_obj = self.get(class_id)
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="教师不存在")
        
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="学科不存在")
        
        # 检查是否已有相同分配
        existing = self.db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == class_id,
                ClassTeacherAssignment.teacher_id == teacher_id,
                ClassTeacherAssignment.subject_id == subject_id,
                ClassTeacherAssignment.assignment_type == assignment_type,
                ClassTeacherAssignment.is_active == True
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="该教师已分配到此班级此学科")
        
        # 如果是班主任，检查是否已有班主任
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
        
        # 创建分配记录
        assignment = ClassTeacherAssignment(
            class_id=class_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            assignment_type=assignment_type,
            start_date=date.today(),
            created_by=creator_id
        )
        
        self.db.add(assignment)
        self.db.commit()
        
        return assignment
    
    def remove_teacher_from_class(self, assignment_id: int) -> bool:
        """移除教师班级分配"""
        assignment = self.db.query(ClassTeacherAssignment).filter(
            ClassTeacherAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            return False
        
        assignment.is_active = False
        assignment.end_date = date.today()
        self.db.commit()
        
        return True
    
    def get_class_teachers(self, class_id: int) -> List[Dict[str, Any]]:
        """获取班级教师列表"""
        assignments = self.db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == class_id,
                ClassTeacherAssignment.is_active == True
            )
        ).all()
        
        result = []
        for assignment in assignments:
            teacher_user = self.db.query(User).filter(User.id == assignment.teacher.user_id).first()
            result.append({
                "assignment_id": assignment.id,
                "teacher_id": assignment.teacher_id,
                "teacher_name": teacher_user.real_name or teacher_user.username,
                "subject_name": assignment.subject.name,
                "assignment_type": assignment.assignment_type,
                "start_date": assignment.start_date,
                "is_class_teacher": assignment.assignment_type == "class_teacher"
            })
        
        return result
    
    def get_teacher_classes(self, teacher_id: int) -> List[Dict[str, Any]]:
        """获取教师负责的班级列表"""
        assignments = self.db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.teacher_id == teacher_id,
                ClassTeacherAssignment.is_active == True
            )
        ).all()
        
        result = []
        for assignment in assignments:
            class_info = self.db.query(ClassInfo).filter(
                ClassInfo.class_id == assignment.class_id
            ).first()
            
            result.append({
                "class_id": assignment.class_id,
                "class_name": assignment.class_.name,
                "grade_name": assignment.class_.grade_name,
                "subject_name": assignment.subject.name,
                "assignment_type": assignment.assignment_type,
                "student_count": class_info.student_count if class_info else 0,
                "is_class_teacher": assignment.assignment_type == "class_teacher"
            })
        
        return result
    
    def add_student_to_class(self, student_id: int, class_id: int, join_reason: str = None) -> bool:
        """添加学生到班级"""
        # 验证学生和班级
        student = self.db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        class_obj = self.get(class_id)
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")
        
        # 检查学生是否已在班级中
        existing = self.db.query(StudentClassHistory).filter(
            and_(
                StudentClassHistory.student_id == student_id,
                StudentClassHistory.class_id == class_id,
                StudentClassHistory.status == "active"
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="学生已在该班级中")
        
        # 检查班级人数限制
        class_info = self.db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
        if class_info and class_info.student_count >= class_info.max_students:
            raise HTTPException(status_code=400, detail="班级人数已满")
        
        # 创建学生班级历史记录
        history = StudentClassHistory(
            student_id=student_id,
            class_id=class_id,
            join_date=date.today(),
            join_reason=join_reason or "手动添加",
            status="active"
        )
        
        self.db.add(history)
        
        # 更新班级人数
        if class_info:
            class_info.student_count += 1
        
        self.db.commit()
        
        return True
    
    def remove_student_from_class(self, student_id: int, class_id: int, leave_reason: str = None) -> bool:
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
        
        history.status = "transferred"
        history.leave_date = date.today()
        history.leave_reason = leave_reason or "手动移除"
        
        # 更新班级人数
        class_info = self.db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
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
            student = history.student
            
            # 获取学生学习画像
            profile = self.db.query(StudentLearningProfile).filter(
                StudentLearningProfile.student_id == student.id
            ).first()
            
            result.append({
                "student_id": student.id,
                "username": student.username,
                "real_name": student.real_name,
                "student_id_number": student.student_id,
                "email": student.email,
                "phone": student.phone,
                "join_date": history.join_date,
                "learning_level": profile.learning_level if profile else None,
                "homework_completion_rate": profile.homework_completion_rate if profile else 0,
                "exam_performance_trend": profile.exam_performance_trend if profile else None
            })
        
        return result
    
    async def import_students_from_excel(
        self, 
        class_id: int, 
        file: UploadFile, 
        creator_id: int
    ) -> StudentImportTask:
        """从Excel批量导入学生"""
        # 验证文件格式
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="文件格式不支持，请上传Excel文件")
        
        # 保存上传文件
        upload_dir = "uploads/student_imports"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 创建导入任务
        task = StudentImportTask(
            task_name=f"导入学生-{file.filename}",
            class_id=class_id,
            imported_by=creator_id,
            file_path=file_path,
            status="pending"
        )
        
        self.db.add(task)
        self.db.commit()
        
        # 异步处理导入（这里简化为同步处理）
        try:
            await self._process_student_import(task.id)
        except Exception as e:
            task.status = "failed"
            task.error_log = str(e)
            self.db.commit()
            raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
        
        return task
    
    async def _process_student_import(self, task_id: int):
        """处理学生导入任务"""
        task = self.db.query(StudentImportTask).filter(StudentImportTask.id == task_id).first()
        if not task:
            return
        
        task.status = "processing"
        self.db.commit()
        
        try:
            # 读取Excel文件
            df = pd.read_excel(task.file_path)
            
            # 验证必需列
            required_columns = ['姓名', '学号', '邮箱']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"缺少必需列: {', '.join(missing_columns)}")
            
            task.total_count = len(df)
            success_count = 0
            failed_count = 0
            error_details = []
            
            for index, row in df.iterrows():
                try:
                    # 验证数据
                    real_name = str(row['姓名']).strip()
                    student_id = str(row['学号']).strip()
                    email = str(row['邮箱']).strip()
                    
                    if not all([real_name, student_id, email]):
                        raise ValueError("姓名、学号、邮箱不能为空")
                    
                    # 生成用户名（使用学号）
                    username = student_id
                    
                    # 检查用户是否已存在
                    existing_user = self.user_service.get_by_username(username)
                    if existing_user:
                        # 如果用户已存在，直接添加到班级
                        self.add_student_to_class(existing_user.id, task.class_id, "批量导入")
                    else:
                        # 创建新用户
                        user_data = {
                            "username": username,
                            "email": email,
                            "password_hash": get_password_hash("123456"),  # 默认密码
                            "real_name": real_name,
                            "student_id": student_id,
                            "phone": str(row.get('手机号', '')).strip() or None,
                            "status": 1
                        }
                        
                        user = self.user_service.create(user_data)
                        
                        # 分配学生角色
                        self.user_service.assign_role(user.id, "student")
                        
                        # 添加到班级
                        self.add_student_to_class(user.id, task.class_id, "批量导入")
                    
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    error_details.append(f"第{index + 2}行: {str(e)}")
            
            # 更新任务状态
            task.success_count = success_count
            task.failed_count = failed_count
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            if error_details:
                task.error_log = "\n".join(error_details)
            
            self.db.commit()
            
        except Exception as e:
            task.status = "failed"
            task.error_log = str(e)
            self.db.commit()
            raise
    
    def create_homework_assignment(
        self, 
        homework_data: Dict[str, Any], 
        teacher_id: int,
        student_ids: List[int] = None
    ) -> Homework:
        """创建作业并分配给学生"""
        try:
            # 创建作业
            homework = Homework(**homework_data)
            self.db.add(homework)
            self.db.flush()
            
            # 如果没有指定学生，获取班级所有学生
            if not student_ids:
                student_ids = [s["student_id"] for s in self.get_class_students(homework_data["class_id"])]
            
            # 创建作业分配
            for student_id in student_ids:
                assignment = HomeworkAssignment(
                    homework_id=homework.id,
                    student_id=student_id,
                    due_date=homework_data["due_date"]
                )
                self.db.add(assignment)
            
            self.db.commit()
            return homework
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"创建作业失败: {str(e)}")
    
    def create_exam_assignment(
        self, 
        exam_data: Dict[str, Any], 
        teacher_id: int,
        student_ids: List[int] = None
    ) -> Exam:
        """创建考试并分配给学生"""
        try:
            # 创建考试
            exam = Exam(**exam_data)
            self.db.add(exam)
            self.db.flush()
            
            # 如果没有指定学生，获取班级所有学生
            if not student_ids:
                student_ids = [s["student_id"] for s in self.get_class_students(exam_data["class_id"])]
            
            # 创建考试分配
            for student_id in student_ids:
                assignment = ExamAssignment(
                    exam_id=exam.id,
                    student_id=student_id
                )
                self.db.add(assignment)
            
            self.db.commit()
            return exam
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"创建考试失败: {str(e)}")
    
    def get_student_assignments(self, student_id: int) -> Dict[str, Any]:
        """获取学生的作业和考试安排"""
        # 获取作业分配
        homework_assignments = self.db.query(HomeworkAssignment).filter(
            HomeworkAssignment.student_id == student_id
        ).all()
        
        homeworks = []
        for assignment in homework_assignments:
            homework = assignment.homework
            submission = self.db.query(HomeworkSubmission).filter(
                and_(
                    HomeworkSubmission.homework_id == homework.id,
                    HomeworkSubmission.student_id == student_id
                )
            ).first()
            
            homeworks.append({
                "assignment_id": assignment.id,
                "homework_id": homework.id,
                "title": homework.title,
                "description": homework.description,
                "subject_name": homework.subject.name if homework.subject else None,
                "assign_date": homework.assign_date,
                "due_date": assignment.due_date,
                "status": assignment.status,
                "submitted": submission is not None,
                "score": submission.score if submission else None,
                "late_submission": assignment.late_submission
            })
        
        # 获取考试分配
        exam_assignments = self.db.query(ExamAssignment).filter(
            ExamAssignment.student_id == student_id
        ).all()
        
        exams = []
        for assignment in exam_assignments:
            exam = assignment.exam
            record = self.db.query(ExamRecord).filter(
                and_(
                    ExamRecord.exam_id == exam.id,
                    ExamRecord.student_id == student_id
                )
            ).first()
            
            exams.append({
                "assignment_id": assignment.id,
                "exam_id": exam.id,
                "title": exam.title,
                "description": exam.description,
                "subject_name": exam.subject.name if exam.subject else None,
                "start_time": exam.start_time,
                "end_time": exam.end_time,
                "duration": exam.duration,
                "status": assignment.status,
                "submitted": record is not None and record.submit_time is not None,
                "score": assignment.final_score,
                "total_score": exam.total_score
            })
        
        return {
            "homeworks": homeworks,
            "exams": exams
        }
    
    def grade_homework(self, submission_id: int, grader_id: int, grade_data: Dict[str, Any]) -> bool:
        """批改作业"""
        submission = self.db.query(HomeworkSubmission).filter(
            HomeworkSubmission.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="作业提交不存在")
        
        # 更新提交记录
        submission.score = grade_data.get("score")
        submission.comment = grade_data.get("comment")
        submission.status = 3  # 已批改
        
        # 更新作业分配记录
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
        
        # 更新学生画像
        self._update_student_profile_after_homework(submission.student_id, submission.homework_id)
        
        return True
    
    def grade_exam(self, exam_record_id: int, grader_id: int, grade_data: Dict[str, Any]) -> bool:
        """批改考试"""
        record = self.db.query(ExamRecord).filter(
            ExamRecord.id == exam_record_id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="考试记录不存在")
        
        # 更新考试记录
        record.total_score = grade_data.get("score")
        record.status = 3  # 已批改
        
        # 更新考试分配记录
        assignment = self.db.query(ExamAssignment).filter(
            and_(
                ExamAssignment.exam_id == record.exam_id,
                ExamAssignment.student_id == record.student_id
            )
        ).first()
        
        if assignment:
            assignment.status = "graded"
            assignment.final_score = grade_data.get("score")
        
        self.db.commit()
        
        # 更新学生画像
        self._update_student_profile_after_exam(record.student_id, record.exam_id)
        
        return True
    
    def _update_student_profile_after_homework(self, student_id: int, homework_id: int):
        """作业完成后更新学生画像"""
        # 获取或创建学生画像
        profile = self.db.query(StudentLearningProfile).filter(
            StudentLearningProfile.student_id == student_id
        ).first()
        
        if not profile:
            # 获取学生班级
            history = self.db.query(StudentClassHistory).filter(
                and_(
                    StudentClassHistory.student_id == student_id,
                    StudentClassHistory.status == "active"
                )
            ).first()
            
            if history:
                profile = StudentLearningProfile(
                    student_id=student_id,
                    class_id=history.class_id
                )
                self.db.add(profile)
        
        if profile:
            # 计算作业完成率
            total_assignments = self.db.query(HomeworkAssignment).filter(
                HomeworkAssignment.student_id == student_id
            ).count()
            
            completed_assignments = self.db.query(HomeworkAssignment).filter(
                and_(
                    HomeworkAssignment.student_id == student_id,
                    HomeworkAssignment.status.in_(["submitted", "graded"])
                )
            ).count()
            
            if total_assignments > 0:
                profile.homework_completion_rate = (completed_assignments / total_assignments) * 100
            
            profile.last_analysis_date = datetime.utcnow()
            self.db.commit()
    
    def _update_student_profile_after_exam(self, student_id: int, exam_id: int):
        """考试完成后更新学生画像"""
        # 获取或创建学生画像
        profile = self.db.query(StudentLearningProfile).filter(
            StudentLearningProfile.student_id == student_id
        ).first()
        
        if profile:
            # 分析考试表现趋势
            recent_exams = self.db.query(ExamAssignment).filter(
                and_(
                    ExamAssignment.student_id == student_id,
                    ExamAssignment.final_score.isnot(None)
                )
            ).order_by(desc(ExamAssignment.id)).limit(5).all()
            
            if len(recent_exams) >= 3:
                scores = [exam.final_score for exam in recent_exams]
                
                # 计算趋势
                if scores[0] > scores[-1]:
                    if scores[0] - scores[-1] >= 10:
                        profile.exam_performance_trend = "improving"
                    else:
                        profile.exam_performance_trend = "stable"
                elif scores[-1] > scores[0]:
                    if scores[-1] - scores[0] >= 10:
                        profile.exam_performance_trend = "declining" 
                    else:
                        profile.exam_performance_trend = "stable"
                else:
                    profile.exam_performance_trend = "stable"
            
            profile.last_analysis_date = datetime.utcnow()
            self.db.commit()
    
    async def generate_student_learning_profile(self, student_id: int) -> StudentLearningProfile:
        """生成学生学习画像"""
        # 获取学生基本信息
        student = self.db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")
        
        # 获取学生班级
        history = self.db.query(StudentClassHistory).filter(
            and_(
                StudentClassHistory.student_id == student_id,
                StudentClassHistory.status == "active"
            )
        ).first()
        
        if not history:
            raise HTTPException(status_code=400, detail="学生未分配班级")
        
        # 获取或创建学习画像
        profile = self.db.query(StudentLearningProfile).filter(
            StudentLearningProfile.student_id == student_id
        ).first()
        
        if not profile:
            profile = StudentLearningProfile(
                student_id=student_id,
                class_id=history.class_id
            )
            self.db.add(profile)
        
        # 分析作业表现
        homework_assignments = self.db.query(HomeworkAssignment).filter(
            HomeworkAssignment.student_id == student_id
        ).all()
        
        total_homeworks = len(homework_assignments)
        completed_homeworks = len([h for h in homework_assignments if h.status in ["submitted", "graded"]])
        
        if total_homeworks > 0:
            profile.homework_completion_rate = (completed_homeworks / total_homeworks) * 100
        
        # 分析考试表现
        exam_assignments = self.db.query(ExamAssignment).filter(
            ExamAssignment.student_id == student_id
        ).all()
        
        exam_scores = [e.final_score for e in exam_assignments if e.final_score is not None]
        
        if exam_scores:
            avg_score = sum(exam_scores) / len(exam_scores)
            
            if avg_score >= 90:
                profile.learning_level = "excellent"
            elif avg_score >= 80:
                profile.learning_level = "good"
            elif avg_score >= 70:
                profile.learning_level = "average"
            else:
                profile.learning_level = "below_average"
        
        # 使用AI分析学习偏好和建议
        try:
            ai_analysis = await self.ai_service.analyze_student_learning_pattern(student_id)
            
            if ai_analysis:
                profile.learning_style = ai_analysis.get("learning_style")
                profile.preferred_difficulty = ai_analysis.get("preferred_difficulty")
                profile.learning_suggestions = ai_analysis.get("suggestions")
                profile.confidence_score = ai_analysis.get("confidence", 0.8)
        except Exception as e:
            print(f"AI分析失败: {e}")
            profile.confidence_score = 0.6
        
        profile.last_analysis_date = datetime.utcnow()
        profile.analysis_version = "1.0"
        
        self.db.commit()
        
        # 生成个性化推荐
        await self._generate_learning_recommendations(student_id)
        
        return profile
    
    async def _generate_learning_recommendations(self, student_id: int):
        """生成学习资源推荐"""
        profile = self.db.query(StudentLearningProfile).filter(
            StudentLearningProfile.student_id == student_id
        ).first()
        
        if not profile:
            return
        
        # 清除旧的推荐
        self.db.query(LearningResourceRecommendation).filter(
            LearningResourceRecommendation.student_id == student_id
        ).delete()
        
        # 基于学习画像生成推荐
        recommendations = []
        
        # 根据薄弱科目推荐资源
        if profile.knowledge_gaps:
            for gap in profile.knowledge_gaps[:3]:  # 前3个薄弱点
                rec = LearningResourceRecommendation(
                    student_id=student_id,
                    resource_type="exercise",
                    resource_title=f"{gap}强化练习",
                    resource_url=f"/exercises/topic/{gap}",
                    difficulty_level=profile.preferred_difficulty or "medium",
                    recommendation_reason=f"根据分析，您在{gap}方面需要加强练习",
                    recommendation_score=0.9,
                    expires_at=datetime.utcnow() + timedelta(days=7)
                )
                recommendations.append(rec)
        
        # 根据学习风格推荐资源
        if profile.learning_style == "visual":
            rec = LearningResourceRecommendation(
                student_id=student_id,
                resource_type="video",
                resource_title="可视化学习视频集",
                resource_url="/videos/visual-learning",
                recommendation_reason="根据您的视觉学习风格推荐",
                recommendation_score=0.8,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            recommendations.append(rec)
        
        # 保存推荐
        for rec in recommendations:
            self.db.add(rec)
        
        self.db.commit()
    
    def get_student_recommendations(self, student_id: int) -> List[Dict[str, Any]]:
        """获取学生的学习推荐"""
        recommendations = self.db.query(LearningResourceRecommendation).filter(
            and_(
                LearningResourceRecommendation.student_id == student_id,
                LearningResourceRecommendation.expires_at > datetime.utcnow()
            )
        ).order_by(desc(LearningResourceRecommendation.recommendation_score)).all()
        
        result = []
        for rec in recommendations:
            result.append({
                "id": rec.id,
                "resource_type": rec.resource_type,
                "resource_title": rec.resource_title,
                "resource_url": rec.resource_url,
                "subject_name": rec.subject.name if rec.subject else None,
                "difficulty_level": rec.difficulty_level,
                "estimated_time": rec.estimated_time,
                "recommendation_reason": rec.recommendation_reason,
                "recommendation_score": rec.recommendation_score,
                "clicked": rec.clicked,
                "completed": rec.completed
            })
        
        return result
    
    def create_teaching_schedule(self, schedule_data: Dict[str, Any], teacher_id: int) -> TeachingSchedule:
        """创建教学进度"""
        schedule_data["teacher_id"] = teacher_id
        schedule = TeachingSchedule(**schedule_data)
        self.db.add(schedule)
        self.db.commit()
        return schedule
    
    def get_teaching_schedules(self, class_id: int, subject_id: int = None) -> List[Dict[str, Any]]:
        """获取教学进度列表"""
        query = self.db.query(TeachingSchedule).filter(
            TeachingSchedule.class_id == class_id
        )
        
        if subject_id:
            query = query.filter(TeachingSchedule.subject_id == subject_id)
        
        schedules = query.order_by(TeachingSchedule.planned_date).all()
        
        result = []
        for schedule in schedules:
            result.append({
                "id": schedule.id,
                "title": schedule.title,
                "description": schedule.description,
                "subject_name": schedule.subject.name,
                "teacher_name": schedule.teacher.user.real_name,
                "planned_date": schedule.planned_date,
                "actual_date": schedule.actual_date,
                "status": schedule.status,
                "completion_rate": schedule.completion_rate,
                "student_understanding": schedule.student_understanding
            })
        
        return result