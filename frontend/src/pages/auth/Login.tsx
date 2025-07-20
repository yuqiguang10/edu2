// src/pages/auth/Login.tsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock, GraduationCap } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { loginSchema, type LoginFormData } from '@/utils/validation';
import { ROUTES } from '@/utils/constants';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const { login, loading, error, clearError } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError();
      await login(data);
      // 登录成功后的重定向在useAuth中处理
    } catch (error) {
      // 错误处理已在useAuth中完成
    }
  };

  React.useEffect(() => {
    // 清除错误信息
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
            欢迎回来
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            登录到K12智能教育平台
          </p>
        </div>

        {/* 登录表单 */}
        <div className="bg-white py-8 px-6 shadow-xl rounded-xl">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <Input
              label="用户名或邮箱"
              type="text"
              placeholder="请输入用户名或邮箱"
              leftIcon={<Mail size={20} className="text-gray-400" />}
              error={errors.username?.message}
              {...register('username')}
            />

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

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  {...register('rememberMe')}
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                  记住我
                </label>
              </div>

              <div className="text-sm">
                <Link
                  to={ROUTES.FORGOT_PASSWORD}
                  className="font-medium text-primary-600 hover:text-primary-500"
                >
                  忘记密码？
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              loading={loading}
              disabled={loading}
            >
              {loading ? '登录中...' : '登录'}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">还没有账号？</span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                to={ROUTES.REGISTER}
                className="w-full flex justify-center py-2 px-4 border border-primary-300 rounded-lg shadow-sm text-sm font-medium text-primary-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                立即注册
              </Link>
            </div>
          </div>
        </div>

        {/* 演示账号 */}
        <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 text-center">
          <p className="text-sm text-gray-600 mb-3">演示账号登录</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-blue-50 p-2 rounded">
              <div className="font-medium text-blue-700">学生</div>
              <div className="text-blue-600">student / 123456</div>
            </div>
            <div className="bg-green-50 p-2 rounded">
              <div className="font-medium text-green-700">教师</div>
              <div className="text-green-600">teacher / 123456</div>
            </div>
            <div className="bg-purple-50 p-2 rounded">
              <div className="font-medium text-purple-700">家长</div>
              <div className="text-purple-600">parent / 123456</div>
            </div>
            <div className="bg-orange-50 p-2 rounded">
              <div className="font-medium text-orange-700">管理员</div>
              <div className="text-orange-600">admin / 123456</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
