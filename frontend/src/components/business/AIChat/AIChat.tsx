// src/components/business/AIChat/AIChat.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Brain, Send, X, Minimize2 } from 'lucide-react';
import { useStore } from '@/store';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/common/Button';
import { formatRelativeTime } from '@/utils/helpers';
import type { UserRole } from '@/types';

interface AIChatProps {
  role: UserRole;
  isOpen: boolean;
  onToggle: () => void;
}

const AIChat: React.FC<AIChatProps> = ({ role, isOpen, onToggle }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();
  const { chatMessages, sendChatMessage, loading, clearChat } = useStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const message = inputMessage.trim();
    setInputMessage('');

    const context = {
      userId: user?.id,
      role,
      subject: 'general'
    };

    try {
      await sendChatMessage(message, context);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getRoleGreeting = () => {
    const greetings = {
      student: '我是您的学习助手，可以帮您推荐学习内容、解答疑问、分析学习进度。',
      teacher: '我是您的教学助手，可以协助您备课、分析学情、智能批改作业。',
      parent: '我是您的家庭教育顾问，可以为您提供孩子的学习报告和教育建议。',
      admin: '我是您的管理助手，可以帮助您进行系统管理和数据分析。'
    };
    return greetings[role] || greetings.student;
  };

  // 初始化对话
  useEffect(() => {
    if (isOpen && chatMessages.length === 0) {
      sendChatMessage('你好', { userId: user?.id, role });
    }
  }, [isOpen, chatMessages.length, role, user?.id, sendChatMessage]);

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all duration-200 flex items-center justify-center z-50"
        title="AI助手"
      >
        <Brain size={24} />
      </button>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ${
      isMinimized ? 'w-80 h-12' : 'w-80 h-96'
    }`}>
      <div className="bg-white rounded-xl shadow-2xl border border-gray-200 h-full flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-blue-50 rounded-t-xl">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">AI智能助手</h3>
          </div>
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1"
            >
              <Minimize2 size={16} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className="p-1"
            >
              <X size={16} />
            </Button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  <Brain className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-sm">{getRoleGreeting()}</p>
                </div>
              )}

              {chatMessages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs mt-1 opacity-70">
                      {formatRelativeTime(message.timestamp)}
                    </p>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 max-w-xs px-4 py-2 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* 输入框 */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="输入您的问题..."
                  className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={1}
                  disabled={loading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || loading}
                  size="sm"
                  className="px-3"
                >
                  <Send size={16} />
                </Button>
              </div>
              
              {chatMessages.length > 0 && (
                <button
                  onClick={clearChat}
                  className="mt-2 text-xs text-gray-500 hover:text-gray-700"
                >
                  清空对话历史
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AIChat;
