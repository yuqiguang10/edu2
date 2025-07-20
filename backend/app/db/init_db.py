# backend/app/db/init_db.py
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models import user, education, question, exam, homework, analytics
from app.core.security import get_password_hash


def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)


def init_basic_data(db: Session):
    """初始化基础数据"""
    
    # 创建默认角色
    from app.models.user import Role, Permission, RolePermission
    
    roles_data = [
        {"name": "admin", "description": "系统管理员"},
        {"name": "teacher", "description": "教师"},
        {"name": "student", "description": "学生"},
        {"name": "parent", "description": "家长"}
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    
    # 创建权限数据
    permissions_data = [
        {"name": "用户管理", "code": "user:manage", "description": "管理用户信息"},
        {"name": "试题管理", "code": "question:manage", "description": "管理试题库"},
        {"name": "考试管理", "code": "exam:manage", "description": "管理考试"},
        {"name": "作业管理", "code": "homework:manage", "description": "管理作业"},
        {"name": "班级管理", "code": "class:manage", "description": "管理班级"},
        {"name": "数据分析", "code": "analytics:view", "description": "查看数据分析"},
        {"name": "系统配置", "code": "system:config", "description": "系统配置管理"}
    ]
    
    for perm_data in permissions_data:
        existing_perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing_perm:
            permission = Permission(**perm_data)
            db.add(permission)
    
    db.commit()
    
    # 为管理员角色分配所有权限
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if admin_role:
        permissions = db.query(Permission).all()
        for permission in permissions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            if not existing:
                role_perm = RolePermission(role_id=admin_role.id, permission_id=permission.id)
                db.add(role_perm)
    
    db.commit()
    
    # 创建学段数据
    from app.models.education import StudyLevel, Subject, StudyLevelSubject
    
    study_levels_data = [
        {"id": 1, "name": "小学", "code": "primary", "description": "小学阶段"},
        {"id": 2, "name": "初中", "code": "junior", "description": "初中阶段"},
        {"id": 3, "name": "高中", "code": "senior", "description": "高中阶段"}
    ]
    
    for level_data in study_levels_data:
        existing_level = db.query(StudyLevel).filter(StudyLevel.id == level_data["id"]).first()
        if not existing_level:
            level = StudyLevel(**level_data)
            db.add(level)
    
    db.commit()
    
    # 创建学科数据
    subjects_data = [
        {"id": 2, "name": "语文", "code": "chinese", "description": "语文学科"},
        {"id": 3, "name": "数学", "code": "math", "description": "数学学科"},
        {"id": 4, "name": "英语", "code": "english", "description": "英语学科"},
        {"id": 5, "name": "物理", "code": "physics", "description": "物理学科"},
        {"id": 6, "name": "化学", "code": "chemistry", "description": "化学学科"},
        {"id": 7, "name": "生物", "code": "biology", "description": "生物学科"},
        {"id": 8, "name": "历史", "code": "history", "description": "历史学科"},
        {"id": 9, "name": "地理", "code": "geography", "description": "地理学科"},
        {"id": 10, "name": "政治", "code": "politics", "description": "政治学科"}
    ]
    
    for subject_data in subjects_data:
        existing_subject = db.query(Subject).filter(Subject.id == subject_data["id"]).first()
        if not existing_subject:
            subject = Subject(**subject_data)
            db.add(subject)
    
    db.commit()
    
    # 创建学段学科关联
    level_subject_relations = [
        # 小学
        (1, 2), (1, 3), (1, 4),  # 语文、数学、英语
        # 初中  
        (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
        # 高中
        (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10)
    ]
    
    for level_id, subject_id in level_subject_relations:
        existing = db.query(StudyLevelSubject).filter(
            StudyLevelSubject.study_level_id == level_id,
            StudyLevelSubject.subject_id == subject_id
        ).first()
        if not existing:
            relation = StudyLevelSubject(study_level_id=level_id, subject_id=subject_id)
            db.add(relation)
    
    db.commit()
    
    # 创建难度级别
    from app.models.question import DifficultyLevel
    
    difficulty_data = [
        {"id": 1, "name": "容易", "level": 1, "description": "基础题目"},
        {"id": 2, "name": "较易", "level": 2, "description": "稍有难度"},
        {"id": 3, "name": "普通", "level": 3, "description": "中等难度"},
        {"id": 4, "name": "较难", "level": 4, "description": "有一定挑战"},
        {"id": 5, "name": "困难", "level": 5, "description": "高难度题目"}
    ]
    
    for diff_data in difficulty_data:
        existing_diff = db.query(DifficultyLevel).filter(DifficultyLevel.id == diff_data["id"]).first()
        if not existing_diff:
            difficulty = DifficultyLevel(**diff_data)
            db.add(difficulty)
    
    db.commit()
    
    # 创建题型数据
    from app.models.question import QuestionType
    
    question_types_data = [
        {"id": 1, "name": "单选题", "code": "single_choice", "display_order": 1},
        {"id": 2, "name": "多选题", "code": "multiple_choice", "display_order": 2},
        {"id": 3, "name": "填空题", "code": "fill_blank", "display_order": 3},
        {"id": 4, "name": "判断题", "code": "true_false", "display_order": 4},
        {"id": 5, "name": "解答题", "code": "essay", "display_order": 5},
        {"id": 6, "name": "计算题", "code": "calculation", "display_order": 6}
    ]
    
    for type_data in question_types_data:
        existing_type = db.query(QuestionType).filter(QuestionType.id == type_data["id"]).first()
        if not existing_type:
            question_type = QuestionType(**type_data)
            db.add(question_type)
    
    db.commit()
    
    # 创建默认管理员用户
    from app.models.user import User, UserRole
    
    admin_user_data = {
        "username": "admin",
        "email": "admin@k12edu.com",
        "password_hash": get_password_hash("admin123"),
        "real_name": "系统管理员",
        "status": 1
    }
    
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        admin_user = User(**admin_user_data)
        db.add(admin_user)
        db.flush()  # 获取user.id
        
        # 分配管理员角色
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.add(user_role)
    
    db.commit()
    
    print("基础数据初始化完成!")


def init_sample_data(db: Session):
    """初始化示例数据"""
    
    # 创建示例学校
    from app.models.education import School, Department, Class
    
    school_data = {
        "name": "示例中学",
        "code": "DEMO_SCHOOL",
        "address": "示例市示例区示例街道123号",
        "phone": "010-12345678",
        "email": "demo@school.edu.cn",
        "description": "这是一个示例学校"
    }
    
    existing_school = db.query(School).filter(School.code == "DEMO_SCHOOL").first()
    if not existing_school:
        school = School(**school_data)
        db.add(school)
        db.flush()
        
        # 创建示例部门
        dept_data = {
            "name": "教务处",
            "school_id": school.id,
            "description": "负责教学管理"
        }
        department = Department(**dept_data)
        db.add(department)
        db.flush()
        
        # 创建示例班级
        class_data = {
            "name": "九年级1班",
            "grade_name": "九年级",
            "study_level_id": 2,  # 初中
            "description": "示例班级"
        }
        demo_class = Class(**class_data)
        db.add(demo_class)
    
    db.commit()
    
    print("示例数据初始化完成!")


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建表
    create_tables()
    print("数据库表创建完成!")
    
    # 初始化数据
    db = SessionLocal()
    try:
        init_basic_data(db)
        init_sample_data(db)
    except Exception as e:
        print(f"初始化数据失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("数据库初始化完成!")


if __name__ == "__main__":
    init_database()