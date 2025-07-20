// src/types/exam.ts
export interface Question extends BaseEntity {
  questionId: string;
  questionTypeId: number;
  subjectId: number;
  difficultyId: number;
  title?: string;
  questionText: string;
  options?: string;
  answer: string;
  explanation?: string;
  isObjective: boolean;
  saveNum: number;
  knowledgePoints: KnowledgePoint[];
}

export interface KnowledgePoint extends BaseEntity {
  title: string;
  upid?: string;
  displayOrder: number;
  hasChild: boolean;
  xd: number;
  chid: number;
}

export interface Exam extends BaseEntity {
  title: string;
  description?: string;
  classId: number;
  subjectId: number;
  teacherId: number;
  startTime: string;
  endTime: string;
  duration: number;
  totalScore: number;
  status: ExamStatus;
  questions: ExamQuestion[];
}

export interface ExamQuestion {
  id: number;
  examId: number;
  questionId: number;
  score: number;
  sequence: number;
  question?: Question;
}

export interface ExamRecord extends BaseEntity {
  studentId: number;
  examId: number;
  startTime: string;
  submitTime?: string;
  totalScore?: number;
  status: number;
  answers: ExamAnswer[];
}

export interface ExamAnswer {
  id: number;
  examRecordId: number;
  questionId: number;
  answer: string;
  score?: number;
  isCorrect?: boolean;
  reviewComment?: string;
}
