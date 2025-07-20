import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { createAuthSlice, AuthSlice } from './slices/authSlice';
import { createAppSlice, AppSlice } from './slices/appSlice';
import { createExamSlice, ExamSlice } from './slices/examSlice';
import { createAISlice, AISlice } from './slices/aiSlice';

export type RootState = AuthSlice & AppSlice & ExamSlice & AISlice;

export const useStore = create<RootState>()(
  devtools(
    (...a) => ({
      ...createAuthSlice(...a),
      ...createAppSlice(...a),
      ...createExamSlice(...a),
      ...createAISlice(...a),
    }),
    {
      name: 'edu-platform-store',
    }
  )
);