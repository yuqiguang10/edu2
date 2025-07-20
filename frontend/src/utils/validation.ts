// src/utils/validation.ts
import { z } from 'zod';

// 基础验证规则
export const validationRules = {
  username: z
    .string()
    .min(3, '用户名至少3个字符')
    .max(20, '用户名最多20个字符')
    .regex(/^[a-zA-Z0-9_]+$/, '用户名只能包含字母、数字和下划线'),
  
  email: z
    .string()
    .email('请输入有效的邮箱地址'),
  
  password: z
    .string()
    .min(6, '密码至少6个字符')
    .max(30, '密码最多30个字符'),
  
  phone: z
    .string()
    .regex(/^1[3-9]\d{9}$/, '请输入有效的手机号'),
  
  realName: z
    .string()
    .min(2, '姓名至少2个字符')
    .max(10, '姓名最多10个字符'),
};

// 登录表单验证
export const loginSchema = z.object({
  username: validationRules.username,
  password: validationRules.password,
  rememberMe: z.boolean().optional(),
});

// 注册表单验证
export const registerSchema = z.object({
  username: validationRules.username,
  email: validationRules.email,
  password: validationRules.password,
  confirmPassword: z.string(),
  realName: validationRules.realName,
  phone: validationRules.phone.optional(),
  role: z.enum(['student', 'teacher', 'parent']),
}).refine((data) => data.password === data.confirmPassword, {
  message: '两次输入的密码不一致',
  path: ['confirmPassword'],
});

// 考试表单验证
export const examSchema = z.object({
  title: z.string().min(1, '请输入考试标题').max(100, '标题最多100个字符'),
  description: z.string().max(500, '描述最多500个字符').optional(),
  classId: z.number().min(1, '请选择班级'),
  subjectId: z.number().min(1, '请选择科目'),
  startTime: z.string().min(1, '请选择开始时间'),
  endTime: z.string().min(1, '请选择结束时间'),
  duration: z.number().min(1, '考试时长至少1分钟').max(300, '考试时长最多300分钟'),
  totalScore: z.number().min(1, '总分至少1分').max(1000, '总分最多1000分'),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ExamFormData = z.infer<typeof examSchema>;
