// frontend/src/components/ai/AIChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, List, Avatar, Spin, message } from 'antd';
import { RobotOutlined, UserOutlined, SendOutlined } from '@ant-design/icons';
import { aiAPI } from '@/api/modules/ai';

const { TextArea } = Input;

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  suggestions?: string[];
}

interface AIChatInterfaceProps {
  onMessage?: (message: string) => void;
}

const AIChatInterface: React.FC<AIChatInterfaceProps> = ({ onMessage }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await aiAPI.chat({
        message: inputValue,
        context: { interface: 'dashboard' },
        history: messages.slice(-5) // 最近5条消息作为上下文
      });

      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date().toISOString(),
        suggestions: response.data.suggestions
      };

      setMessages(prev => [...prev, aiMessage]);
      onMessage?.(inputValue);
    } catch (error) {
      message.error('AI对话失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const renderMessage = (msg: ChatMessage) => (
    <List.Item key={msg.id} className="border-none">
      <div className={`w-full flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-[70%] ${msg.role === 'user' ? 'order-1' : 'order-2'}`}>
          <div
            className={`px-4 py-3 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-500 text-white ml-auto'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            <div className="whitespace-pre-wrap">{msg.content}</div>
          </div>
          
          {msg.suggestions && msg.suggestions.length > 0 && (
            <div className="mt-2 space-y-1">
              <div className="text-xs text-gray-500">建议回复:</div>
              {msg.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  size="small"
                  type="link"
                  className="p-0 h-auto text-left"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          )}
        </div>
        
        <Avatar
          className={`${msg.role === 'user' ? 'order-2 ml-2' : 'order-1 mr-2'}`}
          icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
          style={{
            backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a'
          }}
        />
      </div>
    </List.Item>
  );

  return (
    <div className="ai-chat-interface h-96 flex flex-col">
      <div className="flex-1 overflow-hidden">
        <List
          className="h-full overflow-y-auto px-2"
          dataSource={messages}
          renderItem={renderMessage}
          locale={{ emptyText: '开始与AI助手对话吧！' }}
        />
        {loading && (
          <div className="flex items-center p-4">
            <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} className="mr-2" />
            <Spin size="small" />
            <span className="ml-2 text-gray-500">AI正在思考...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="border-t pt-4">
        <div className="flex space-x-2">
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="向AI助手提问..."
            autoSize={{ minRows: 1, maxRows: 3 }}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSendMessage}
            loading={loading}
            disabled={!inputValue.trim()}
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  );
};

export { AIChatInterface };