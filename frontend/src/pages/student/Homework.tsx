// src/pages/student/Homework.tsx
import React, { useState, useEffect } from 'react';
import { FileText, Clock, CheckCircle, AlertCircle, Download, Upload } from 'lucide-react';
import Button from '@/components/common/Button';
import Table from '@/components/common/Table';
import Modal from '@/components/common/Modal';
import { formatDate, formatRelativeTime } from '@/utils/helpers';
import type { Column } from '@/types';

interface Homework {
  id: number;
  title: string;
  description: string;
  subject: string;
  assignDate: string;
  dueDate: string;
  status: 'pending' | 'submitted' | 'graded';
  score?: number;
  maxScore: number;
  attachment?: string;
  teacherComment?: string;
}

const StudentHomework: React.FC = () => {
  const [homeworks, setHomeworks] = useState<Homework[]>([]);
  const [selectedHomework, setSelectedHomework] = useState<Homework | null>(null);
  const [showHomeworkModal, setShowHomeworkModal] = useState(false);
  const [submissionText, setSubmissionText] = useState('');
  const [submissionFile, setSubmissionFile] = useState<File | null>(null);

  useEffect(() => {
    // 模拟获取作业数据
    const mockHomeworks: Homework[] = [
      {
        id: 1,
        title: '二次函数综合练习',
        description: '完成教材第5章习题1-20题，重点掌握函数图像的变换规律',
        subject: '数学',
        assignDate: '2024-01-10',
        dueDate: '2024-01-15',
        status: 'pending',
        maxScore: 100,
      },
      {
        id: 2,
        title: '英语阅读理解练习',
        description: '阅读指定文章，完成理解题并写出读后感',
        subject: '英语',
        assignDate: '2024-01-08',
        dueDate: '2024-01-14',
        status: 'submitted',
        maxScore: 100,
      },
      {
        id: 3,
        title: '物理实验报告',
        description: '完成"测量重力加速度"实验，提交实验报告',
        subject: '物理',
        assignDate: '2024-01-05',
        dueDate: '2024-01-12',
        status: 'graded',
        score: 92,
        maxScore: 100,
        teacherComment: '实验步骤清晰，数据记录准确，分析有理有据。建议在误差分析部分更加深入。',
      },
    ];
    setHomeworks(mockHomeworks);
  }, []);

  const columns: Column<Homework>[] = [
    {
      key: 'title',
      title: '作业标题',
      dataIndex: 'title',
      render: (value, record) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500 truncate max-w-xs">{record.description}</div>
        </div>
      ),
    },
    {
      key: 'subject',
      title: '科目',
      dataIndex: 'subject',
      render: (value) => (
        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
          {value}
        </span>
      ),
    },
    {
      key: 'dueDate',
      title: '截止日期',
      dataIndex: 'dueDate',
      render: (value) => {
        const isOverdue = new Date(value) < new Date() && new Date(value).toDateString() !== new Date().toDateString();
        return (
          <div className={isOverdue ? 'text-red-600' : 'text-gray-900'}>
            <div>{formatDate(value)}</div>
            <div className="text-xs text-gray-500">{formatRelativeTime(value)}</div>
          </div>
        );
      },
    },
    {
      key: 'status',
      title: '状态',
      dataIndex: 'status',
      render: (value, record) => {
        const statusConfig = {
          pending: { label: '待完成', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
          submitted: { label: '已提交', color: 'bg-blue-100 text-blue-800', icon: CheckCircle },
          graded: { label: '已批改', color: 'bg-green-100 text-green-800', icon: CheckCircle },
        };
        const config = statusConfig[value];
        const Icon = config.icon;
        
        return (
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded text-sm flex items-center ${config.color}`}>
              <Icon size={14} className="mr-1" />
              {config.label}
            </span>
            {value === 'graded' && record.score !== undefined && (
              <span className="text-sm font-medium text-green-600">
                {record.score}/{record.maxScore}
              </span>
            )}
          </div>
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
            onClick={() => handleViewHomework(record)}
          >
            查看详情
          </Button>
          {record.status === 'pending' && (
            <Button
              size="sm"
              onClick={() => handleSubmitHomework(record)}
            >
              提交作业
            </Button>
          )}
          {record.attachment && (
            <Button
              size="sm"
              variant="outline"
              icon={<Download size={16} />}
              onClick={() => handleDownloadAttachment(record)}
            >
              下载
            </Button>
          )}
        </div>
      ),
    },
  ];

  const handleViewHomework = (homework: Homework) => {
    setSelectedHomework(homework);
    setShowHomeworkModal(true);
  };

  const handleSubmitHomework = (homework: Homework) => {
    setSelectedHomework(homework);
    setSubmissionText('');
    setSubmissionFile(null);
    setShowHomeworkModal(true);
  };

  const handleDownloadAttachment = (homework: Homework) => {
    // 模拟下载附件
    console.log('下载附件:', homework.attachment);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSubmissionFile(file);
    }
  };

  const handleSubmit = () => {
    if (!selectedHomework) return;
    
    // 模拟提交作业
    const updatedHomeworks = homeworks.map(hw => 
      hw.id === selectedHomework.id 
        ? { ...hw, status: 'submitted' as const }
        : hw
    );
    setHomeworks(updatedHomeworks);
    setShowHomeworkModal(false);
    
    // 重置表单
    setSubmissionText('');
    setSubmissionFile(null);
  };

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">作业练习</h1>
        <p className="text-gray-600 mt-1">完成老师布置的作业，巩固学习成果</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">待完成</p>
              <p className="text-xl font-bold text-gray-900">
                {homeworks.filter(hw => hw.status === 'pending').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">已提交</p>
              <p className="text-xl font-bold text-gray-900">
                {homeworks.filter(hw => hw.status === 'submitted').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center">
            <FileText className="w-8 h-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">已批改</p>
              <p className="text-xl font-bold text-gray-900">
                {homeworks.filter(hw => hw.status === 'graded').length}
              </p>
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
              <p className="text-xl font-bold text-gray-900">
                {homeworks.filter(hw => hw.score !== undefined).length > 0
                  ? Math.round(
                      homeworks
                        .filter(hw => hw.score !== undefined)
                        .reduce((sum, hw) => sum + hw.score!, 0) /
                      homeworks.filter(hw => hw.score !== undefined).length
                    )
                  : 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 作业列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold">作业列表</h2>
        </div>
        
        <Table
          columns={columns}
          data={homeworks}
          rowKey="id"
        />
      </div>

      {/* 作业详情/提交模态框 */}
      <Modal
        isOpen={showHomeworkModal}
        onClose={() => setShowHomeworkModal(false)}
        title={selectedHomework?.status === 'pending' ? '提交作业' : '作业详情'}
        size="lg"
      >
        {selectedHomework && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">{selectedHomework.title}</h3>
              <p className="text-gray-600 mt-2">{selectedHomework.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">科目</label>
                <p className="text-gray-900">{selectedHomework.subject}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">布置时间</label>
                <p className="text-gray-900">{formatDate(selectedHomework.assignDate)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">截止时间</label>
                <p className="text-gray-900">{formatDate(selectedHomework.dueDate)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">总分</label>
                <p className="text-gray-900">{selectedHomework.maxScore} 分</p>
              </div>
            </div>

            {selectedHomework.status === 'pending' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    作业内容
                  </label>
                  <textarea
                    value={submissionText}
                    onChange={(e) => setSubmissionText(e.target.value)}
                    className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="请输入作业答案或说明..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    上传附件（可选）
                  </label>
                  <div className="flex items-center space-x-3">
                    <input
                      type="file"
                      onChange={handleFileChange}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                      accept=".pdf,.doc,.docx,.txt,.jpg,.png"
                    />
                    {submissionFile && (
                      <span className="text-sm text-green-600">
                        已选择: {submissionFile.name}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {selectedHomework.status === 'graded' && (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-green-800">作业成绩</h4>
                    <span className="text-2xl font-bold text-green-600">
                      {selectedHomework.score}/{selectedHomework.maxScore}
                    </span>
                  </div>
                </div>

                {selectedHomework.teacherComment && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      老师评语
                    </label>
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <p className="text-gray-700">{selectedHomework.teacherComment}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {selectedHomework.status === 'submitted' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2" />
                  <p className="text-blue-800">作业已提交，等待老师批改</p>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex justify-end space-x-3 mt-6">
          <Button
            variant="outline"
            onClick={() => setShowHomeworkModal(false)}
          >
            {selectedHomework?.status === 'pending' ? '取消' : '关闭'}
          </Button>
          {selectedHomework?.status === 'pending' && (
            <Button
              onClick={handleSubmit}
              disabled={!submissionText.trim()}
              icon={<Upload size={16} />}
            >
              提交作业
            </Button>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default StudentHomework;
