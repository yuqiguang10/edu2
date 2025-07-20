from app.models.base import Base
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.models.education import (
    StudyLevel, Subject, StudyLevelSubject, School, Department,
    Teacher, Class, ClassStudent
)
from app.models.content import (
    TextbookVersion, Chapter, KnowledgePoint, QuestionType,
    DifficultyLevel, Question, QuestionKnowledge
)
from app.models.exam import (
    Exam, ExamQuestion, ExamRecord, ExamAnswer,
    Homework, HomeworkSubmission
)
from app.models.analytics import (
    StudentProfile, StudentKnowledgeMastery, LearningBehavior,
    LearningRecommendation
)

# 确保所有模型都被导入，这样alembic才能检测到它们
__all__ = [
    "Base",
    "User", "Role", "Permission", "UserRole", "RolePermission",
    "StudyLevel", "Subject", "StudyLevelSubject", "School", "Department",
    "Teacher", "Class", "ClassStudent",
    "TextbookVersion", "Chapter", "KnowledgePoint", "QuestionType",
    "DifficultyLevel", "Question", "QuestionKnowledge",
    "Exam", "ExamQuestion", "ExamRecord", "ExamAnswer",
    "Homework", "HomeworkSubmission",
    "StudentProfile", "StudentKnowledgeMastery", "LearningBehavior",
    "LearningRecommendation"
]
