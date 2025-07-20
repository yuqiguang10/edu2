// frontend/src/components/business/AIChat/index.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Card, Button, Avatar, Loading } from '@/components/common';
import { X, Send, Bot, User, Lightbulb, BookOpen, BarChart3, MessageSquare } from 'lucide-react';
import { aiAPI } from '@/api/modules';
import { useStore } from '@/store';
import { formatTime } from '@/utils/formatters';
import type { ChatMessage, AIRole, ChatContext } from '@/types';

interface AIChatProps {
  role: AIRole;
  onClose: () => void;
  context?: ChatContext;
  initialMessage?: string;
}

const AIChat: React.FC<AIChatProps> = ({ 
  role, 
  onClose, 
  context,
  initialMessage 
}) => {
  const { user } = useStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const roleConfig = {
    student: {
      name: '小智助手',
      avatar: '/avatars/ai-student.png',
      color: 'bg-blue-500',
      greeting: '你好！我是你的专属学习助手小智，可以帮你解答学习问题、制定学习计划、分析学习情况。有什么可以帮助你的吗？',
      quickActions: [
        { icon: BookOpen, text: '推荐学习内容', action: 'recommend' },
        { icon: BarChart3, text: '分析学习情况', action: 'analyze' },
        { icon: Lightbulb, text: '解答疑问', action: 'explain' }
      ]
    },
    teacher: {
      name: '教学助手',
      avatar: '/avatars/ai-teacher.png',
      color: 'bg-green-500',
      greeting: '您好！我是您的教学助手，可以协助您进行班级管理、学情分析、备课建议等工作。请问需要什么帮助？',
      quickActions: [
        { icon: BarChart3, text: '学情分析', action: 'student_analysis' },
        { icon: BookOpen, text: '备课建议', action: 'lesson_plan' },
        { icon: MessageSquare, text: '作业建议', action: 'homework_suggest' }
      ]
    },
    parent: {
      name: '家长助手',
      avatar: '/avatars/ai-parent.png', 
      color: 'bg-purple-500',
      greeting: '您好！我是您的家庭教育助手，可以帮您了解孩子的学习情况、提供教育建议、协助家校沟通。',
      quickActions: [
        { icon: BarChart3, text: '孩子学习报告', action: 'child_report' },
        { icon: Lightbulb, text: '教育建议', action: 'parenting_tips' },
        { icon: MessageSquare, text: '家校沟通', action: 'communication' }
      ]
    }
  };

  const config = roleConfig[role];

  useEffect(() => {
    // 初始化对话
    const welcomeMessage: ChatMessage = {
      id: Date.now().toString(),
      content: initialMessage || config.greeting,
      sender: 'ai',
      timestamp: new Date(),
      type: 'text'
    };
    setMessages([welcomeMessage]);

    // 自动聚焦输入框
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await aiAPI.chat({
        message: userMessage.content,
        role,
        context: {
          ...context,
          conversationHistory: messages.slice(-10) // 只发送最近10条消息作为上下文
        }
      });

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.data.content,
        sender: 'ai',
        timestamp: new Date(),
        type: 'text',
        suggestions: response.data.suggestions,
        resources: response.data.resources
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('AI聊天错误:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: '抱歉，我暂时无法回复。请稍后再试。',
        sender: 'ai',
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    const actionMessages = {
      recommend: '请为我推荐适合的学习内容',
      analyze: '请分析我最近的学习情况',
      explain: '我有一些学习问题需要解答',
      student_analysis: '请帮我分析班级学生的学习情况',
      lesson_plan: '请为我提供备课建议',
      homework_suggest: '请为我推荐合适的作业内容',
      child_report: '请生成我孩子的学习报告',
      parenting_tips: '请给我一些教育孩子的建议',
      communication: '请帮助我与老师更好地沟通'
    };

    const message = actionMessages[action];
    if (message) {
      setInputValue(message);
      setTimeout(() => handleSendMessage(), 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const MessageBubble: React.FC<{ message: ChatMessage }> = ({ message }) => (
    <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start space-x-2 max-w-[80%] ${
        message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
      }`}>
        <Avatar
          src={message.sender === 'user' ? user?.avatar : config.avatar}
          size="sm"
          fallback={message.sender === 'user' ? 'U' : 'AI'}
          className={message.sender === 'ai' ? config.color : 'bg-gray-500'}
        />
        <div className={`rounded-lg p-3 ${
          message.sender === 'user' 
            ? 'bg-blue-500 text-white' 
            : message.type === 'error'
            ? 'bg-red-50 border border-red-200 text-red-800'
            : 'bg-gray-100 text-gray-900'
        }`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
          
          {/* 建议按钮 */}
          {message.suggestions && message.suggestions.length > 0 && (
            <div className="mt-3 space-y-2">
              <div className="text-sm font-medium text-gray-600">相关建议:</div>
              <div className="flex flex-wrap gap-2">
                {message.suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    size="sm"
                    variant="outline"
                    onClick={() => setInputValue(suggestion)}
                    className="text-xs"
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* 推荐资源 */}
          {message.resources && message.resources.length > 0 && (
            <div className="mt-3 space-y-2">
              <div className="text-sm font-medium text-gray-600">推荐资源:</div>
              <div className="space-y-1">
                {message.resources.map((resource, index) => (
                  <a
                    key={index}
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-blue-600 hover:text-blue-800 underline"
                  >
                    📚 {resource.title}
                  </a>
                ))}
              </div>
            </div>
          )}

          <div className="text-xs opacity-70 mt-2">
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl h-[80vh] flex flex-col">
        {/* 头部 */}
        <div className={`${config.color} text-white p-4 rounded-t-lg flex items-center justify-between`}>
          <div className="flex items-center space-x-3">
            <Avatar
              src={config.avatar}
              size="sm"
              fallback="AI"
              className="bg-white/20"
            />
            <div>
              <h3 className="font-medium">{config.name}</h3>
              <p className="text-sm opacity-90">
                {role === 'student' ? '学习助手' : 
                 role === 'teacher' ? '教学助手' : '家长助手'}
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="text-white hover:bg-white/20"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* 快捷操作 */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex flex-wrap gap-2">
            {config.quickActions.map((action, index) => (
              <Button
                key={index}
                size="sm"
                variant="outline"
                onClick={() => handleQuickAction(action.action)}
                className="text-sm"
              >
                <action.icon className="w-4 h-4 mr-1" />
                {action.text}
              </Button>
            ))}
          </div>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="flex items-center space-x-2">
                <Avatar
                  src={config.avatar}
                  size="sm"
                  fallback="AI"
                  className={config.color}
                />
                <div className="bg-gray-100 rounded-lg p-3">
                  <Loading size="sm" />
                  <span className="text-sm text-gray-600 ml-2">思考中...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="flex items-end space-x-2">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入你的问题..."
                className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                disabled={isLoading}
              />
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className={`${config.color} hover:opacity-90 p-3`}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            按 Enter 发送，Shift + Enter 换行
          </div>
        </div>
      </Card>
    </div>
  );
};

export default AIChat;