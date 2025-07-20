// frontend/src/pages/student/Dashboard/index.tsx
import React, { useEffect, useState } from 'react';
import { useStore } from '@/store';
import { Card, Button, Avatar, Progress, Tag } from '@/components/common';
import { AIChat } from '@/components/business/AIChat';
import { QuestionCard } from '@/components/business/QuestionCard';
import { ProgressChart } from '@/components/business/ProgressChart';
import { BookOpen, Brain, Trophy, Clock, Target, MessageCircle } from 'lucide-react';
import { studentAPI, analyticsAPI } from '@/api/modules';
import { formatTime, formatDate } from '@/utils/formatters';
import type { StudentDashboardData, LearningRecommendation } from '@/types';

const StudentDashboard: React.FC = () => {
  const { user } = useStore();
  const [dashboardData, setDashboardData] = useState<StudentDashboardData | null>(null);
  const [recommendations, setRecommendations] = useState<LearningRecommendation[]>([]);
  const [showAIChat, setShowAIChat] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    loadRecommendations();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await studentAPI.getDashboard();
      setDashboardData(response.data);
    } catch (error) {
      console.error('加载仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await analyticsAPI.getPersonalizedRecommendations();
      setRecommendations(response.data.slice(0, 3)); // 只显示前3个推荐
    } catch (error) {
      console.error('加载推荐失败:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 欢迎区域 */}
        <div className="mb-8">
          <div className="flex items-center justify-between bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center space-x-4">
              <Avatar
                src={user?.avatar}
                alt={user?.real_name}
                size="lg"
                fallback={user?.real_name?.charAt(0) || 'S'}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  你好，{user?.real_name || '同学'}！
                </h1>
                <p className="text-gray-600">
                  今天是{formatDate(new Date())}，让我们继续学习之旅吧！
                </p>
              </div>
            </div>
            <Button
              onClick={() => setShowAIChat(true)}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              icon={<Brain className="w-4 h-4" />}
            >
              AI学习助手
            </Button>
          </div>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">今日学习时长</p>
                <p className="text-2xl font-bold">{formatTime(dashboardData?.todayStudyTime || 0)}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-200" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100">本周完成作业</p>
                <p className="text-2xl font-bold">{dashboardData?.weeklyHomeworkCount || 0}</p>
              </div>
              <BookOpen className="w-8 h-8 text-green-200" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-500 to-orange-500 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-100">正确率</p>
                <p className="text-2xl font-bold">{dashboardData?.accuracyRate || 0}%</p>
              </div>
              <Target className="w-8 h-8 text-yellow-200" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100">获得积分</p>
                <p className="text-2xl font-bold">{dashboardData?.totalPoints || 0}</p>
              </div>
              <Trophy className="w-8 h-8 text-purple-200" />
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 学习进度 */}
          <div className="lg:col-span-2">
            <Card title="学习进度">
              <div className="space-y-6">
                {dashboardData?.subjectProgress?.map((subject) => (
                  <div key={subject.id} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-700">{subject.name}</span>
                      <span className="text-sm text-gray-500">{subject.progress}%</span>
                    </div>
                    <Progress 
                      value={subject.progress} 
                      className="h-2"
                      color={subject.progress >= 80 ? 'green' : subject.progress >= 60 ? 'yellow' : 'red'}
                    />
                  </div>
                ))}
              </div>
            </Card>

            {/* 学习图表 */}
            <Card title="本周学习统计" className="mt-6">
              <ProgressChart data={dashboardData?.weeklyStats || []} />
            </Card>
          </div>

          {/* 右侧栏 */}
          <div className="space-y-6">
            {/* AI推荐 */}
            <Card title="智能推荐">
              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                          {rec.title}
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">
                          {rec.description}
                        </p>
                        <div className="flex items-center space-x-2">
                          <Tag variant="outline" size="sm">
                            {rec.subject}
                          </Tag>
                          <Tag variant="outline" size="sm" color="blue">
                            难度: {rec.difficulty}
                          </Tag>
                        </div>
                      </div>
                    </div>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="mt-3 w-full"
                      onClick={() => window.open(rec.url, '_blank')}
                    >
                      开始学习
                    </Button>
                  </div>
                ))}
              </div>
            </Card>

            {/* 最近错题 */}
            <Card title="最近错题">
              <div className="space-y-3">
                {dashboardData?.recentMistakes?.slice(0, 3).map((mistake) => (
                  <QuestionCard
                    key={mistake.id}
                    question={mistake}
                    compact
                    showAnalysis
                  />
                ))}
                {(!dashboardData?.recentMistakes || dashboardData.recentMistakes.length === 0) && (
                  <div className="text-center py-8 text-gray-500">
                    <BookOpen className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>暂无错题记录</p>
                    <p className="text-sm">继续练习积累错题集</p>
                  </div>
                )}
              </div>
            </Card>

            {/* 今日任务 */}
            <Card title="今日任务">
              <div className="space-y-3">
                {dashboardData?.todayTasks?.map((task) => (
                  <div key={task.id} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => {/* 处理任务完成状态 */}}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="flex-1">
                      <p className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                        {task.title}
                      </p>
                      <p className="text-sm text-gray-600">{task.subject}</p>
                    </div>
                    <Tag 
                      size="sm" 
                      color={task.urgent ? 'red' : 'blue'}
                      variant="outline"
                    >
                      {task.urgent ? '紧急' : '普通'}
                    </Tag>
                  </div>
                ))}
                {(!dashboardData?.todayTasks || dashboardData.todayTasks.length === 0) && (
                  <div className="text-center py-6 text-gray-500">
                    <Trophy className="w-10 h-10 mx-auto mb-2 text-gray-300" />
                    <p>今日任务已完成！</p>
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* AI聊天对话框 */}
      {showAIChat && (
        <AIChat
          role="student"
          onClose={() => setShowAIChat(false)}
          context={{
            userId: user?.id,
            currentSubjects: dashboardData?.subjectProgress?.map(s => s.name) || [],
            recentPerformance: dashboardData?.weeklyStats || []
          }}
        />
      )}
    </div>
  );
};

export default StudentDashboard;