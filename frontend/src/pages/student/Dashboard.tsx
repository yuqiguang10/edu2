// src/pages/student/Dashboard.tsx
import React, { useEffect } from 'react';
import { useStore } from '@/store';
import { useAuth } from '@/hooks/useAuth';
import {
  Clock, CheckCircle, Target, TrendingUp, Brain, AlertCircle,
  BookOpen, Award, Calendar, BarChart3
} from 'lucide-react';
import Chart from '@/components/common/Chart';
import Button from '@/components/common/Button';

const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const { recommendations, getRecommendations, loading } = useStore();

  useEffect(() => {
    if (user) {
      // 获取AI推荐
      getRecommendations({
        userId: user.id,
        subjectId: 1, // 数学
        context: {
          currentLevel: 3,
          learningGoals: ['提高解题速度', '掌握函数图像'],
          weakPoints: ['几何证明', '应用题理解']
        }
      });
    }
  }, [user, getRecommendations]);

  // 学习统计数据
  const studyStats = {
    todayTime: 2.5,
    completedExercises: 15,
    accuracy: 85,
    weeklyGoal: 75
  };

  // 图表数据
  const progressData = [
    { name: '周一', score: 78 },
    { name: '��二', score: 82 },
    { name: '周三', score: 79 },
    { name: '周四', score: 85 },
    { name: '周五', score: 88 },
    { name: '周六', score: 92 },
    { name: '周日', score: 89 }
  ];

  const subjectData = [
    { name: '数学', value: 85 },
    { name: '英语', value: 78 },
    { name: '物理', value: 82 },
    { name: '化学', value: 76 }
  ];

  // 近期考试
  const upcomingExams = [
    { id: 1, subject: '数学', title: '二次函数单元测试', date: '2024-01-15', time: '09:00' },
    { id: 2, subject: '英语', title: '阅读理解专项练习', date: '2024-01-18', time: '14:30' },
    { id: 3, subject: '物理', title: '力学综合测评', date: '2024-01-20', time: '10:00' }
  ];

  // 最新作业
  const recentHomework = [
    { id: 1, subject: '数学', title: '函数图像练习', status: 'pending', dueDate: '2024-01-14' },
    { id: 2, subject: '英语', title: '词汇背诵打卡', status: 'submitted', dueDate: '2024-01-13' },
    { id: 3, subject: '物理', title: '实验报告', status: 'graded', score: 92, dueDate: '2024-01-12' }
  ];

  return (
    <div className="space-y-6">
      {/* 欢迎信息 */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-xl">
        <h1 className="text-2xl font-bold mb-2">
          早上好，{user?.realName || user?.username}！
        </h1>
        <p className="opacity-90">
          今天是您学习旅程的第 {Math.floor(Math.random() * 100) + 50} 天，继续加油！
        </p>
      </div>

      {/* 学习统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">今日学习时长</h3>
              <p className="text-2xl font-bold text-blue-600 mt-1">{studyStats.todayTime}小时</p>
            </div>
            <Clock className="w-12 h-12 text-blue-500 opacity-80" />
          </div>
          <div className="mt-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">目标: 3小时</span>
              <span className="text-blue-600">{Math.round((studyStats.todayTime / 3) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((studyStats.todayTime / 3) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">完成练习</h3>
              <p className="text-2xl font-bold text-green-600 mt-1">{studyStats.completedExercises}题</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-500 opacity-80" />
          </div>
          <div className="mt-2">
            <span className="text-sm text-green-600">+5 比昨天</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">正确率</h3>
              <p className="text-2xl font-bold text-purple-600 mt-1">{studyStats.accuracy}%</p>
            </div>
            <Target className="w-12 h-12 text-purple-500 opacity-80" />
          </div>
          <div className="mt-2">
            <span className="text-sm text-purple-600">+3% 比上周</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-500">周目标进度</h3>
              <p className="text-2xl font-bold text-orange-600 mt-1">{studyStats.weeklyGoal}%</p>
            </div>
            <TrendingUp className="w-12 h-12 text-orange-500 opacity-80" />
          </div>
          <div className="mt-2">
            <span className="text-sm text-gray-500">还需努力一点点</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI个性化推荐 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold flex items-center">
              <Brain className="w-6 h-6 mr-2 text-blue-600" />
              AI个性化推荐
            </h2>
            {loading && <div className="text-sm text-blue-600">分析中...</div>}
          </div>

          {recommendations && (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-3">推荐练习题</h3>
                <div className="space-y-2">
                  {recommendations.questions.slice(0, 3).map(q => (
                    <div key={q.id} className="p-3 bg-gray-50 rounded-lg flex items-center justify-between">
                      <div>
                        <span className="font-medium">{q.title}</span>
                        <div className="text-sm text-gray-500 mt-1">
                          <span className="mr-4">难度: {q.difficulty}/5</span>
                          <span>科目: {q.subject}</span>
                        </div>
                      </div>
                      <Button size="sm" variant="outline">
                        开始练习
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {recommendations.weakPoints.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">需要加强的知识点</h3>
                  <div className="flex flex-wrap gap-2">
                    {recommendations.weakPoints.map(point => (
                      <span key={point} className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-sm">
                        {point}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="p-3 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-700 mb-1">下一个目标</h4>
                <p className="text-sm text-blue-600">{recommendations.nextGoal}</p>
              </div>
            </div>
          )}
        </div>

        {/* 学习进度图表 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <BarChart3 className="w-6 h-6 mr-2 text-green-600" />
            本周学习进度
          </h2>
          <Chart
            type="line"
            data={progressData}
            height={240}
            xKey="name"
            yKey="score"
            colors={['#3B82F6']}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 近期考试 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Award className="w-6 h-6 mr-2 text-yellow-600" />
            近期考试
          </h2>
          <div className="space-y-3">
            {upcomingExams.map(exam => (
              <div key={exam.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div>
                  <div className="font-medium">{exam.title}</div>
                  <div className="text-sm text-gray-500 mt-1">
                    {exam.subject} • {exam.date} {exam.time}
                  </div>
                </div>
                <Button size="sm" variant="outline">
                  准备考试
                </Button>
              </div>
            ))}
          </div>
        </div>

        {/* 最新作业 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <BookOpen className="w-6 h-6 mr-2 text-purple-600" />
            最新作业
          </h2>
          <div className="space-y-3">
            {recentHomework.map(hw => (
              <div key={hw.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex-1">
                  <div className="font-medium">{hw.title}</div>
                  <div className="text-sm text-gray-500 mt-1">
                    {hw.subject} • 截止: {hw.dueDate}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {hw.status === 'pending' && (
                    <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded text-xs">
                      待完成
                    </span>
                  )}
                  {hw.status === 'submitted' && (
                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">
                      已提交
                    </span>
                  )}
                  {hw.status === 'graded' && (
                    <>
                      <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
                        已批改
                      </span>
                      <span className="text-sm font-medium text-green-600">
                        {hw.score}分
                      </span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 各��目成绩分布 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold mb-4">各科目成绩分布</h2>
        <Chart
          type="bar"
          data={subjectData}
          height={300}
          xKey="name"
          yKey="value"
          colors={['#3B82F6', '#EF4444', '#10B981', '#F59E0B']}
        />
      </div>
    </div>
  );
};

export default StudentDashboard;
