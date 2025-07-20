from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class StudyLevel(Base):
    """学段表"""
    __tablename__ = "study_levels"
    
    name = Column(String(50), nullable=False)
    code = Column(String(20))
    description = Column(Text)
    display_order = Column(Integer, default=0)
    
    # 关系
    classes = relationship("Class", back_populates="study_level")
    subjects = relationship("Subject", secondary="study_level_subject", back_populates="study_levels")


class Subject(Base):
    """学科表"""
    __tablename__ = "subjects"
    
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    
    # 关系
    study_levels = relationship("StudyLevel", secondary="study_level_subject", back_populates="subjects")
    teachers = relationship("Teacher", back_populates="subject")
    exams = relationship("Exam", back_populates="subject")


class StudyLevelSubject(Base):
    """学段-学科关联表"""
    __tablename__ = "study_level_subject"
    
    study_level_id = Column(Integer, ForeignKey("study_levels.id"), primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), primary_key=True)


class School(Base):
    """学校表"""
    __tablename__ = "schools"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True)
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(100))
    description = Column(Text)
    status = Column(Integer, nullable=False, default=1)
    
    # 关系
    departments = relationship("Department", back_populates="school")


class Department(Base):
    """部门表"""
    __tablename__ = "departments"
    
    name = Column(String(50), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"))
    description = Column(String(255))
    status = Column(Integer, nullable=False, default=1)
    
    # 关系
    school = relationship("School", back_populates="departments")
    parent = relationship("Department", remote_side=[Base.id])
    teachers = relationship("Teacher", back_populates="department")


class Teacher(Base):
    """教师表"""
    __tablename__ = "teachers"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    title = Column(String(50))
    education = Column(String(50))
    experience = Column(Integer)
    bio = Column(Text)
    status = Column(Integer, nullable=False, default=1)
    
    # 关系
    user = relationship("User", back_populates="teacher_profile")
    department = relationship("Department", back_populates="teachers")
    subject = relationship("Subject", back_populates="teachers")
    classes = relationship("Class", foreign_keys="Class.class_teacher_id", back_populates="class_teacher")
    exams = relationship("Exam", back_populates="teacher")


class Class(Base):
    """班级表"""
    __tablename__ = "classes"
    
    name = Column(String(50), nullable=False)
    grade_name = Column(String(50), nullable=False)
    study_level_id = Column(Integer, ForeignKey("study_levels.id"), nullable=False)
    class_teacher_id = Column(Integer, ForeignKey("teachers.id"))
    description = Column(String(255))
    status = Column(Integer, nullable=False, default=1)
    
    # 关系
    study_level = relationship("StudyLevel", back_populates="classes")
    class_teacher = relationship("Teacher", foreign_keys=[class_teacher_id], back_populates="classes")
    students = relationship("ClassStudent", back_populates="class_obj")
    exams = relationship("Exam", back_populates="class_obj")


class ClassStudent(Base):
    """班级-学生关联表"""
    __tablename__ = "class_students"
    
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    join_date = Column(Date, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    
    # 关系
    class_obj = relationship("Class", back_populates="students")
    student = relationship("User")
