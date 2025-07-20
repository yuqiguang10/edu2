
数据库初始化脚本
"""
import asyncio
from sqlalchemy.orm import Session
from app.core.database import engine, Base
from app.core.config import settings
from app.models import *  # 导入所有模型
from app.services.user_service import UserService
from app.schemas.auth import UserCreate


def create_tables():
    """创建所有表"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def init_basic_data():
    """初始化基础数据"""
    print("Initializing basic data...")
    
    with Session(engine) as db:
        # 创建角色
        roles_data = [
            {"name": "admin", "description": "系统管理员"},
            {"name": "teacher", "description": "教师"},
            {"name": "student", "description": "学生"},
            {"name": "parent", "description": "家长"},
        ]
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
        
        # 创建权限
        permissions_data = [
            {"name": "用户管理", "code": "user:manage", "description": "用户管理权限"},
            {"name": "考试管理", "code": "exam:manage", "description": "考试管理权限"},
            {"name": "题库管理", "code": "question:manage", "description": "题库管理权限"},
            {"name": "数据分析", "code": "analytics:view", "description": "数据分析权限"},
            {"name": "系统配置", "code": "system:config", "description": "系统配置权限"},
            {"name": "班级管理", "code": "class:manage", "description": "班级管理权限"},
            {"name": "作业管理", "code": "homework:manage", "description": "作业管理权限"},
            {"name": "学生查看", "code": "student:view", "description": "学生查看权限"},
            {"name": "成绩查看", "code": "grade:view", "description": "成绩查看权限"},
        ]
        
        for perm_data in permissions_data:
            existing_perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
            if not existing_perm:
                permission = Permission(**perm_data)
                db.add(permission)
        
        db.commit()
        
        # 分配权限给角色
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        teacher_role = db.query(Role).filter(Role.name == "teacher").first()
        student_role = db.query(Role).filter(Role.name == "student").first()
        parent_role = db.query(Role).filter(Role.name == "parent").first()
        
        # 管理员拥有所有权限
        if admin_role:
            all_permissions = db.query(Permission).all()
            for permission in all_permissions:
                existing_rp = db.query(RolePermission).filter(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == permission.id
                ).first()
                if not existing_rp:
                    role_permission = RolePermission(
                        role_id=admin_role.id,
                        permission_id=permission.id
                    )
                    db.add(role_permission)
        
        # 教师权限
        if teacher_role:
            teacher_permissions = ["exam:manage", "homework:manage", "class:manage", "question:manage", "student:view", "grade:view", "analytics:view"]
            for perm_code in teacher_permissions:
                permission = db.query(Permission).filter(Permission.code == perm_code).first()
                if permission:
                    existing_rp = db.query(RolePermission).filter(
                        RolePermission.role_id == teacher_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not existing_rp:
                        role_permission = RolePermission(
                            role_id=teacher_role.id,
                            permission_id=permission.id
                        )
                        db.add(role_permission)
        
        # 学生权限
        if student_role:
            student_permissions = ["student:view", "grade:view"]
            for perm_code in student_permissions:
                permission = db.query(Permission).filter(Permission.code == perm_code).first()
                if permission:
                    existing_rp = db.query(RolePermission).filter(
                        RolePermission.role_id == student_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not existing_rp:
                        role_permission = RolePermission(
                            role_id=student_role.id,
                            permission_id=permission.id
                        )
                        db.add(role_permission)
        
        # 家长权限
        if parent_role:
            parent_permissions = ["student:view", "grade:view"]
            for perm_code in parent_permissions:
                permission = db.query(Permission).filter(Permission.code == perm_code).first()
                if permission:
                    existing_rp = db.query(RolePermission).filter(
                        RolePermission.role_id == parent_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not existing_rp:
                        role_permission = RolePermission(
                            role_id=parent_role.id,
                            permission_id=permission.id
                        )
                        db.add(role_permission)
        
        # 创建学段
        study_levels_data = [
            {"id": 1, "name": "小学", "code": "primary", "description": "小学阶段"},
            {"id": 2, "name": "初中", "code": "junior", "description": "初中阶段"},
            {"id": 3, "name": "高中", "code": "senior", "description": "高中阶段"},
        ]
        
        for level_data in study_levels_data:
            existing_level = db.query(StudyLevel).filter(StudyLevel.id == level_data["id"]).first()
            if not existing_level:
                study_level = StudyLevel(**level_data)
                db.add(study_level)
        
        # 创建学科
        subjects_data = [
            {"id": 1, "name": "数学", "code": "math", "description": "数学学科"},
            {"id": 2, "name": "英语", "code": "english", "description": "英语学科"},
            {"id": 3, "name": "物理", "code": "physics", "description": "物理学科"},
            {"id": 4, "name": "化学", "code": "chemistry", "description": "化学学科"},
            {"id": 5, "name": "语文", "code": "chinese", "description": "语文学科"},
            {"id": 6, "name": "生物", "code": "biology", "description": "生物学科"},
        ]
        
        for subject_data in subjects_data:
            existing_subject = db.query(Subject).filter(Subject.id == subject_data["id"]).first()
            if not existing_subject:
                subject = Subject(**subject_data)
                db.add(subject)
        
        # 创建学段-学科关联
        study_level_subjects = [
            (1, 1), (1, 2), (1, 5),  # 小学：数学、英语、语文
            (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),  # 初中：全部学科
            (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),  # 高中：全部学科
        ]
        
        for study_level_id, subject_id in study_level_subjects:
            existing = db.query(StudyLevelSubject).filter(
                StudyLevelSubject.study_level_id == study_level_id,
                StudyLevelSubject.subject_id == subject_id
            ).first()
            if not existing:
                relation = StudyLevelSubject(
                    study_level_id=study_level_id,
                    subject_id=subject_id
                )
                db.add(relation)
        
        # 创建题型
        question_types_data = [
            {"id": 1, "name": "单选题", "code": "single_choice", "display_order": 1},
            {"id": 2, "name": "多选题", "code": "multiple_choice", "display_order": 2},
            {"id": 3, "name": "填空题", "code": "fill_blank", "display_order": 3},
            {"id": 4, "name": "判断题", "code": "true_false", "display_order": 4},
            {"id": 5, "name": "简答题", "code": "short_answer", "display_order": 5},
            {"id": 6, "name": "论述题", "code": "essay", "display_order": 6},
            {"id": 7, "name": "计算", "code": "calculation", "display_order": 7},
            {"id": 8, "name": "证明题", "code": "proof", "display_order": 8},
        ]
        
        for type_data in question_types_data:
            existing_type = db.query(QuestionType).filter(QuestionType.id == type_data["id"]).first()
            if not existing_type:
                question_type = QuestionType(**type_data)
                db.add(question_type)
        
        # 创建难度级别
        difficulty_levels_data = [
            {"id": 1, "name": "容易", "level": 1, "description": "基础题目，难度较低"},
            {"id": 2, "name": "较易", "level": 2, "description": "稍有难度的基础题"},
            {"id": 3, "name": "普通", "level": 3, "description": "中等难度题目"},
            {"id": 4, "name": "较难", "level": 4, "description": "有一定挑战性的题目"},
            {"id": 5, "name": "困难", "level": 5, "description": "高难度题目"},
        ]
        
        for difficulty_data in difficulty_levels_data:
            existing_difficulty = db.query(DifficultyLevel).filter(DifficultyLevel.id == difficulty_data["id"]).first()
            if not existing_difficulty:
                difficulty = DifficultyLevel(**difficulty_data)
                db.add(difficulty)
        
        # 创建示例学校
        school_data = {
            "name": "示例中学",
            "code": "DEMO_SCHOOL",
            "address": "北京市海淀区示例路123号",
            "phone": "010-12345678",
            "email": "demo@school.edu.cn",
            "description": "这是一个示例学校"
        }
        
        existing_school = db.query(School).filter(School.code == school_data["code"]).first()
        if not existing_school:
            school = School(**school_data)
            db.add(school)
            db.commit()  # 提交以获取ID
            
            # 创建示例部门
            departments_data = [
                {"name": "教务处", "school_id": school.id, "description": "负责教学管理"},
                {"name": "学生处", "school_id": school.id, "description": "负责学生管理"},
                {"name": "数学教研组", "school_id": school.id, "description": "数学学科教研"},
                {"name": "英语教研组", "school_id": school.id, "description": "英语学科教研"},
            ]
            
            for dept_data in departments_data:
                department = Department(**dept_data)
                db.add(department)
        
        # 提交所有基础数据
        db.commit()
        print("Basic data initialized successfully!")


def create_demo_users():
    """创建演示用户"""
    print("Creating demo users...")
    
    with Session(engine) as db:
        user_service = UserService(db)
        
        # 创建管理员用户
        admin_exists = user_service.get_by_username("admin")
        if not admin_exists:
            admin_data = UserCreate(
                username="admin",
                email="admin@edu-platform.com",
                password="123456",
                real_name="系统管理员",
                role="admin"
            )
            user_service.create_user(admin_data)
            print("Admin user created: admin/123456")
        
        # 创建教师用户
        teacher_exists = user_service.get_by_username("teacher")
        if not teacher_exists:
            teacher_data = UserCreate(
                username="teacher",
                email="teacher@edu-platform.com",
                password="123456",
                real_name="张老师",
                phone="13800138001",
                role="teacher"
            )
            teacher_user = user_service.create_user(teacher_data)
            
            # 为教师创建详细信息
            teacher_profile = Teacher(
                user_id=teacher_user.id,
                subject_id=1,  # 数学
                title="高级教师",
                education="硕士研究生",
                experience=10,
                bio="资深数学教师，擅长初高中数学教学"
            )
            db.add(teacher_profile)
            print("Teacher user created: teacher/123456")
        
        # 创建学生用户
        student_exists = user_service.get_by_username("student")
        if not student_exists:
            student_data = UserCreate(
                username="student",
                email="student@edu-platform.com",
                password="123456",
                real_name="李同学",
                student_id="2024001",
                role="student"
            )
            student_user = user_service.create_user(student_data)
            print("Student user created: student/123456")
        
        # 创建家长用户
        parent_exists = user_service.get_by_username("parent")
        if not parent_exists:
            parent_data = UserCreate(
                username="parent",
                email="parent@edu-platform.com",
                password="123456",
                real_name="李家长",
                phone="13800138002",
                role="parent"
            )
            parent_user = user_service.create_user(parent_data)
            print("Parent user created: parent/123456")
        
        db.commit()


def create_demo_class_and_relations():
    """创建演示班级和关联关系"""
    print("Creating demo class and relations...")
    
    with Session(engine) as db:
        # 创建示例班级
        class_data = {
            "name": "高一(1)班",
            "grade_name": "高一",
            "study_level_id": 3,  # 高中
            "description": "示例班级"
        }
        
        existing_class = db.query(Class).filter(Class.name == class_data["name"]).first()
        if not existing_class:
            demo_class = Class(**class_data)
            db.add(demo_class)
            db.commit()
            
            # 获取演示用户
            student_user = db.query(User).filter(User.username == "student").first()
            teacher_user = db.query(User).filter(User.username == "teacher").first()
            parent_user = db.query(User).filter(User.username == "parent").first()
            
            if student_user and demo_class:
                # 将学生加入班级
                from datetime import date
                class_student = ClassStudent(
                    class_id=demo_class.id,
                    student_id=student_user.id,
                    join_date=date.today()
                )
                db.add(class_student)
            
            if teacher_user and demo_class:
                # 设置班主任
                demo_class.class_teacher_id = teacher_user.id
            
            if parent_user and student_user:
                # 建立家长-学生关系
                from app.models.education import ParentStudentRelation
                parent_relation = ParentStudentRelation(
                    parent_id=parent_user.id,
                    student_id=student_user.id,
                    relation_type="父母"
                )
                db.add(parent_relation)
            
            db.commit()
            print("Demo class and relations created successfully!")


def create_sample_questions():
    """创建示例试题"""
    print("Creating sample questions...")
    
    with Session(engine) as db:
        # 创建一些示例试题
        questions_data = [
            {
                "question_id": "DEMO_Q001",
                "question_type_id": 1,  # 单选题
                "subject_id": 1,  # 数学
                "difficulty_id": 2,  # 较易
                "title": "二次函数基础题",
                "question_text": "函数 f(x) = x² - 2x + 1 的最小值是多少？",
                "options": '{"A": "0", "B": "1", "C": "-1", "D": "2"}',
                "answer": "A",
                "explanation": "f(x) = x² - 2x + 1 = (x-1)²，当x=1时取得最小值0",
                "is_objective": True,
                "save_num": 50
            },
            {
                "question_id": "DEMO_Q002",
                "question_type_id": 1,  # 单选题
                "subject_id": 1,  # 数学
                "difficulty_id": 3,  # 普通
                "title": "三角函数题",
                "question_text": "sin(30°) + cos(60°) 的值是多少？",
                "options": '{"A": "1", "B": "0.5", "C": "1.5", "D": "√3"}',
                "answer": "A",
                "explanation": "sin(30°) = 1/2, cos(60°) = 1/2, 所以和为1",
                "is_objective": True,
                "save_num": 30
            },
            {
                "question_id": "DEMO_Q003",
                "question_type_id": 5,  # 简答题
                "subject_id": 1,  # 数学
                "difficulty_id": 4,  # 较难
                "title": "导数应用题",
                "question_text": "已知函数 f(x) = x³ - 3x² + 2，求函数的极值点和极值。",
                "answer": "f'(x) = 3x² - 6x = 3x(x-2)，令f'(x)=0得x=0或x=2。当x=0时f(0)=2为极大值，当x=2时f(2)=-2为极小值。",
                "explanation": "通过求导数并令其为零找到极值点，然后计算二阶导数判断极值类型",
                "is_objective": False,
                "save_num": 20
            },
            {
                "question_id": "DEMO_Q004",
                "question_type_id": 1,  # 单选题
                "subject_id": 2,  # 英语
                "difficulty_id": 2,  # 较易
                "title": "英语语法题",
                "question_text": "Choose the correct answer: I _____ to Beijing twice.",
                "options": '{"A": "have been", "B": "have gone", "C": "went", "D": "go"}',
                "answer": "A",
                "explanation": "现在完成时表示过去的经历，have been表示去过并已回来",
                "is_objective": True,
                "save_num": 40
            },
            {
                "question_id": "DEMO_Q005",
                "question_type_id": 3,  # 填空题
                "subject_id": 3,  # 物理
                "difficulty_id": 3,  # 普通
                "title": "物理计算题",
                "question_text": "一个质量为2kg的物体在水平面上运动，受到8N的水平推力，摩擦系数为0.2，重力加速度g=10m/s²，则物体的加速度为___m/s²。",
                "answer": "3",
                "explanation": "摩擦力f=μmg=0.2×2×10=4N，净力F净=8-4=4N，根据F=ma得a=F净/m=4/2=2m/s²",
                "is_objective": True,
                "save_num": 25
            }
        ]
        
        for q_data in questions_data:
            existing_q = db.query(Question).filter(Question.question_id == q_data["question_id"]).first()
            if not existing_q:
                question = Question(**q_data)
                db.add(question)
        
        db.commit()
        print("Sample questions created successfully!")


def create_sample_exam():
    """创建示例考试"""
    print("Creating sample exam...")
    
    with Session(engine) as db:
        # 获取演示数据
        demo_class = db.query(Class).filter(Class.name == "高一(1)班").first()
        teacher_user = db.query(User).filter(User.username == "teacher").first()
        questions = db.query(Question).limit(3).all()
        
        if demo_class and teacher_user and questions:
            from datetime import datetime, timedelta
            
            exam_data = {
                "title": "数学单元测试",
                "description": "函数与导数单元测试",
                "class_id": demo_class.id,
                "subject_id": 1,  # 数学
                "teacher_id": teacher_user.id,
                "start_time": datetime.now() + timedelta(days=1),
                "end_time": datetime.now() + timedelta(days=1, hours=2),
                "duration": 120,
                "total_score": 100.0,
                "status": "published"
            }
            
            existing_exam = db.query(Exam).filter(Exam.title == exam_data["title"]).first()
            if not existing_exam:
                exam = Exam(**exam_data)
                db.add(exam)
                db.commit()
                
                # 添加考试题目
                for i, question in enumerate(questions):
                    exam_question = ExamQuestion(
                        exam_id=exam.id,
                        question_id=question.id,
                        score=30.0 if i < 2 else 40.0,  # 前两题30分，最后一题40分
                        sequence=i + 1
                    )
                    db.add(exam_question)
                
                db.commit()
                print("Sample exam created successfully!")


def init_system_configs():
    """初始化系统配置"""
    print("Initializing system configurations...")
    
    with Session(engine) as db:
        from app.models.system import SystemConfig
        
        configs_data = [
            {
                "config_key": "system_name",
                "config_value": "K12智能教育平台",
                "description": "系统名称"
            },
            {
                "config_key": "system_version",
                "config_value": "1.0.0",
                "description": "系统版本"
            },
            {
                "config_key": "max_upload_size",
                "config_value": "10485760",
                "description": "最大上传文件大小(字节)"
            },
            {
                "config_key": "session_timeout",
                "config_value": "3600",
                "description": "会话超时时间(秒)"
            },
            {
                "config_key": "enable_ai_features",
                "config_value": "true",
                "description": "是否启用AI功能"
            }
        ]
        
        for config_data in configs_data:
            existing_config = db.query(SystemConfig).filter(
                SystemConfig.config_key == config_data["config_key"]
            ).first()
            if not existing_config:
                config = SystemConfig(**config_data)
                db.add(config)
        
        db.commit()
        print("System configurations initialized successfully!")


def main():
    """主函数"""
    print("🚀 Starting database initialization...")
    
    try:
        # 1. 创建表结构
        create_tables()
        
        # 2. 初始化基础数据
        init_basic_data()
        
        # 3. 创建演示用户
        create_demo_users()
        
        # 4. 创建演示班级和关联关系
        create_demo_class_and_relations()
        
        # 5. 创建示例试题
        create_sample_questions()
        
        # 6. 创建示例考试
        create_sample_exam()
        
        # 7. 初始化系统配置
        init_system_configs()
        
        print("✅ Database initialization completed successfully!")
        print("\n📊 Demo users created:")
        print("👑 Admin: admin / 123456")
        print("👨‍🏫 Teacher: teacher / 123456")
        print("👨‍🎓 Student: student / 123456")
        print("👨‍👩‍👧‍👦 Parent: parent / 123456")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {str(e)}")
        raise


if __name__ == "__main__":
    main()
