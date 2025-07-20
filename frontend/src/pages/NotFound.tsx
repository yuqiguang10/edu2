// src/pages/NotFound.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import Button from '@/components/common/Button';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-gray-300">404</h1>
          <h2 className="text-2xl font-semibold text-gray-900 mt-4">页面未找到</h2>
          <p className="text-gray-600 mt-2">
            抱歉，您访问的页面不存在或已被移动
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              onClick={() => window.history.back()}
              variant="outline"
              icon={<ArrowLeft size={16} />}
            >
              返回上页
            </Button>
            
            <Link to="/">
              <Button icon={<Home size={16} />}>
                回到首页
              </Button>
            </Link>
          </div>
          
          <div className="mt-8 text-sm text-gray-500">
            <p>如果您认为这是一个错误，请联系技术支持</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
