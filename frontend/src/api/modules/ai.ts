// frontend/src/api/modules/ai.ts (更新版本)
import { request } from '../request';
import { API_ENDPOINTS } from '@/utils/constants';
import type { ApiResponse } from '@/types';

export interface AIAgentInitResponse {
  agent_id: string;
  status: string;
  agent_type: string;
  recommendations: any[];
  initial_context: any;
}

export interface ActionRequest {
  action_type: string;
  data: any;
  context?: any;
  timestamp?: string;
}

export interface ActionResponse {
  response_type: string;
  suggestions: string[];
  recommendations: any[];
  feedback: string;
  next_actions: any[];
  context_updates: any;
}

export interface Recommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  priority: number;
  estimated_time: number;
  data: any;
  reasoning: string;
}

export interface ChatRequest {
  message: string;
  context?: any;
  history?: Array<{role: string; content: string}>;
}

export interface ChatResponse {
  message: string;
  suggestions: string[];
  actions: any[];
  context: any;
}

export interface LearningAnalysis {
  period_days: number;
  total_learning_time: number;
  session_count: number;
  average_session_duration: number;
  most_active_hour: number;
  consistency_score: number;
  recent_activities: number;
  activity_trend: string;
  focus_level?: number;
  suggestions?: string[];
}

export const aiAPI = {
  // 初始化AI Agent
  initializeAgent: (): Promise<ApiResponse<AIAgentInitResponse>> =>
    request.post(API_ENDPOINTS.AI.AGENT_INIT),

  // 处理用户行为
  processAction: (data: ActionRequest): Promise<ApiResponse<ActionResponse>> =>
    request.post(API_ENDPOINTS.AI.AGENT_ACTION, data),

  // 获取个性化推荐
  getRecommendations: (params?: { context?: string }): Promise<ApiResponse<Recommendation[]>> =>
    request.get(API_ENDPOINTS.AI.RECOMMENDATIONS, { params }),

  // AI对话
  chat: (data: ChatRequest): Promise<ApiResponse<ChatResponse>> =>
    request.post(API_ENDPOINTS.AI.CHAT, data),

  // 获取Agent状态
  getAgentStatus: (): Promise<ApiResponse<any>> =>
    request.get(API_ENDPOINTS.AI.AGENT_STATUS),

  // 关闭Agent
  shutdownAgent: (): Promise<ApiResponse<any>> =>
    request.post(API_ENDPOINTS.AI.AGENT_SHUTDOWN),

  // 获取学习分析
  getLearningAnalysis: (days: number = 7): Promise<ApiResponse<LearningAnalysis>> =>
    request.get(API_ENDPOINTS.AI.LEARNING_ANALYSIS, { params: { days } }),
};
