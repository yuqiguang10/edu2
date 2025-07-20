import { StateCreator } from 'zustand';
import { examAPI } from '@/api/modules/exam';
import type { Exam, ExamRecord, Question } from '@/types';

export interface ExamState {
  exams: Exam[];
  currentExam: Exam | null;
  currentExamRecord: ExamRecord | null;
  examQuestions: Question[];
  loading: boolean;
  error: string | null;
}

export interface ExamActions {
  fetchExams: () => Promise<void>;
  fetchExamDetail: (id: number) => Promise<void>;
  createExam: (data: any) => Promise<void>;
  updateExam: (id: number, data: any) => Promise<void>;
  deleteExam: (id: number) => Promise<void>;
  startExam: (id: number) => Promise<void>;
  submitExam: (id: number, answers: any[]) => Promise<void>;
  fetchExamQuestions: (id: number) => Promise<void>;
  clearCurrentExam: () => void;
  clearError: () => void;
}

export type ExamSlice = ExamState & ExamActions;

export const createExamSlice: StateCreator<ExamSlice> = (set, get) => ({
  // 初始状态
  exams: [],
  currentExam: null,
  currentExamRecord: null,
  examQuestions: [],
  loading: false,
  error: null,

  // 获取考试列表
  fetchExams: async () => {
    try {
      set({ loading: true, error: null });
      
      const response = await examAPI.getExams();
      const exams = response.data.data;

      set({ exams, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // 获取考试详情
  fetchExamDetail: async (id) => {
    try {
      set({ loading: true, error: null });
      
      const response = await examAPI.getExamDetail(id);
      const exam = response.data;

      set({ currentExam: exam, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // 创建考试
  createExam: async (data) => {
    try {
      set({ loading: true, error: null });
      
      const response = await examAPI.createExam(data);
      const newExam = response.data;

      set((state) => ({
        exams: [newExam, ...state.exams],
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // 更新考试
  updateExam: async (id, data) => {
    try {
      set({ loading: true, error: null });
      
      const response = await examAPI.updateExam(id, data);
      const updatedExam = response.data;

      set((state) => ({
        exams: state.exams.map(exam => 
          exam.id === id ? updatedExam : exam
        ),
        currentExam: state.currentExam?.id === id ? updatedExam : state.currentExam,
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // 删除考试
  deleteExam: async (id) => {
    try {
      set({ loading: true, error: null });
      
      await examAPI.deleteExam(id);

      set((state) => ({
        exams: state.exams.filter(exam => exam.id !== id),
        currentExam: state.currentExam?.id === id ? null : state.currentExam,
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // 开始考试
  startExam: async (id) => {
    try {
      set({ loading: true, error: null });
      
      const response = await examAPI.startExam(id);
      const examRecord = response.data;

      set({ currentExamRecord: examRecord, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // 提交考试
  submitExam: async (id, answers) => {
    try {
      set({ loading: true, error: null });
      
      const response = await examAPI.submitExam(id, { answers });
      const examRecord = response.data;

      set({ currentExamRecord: examRecord, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // 获取考试题目
  fetchExamQuestions: async (id) => {
    try {
      set({ loading: true, error: null });
      
      const response = await examAPI.getExamQuestions(id);
      const questions = response.data;

      set({ examQuestions: questions, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // 清除当前考试
  clearCurrentExam: () => {
    set({ 
      currentExam: null, 
      currentExamRecord: null, 
      examQuestions: [] 
    });
  },

  // 清除错误
  clearError: () => {
    set({ error: null });
  },
});