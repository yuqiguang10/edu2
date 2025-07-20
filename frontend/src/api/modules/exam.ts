import { request } from '../request';
import { API_ENDPOINTS } from '@/utils/constants';
import type { 
  Exam, 
  ExamRecord, 
  Question,
  ApiResponse,
  PaginationParams,
  PaginationResponse 
} from '@/types';

export interface CreateExamData {
  title: string;
  description?: string;
  classId: number;
  subjectId: number;
  startTime: string;
  endTime: string;
  duration: number;
  totalScore: number;
  questionIds: number[];
}

export interface ExamQuestionParams {
  subjectId: number;
  difficultyLevel?: number;
  knowledgePointIds?: number[];
  questionCount: number;
}

export interface SubmitExamData {
  answers: {
    questionId: number;
    answer: string;
  }[];
}

export const examAPI = {
  // 获取考试列表
  getExams: (params?: PaginationParams & { status?: string }): Promise<ApiResponse<PaginationResponse<Exam>>> =>
    request.get(API_ENDPOINTS.EXAMS.LIST, { params }),

  // 创建考试
  createExam: (data: CreateExamData): Promise<ApiResponse<Exam>> =>
    request.post(API_ENDPOINTS.EXAMS.CREATE, data),

  // 获取考试详情
  getExamDetail: (id: number): Promise<ApiResponse<Exam>> =>
    request.get(API_ENDPOINTS.EXAMS.DETAIL(id)),

  // 更新考试
  updateExam: (id: number, data: Partial<CreateExamData>): Promise<ApiResponse<Exam>> =>
    request.put(API_ENDPOINTS.EXAMS.UPDATE(id), data),

  // 删除考试
  deleteExam: (id: number): Promise<ApiResponse<void>> =>
    request.delete(API_ENDPOINTS.EXAMS.DELETE(id)),

  // 开始考试
  startExam: (id: number): Promise<ApiResponse<ExamRecord>> =>
    request.post(API_ENDPOINTS.EXAMS.START(id)),

  // 提交考试
  submitExam: (id: number, data: SubmitExamData): Promise<ApiResponse<ExamRecord>> =>
    request.post(API_ENDPOINTS.EXAMS.SUBMIT(id), data),

  // 获取考试题目
  getExamQuestions: (id: number): Promise<ApiResponse<Question[]>> =>
    request.get(API_ENDPOINTS.EXAMS.QUESTIONS(id)),

  // AI智能组卷
  generateExamQuestions: (params: ExamQuestionParams): Promise<ApiResponse<Question[]>> =>
    request.post(`${API_ENDPOINTS.EXAMS.LIST}/generate-questions`, params),
};