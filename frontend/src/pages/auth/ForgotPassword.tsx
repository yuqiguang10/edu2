// src/pages/auth/ForgotPassword.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Mail, ArrowLeft, GraduationCap } from 'lucide-react';
import { ROUTES } from '@/utils/constants';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import toast from 'react-hot-toast';

interface ForgotPasswordForm {
  email: string;
}

const ForgotPassword: React.FC = () => {
  const [isSubmitted, setIsSubmitted] = React.useState(false);
  const [loading, setLoading] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordForm>();

  const onSubmit = async (data: ForgotPasswordForm) => {
    try {
      setLoading(true);
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      setIsSubmitted(true);
      toast.success('重置邮件已发送！');
    } catch (error) {
      toast.error('发送失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-green-600 rounded-xl flex items-center justify-center shadow-lg">
                <Mail className="w-8 h-8 text-white" />
              </div>
            </div>
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              邮件已发送
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              我们已向您的邮箱发送了密码重置链接，请查收邮件并按照指示操作。
            </p>
          </div>

          <div className="bg-white py-8 px-6 shadow-xl rounded-xl text-center">
            <p className="text-sm text-gray-600 mb-6">
              没有收到邮件？请检查垃圾邮件文件夹，或者
            </p>
            
            <div className="space-y-3">
              <Button
                onClick={() => setIsSubmitted(false)}
                variant="outline"
                className="w-full"
              >
                重新发送
              </Button>
              
              <Link
                to={ROUTES.LOGIN}
                className="w-full flex justify-center py-2 px-4 border border-primary-300 rounded-lg shadow-sm text-sm font-medium text-primary-700 bg-white hover:bg-gray-50"
              >
                返回登录
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
            忘记密码
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            输入您的邮箱地址，我们将发送重置链接
          </p>
        </div>

        {/* 表单 */}
        <div className="bg-white py-8 px-6 shadow-xl rounded-xl">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <Input
              label="邮箱地址"
              type="email"
              placeholder="请输入您的邮箱地址"
              leftIcon={<Mail size={20} className="text-gray-400" />}
              error={errors.email?.message}
              {...register('email', {
                required: '请输入邮箱地址',
                pattern: {
                  value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: '请输入有效的邮箱地址',
                },
              })}
            />

            <Button
              type="submit"
              className="w-full"
              loading={loading}
              disabled={loading}
            >
              {loading ? '发送中...' : '发送重置链接'}
            </Button>
          </form>

          <div className="mt-6">
            <Link
              to={ROUTES.LOGIN}
              className="flex items-center justify-center text-sm text-primary-600 hover:text-primary-500"
            >
              <ArrowLeft size={16} className="mr-1" />
              返回登录
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
