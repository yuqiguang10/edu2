// src/pages/auth/Register.tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock, User, Phone, GraduationCap } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { registerSchema, type RegisterFormData } from '@/utils/validation';
import { ROUTES } from '@/utils/constants';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import toast from 'react-hot-toast';

const Register: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { register: registerUser, loading, error, clearError } = useAuth();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      clearError();
      await registerUser(data);
      toast.success('注册成功！请登录');
      // 可以重定向到登录页面
      window.location.href = ROUTES.LOGIN;
    } catch (error) {
      // 错误处理已在useAuth中完成
    }
  };

  React.useEffect(() => {
    return () => clearError();
  }, [clearError]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* 头部 */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-primary-600 rounded-xl flex items-center justify-center shadow-lg">
              <GraduationCap className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            创建账号
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            加入K12智能教育平台
          </p>
        </div>

        {/* 注册表单 */}
        <div className="bg-white py-8 px-6 shadow-xl rounded-xl">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <Input
              label="用户名"
              type="text"
              placeholder="请输入用户名"
              leftIcon={<User size={20} className="text-gray-400" />}
              error={errors.username?.message}
              {...register('username')}
            />

            <Input
              label="邮箱"
              type="email"
              placeholder="请输入邮箱地址"
              leftIcon={<Mail size={20} className="text-gray-400" />}
              error={errors.email?.message}
              {...register('email')}
            />

            <Input
              label="真实姓名"
              type="text"
              placeholder="请输入真实姓名"
              leftIcon={<User size={20} className="text-gray-400" />}
              error={errors.realName?.message}
              {...register('realName')}
            />

            <Input
              label="手机号（可选）"
              type="tel"
              placeholder="请输入手机号"
              leftIcon={<Phone size={20} className="text-gray-400" />}
              error={errors.phone?.message}
              {...register('phone')}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                角色类型 <span className="text-error-500">*</span>
              </label>
              <select
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500"
                {...register('role')}
              >
                <option value="">请选择角色</option>
                <option value="student">学生</option>
                <option value="teacher">教师</option>
                <option value="parent">家长</option>
              </select>
              {errors.role && (
                <p className="mt-1 text-sm text-error-600">{errors.role.message}</p>
              )}
            </div>

            <Input
              label="密码"
              type={showPassword ? 'text' : 'password'}
              placeholder="请输入密码"
              leftIcon={<Lock size={20} className="text-gray-400" />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              }
              error={errors.password?.message}
              {...register('password')}
            />

            <Input
              label="确认密码"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="请再次输入密码"
              leftIcon={<Lock size={20} className="text-gray-400" />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              }
              error={errors.confirmPassword?.message}
              {...register('confirmPassword')}
            />

            <Button
              type="submit"
              className="w-full"
              loading={loading}
              disabled={loading}
            >
              {loading ? '注册中...' : '立即注册'}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">已有账号？</span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                to={ROUTES.LOGIN}
                className="w-full flex justify-center py-2 px-4 border border-primary-300 rounded-lg shadow-sm text-sm font-medium text-primary-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                立即登录
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
