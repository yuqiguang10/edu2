# backend/app/models/education.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class School(Base):
    """学校表"""
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True)
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(100))
    description = Column(Text)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    departments = relationship("Department", back_populates="school")


class Department(Base):
    """部门表"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"))
    description = Column(String(255))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    school = relationship("School", back_populates="departments")
    parent = relationship("Department", remote_side="Department.id")
    teachers = relationship("Teacher", back_populates="department")


class StudyLevel(Base):
    """学段表"""
    __tablename__ = "study_levels"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    code = Column(String(20))
    description = Column(Text)
    display_order = Column(Integer, default=0)

    # 关联关系
    subjects = relationship("StudyLevelSubject", back_populates="study_level")
    classes = relationship("Class", back_populates="study_level")
    textbook_versions = relationship("TextbookVersion", back_populates="study_level")


class Subject(Base):
    """学科表"""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)

    # 关联关系
    study_levels = relationship("StudyLevelSubject", back_populates="subject")
    teachers = relationship("Teacher", back_populates="subject")
    textbook_versions = relationship("TextbookVersion", back_populates="subject")


class StudyLevelSubject(Base):
    """学段学科关联表"""
    __tablename__ = "study_level_subject"

    study_level_id = Column(Integer, ForeignKey("study_levels.id"), primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), primary_key=True)

    # 关联关系
    study_level = relationship("StudyLevel", back_populates="subjects")
    subject = relationship("Subject", back_populates="study_levels")


class TextbookVersion(Base):
    """教材版本表"""
    __tablename__ = "textbook_versions"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    xd = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    publisher = Column(String(100))

    # 关联关系
    subject = relationship("Subject", back_populates="textbook_versions")
    study_level = relationship("StudyLevel", back_populates="textbook_versions")
    grades = relationship("Grade", back_populates="version")


class Grade(Base):
    """年级表"""
    __tablename__ = "grades"

    id = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False)
    study_level_id = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    term = Column(String(20), nullable=False)  # 上学期/下学期
    display_order = Column(Integer, nullable=False)
    version_id = Column(String(50), ForeignKey("textbook_versions.id"), nullable=False)

    # 关联关系
    study_level = relationship("StudyLevel")
    version = relationship("TextbookVersion", back_populates="grades")
    chapters = relationship("Chapter", back_populates="grade")


class Class(Base):
    """班级表"""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    grade_name = Column(String(50), nullable=False)
    study_level_id = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    class_teacher_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String(255))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    study_level = relationship("StudyLevel", back_populates="classes")
    class_teacher = relationship("User")
    students = relationship("ClassStudent", back_populates="class_")
    teachers = relationship("ClassTeacher", back_populates="class_")
    courses = relationship("Course", back_populates="class_")


class ClassStudent(Base):
    """班级学生关联表"""
    __tablename__ = "class_students"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    join_date = Column(Date, nullable=False)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    class_ = relationship("Class", back_populates="students")
    student = relationship("User")


class ClassTeacher(Base):
    """班级教师关联表"""
    __tablename__ = "class_teachers"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # 关联关系
    class_ = relationship("Class", back_populates="teachers")
    teacher = relationship("Teacher", back_populates="class_teachers")
    subject = relationship("Subject")


class Course(Base):
    """课程表"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    description = Column(Text)
    semester = Column(String(20), nullable=False)
    credit = Column(Integer, default=0)
    total_hours = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    class_ = relationship("Class", back_populates="courses")
    schedules = relationship("CourseSchedule", back_populates="course")


class CourseSchedule(Base):
    """课程安排表"""
    __tablename__ = "course_schedules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1-7
    start_time = Column(String(5), nullable=False)  # "08:00"
    end_time = Column(String(5), nullable=False)    # "08:45"
    classroom = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联关系
    course = relationship("Course", back_populates="schedules")
