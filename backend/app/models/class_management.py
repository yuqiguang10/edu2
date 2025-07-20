# backend/app/models/class_management.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class ClassInfo(Base):
    """班级信息表（扩展原有Class模型）"""
    __tablename__ = "class_info"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, unique=True)
    student_count = Column(Integer, default=0)
    max_students = Column(Integer, default=50)
    class_motto = Column(String(200))  # 班级口号
    class_rules = Column(Text)  # 班级规则
    contact_info = Column(JSON)  # 联系方式信息
    academic_year = Column(String(20), nullable=False)  # 学年，如"2023-2024"
    semester = Column(String(10), nullable=False)  # 学期，如"上学期"
    status = Column(Integer, default=1)  # 1-正常, 0-停用
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    class_ = relationship("Class", back_populates="class_info")


class ClassTeacherAssignment(Base):
    """班级教师分配表"""
    __tablename__ = "class_teacher_assignments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    assignment_type = Column(String(20), nullable=False)  # class_teacher(班主任), subject_teacher(科任老师)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关联关系
    class_ = relationship("Class")
    teacher = relationship("Teacher")
    subject = relationship("Subject")
    creator = relationship("User")


class StudentClassHistory(Base):
    """学生班级历史表"""
    __tablename__ = "student_class_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    join_date = Column(Date, nullable=False)
    leave_date = Column(Date)
    join_reason = Column(String(100))  # 入班原因
    leave_reason = Column(String(100))  # 离班原因
    status = Column(String(20), default="active")  # active, transferred, graduated
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    student = relationship("User")
    class_ = relationship("Class")


class StudentImportTask(Base):
    """学生批量导入任务表"""
    __tablename__ = "student_import_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    imported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String(255))  # 上传文件路径
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_log = Column(Text)  # 错误日志
    result_file = Column(String(255))  # 结果文件路径
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    # 关联关系
    class_ = relationship("Class")
    importer = relationship("User")


class HomeworkAssignment(Base):
    """作业分配表（扩展原有Homework模型）"""
    __tablename__ = "homework_assignments"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=func.now())
    due_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="assigned")  # assigned, started, submitted, graded
    submission_count = Column(Integer, default=0)  # 提交次数
    late_submission = Column(Boolean, default=False)
    auto_grade_score = Column(Float)  # 自动批改得分
    manual_grade_score = Column(Float)  # 手动批改得分
    final_score = Column(Float)  # 最终得分

    # 关联关系
    homework = relationship("Homework")
    student = relationship("User")


class ExamAssignment(Base):
    """考试分配表（扩展原有Exam模型）"""
    __tablename__ = "exam_assignments"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=func.now())
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)  # 实际考试时长
    status = Column(String(20), default="assigned")  # assigned, started, submitted, graded
    auto_grade_score = Column(Float)  # 自动批改得分
    manual_grade_score = Column(Float)  # 手动批改得分
    final_score = Column(Float)  # 最终得分
    cheating_detected = Column(Boolean, default=False)  # 作弊检测

    # 关联关系
    exam = relationship("Exam")
    student = relationship("User")


class HomeworkSubmissionDetail(Base):
    """作业提交详情表"""
    __tablename__ = "homework_submission_details"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    question_text = Column(Text)  # 题目内容快照
    student_answer = Column(Text)  # 学生答案
    correct_answer = Column(Text)  # 正确答案
    score = Column(Float)  # 单题得分
    max_score = Column(Float)  # 单题满分
    is_correct = Column(Boolean)  # 是否正确
    auto_graded = Column(Boolean, default=False)  # 是否自动批改
    teacher_comment = Column(Text)  # 教师评语
    graded_at = Column(DateTime)
    graded_by = Column(Integer, ForeignKey("users.id"))

    # 关联关系
    submission = relationship("HomeworkSubmission")
    question = relationship("Question")
    grader = relationship("User")


