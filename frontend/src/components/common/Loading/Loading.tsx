// src/components/common/Loading/Loading.tsx
import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/utils/helpers';

export interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
  fullScreen?: boolean;
}

const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  text = '加载中...',
  className,
  fullScreen = false,
}) => {
  const sizes = {
    sm: 16,
    md: 24,
    lg: 32,
  };

  const content = (
    <div className={cn('flex flex-col items-center justify-center', className)}>
      <Loader2 className="animate-spin text-primary-600" size={sizes[size]} />
      {text && (
        <p className="mt-2 text-sm text-gray-600">{text}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
};

export default Loading;
