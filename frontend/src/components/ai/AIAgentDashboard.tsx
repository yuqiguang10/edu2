// frontend/src/components/ai/AIAgentDashboard.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { Card, Badge, Timeline, Button, notification, Spin, Tabs, Progress, Alert } from 'antd';
import { 
  RobotOutlined, 
  BulbOutlined, 
  ClockCircleOutlined, 
  TrophyOutlined,
  BookOutlined,
  MessageOutlined
} from '@ant-design/icons';
import { aiAPI } from '@/api/modules/ai';
import type { Recommendation, AIAgentStatus, LearningAnalysis } from '@/types/ai';

const { TabPane } = Tabs;

interface AIAgentDashboardProps {
  userId: number;
  userRole: string;
}

const AIAgentDashboard: React.FC<AIAgentDashboardProps> = ({ userId, userRole }) => {
  const [agentStatus, setAgentStatus] = useState<'inactive' | 'initializing' | 'active' | 'error'>('inactive');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [realtimeAnalysis, setRealtimeAnalysis] = useState<LearningAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  // AI Agent初始化
  const initializeAIAgent = useCallback(async () => {
    try {
      setLoading(true);
      setAgentStatus('initializing');
      
      const response = await aiAPI.initializeAgent();
      
      if (response.success) {
        setAgentStatus('active');
        setRecommendations(response.data.recommendations || []);
        
        notification.success({
          message: 'AI学习助手已启动',
          description: '为您准备了个性化学习建议',
          icon: <RobotOutlined style={{ color: '#52c41a' }} />
        });
        
        // 启动后立即获取分析数据
        await fetchRealtimeAnalysis();
      }
    } catch (error) {
      setAgentStatus('error');
      notification.error({
        message: 'AI助手启动失败',
        description: '请刷新页面重试',
        icon: <RobotOutlined style={{ color: '#ff4d4f' }} />
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // 获取实时分析
  const fetchRealtimeAnalysis = useCallback(async () => {
    try {
      const response = await aiAPI.getLearningAnalysis(7); // 最近7天
      setRealtimeAnalysis(response.data);
    } catch (error) {
      console.error('Failed to fetch realtime analysis:', error);
    }
  }, []);

  // 更新推荐
  const updateRecommendations = useCallback(async (context?: string) => {
    try {
      const response = await aiAPI.getRecommendations({ context });
      setRecommendations(response.data);
    } catch (error) {
      console.error('Failed to update recommendations:', error);
    }
  }, []);

  // 处理用户行为
  const handleUserAction = useCallback(async (actionType: string, data: any) => {
    try {
      const response = await aiAPI.processAction({
        action_type: actionType,
        data: data,
        context: { tab: activeTab, timestamp: new Date().toISOString() }
      });
      
      if (response.data.recommendations?.length > 0) {
        setRecommendations(response.data.recommendations);
      }
      
      // 显示AI反馈
      if (response.data.feedback) {
        notification.info({
          message: 'AI助手反馈',
          description: response.data.feedback,
          duration: 4.5
        });
      }
    } catch (error) {
      console.error('Failed to process user action:', error);
    }
  }, [activeTab]);

  // 开始学习行为
  const handleStartLearning = useCallback((recommendation: Recommendation) => {
    handleUserAction('start_learning', {
      recommendation_id: recommendation.id,
      type: recommendation.type,
      subject: recommendation.data?.subject
    });
  }, [handleUserAction]);

  // 定期更新分析数据
  useEffect(() => {
    if (agentStatus === 'active') {
      const interval = setInterval(fetchRealtimeAnalysis, 30000); // 30秒更新一次
      return () => clearInterval(interval);
    }
  }, [agentStatus, fetchRealtimeAnalysis]);

  // 组件挂载时初始化
  useEffect(() => {
    initializeAIAgent();
  }, [initializeAIAgent]);

  // 渲染状态指示器
  const renderStatusBadge = () => {
    const statusConfig = {
      inactive: { status: 'default', text: '离线' },
      initializing: { status: 'processing', text: '启动中' },
      active: { status: 'success', text: '运行中' },
      error: { status: 'error', text: '错误' }
    };
    
    const config = statusConfig[agentStatus];
    return <Badge status={config.status as any} text={config.text} />;
  };

  // 渲染实时分析
  const renderRealtimeAnalysis = () => {
    if (!realtimeAnalysis) {
      return <Spin size="small" />;
    }

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="text-sm text-blue-600 mb-1">今日学习时间</div>
            <div className="text-xl font-bold text-blue-800">
              {Math.round(realtimeAnalysis.total_learning_time / 60)}分钟
            </div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="text-sm text-green-600 mb-1">学习一致性</div>
            <div className="text-xl font-bold text-green-800">
              {(realtimeAnalysis.consistency_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">专注度</span>
            <span className="text-sm font-medium">
              {realtimeAnalysis.focus_level ? (realtimeAnalysis.focus_level * 100).toFixed(0) + '%' : 'N/A'}
            </span>
          </div>
          <Progress 
            percent={realtimeAnalysis.focus_level ? realtimeAnalysis.focus_level * 100 : 0}
            size="small"
            strokeColor={realtimeAnalysis.focus_level > 0.7 ? '#52c41a' : '#faad14'}
          />
        </div>

        {realtimeAnalysis.activity_trend && (
          <Alert
            message={`学习趋势: ${realtimeAnalysis.activity_trend === 'increasing' ? '上升' : 
                     realtimeAnalysis.activity_trend === 'decreasing' ? '下降' : '稳定'}`}
            type={realtimeAnalysis.activity_trend === 'increasing' ? 'success' : 
                  realtimeAnalysis.activity_trend === 'decreasing' ? 'warning' : 'info'}
            size="small"
            showIcon
          />
        )}

        {realtimeAnalysis.suggestions?.length > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <h5 className="text-blue-800 mb-2 flex items-center">
              <BulbOutlined className="mr-1" /> 实时建议
            </h5>
            <ul className="text-blue-700 text-sm space-y-1">
              {realtimeAnalysis.suggestions.map((suggestion, index) => (
                <li key={index}>• {suggestion}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  // 渲染推荐列表
  const renderRecommendations = () => {
    if (recommendations.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <BookOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
          <p>暂无推荐，AI正在分析您的学习情况...</p>
        </div>
      );
    }

    return (
      <Timeline>
        {recommendations.slice(0, 5).map((rec, index) => (
          <Timeline.Item
            key={rec.id}
            color={rec.priority >= 4 ? 'red' : rec.priority >= 3 ? 'blue' : 'green'}
            dot={rec.priority >= 4 ? <TrophyOutlined /> : <BookOutlined />}
          >
            <div className="bg-white border rounded-lg p-4 shadow-sm">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">{rec.title}</h4>
                  <p className="text-sm text-gray-600 mb-2">{rec.description}</p>
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                    <span className="flex items-center">
                      <ClockCircleOutlined className="mr-1" />
                      {rec.estimated_time}分钟
                    </span>
                    <span>优先级: {rec.priority}/5</span>
                  </div>

                  {rec.reasoning && (
                    <div className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded mb-3">
                      💡 {rec.reasoning}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex space-x-2">
                <Button 
                  size="small" 
                  type="primary"
                  onClick={() => handleStartLearning(rec)}
                >
                  开始学习
                </Button>
                <Button 
                  size="small"
                  onClick={() => handleUserAction('view_recommendation', { recommendation_id: rec.id })}
                >
                  查看详情
                </Button>
              </div>
            </div>
          </Timeline.Item>
        ))}
      </Timeline>
    );
  };

  return (
    <div className="ai-agent-dashboard">
      <Card
        title={
          <div className="flex items-center space-x-2">
            <RobotOutlined style={{ color: '#1890ff' }} />
            <span>AI学习助手</span>
            {renderStatusBadge()}
          </div>
        }
        extra={
          <Button 
            type="primary" 
            onClick={initializeAIAgent}
            loading={loading}
            disabled={agentStatus === 'active'}
          >
            {agentStatus === 'active' ? '运行中' : '启动助手'}
          </Button>
        }
        className="shadow-md"
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          className="ai-dashboard-tabs"
        >
          <TabPane 
            tab={
              <span>
                <TrophyOutlined />
                学习概览
              </span>
            } 
            key="dashboard"
          >
            {renderRealtimeAnalysis()}
          </TabPane>

          <TabPane 
            tab={
              <span>
                <BulbOutlined />
                AI推荐 {recommendations.length > 0 && `(${recommendations.length})`}
              </span>
            } 
            key="recommendations"
          >
            <div className="mb-4 flex justify-between items-center">
              <h4 className="text-lg font-medium">个性化推荐</h4>
              <Button 
                size="small"
                onClick={() => updateRecommendations('manual_refresh')}
              >
                刷新推荐
              </Button>
            </div>
            {renderRecommendations()}
          </TabPane>

          <TabPane 
            tab={
              <span>
                <MessageOutlined />
                AI对话
              </span>
            } 
            key="chat"
          >
            <AIChatInterface 
              onMessage={(message) => handleUserAction('ai_chat', { message })}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default AIAgentDashboard;
