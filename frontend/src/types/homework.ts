// src/types/homework.ts
export interface Homework extends BaseEntity {
  title: string;
  description?: string;
  classId: number;
  subjectId: number;
  teacherId: number;
  assignDate: string;
  dueDate: string;
  questions: Question[];
}

export interface HomeworkSubmission extends BaseEntity {
  homeworkId: number;
  studentId: number;
  content?: string;
  attachment?: string;
  score?: number;
  comment?: string;
  submitDate?: string;
  status: HomeworkStatus;
}
