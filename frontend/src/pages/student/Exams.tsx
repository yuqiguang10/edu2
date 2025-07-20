// src/pages/student/Exams.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Award, Play, Eye, Calendar, BookOpen } from 'lucide-react';
import { useStore } from '@/store';
import Button from '@/components/common/Button';
import Table from '@/components/common/Table';
import Modal from '@/components/common/Modal';
import { formatDateTime, getExamStatusLabel } from '@/utils/helpers';
import type { Exam, Column } from '@/types';

const StudentExams: React.FC = () => {
  const navigate = useNavigate();
  const { exams, fetchExams, loading } = useStore();
  const [selectedExam, setSelectedExam] = useState<Exam | null>(null);
  const [showExamModal, setShowExamModal] = useState(false);

  useEffect(() => {
    fetchExams();
  }, [fetchExams]);

  const columns: Column<Exam>[] = [
    {
      key: 'title',
      title: '考试名称',
      dataIndex: 'title',
      render: (value, record) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{record.description}</div>
        </div>
      ),
    },
    {
      key: 'subject',
      title: '科目',
      render: (_, record) => (
        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
          {record.subjectId === 1 ? '数学' : record.subjectId === 2 ? '英语' : '物理'}
        </span>
      ),
    },
    {
      key: 'duration',
      title: '考试时长',
      dataIndex: 'duration',
      render: (value) => `${value} 分钟`,
    },
    {
      key: 'totalScore',
      title: '总分',
      dataIndex: 'totalScore',
      render: (value) => `${value} 分`,
    },
    {
      key: 'startTime',
      title: '开始时间',
      dataIndex: 'startTime',
      render: (value) => formatDateTime(value),
    },
    {
      key: 'status',
      title: '状态',
      dataIndex: 'status',
      render: (value) => {
        const statusColors = {
          draft: 'bg-gray-100 text-gray-800',
          published: 'bg-blue-100 text-blue-800',
          ongoing: 'bg-green-100 text-green-800',
          completed: 'bg-purple-100 text-purple-800',
          cancelled: 'bg-red-100 text-red-800',
        };
        return (
          <span className={`px-2 py-1 rounded text-sm ${statusColors[value] || statusColors.draft}`}>
            {getExamStatusLabel(value)}
          </span>
        );
      },
    },
    {
      key: 'actions',
      title: '操作',
      render: (_, record) => (
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleViewExam(record)}
            icon={<Eye size={16} />}
          >
            查看
          </Button>
          {record.status === 'published' && (
            <Button
              size="sm"
              onClick={() => handleStartExam(record)}
              icon={<Play size={16} />}
            >
              开始考试
            </Button>
          )}
          {record.status === 'completed' && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleViewResult(record)}
            >
              查看成绩
            </Button>
          )}
        </div>
      ),
    },
  ];

  const handleViewExam = (exam: Exam) => {
    setSelectedExam(exam);
    setShowExamModal(true);
  };

  const handleStartExam = (exam: Exam) => {
    navigate(`/student/exams/${exam.id}/take`);
  };

  const handleViewResult = (exam: Exam) => {
    navigate(`/student/exams/${exam.id}/result`);
  };

  // 模拟考试数据
  const mockExams: Exam[] = [
    {
      id: 1,
      title: '数学期中考试',
      description: '涵盖函数、几何、概率统计等内容',
      classId: 1,
      subjectId: 1,
      teacherId: 1,
      startTime: '2024-01-15T09:00:00Z',
      endTime: '2024-01-15T11:00:00Z',
      duration: 120,
      totalScore: 100,
      status: 'published',
      questions: [],
      createdAt: '2024-01-10T10:00:00Z',
    },
    {
      id: 2,
      title: '英语听力测试',
      description: '专项听力能力测评',
      classId: 1,
      subjectId: 2,
      teacherId: 2,
      startTime: '2024-01-18T14:00:00Z',
      endTime: '2024-01-18T15:30:00Z',
      duration: 90,
      totalScore: 100,
      status: 'ongoing',
      questions: [],
      createdAt: '2024-01-12T10:00:00Z',
    },
    {
      id: 3,
      title: '物理实验考试',
      description: '力学实验操作及理论考核',
      classId: 1,
      subjectId: 3,
      teacherId: 3,
      startTime: '2024-01-12T10:00:00Z',
      endTime: '2024-01-12T12:00:00Z',
      duration: 120,
      totalScore: 100,
      status: 'completed',
      questions: [],
      createdAt: '2024-01-08T10:00:00Z',
    },
  ];

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">考试测评</h1>
          <p className="text-gray-600 mt-1">参加考试，检验学习成果</p>
        </div>
        <Button
          onClick={() => navigate('/student/exams/practice')}
          icon={<BookOpen size={20} />}
        >
          模拟练习
        </Button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Calendar className="w-8 h-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">待参加</p>
              <p className="text-xl font-bold text-gray-900">2</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">进行中</p>
              <p className="text-xl font-bold text-gray-900">1</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Award className="w-8 h-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">已完成</p>
              <p className="text-xl font-bold text-gray-900">5</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-purple-600 font-bold text-sm">%</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">平均分</p>
              <p className="text-xl font-bold text-gray-900">87.5</p>
            </div>
          </div>
        </div>
      </div>

      {/* 考试列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold">考试列表</h2>
        </div>
        
        <Table
          columns={columns}
          data={mockExams}
          loading={loading}
          rowKey="id"
          onRow={(record) => ({
            onClick: () => handleViewExam(record),
          })}
        />
      </div>

      {/* 考试详情模态框 */}
      <Modal
        isOpen={showExamModal}
        onClose={() => setShowExamModal(false)}
        title="考试详情"
        size="lg"
      >
        {selectedExam && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">考试名称</label>
                <p className="text-gray-900">{selectedExam.title}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">科目</label>
                <p className="text-gray-900">
                  {selectedExam.subjectId === 1 ? '数学' : selectedExam.subjectId === 2 ? '英语' : '物理'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">考试时长</label>
                <p className="text-gray-900">{selectedExam.duration} 分钟</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">总分</label>
                <p className="text-gray-900">{selectedExam.totalScore} 分</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">开始时间</label>
                <p className="text-gray-900">{formatDateTime(selectedExam.startTime)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">结束时间</label>
                <p className="text-gray-900">{formatDateTime(selectedExam.endTime)}</p>
              </div>
            </div>
            
            {selectedExam.description && (
              <div>
                <label className="text-sm font-medium text-gray-500">考试说明</label>
                <p className="text-gray-900 mt-1">{selectedExam.description}</p>
              </div>
            )}

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-medium text-yellow-800 mb-2">考试须知</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• 请确保网络连接稳定</li>
                <li>• 考试过程中不能切换浏览器标签页</li>
                <li>• 答题时间有限，请合理安排</li>
                <li>• 提交后不能修改答案</li>
              </ul>
            </div>
          </div>
        )}
        
        <div className="flex justify-end space-x-3 mt-6">
          <Button
            variant="outline"
            onClick={() => setShowExamModal(false)}
          >
            关闭
          </Button>
          {selectedExam?.status === 'published' && (
            <Button
              onClick={() => {
                setShowExamModal(false);
                handleStartExam(selectedExam);
              }}
              icon={<Play size={16} />}
            >
              开始考试
            </Button>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default StudentExams;
