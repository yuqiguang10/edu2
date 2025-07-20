// src/pages/student/Progress.tsx
import React, { useState, useEffect } from 'react';
import { TrendingUp, Target, Award, Brain, Calendar, BarChart3 } from 'lucide-react';
import { useStore } from '@/store';
import { useAuth } from '@/hooks/useAuth';
import Chart from '@/components/common/Chart';
import Button from '@/components/common/Button';

const StudentProgress: React.FC = () => {
  const { user } = useAuth();
  const { analysis, analyzePerformance, loading } = useStore();
  const [selectedPeriod, setSelectedPeriod] = useState('month');

  useEffect(() => {
    if (user) {
      analyzePerformance({
        studentId: user.id,
        timeRange: {
          start: '2024-01-01',
          end: '2024-01-31'
        },
        subjects: [1, 2, 3] // 数学、英语、物理
      });
    }
  }, [user, analyzePerformance]);

  // 模拟数据
  const performanceData = [
    { date: '1/1', score: 75, subject: '数学' },
    { date: '1/8', score: 82, subject: '数学' },
    { date: '1/15', score: 78, subject: '数学' },
    { date: '1/22', score: 85, subject: '数学' },
    { date: '1/29', score: 88, subject: '数学' },
  ];

  const subjectProgress = [
    { name: '数学', current: 85, target: 90, improvement: 8 },
    { name: '英语', current: 78, target: 85, improvement: 5 },
    { name: '物理', current: 82, target: 88, improvement: 12 },
    { name: '化学', current: 76, target: 80, improvement: -2 },
  ];

  const knowledgePoints = [
    { name: '函数与方程', mastery: 85, difficulty: 4, progress: 92 },
    { name: '几何证明', mastery: 72, difficulty: 5, progress: 68 },
    { name: '概率统计', mastery: 88, difficulty: 3, progress: 95 },
    { name: '数列极限', mastery: 65, difficulty: 5, progress: 45 },
  ];

  const studyHabits = {
    averageStudyTime: 2.5,
    peakStudyHour: '19:00-21:00',
    preferredSubject: '数学',
    weakestTime: '13:00-15:00',
    focusScore: 82,
    consistencyScore: 76
  };

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">学习分析</h1>
          <p className="text-gray-600 mt-1">深入了解您的学习进步和表现</p>
        </div>
        
        <div className="flex space-x-2">
          {['week', 'month', 'semester'].map(period => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSelectedPeriod(period)}
            >
              {period === 'week' ? '本周' : period === 'month' ? '本月' : '本学期'}
            </Button>
          ))}
        </div>
      </div>

      {/* 总体表现卡片 */}
      {analysis && (
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">综合评分</h3>
              <div className="text-4xl font-bold">{analysis.overallScore}</div>
              <p className="text-blue-100 mt-1">
                较上月 {analysis.improvement > 0 ? '+' : ''}{analysis.improvement} 分
              </p>
            </div>
            
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">优势领域</h3>
              <div className="space-y-1">
                {analysis.strengths.slice(0, 2).map(strength => (
                  <div key={strength} className="bg-white/20 rounded px-2 py-1 text-sm">
                    {strength}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">改进建议</h3>
              <p className="text-blue-100 text-sm">{analysis.recommendation}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 学习趋势图 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
              学习趋势
            </h2>
          </div>
          
          <Chart
            type="line"
            data={performanceData}
            height={280}
            xKey="date"
            yKey="score"
            colors={['#3B82F6']}
          />
          
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-500">最高分</p>
              <p className="text-lg font-semibold text-green-600">88</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">平均分</p>
              <p className="text-lg font-semibold text-blue-600">81.6</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">进步幅度</p>
              <p className="text-lg font-semibold text-purple-600">+13</p>
            </div>
          </div>
        </div>

        {/* 各科目进度 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-green-600" />
            各科目进度
          </h2>
          
          <div className="space-y-4">
            {subjectProgress.map(subject => (
              <div key={subject.name} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{subject.name}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">
                      {subject.current}/{subject.target}
                    </span>
                    <span className={`text-sm font-medium ${
                      subject.improvement > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {subject.improvement > 0 ? '+' : ''}{subject.improvement}%
                    </span>
                  </div>
                </div>
                
                <div className="relative">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(subject.current / subject.target) * 100}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0</span>
                    <span>{subject.target}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 知识点掌握情况 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center">
          <Brain className="w-5 h-5 mr-2 text-purple-600" />
          知识点掌握情况
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {knowledgePoints.map(point => (
            <div key={point.name} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-medium">{point.name}</h4>
                  <div className="flex items-center space-x-3 mt-1">
                    <span className="text-sm text-gray-500">
                      难度: {'★'.repeat(point.difficulty)}{'☆'.repeat(5 - point.difficulty)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-blue-600">{point.mastery}%</div>
                  <div className="text-xs text-gray-500">掌握度</div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>学习进度</span>
                  <span>{point.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${point.progress}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="mt-3">
                <Button size="sm" variant="outline" className="w-full">
                  {point.mastery < 80 ? '加强练习' : '巩固复习'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 学习习惯分析 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center">
          <Calendar className="w-5 h-5 mr-2 text-orange-600" />
          学习习惯分析
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-4">
            <h3 className="font-medium text-gray-800">时间分布</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">平均每日学习</span>
                <span className="font-medium">{studyHabits.averageStudyTime}小时</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">最佳学习时段</span>
                <span className="font-medium">{studyHabits.peakStudyHour}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">效率较低时段</span>
                <span className="font-medium">{studyHabits.weakestTime}</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="font-medium text-gray-800">学习偏好</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">偏好科目</span>
                <span className="font-medium">{studyHabits.preferredSubject}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">专注度评分</span>
                <span className="font-medium text-blue-600">{studyHabits.focusScore}/100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">学习一致性</span>
                <span className="font-medium text-green-600">{studyHabits.consistencyScore}/100</span>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="font-medium text-gray-800">改进建议</h3>
            <div className="space-y-2">
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-700">
                  建议在19-21点进行重点学习，这是您的黄金时段
                </p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-green-700">
                  午后时段可以安排轻松的复习活动
                </p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg">
                <p className="text-sm text-orange-700">
                  增加弱势科目的练习时间
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentProgress;
