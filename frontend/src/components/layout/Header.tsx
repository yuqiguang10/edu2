// src/components/layout/Header.tsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, Bell, Search, User, LogOut, Settings } from 'lucide-react';
import { Menu as HeadlessMenu, Transition } from '@headlessui/react';
import { useAuth } from '@/hooks/useAuth';
import { useStore } from '@/store';
import { formatRelativeTime } from '@/utils/helpers';
import Button from '@/components/common/Button';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { toggleSidebar, notifications, markNotificationAsRead } = useStore();
  const navigate = useNavigate();

  const unreadNotifications = notifications.filter(n => !n.read);

  const handleNotificationClick = (notification: any) => {
    markNotificationAsRead(notification.id);
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  const handleSettingsClick = () => {
    navigate('/settings');
  };

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6">
      {/* 左侧 */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleSidebar}
          icon={<Menu size={20} />}
          className="p-2"
        />
        
        <Link to="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">K12</span>
          </div>
          <span className="text-xl font-bold text-gray-900">智能教育平台</span>
        </Link>
      </div>

      {/* 中间搜索框 */}
      <div className="flex-1 max-w-lg mx-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="搜索课程、题目、资源..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* 右侧 */}
      <div className="flex items-center space-x-4">
        {/* 通知 */}
        <HeadlessMenu as="div" className="relative">
          <HeadlessMenu.Button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
            <Bell size={20} />
            {unreadNotifications.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {unreadNotifications.length}
              </span>
            )}
          </HeadlessMenu.Button>

          <Transition
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <HeadlessMenu.Items className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold">通知</h3>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">
                    暂无通知
                  </div>
                ) : (
                  notifications.slice(0, 10).map((notification) => (
                    <HeadlessMenu.Item key={notification.id}>
                      {({ active }) => (
                        <div
                          className={`p-4 border-b border-gray-100 cursor-pointer ${
                            active ? 'bg-gray-50' : ''
                          } ${!notification.read ? 'bg-blue-50' : ''}`}
                          onClick={() => handleNotificationClick(notification)}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className="text-sm font-medium text-gray-900">
                                {notification.title}
                              </h4>
                              <p className="text-sm text-gray-600 mt-1">
                                {notification.message}
                              </p>
                              <p className="text-xs text-gray-400 mt-2">
                                {formatRelativeTime(notification.timestamp)}
                              </p>
                            </div>
                            {!notification.read && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full ml-2 mt-1"></div>
                            )}
                          </div>
                        </div>
                      )}
                    </HeadlessMenu.Item>
                  ))
                )}
              </div>
              
              {notifications.length > 0 && (
                <div className="p-3 border-t border-gray-200">
                  <button className="w-full text-center text-sm text-primary-600 hover:text-primary-700">
                    查看全部通知
                  </button>
                </div>
              )}
            </HeadlessMenu.Items>
          </Transition>
        </HeadlessMenu>

        {/* 用户菜单 */}
        <HeadlessMenu as="div" className="relative">
          <HeadlessMenu.Button className="flex items-center space-x-2 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
            {user?.avatar ? (
              <img src={user.avatar} alt="Avatar" className="w-8 h-8 rounded-full" />
            ) : (
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <User size={16} />
              </div>
            )}
            <span className="text-sm font-medium">{user?.realName || user?.username}</span>
          </HeadlessMenu.Button>

          <Transition
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <HeadlessMenu.Items className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
              <div className="p-3 border-b border-gray-200">
                <p className="text-sm font-medium text-gray-900">{user?.realName}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              
              <div className="py-1">
                <HeadlessMenu.Item>
                  {({ active }) => (
                    <button
                      onClick={handleProfileClick}
                      className={`flex items-center w-full px-4 py-2 text-sm text-gray-700 ${
                        active ? 'bg-gray-100' : ''
                      }`}
                    >
                      <User size={16} className="mr-3" />
                      个人资料
                    </button>
                  )}
                </HeadlessMenu.Item>
                
                <HeadlessMenu.Item>
                  {({ active }) => (
                    <button
                      onClick={handleSettingsClick}
                      className={`flex items-center w-full px-4 py-2 text-sm text-gray-700 ${
                        active ? 'bg-gray-100' : ''
                      }`}
                    >
                      <Settings size={16} className="mr-3" />
                      设置
                    </button>
                  )}
                </HeadlessMenu.Item>
              </div>
              
              <div className="py-1 border-t border-gray-200">
                <HeadlessMenu.Item>
                  {({ active }) => (
                    <button
                      onClick={logout}
                      className={`flex items-center w-full px-4 py-2 text-sm text-red-700 ${
                        active ? 'bg-red-50' : ''
                      }`}
                    >
                      <LogOut size={16} className="mr-3" />
                      退出登录
                    </button>
                  )}
                </HeadlessMenu.Item>
              </div>
            </HeadlessMenu.Items>
          </Transition>
        </HeadlessMenu>
      </div>
    </header>
  );
};

export default Header;
