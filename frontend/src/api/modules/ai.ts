import { request } from '../request';
import { API_ENDPOINTS } from '@/utils/constants';
import type { ApiResponse } from '@/types';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  context?: {
    userId: number;
    role: string;
    subject?: string;
  };
  history?: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  suggestions?: string[];
  actions?: {
    type: string;
    data: any;
  }[];
}

export interface RecommendationRequest {
  userId: number;
  subjectId: number;
  context?: {
    currentLevel?: number;
    learningGoals?: string[];
    weakPoints?: string[];
  };
}

export interface RecommendationResponse {
  questions: Question[];
  learningPath: {
    step: number;
    title: string;
    progress: number;
    resources: any[];
  }[];
  weakPoints: string[];
  nextGoal: string;
}

export interface AnalysisRequest {
  studentId: number;
  timeRange?: {
    start: string;
    end: string;
  };
  subjects?: number[];
}

export interface AnalysisResponse {
  overallScore: number;
  improvement: number;
  strengths: string[];
  weaknesses: string[];
  recommendation: string;
  trendData: {
    date: string;
    score: number;
    subject: string;
  }[];
}

export const aiAPI = {
  // AI聊天
  chat: (data: ChatRequest): Promise<ApiResponse<ChatResponse>> =>
    request.post(API_ENDPOINTS.AI.CHAT, data),

  // 获取个性化推荐
  getRecommendations: (data: RecommendationRequest): Promise<ApiResponse<RecommendationResponse>> =>
    request.post(API_ENDPOINTS.AI.RECOMMENDATIONS, data),

  // 学习分析
  analyzePerformance: (data: AnalysisRequest): Promise<ApiResponse<AnalysisResponse>> =>
    request.post(API_ENDPOINTS.AI.ANALYSIS, data),

  // AI自动组卷
  generateExam: (data: ExamQuestionParams): Promise<ApiResponse<Question[]>> =>
    request.post(API_ENDPOINTS.AI.GENERATE_EXAM, data),
};