from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from datetime import datetime
from fastapi import HTTPException, status
from app.models.exam import Exam, ExamQuestion, ExamRecord, ExamAnswer
from app.models.content import Question
from app.schemas.exam import ExamCreate, ExamUpdate, ExamSubmission
from app.services.base_service import BaseService


class ExamService(BaseService[Exam]):
    """考试服务"""
    
    def __init__(self, db: Session):
        super().__init__(db, Exam)
    
    def create_exam(self, exam_create: ExamCreate, teacher_id: int) -> Exam:
        """创建考试"""
        # 创建考试基本信息
        exam_data = exam_create.dict(exclude={"questions"})
        exam_data["teacher_id"] = teacher_id
        
        exam = self.create(exam_data)
        
        # 添加考试题目
        for question_data in exam_create.questions:
            exam_question = ExamQuestion(
                exam_id=exam.id,
                question_id=question_data.question_id,
                score=question_data.score,
                sequence=question_data.sequence
            )
            self.db.add(exam_question)
        
        self.db.commit()
        return exam
    
    def update_exam(self, exam_id: int, exam_update: ExamUpdate, teacher_id: int) -> Exam:
        """更新考试"""
        exam = self.get(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考试不存在"
            )
        
        # 检查权限
        if exam.teacher_id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此考试"
            )
        
        # 检查考试状态
        if exam.status not in ["draft", "published"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="考试已开始或结束，无法修改"
            )
        
        update_data = exam_update.dict(exclude_unset=True)
        return self.update(exam, update_data)
    
    def get_exam_with_questions(self, exam_id: int) -> Optional[Exam]:
        """获取考试及其题目"""
        return self.db.query(Exam).options(
            joinedload(Exam.questions).joinedload(ExamQuestion.question)
        ).filter(Exam.id == exam_id).first()
    
    def get_exams_by_class(self, class_id: int, student_id: Optional[int] = None) -> List[Exam]:
        """获取班级考试"""
        query = self.db.query(Exam).filter(Exam.class_id == class_id)
        
        if student_id:
            # 如果是学生查询，只返回已发布的考试
            query = query.filter(Exam.status.in_(["published", "ongoing", "completed"]))
        
        return query.order_by(Exam.start_time.desc()).all()
    
    def start_exam(self, exam_id: int, student_id: int) -> ExamRecord:
        """开始考试"""
        exam = self.get(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考试不存在"
            )
        
        # 检查考试状态
        now = datetime.now()
        if exam.status != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="考试未发布"
            )
        
        if now < exam.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="考试尚未开始"
            )
        
        if now > exam.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="考试已结束"
            )
        
        # 检查是否已有考试记录
        existing_record = self.db.query(ExamRecord).filter(
            and_(
                ExamRecord.exam_id == exam_id,
                ExamRecord.student_id == student_id
            )
        ).first()
        
        if existing_record:
            if existing_record.status == 2:  # 已提交
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="考试已提交，无法重新开始"
                )
            return existing_record
        
        # 创建考试记录
        exam_record = ExamRecord(
            student_id=student_id,
            exam_id=exam_id,
            start_time=now,
            status=1  # 进行中
        )
        self.db.add(exam_record)
        self.db.commit()
        self.db.refresh(exam_record)
        
        return exam_record
    
    def submit_exam(self, exam_id: int, student_id: int, submission: ExamSubmission) -> ExamRecord:
        """提交考试"""
        exam_record = self.db.query(ExamRecord).filter(
            and_(
                ExamRecord.exam_id == exam_id,
                ExamRecord.student_id == student_id,
                ExamRecord.status == 1  # 进行中
            )
        ).first()
        
        if not exam_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考试记录不存在或已提交"
            )
        
        # 更新考试记录
        exam_record.submit_time = datetime.now()
        exam_record.status = 2  # 已提交
        
        # 保存答案
        for answer_data in submission.answers:
            exam_answer = ExamAnswer(
                exam_record_id=exam_record.id,
                question_id=answer_data.question_id,
                answer=answer_data.answer
            )
            self.db.add(exam_answer)
        
        self.db.commit()
        
        # 自动批改
        self.auto_grade_exam(exam_record.id)
        
        return exam_record
    
    def auto_grade_exam(self, exam_record_id: int) -> None:
        """自动批改考试"""
        exam_record = self.db.query(ExamRecord).filter(
            ExamRecord.id == exam_record_id
        ).first()
        
        if not exam_record:
            return
        
        total_score = 0.0
        
        # 获取所有答案
        answers = self.db.query(ExamAnswer).filter(
            ExamAnswer.exam_record_id == exam_record_id
        ).all()
        
        for answer in answers:
            # 获取题目信息
            exam_question = self.db.query(ExamQuestion).filter(
                and_(
                    ExamQuestion.exam_id == exam_record.exam_id,
                    ExamQuestion.question_id == answer.question_id
                )
            ).first()
            
            if not exam_question:
                continue
            
            question = self.db.query(Question).filter(
                Question.id == answer.question_id
            ).first()
            
            if not question:
                continue
            
            # 自动批改（仅支持客观题）
            if question.is_objective:
                is_correct = self.check_answer_correctness(
                    answer.answer, 
                    question.answer
                )
                answer.is_correct = is_correct
                answer.score = exam_question.score if is_correct else 0.0
                total_score += answer.score
            else:
                # 主观题需要人工批改
                answer.score = 0.0
                answer.is_correct = None
        
        # 更新总分
        exam_record.total_score = total_score
        exam_record.status = 3  # 已批改
        
        self.db.commit()
    
    def check_answer_correctness(self, student_answer: str, correct_answer: str) -> bool:
        """检查答案正确性"""
        # 简单的字符串比较，实际实现可能需要更复杂的逻辑
        return student_answer.strip().lower() == correct_answer.strip().lower()
    
    def get_exam_statistics(self, exam_id: int) -> Dict[str, Any]:
        """获取考试统计信息"""
        exam = self.get(exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考试不存在"
            )
        
        # 参与人数
        total_participants = self.db.query(ExamRecord).filter(
            ExamRecord.exam_id == exam_id
        ).count()
        
        # 已提交人数
        submitted_count = self.db.query(ExamRecord).filter(
            and_(
                ExamRecord.exam_id == exam_id,
                ExamRecord.status.in_([2, 3])
            )
        ).count()
        
        # 平均分
        avg_score = self.db.query(func.avg(ExamRecord.total_score)).filter(
            and_(
                ExamRecord.exam_id == exam_id,
                ExamRecord.total_score.isnot(None)
            )
        ).scalar() or 0.0
        
        # 最高分
        max_score = self.db.query(func.max(ExamRecord.total_score)).filter(
            and_(
                ExamRecord.exam_id == exam_id,
                ExamRecord.total_score.isnot(None)
            )
        ).scalar() or 0.0
        
        # 及格率
        pass_count = self.db.query(ExamRecord).filter(
            and_(
                ExamRecord.exam_id == exam_id,
                ExamRecord.total_score >= exam.total_score * 0.6
            )
        ).count()
        
        pass_rate = (pass_count / submitted_count * 100) if submitted_count > 0 else 0.0
        
        return {
            "total_participants": total_participants,
            "submitted_count": submitted_count,
            "completion_rate": (submitted_count / total_participants * 100) if total_participants > 0 else 0.0,
            "average_score": round(avg_score, 2),
            "max_score": max_score,
            "pass_rate": round(pass_rate, 2)
        }
