import { StateCreator } from 'zustand';
import { aiAPI, type ChatMessage, type RecommendationResponse, type AnalysisResponse } from '@/api/modules/ai';

export interface AIState {
  chatMessages: ChatMessage[];
  recommendations: RecommendationResponse | null;
  analysis: AnalysisResponse | null;
  loading: boolean;
  error: string | null;
}

export interface AIActions {
  sendChatMessage: (message: string, context?: any) => Promise<void>;
  getRecommendations: (data: any) => Promise<void>;
  analyzePerformance: (data: any) => Promise<void>;
  clearChat: () => void;
  clearError: () => void;
}

export type AISlice = AIState & AIActions;

export const createAISlice: StateCreator<AISlice> = (set, get) => ({
  // 初始状态
  chatMessages: [],
  recommendations: null,
  analysis: null,
  loading: false,
  error: null,

  // 发送聊天消息
  sendChatMessage: async (message, context) => {
    try {
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        chatMessages: [...state.chatMessages, userMessage],
        loading: true,
        error: null,
      }));

      const response = await aiAPI.chat({
        message,
        context,
        history: get().chatMessages,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        chatMessages: [...state.chatMessages, assistantMessage],
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // 获取推荐
  getRecommendations: async (data) => {
    try {
      set({ loading: true, error: null });
      
      const response = await aiAPI.getRecommendations(data);
      
      set({ 
        recommendations: response.data, 
        loading: false 
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // 分析表现
  analyzePerformance: async (data) => {
    try {
      set({ loading: true, error: null });
      
      const response = await aiAPI.analyzePerformance(data);
      
      set({ 
        analysis: response.data, 
        loading: false 
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // 清空聊天记录
  clearChat: () => {
    set({ chatMessages: [] });
  },

  // 清除错误
  clearError: () => {
    set({ error: null });
  },
});