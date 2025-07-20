// frontend/src/api/classManagement.ts
import { request } from './request';

export interface CreateClassRequest {
  name: string;
  grade_name: string;
  study_level_id: number;
  description?: string;
  academic_year?: string;
  semester?: string;
  max_students?: number;
  class_motto?: string;
  class_rules?: string;
}

export interface AssignTeacherRequest {
  teacher_id: number;
  subject_id: number;
  assignment_type: 'class_teacher' | 'subject_teacher';
}

export interface CreateHomeworkRequest {
  title: string;
  description: string;
  class_id: number;
  subject_id: number;
  due_date: string;
  student_ids?: number[];
}

export interface CreateExamRequest {
  title: string;
  description?: string;
  class_id: number;
  subject_id: number;
  start_time: string;
  end_time: string;
  duration?: number;
  total_score: number;
  student_ids?: number[];
}

export interface GradeHomeworkRequest {
  score: number;
  comment?: string;
}

export const classManagementAPI = {
  // ==================== 管理员功能 ====================
  
  /**
   * 获取班级列表
   */
  getClasses: (params?: { page?: number; page_size?: number }) => 
    request.get('/api/v1/class-management/classes', { params }),

  /**
   * 创建班级
   */
  createClass: (data: CreateClassRequest) =>
    request.post('/api/v1/class-management/classes', data),

  /**
   * 更新班级
   */
  updateClass: (classId: number, data: Partial<CreateClassRequest>) =>
    request.put(`/api/v1/class-management/classes/${classId}`, data),

  /**
   * 删除班级
   */
  deleteClass: (classId: number) =>
    request.delete(`/api/v1/class-management/classes/${classId}`),

  /**
   * 获取班级详情
   */
  getClassDetail: (classId: number) =>
    request.get(`/api/v1/class-management/classes/${classId}`),

  /**
   * 分配教师到班级
   */
  assignTeacher: (classId: number, data: AssignTeacherRequest) =>
    request.post(`/api/v1/class-management/classes/${classId}/assign-teacher`, data),

  /**
   * 移除教师分配
   */
  removeTeacherAssignment: (classId: number, teacherId: number, subjectId: number) =>
    request.delete(`/api/v1/class-management/classes/${classId}/teachers/${teacherId}/subjects/${subjectId}`),

  /**
   * 添加学生到班级
   */
  addStudentToClass: (classId: number, studentId: number, joinReason?: string) =>
    request.post(`/api/v1/class-management/classes/${classId}/students/${studentId}`, { join_reason: joinReason }),

  /**
   * 从班级移除学生
   */
  removeStudentFromClass: (classId: number, studentId: number, leaveReason?: string) =>
    request.delete(`/api/v1/class-management/classes/${classId}/students/${studentId}`, { data: { leave_reason: leaveReason } }),

  /**
   * 获取班级学生列表
   */
  getClassStudents: (classId: number) =>
    request.get(`/api/v1/class-management/classes/${classId}/students`),

  /**
   * 批量导入学生
   */
  importStudents: (classId: number, file: FormData) =>
    request.post(`/api/v1/class-management/classes/${classId}/import-students`, file, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  /**
   * 导出学生名单
   */
  exportStudents: (classId: number) =>
    request.get(`/api/v1/class-management/classes/${classId}/export-students`, {
      responseType: 'blob'
    }),

  /**
   * 获取班级统计信息
   */
  getClassStatistics: (classId: number) =>
    request.get(`/api/v1/class-management/classes/${classId}/statistics`),

  // ==================== 教师功能 ====================

  /**
   * 获取我负责的班级
   */
  getMyTeachingClasses: () =>
    request.get('/api/v1/class-management/my-teaching-classes'),

  /**
   * 创建作业
   */
  createHomework: (data: CreateHomeworkRequest) =>
    request.post('/api/v1/class-management/homeworks', data),

  /**
   * 创建考试
   */
  createExam: (data: CreateExamRequest) =>
    request.post('/api/v1/class-management/exams', data),

  /**
   * 批改作业
   */
  gradeHomework: (submissionId: number, data: GradeHomeworkRequest) =>
    request.post(`/api/v1/class-management/homework-submissions/${submissionId}/grade`, data),

  /**
   * 批改考试
   */
  gradeExam: (submissionId: number, data: GradeHomeworkRequest) =>
    request.post(`/api/v1/class-management/exam-submissions/${submissionId}/grade`, data),

  /**
   * 获取教学进度
   */
  getTeachingSchedules: (params?: { class_id?: number; subject_id?: number }) =>
    request.get('/api/v1/class-management/teaching-schedules', { params }),

  /**
   * 创建教学进度
   */
  createTeachingSchedule: (data: any) =>
    request.post('/api/v1/class-management/teaching-schedules', data),

  /**
   * 更新教学进度
   */
  updateTeachingSchedule: (scheduleId: number, data: any) =>
    request.put(`/api/v1/class-management/teaching-schedule/${scheduleId}`, data),

  // ==================== 学生功能 ====================

  /**
   * 获取我的班级信息
   */
  getMyClasses: () =>
    request.get('/api/v1/class-management/my-classes'),

  /**
   * 获取我的作业和考试安排
   */
  getMyAssignments: () =>
    request.get('/api/v1/class-management/my-assignments'),

  /**
   * 获取学生作业和考试安排（教师查看用）
   */
  getStudentAssignments: (studentId: number) =>
    request.get(`/api/v1/class-management/students/${studentId}/assignments`),

  /**
   * 获取我的学习画像
   */
  getMyProfile: () =>
    request.get('/api/v1/class-management/my-profile'),

  /**
   * 获取我的学习推荐
   */
  getMyRecommendations: () =>
    request.get('/api/v1/class-management/my-recommendations'),

  /**
   * 获取学生学习分析
   */
  getStudentLearningAnalytics: (studentId: number) =>
    request.get(`/api/v1/class-management/students/${studentId}/analytics`),

  // ==================== 通用功能 ====================

  /**
   * 获取导入任务状态
   */
  getImportTaskStatus: (taskId: number) =>
    request.get(`/api/v1/class-management/import-tasks/${taskId}`),

  /**
   * 获取导入任务列表
   */
  getImportTasks: (params?: { page?: number; page_size?: number }) =>
    request.get('/api/v1/class-management/import-tasks', { params }),
};

// ==================== 作业相关API ====================
export const homeworkAPI = {
  /**
   * 获取班级作业列表
   */
  getClassHomeworks: (classId: number) =>
    request.get(`/api/v1/homeworks/class/${classId}`),

  /**
   * 获取我的作业列表
   */
  getMyHomeworks: () =>
    request.get('/api/v1/homeworks/my'),

  /**
   * 获取作业详情
   */
  getHomeworkDetail: (homeworkId: number) =>
    request.get(`/api/v1/homeworks/${homeworkId}`),

  /**
   * 提交作业
   */
  submitHomework: (homeworkId: number, data: { content: string; attachment?: string }) =>
    request.post(`/api/v1/homeworks/${homeworkId}/submit`, data),

  /**
   * 获取作业提交列表
   */
  getHomeworkSubmissions: (homeworkId: number) =>
    request.get(`/api/v1/homeworks/${homeworkId}/submissions`),

  /**
   * 获取我的作业提交
   */
  getMyHomeworkSubmission: (homeworkId: number) =>
    request.get(`/api/v1/homeworks/${homeworkId}/my-submission`),
};

// ==================== 考试相关API ====================
export const examAPI = {
  /**
   * 获取班级考试列表
   */
  getClassExams: (classId: number) =>
    request.get(`/api/v1/exams/class/${classId}`),

  /**
   * 获取我的考试列表
   */
  getMyExams: () =>
    request.get('/api/v1/exams/my'),

  /**
   * 获取考试详情
   */
  getExamDetail: (examId: number) =>
    request.get(`/api/v1/exams/${examId}`),

  /**
   * 开始考试
   */
  startExam: (examId: number) =>
    request.post(`/api/v1/exams/${examId}/start`),

  /**
   * 提交考试答案
   */
  submitExam: (examId: number, data: { answers: any[] }) =>
    request.post(`/api/v1/exams/${examId}/submit`, data),

  /**
   * 获取考试记录
   */
  getExamRecords: (examId: number) =>
    request.get(`/api/v1/exams/${examId}/records`),

  /**
   * 获取我的考试记录
   */
  getMyExamRecord: (examId: number) =>
    request.get(`/api/v1/exams/${examId}/my-record`),
};

// ==================== AI相关API ====================
export const aiAPI = {
  /**
   * 获取学习建议
   */
  getLearningAdvice: (studentId?: number) =>
    request.get('/api/v1/ai/learning-advice', { params: { student_id: studentId } }),

  /**
   * 生成个性化推荐
   */
  generateRecommendations: (data: { student_id?: number; subject_id?: number; type?: string }) =>
    request.post('/api/v1/ai/recommendations', data),

  /**
   * AI对话
   */
  chat: (data: { message: string; context?: any }) =>
    request.post('/api/v1/ai/chat', data),

  /**
   * 分析学习情况
   */
  analyzeLearning: (studentId: number, timeRange?: string) =>
    request.get(`/api/v1/ai/analyze-learning/${studentId}`, { 
      params: { time_range: timeRange } 
    }),
};

// ==================== 用户相关API ====================
export const userAPI = {
  /**
   * 获取教师列表
   */
  getTeachers: () =>
    request.get('/api/v1/users/teachers'),

  /**
   * 获取学生列表
   */
  getStudents: (params?: { class_id?: number; grade?: string }) =>
    request.get('/api/v1/users/students', { params }),

  /**
   * 获取用户详情
   */
  getUserDetail: (userId: number) =>
    request.get(`/api/v1/users/${userId}`),

  /**
   * 更新用户信息
   */
  updateUser: (userId: number, data: any) =>
    request.put(`/api/v1/users/${userId}`, data),

  /**
   * 重置用户密码
   */
  resetPassword: (userId: number, newPassword: string) =>
    request.post(`/api/v1/users/${userId}/reset-password`, { new_password: newPassword }),
};

// ==================== 教育相关API ====================
export const educationAPI = {
  /**
   * 获取学段列表
   */
  getStudyLevels: () =>
    request.get('/api/v1/education/study-levels'),

  /**
   * 获取学科列表
   */
  getSubjects: () =>
    request.get('/api/v1/education/subjects'),

  /**
   * 获取年级列表
   */
  getGrades: (studyLevelId?: number) =>
    request.get('/api/v1/education/grades', { params: { study_level_id: studyLevelId } }),

  /**
   * 获取教材版本
   */
  getTextbookVersions: (subjectId?: number) =>
    request.get('/api/v1/education/textbook-versions', { params: { subject_id: subjectId } }),

  /**
   * 获取章节列表
   */
  getChapters: (params?: { grade_id?: string; subject_id?: number }) =>
    request.get('/api/v1/education/chapters', { params }),

  /**
   * 获取知识点列表
   */
  getKnowledgePoints: (params?: { chapter_id?: string; subject_id?: number }) =>
    request.get('/api/v1/education/knowledge-points', { params }),
};

// ==================== 数据分析相关API ====================
export const analyticsAPI = {
  /**
   * 获取学习数据统计
   */
  getLearningStatistics: (params?: { 
    student_id?: number; 
    class_id?: number; 
    subject_id?: number; 
    time_range?: string 
  }) =>
    request.get('/api/v1/analytics/learning-statistics', { params }),

  /**
   * 获取成绩分析
   */
  getScoreAnalysis: (params?: { 
    student_id?: number; 
    class_id?: number; 
    subject_id?: number 
  }) =>
    request.get('/api/v1/analytics/score-analysis', { params }),

  /**
   * 获取学习行为分析
   */
  getBehaviorAnalysis: (studentId: number, timeRange?: string) =>
    request.get(`/api/v1/analytics/behavior-analysis/${studentId}`, { 
      params: { time_range: timeRange } 
    }),

  /**
   * 获取班级对比分析
   */
  getClassComparison: (classId: number, compareClassId?: number) =>
    request.get(`/api/v1/analytics/class-comparison/${classId}`, { 
      params: { compare_class_id: compareClassId } 
    }),

  /**
   * 获取知识点掌握情况
   */
  getKnowledgeMastery: (studentId: number, subjectId?: number) =>
    request.get(`/api/v1/analytics/knowledge-mastery/${studentId}`, { 
      params: { subject_id: subjectId } 
    }),
};

// ==================== 通知相关API ====================
export const notificationAPI = {
  /**
   * 获取我的通知
   */
  getMyNotifications: (params?: { page?: number; page_size?: number; unread_only?: boolean }) =>
    request.get('/api/v1/notifications/my', { params }),

  /**
   * 标记通知为已读
   */
  markAsRead: (notificationId: number) =>
    request.put(`/api/v1/notifications/${notificationId}/read`),

  /**
   * 标记所有通知为已读
   */
  markAllAsRead: () =>
    request.put('/api/v1/notifications/mark-all-read'),

  /**
   * 发送通知
   */
  sendNotification: (data: {
    recipients: number[];
    title: string;
    content: string;
    type?: string;
    priority?: string;
  }) =>
    request.post('/api/v1/notifications/send', data),
};

// ==================== 文件上传相关API ====================
export const fileAPI = {
  /**
   * 上传文件
   */
  uploadFile: (file: FormData, type?: string) =>
    request.post('/api/v1/files/upload', file, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { type }
    }),

  /**
   * 获取文件信息
   */
  getFileInfo: (fileId: string) =>
    request.get(`/api/v1/files/${fileId}`),

  /**
   * 下载文件
   */
  downloadFile: (fileId: string) =>
    request.get(`/api/v1/files/${fileId}/download`, {
      responseType: 'blob'
    }),

  /**
   * 删除文件
   */
  deleteFile: (fileId: string) =>
    request.delete(`/api/v1/files/${fileId}`),
};

