// src/types/analytics.ts
export interface StudentProfile extends BaseEntity {
  studentId: number;
  learningStyle?: string;
  abilityVisual?: number;
  abilityVerbal?: number;
  abilityLogical?: number;
  abilityMathematical?: number;
  attentionDuration?: number;
  preferredContentType?: string;
}

export interface LearningBehavior {
  date: string;
  studyDuration: number;
  resourceViews: number;
  questionAttempts: number;
  correctRate: number;
  focusDuration: number;
  activityType: string;
}

export interface PerformanceAnalysis {
  overallScore: number;
  improvement: number;
  strengths: string[];
  weaknesses: string[];
  recommendation: string;
  trendData: { date: string; score: number }[];
}