class ExamSubmissionDetail(Base):
    """考试提交详情表"""
    __tablename__ = "exam_submission_details"

    id = Column(Integer, primary_key=True, index=True)
    exam_record_id = Column(Integer, ForeignKey("exam_records.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question_order = Column(Integer, nullable=False)  # 题目顺序
    student_answer = Column(Text)  # 学生答案
    correct_answer = Column(Text)  # 正确答案
    score = Column(Float)  # 单题得分
    max_score = Column(Float)  # 单题满分
    is_correct = Column(Boolean)  # 是否正确
    answer_time = Column(Integer)  # 答题用时（秒）
    auto_graded = Column(Boolean, default=False)  # 是否自动批改
    teacher_comment = Column(Text)  # 教师评语
    graded_at = Column(DateTime)
    graded_by = Column(Integer, ForeignKey("users.id"))

    # 关联关系
    exam_record = relationship("ExamRecord")
    question = relationship("Question")
    grader = relationship("User")


class StudentLearningProfile(Base):
    """学生学习画像表"""
    __tablename__ = "student_learning_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    # 基础信息
    learning_level = Column(String(20))  # 学习水平：excellent, good, average, below_average
    learning_style = Column(String(20))  # 学习风格：visual, auditory, kinesthetic
    attention_span = Column(Integer)  # 注意力持续时间（分钟）
    study_efficiency = Column(Float)  # 学习效率评分（0-100）
    
    # 学科能力评估
    math_ability = Column(Float, default=0)  # 数学能力（0-100）
    language_ability = Column(Float, default=0)  # 语言能力（0-100）
    science_ability = Column(Float, default=0)  # 理科能力（0-100）
    arts_ability = Column(Float, default=0)  # 文科能力（0-100）
    
    # 学习行为特征
    homework_completion_rate = Column(Float, default=0)  # 作业完成率
    exam_performance_trend = Column(String(20))  # 考试表现趋势：improving, stable, declining
    mistake_pattern = Column(JSON)  # 错题模式分析
    knowledge_gaps = Column(JSON)  # 知识薄弱点
    
    # 学习偏好
    preferred_difficulty = Column(String(20))  # 偏好难度：easy, medium, hard
    preferred_question_types = Column(JSON)  # 偏好题型
    optimal_study_time = Column(JSON)  # 最佳学习时间段
    
    # 推荐信息
    recommended_resources = Column(JSON)  # 推荐资源
    recommended_exercises = Column(JSON)  # 推荐练习
    learning_suggestions = Column(Text)  # 学习建议
    
    # 元数据
    last_analysis_date = Column(DateTime)  # 最后分析时间
    analysis_version = Column(String(10), default="1.0")  # 分析版本
    confidence_score = Column(Float)  # 画像置信度（0-1）
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    student = relationship("User")
    class_ = relationship("Class")


class LearningResourceRecommendation(Base):
    """学习资源推荐表"""
    __tablename__ = "learning_resource_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # video, article, exercise, book
    resource_id = Column(Integer)  # 资源ID
    resource_title = Column(String(200), nullable=False)
    resource_url = Column(String(500))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    knowledge_point_ids = Column(JSON)  # 相关知识点ID列表
    difficulty_level = Column(String(20))  # easy, medium, hard
    estimated_time = Column(Integer)  # 预估学习时间（分钟）
    recommendation_reason = Column(Text)  # 推荐理由
    recommendation_score = Column(Float)  # 推荐评分（0-1）
    clicked = Column(Boolean, default=False)  # 是否点击
    completed = Column(Boolean, default=False)  # 是否完成
    rating = Column(Integer)  # 用户评分（1-5）
    feedback = Column(Text)  # 用户反馈
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)  # 推荐过期时间

    # 关联关系
    student = relationship("User")
    subject = relationship("Subject")


class TeachingSchedule(Base):
    """教学进度表"""
    __tablename__ = "teaching_schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    chapter_id = Column(String(50), ForeignKey("chapters.id"))
    knowledge_point_ids = Column(JSON)  # 涉及的知识点ID列表
    
    # 进度信息
    title = Column(String(200), nullable=False)  # 教学内容标题
    description = Column(Text)  # 内容描述
    teaching_objectives = Column(JSON)  # 教学目标
    key_points = Column(JSON)  # 重点内容
    difficult_points = Column(JSON)  # 难点内容
    
    # 时间安排
    planned_date = Column(Date, nullable=False)  # 计划授课日期
    actual_date = Column(Date)  # 实际授课日期
    duration_minutes = Column(Integer, default=45)  # 课时长度
    
    # 状态信息
    status = Column(String(20), default="planned")  # planned, ongoing, completed, postponed
    completion_rate = Column(Float, default=0)  # 完成度（0-100）
    student_understanding = Column(Float)  # 学生理解度评估（0-100）
    
    # 关联作业和考试
    homework_ids = Column(JSON)  # 相关作业ID列表
    exam_ids = Column(JSON)  # 相关考试ID列表
    
    # 教学反馈
    teaching_notes = Column(Text)  # 教学笔记
    student_feedback = Column(JSON)  # 学生反馈统计
    next_actions = Column(Text)  # 下一步行动
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    class_ = relationship("Class")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    chapter = relationship("Chapter")


# 为原有模型添加关联关系
# 需要在原有模型文件中添加以下关联关系

# 在 app/models/education.py 的 Class 模型中添加：
# class_info = relationship("ClassInfo", back_populates="class_", uselist=False)
# teacher_assignments = relationship("ClassTeacherAssignment", back_populates="class_")
# student_histories = relationship("StudentClassHistory", back_populates="class_")

# 在 app/models/user.py 的 Teacher 模型中添加：
# class_assignments = relationship("ClassTeacherAssignment", back_populates="teacher")
# teaching_schedules = relationship("TeachingSchedule", back_populates="teacher")

# 在 app/models/homework.py 的 Homework 模型中添加：
# assignments = relationship("HomeworkAssignment", back_populates="homework")

# 在 app/models/exam.py 的 Exam 模型中添加：
# assignments = relationship("ExamAssignment", back_populates="exam")