// ==================== 系统配置相关API ====================
export const systemAPI = {
  /**
   * 获取系统配置
   */
  getSystemConfig: () =>
    request.get('/api/v1/system/config'),

  /**
   * 更新系统配置
   */
  updateSystemConfig: (data: any) =>
    request.put('/api/v1/system/config', data),

  /**
   * 获取系统统计
   */
  getSystemStatistics: () =>
    request.get('/api/v1/system/statistics'),

  /**
   * 获取操作日志
   */
  getOperationLogs: (params?: { 
    page?: number; 
    page_size?: number; 
    user_id?: number; 
    action?: string 
  }) =>
    request.get('/api/v1/system/logs', { params }),
};

// ==================== 类型定义 ====================
export interface APIResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Class {
  id: number;
  name: string;
  grade_name: string;
  study_level_id: number;
  description?: string;
  status: number;
  created_at: string;
  updated_at?: string;
}

export interface Teacher {
  id: number;
  user_id: number;
  name: string;
  subject_name?: string;
  title?: string;
  department_id?: number;
}

export interface Student {
  id: number;
  user_id: number;
  username: string;
  real_name: string;
  student_id_number: string;
  email: string;
  phone?: string;
  class_id?: number;
  join_date?: string;
}

export interface Assignment {
  id: number;
  title: string;
  description?: string;
  type: 'homework' | 'exam';
  class_id: number;
  subject_id: number;
  teacher_id: number;
  due_date?: string;
  start_time?: string;
  end_time?: string;
  total_score?: number;
  status: string;
  created_at: string;
}

export interface LearningRecommendation {
  id: number;
  student_id: number;
  subject_id: number;
  knowledge_point: string;
  difficulty_level: number;
  resource_type: string;
  resource_id: number;
  reason: string;
  priority: number;
  status: number;
  created_at: string;
}

export default {
  classManagementAPI,
  homeworkAPI,
  examAPI,
  aiAPI,
  userAPI,
  educationAPI,
  analyticsAPI,
  notificationAPI,
  fileAPI,
  systemAPI
};