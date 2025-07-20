import React, { ReactNode, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useStore } from '@/store';
import { useAuth } from '@/hooks/useAuth';
import Header from './Header';
import Sidebar from './Sidebar';
import AIChat from '@/components/business/AIChat';

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { sidebarCollapsed } = useStore();
  const { user } = useAuth();
  const location = useLocation();
  const [showAIChat, setShowAIChat] = useState(false);

  // 获取当前用户角色
  const getCurrentRole = () => {
    const path = location.pathname;
    if (path.startsWith('/student')) return 'student';
    if (path.startsWith('/teacher')) return 'teacher';
    if (path.startsWith('/parent')) return 'parent';
    if (path.startsWith('/admin')) return 'admin';
    return user?.roles?.[0] || 'student';
  };

  const currentRole = getCurrentRole();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="flex h-[calc(100vh-64px)]">
        <Sidebar currentRole={currentRole} collapsed={sidebarCollapsed} />
        
        <main
          className={`flex-1 overflow-y-auto transition-all duration-300 ${
            sidebarCollapsed ? 'ml-16' : 'ml-64'
          }`}
        >
          <div className="p-6">
            {children}
          </div>
        </main>
        
        {/* AI聊天助手 */}
        <AIChat
          role={currentRole}
          isOpen={showAIChat}
          onToggle={() => setShowAIChat(!showAIChat)}
        />
      </div>
    </div>
  );
};

export default MainLayout;