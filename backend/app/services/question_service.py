from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.models.content import Question, QuestionKnowledge, KnowledgePoint, QuestionType, DifficultyLevel
from app.schemas.exam import QuestionCreate, QuestionResponse
from app.services.base_service import BaseService


class QuestionService(BaseService[Question]):
    """题库服务"""
    
    def __init__(self, db: Session):
        super().__init__(db, Question)
    
    def search_questions(
        self,
        keyword: Optional[str] = None,
        subject_id: Optional[int] = None,
        difficulty_id: Optional[int] = None,
        question_type_id: Optional[int] = None,
        knowledge_point_ids: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """搜索题目"""
        query = self.db.query(Question).filter(Question.status == 1)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Question.question_text.contains(keyword),
                    Question.title.contains(keyword) if Question.title.isnot(None) else False
                )
            )
        
        # 学科筛选
        if subject_id:
            query = query.filter(Question.subject_id == subject_id)
        
        # 难度筛选
        if difficulty_id:
            query = query.filter(Question.difficulty_id == difficulty_id)
        
        # 题型筛选
        if question_type_id:
            query = query.filter(Question.question_type_id == question_type_id)
        
        # 知识点筛选
        if knowledge_point_ids:
            query = query.join(QuestionKnowledge).filter(
                QuestionKnowledge.knowledge_id.in_(knowledge_point_ids)
            )
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        questions = query.offset(offset).limit(page_size).all()
        
        return {
            "questions": questions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_question_with_knowledge_points(self, question_id: int) -> Optional[Question]:
        """获取题目及其知识点"""
        return self.db.query(Question).options(
            joinedload(Question.knowledge_points).joinedload(QuestionKnowledge.knowledge_point)
        ).filter(Question.id == question_id).first()
    
    def get_recommended_questions(
        self,
        student_id: int,
        subject_id: int,
        count: int = 10
    ) -> List[Question]:
        """获取推荐题目"""
        # 这里可以实现复杂的推荐算法
        # 现在简单返回按难度和热度排序的题目
        questions = self.db.query(Question).filter(
            and_(
                Question.subject_id == subject_id,
                Question.status == 1
            )
        ).order_by(
            Question.difficulty_id.asc(),
            Question.save_num.desc()
        ).limit(count).all()
        
        return questions
    
    def get_similar_questions(self, question_id: int, count: int = 5) -> List[Question]:
        """获取相似题目"""
        question = self.get(question_id)
        if not question:
            return []
        
        # 基于相同知识点和相近难度查找相似题目
        similar_questions = self.db.query(Question).join(QuestionKnowledge).filter(
            and_(
                Question.id != question_id,
                Question.subject_id == question.subject_id,
                Question.difficulty_id.in_([
                    question.difficulty_id - 1,
                    question.difficulty_id,
                    question.difficulty_id + 1
                ]),
                Question.status == 1,
                QuestionKnowledge.knowledge_id.in_(
                    self.db.query(QuestionKnowledge.knowledge_id).filter(
                        QuestionKnowledge.question_id == question_id
                    )
                )
            )
        ).distinct().limit(count).all()
        
        return similar_questions
    
    def create_question(self, question_create: QuestionCreate) -> Question:
        """创建题目"""
        # 生成题目ID
        import uuid
        question_id = str(uuid.uuid4())[:8].upper()
        
        question_data = question_create.dict(exclude={"knowledge_point_ids"})
        question_data["question_id"] = question_id
        
        question = self.create(question_data)
        
        # 关联知识点
        for knowledge_id in question_create.knowledge_point_ids:
            question_knowledge = QuestionKnowledge(
                question_id=question.id,
                knowledge_id=knowledge_id
            )
            self.db.add(question_knowledge)
        
        self.db.commit()
        return question
    
    def get_question_statistics(self, subject_id: Optional[int] = None) -> Dict[str, Any]:
        """获取题库统计信息"""
        query = self.db.query(Question).filter(Question.status == 1)
        
        if subject_id:
            query = query.filter(Question.subject_id == subject_id)
        
        total_questions = query.count()
        
        # 按难度统计
        difficulty_stats = self.db.query(
            DifficultyLevel.name,
            func.count(Question.id).label('count')
        ).join(Question).filter(Question.status == 1)
        
        if subject_id:
            difficulty_stats = difficulty_stats.filter(Question.subject_id == subject_id)
        
        difficulty_stats = difficulty_stats.group_by(DifficultyLevel.name).all()
        
        # 按题型统计
        type_stats = self.db.query(
            QuestionType.name,
            func.count(Question.id).label('count')
        ).join(Question).filter(Question.status == 1)
        
        if subject_id:
            type_stats = type_stats.filter(Question.subject_id == subject_id)
        
        type_stats = type_stats.group_by(QuestionType.name).all()
        
        return {
            "total_questions": total_questions,
            "difficulty_distribution": [
                {"name": stat.name, "count": stat.count}
                for stat in difficulty_stats
            ],
            "type_distribution": [
                {"name": stat.name, "count": stat.count}
                for stat in type_stats
            ]
        }
    