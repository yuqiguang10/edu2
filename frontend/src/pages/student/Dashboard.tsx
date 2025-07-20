// frontend/src/pages/student/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  List,
  Progress,
  Tag,
  Button,
  Statistic,
  Calendar,
  Badge,
  Timeline,
  Avatar,
  Space,
  Typography,
  Divider,
  Alert,
  Tooltip,
  Modal
} from 'antd';
import {
  BookOutlined,
  FileTextOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CalendarOutlined,
  StarOutlined,
  BulbOutlined,
  RocketOutlined,
  UserOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { classManagementAPI } from '@/api/classManagement';
import { homeworkAPI } from '@/api/homework';
import { examAPI } from '@/api/exam';
import { aiAPI } from '@/api/ai';

const { Title, Text, Paragraph } = Typography;

interface Assignment {
  id: number;
  title: string;
  type: 'homework' | 'exam';
  due_date: string;
  status: string;
  score?: number;
  submitted: boolean;
  submit_time?: string;
}

interface LearningProgress {
  subject: string;
  progress: number;
  total_hours: number;
  completed_hours: number;
  knowledge_points: {
    mastered: number;
    total: number;
  };
}

interface Recommendation {
  id: number;
  type: 'question' | 'resource' | 'video';
  title: string;
  description: string;
  difficulty: string;
  reason: string;
  priority: number;
}

interface StudentProfile {
  learning_style: string;
  strengths: string[];
  weaknesses: string[];
  avg_score: number;
  study_time_today: number;
  study_streak: number;
}

const StudentDashboard: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [learningProgress, setLearningProgress] = useState<LearningProgress[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [myClasses, setMyClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState<moment.Moment>(moment());

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [
        assignmentsRes,
        classesRes,
        profileRes,
        recommendationsRes
      ] = await Promise.all([
        classManagementAPI.getMyAssignments(),
        classManagementAPI.getMyClasses(),
        classManagementAPI.getMyProfile(),
        classManagementAPI.getMyRecommendations()
      ]);

      setAssignments(assignmentsRes.data.homeworks.concat(assignmentsRes.data.exams));
      setMyClasses(classesRes.data);
      setProfile(profileRes.data);
      setRecommendations(recommendationsRes.data);

      // 模拟学习进度数据
      setLearningProgress([
        {
          subject: '数学',
          progress: 75,
          total_hours: 120,
          completed_hours: 90,
          knowledge_points: { mastered: 45, total: 60 }
        },
        {
          subject: '语文',
          progress: 80,
          total_hours: 100,
          completed_hours: 80,
          knowledge_points: { mastered: 32, total: 40 }
        },
        {
          subject: '英语',
          progress: 65,
          total_hours: 80,
          completed_hours: 52,
          knowledge_points: { mastered: 26, total: 40 }
        }
      ]);
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAssignmentStatus = (assignment: Assignment) => {
    const dueDate = moment(assignment.due_date);
    const now = moment();
    
    if (assignment.submitted) {
      return { color: 'success', text: '已提交', icon: <CheckCircleOutlined /> };
    } else if (dueDate.isBefore(now)) {
      return { color: 'error', text: '已逾期', icon: <ExclamationCircleOutlined /> };
    } else if (dueDate.diff(now, 'hours') <= 24) {
      return { color: 'warning', text: '即将截止', icon: <ClockCircleOutlined /> };
    } else {
      return { color: 'processing', text: '进行中', icon: <ClockCircleOutlined /> };
    }
  };

  const getCalendarDateCellRender = (date: moment.Moment) => {
    const dayAssignments = assignments.filter(assignment => 
      moment(assignment.due_date).isSame(date, 'day')
    );

    if (dayAssignments.length === 0) return null;

    return (
      <ul className="events">
        {dayAssignments.slice(0, 2).map(assignment => (
          <li key={assignment.id}>
            <Badge 
              status={assignment.type === 'homework' ? 'processing' : 'error'}
              text={assignment.title.length > 8 ? assignment.title.slice(0, 8) + '...' : assignment.title}
            />
          </li>
        ))}
        {dayAssignments.length > 2 && <li>+{dayAssignments.length - 2} 项</li>}
      </ul>
    );
  };

  const handleStartAssignment = (assignment: Assignment) => {
    if (assignment.type === 'homework') {
      // 跳转到作业页面
      window.location.href = `/student/homework/${assignment.id}`;
    } else {
      // 跳转到考试页面
      window.location.href = `/student/exam/${assignment.id}`;
    }
  };

  const handleViewRecommendation = (recommendation: Recommendation) => {
    Modal.info({
      title: '学习推荐详情',
      content: (
        <div>
          <p><strong>标题：</strong>{recommendation.title}</p>
          <p><strong>类型：</strong>{recommendation.type}</p>
          <p><strong>难度：</strong>{recommendation.difficulty}</p>
          <p><strong>推荐理由：</strong>{recommendation.reason}</p>
          <p><strong>描述：</strong>{recommendation.description}</p>
        </div>
      ),
      width: 500
    });
  };

  return (
    <div className="student-dashboard">
      {/* 欢迎横幅 */}
      <Card className="welcome-banner" style={{ marginBottom: 24, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Row align="middle">
          <Col flex="auto">
            <Title level={3} style={{ color: 'white', margin: 0 }}>
              欢迎回来！今天也要努力学习哦 🌟
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
              {moment().format('YYYY年MM月DD日 dddd')}
            </Text>
          </Col>
          <Col>
            <Space direction="vertical" align="center">
              <Avatar size={64} icon={<UserOutlined />} />
              {profile && (
                <div style={{ textAlign: 'center' }}>
                  <div>连续学习 {profile.study_streak} 天</div>
                  <div>今日学习 {profile.study_time_today} 分钟</div>
                </div>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      <Row gutter={[24, 24]}>
        {/* 左侧主要内容 */}
        <Col xs={24} lg={16}>
          {/* 学习统计 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="平均成绩"
                  value={profile?.avg_score || 0}
                  precision={1}
                  valueStyle={{ color: '#3f8600' }}
                  prefix={<TrophyOutlined />}
                  suffix="分"
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="待完成作业"
                  value={assignments.filter(a => !a.submitted && a.type === 'homework').length}
                  valueStyle={{ color: '#cf1322' }}
                  prefix={<FileTextOutlined />}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="即将考试"
                  value={assignments.filter(a => a.type === 'exam' && moment(a.due_date).diff(moment(), 'days') <= 7).length}
                  valueStyle={{ color: '#fa8c16' }}
                  prefix={<BookOutlined />}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="学习时长"
                  value={profile?.study_time_today || 0}
                  valueStyle={{ color: '#722ed1' }}
                  prefix={<ClockCircleOutlined />}
                  suffix="分钟"
                />
              </Card>
            </Col>
          </Row>

          {/* 学习进度 */}
          <Card title="学习进度" style={{ marginBottom: 24 }}>
            <Row gutter={[16, 16]}>
              {learningProgress.map((subject, index) => (
                <Col xs={24} md={8} key={index}>
                  <div className="subject-progress">
                    <div className="flex justify-between items-center mb-2">
                      <Text strong>{subject.subject}</Text>
                      <Text type="secondary">{subject.progress}%</Text>
                    </div>
                    <Progress 
                      percent={subject.progress} 
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                      style={{ marginBottom: 8 }}
                    />
                    <div className="text-sm text-gray-500">
                      <div>知识点: {subject.knowledge_points.mastered}/{subject.knowledge_points.total}</div>
                      <div>学时: {subject.completed_hours}/{subject.total_hours}h</div>
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>

          {/* 近期作业和考试 */}
          <Card 
            title="近期任务" 
            extra={<Button type="link" onClick={() => window.location.href = '/student/assignments'}>查看全部</Button>}
          >
            <List
              itemLayout="horizontal"
              dataSource={assignments.slice(0, 5)}
              renderItem={(assignment) => {
                const status = getAssignmentStatus(assignment);
                return (
                  <List.Item
                    actions={[
                      !assignment.submitted && (
                        <Button 
                          type="primary" 
                          size="small"
                          onClick={() => handleStartAssignment(assignment)}
                        >
                          {assignment.type === 'homework' ? '开始作业' : '进入考试'}
                        </Button>
                      ),
                      assignment.submitted && assignment.score && (
                        <Tag color="green">得分: {assignment.score}</Tag>
                      )
                    ].filter(Boolean)}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar 
                          icon={assignment.type === 'homework' ? <FileTextOutlined /> : <BookOutlined />}
                          style={{ 
                            backgroundColor: assignment.type === 'homework' ? '#1890ff' : '#f5222d' 
                          }}
                        />
                      }
                      title={
                        <Space>
                          {assignment.title}
                          <Tag color={status.color} icon={status.icon}>
                            {status.text}
                          </Tag>
                        </Space>
                      }
                      description={
                        <div>
                          <div>截止时间: {moment(assignment.due_date).format('MM-DD HH:mm')}</div>
                          {assignment.submit_time && (
                            <div className="text-green-600">
                              提交时间: {moment(assignment.submit_time).format('MM-DD HH:mm')}
                            </div>
                          )}
                        </div>
                      }
                    />
                  </List.Item>
                );
              }}
            />
          </Card>
        </Col>

        {/* 右侧边栏 */}
        <Col xs={24} lg={8}>
          {/* AI学习建议 */}
          <Card 
            title={
              <Space>
                <BulbOutlined style={{ color: '#faad14' }} />
                AI学习建议
              </Space>
            }
            style={{ marginBottom: 24 }}
          >
            {profile && (
              <div>
                <Alert
                  message="个性化学习建议"
                  description={`根据您的学习风格（${profile.learning_style}），建议您：多做视觉化练习，加强逻辑思维训练。`}
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                
                <div>
                  <Text strong>优势学科:</Text>
                  <div style={{ marginTop: 8, marginBottom: 16 }}>
                    {profile.strengths?.map((strength, index) => (
                      <Tag color="green" key={index}>{strength}</Tag>
                    ))}
                  </div>
                  
                  <Text strong>需要加强:</Text>
                  <div style={{ marginTop: 8 }}>
                    {profile.weaknesses?.map((weakness, index) => (
                      <Tag color="orange" key={index}>{weakness}</Tag>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </Card>

          {/* 智能推荐 */}
          <Card 
            title={
              <Space>
                <RocketOutlined style={{ color: '#722ed1' }} />
                为你推荐
              </Space>
            }
            style={{ marginBottom: 24 }}
          >
            <List
              size="small"
              dataSource={recommendations.slice(0, 4)}
              renderItem={(rec) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        size="small"
                        style={{ 
                          backgroundColor: rec.type === 'question' ? '#1890ff' : 
                                           rec.type === 'video' ? '#f5222d' : '#52c41a'
                        }}
                      >
                        {rec.type === 'question' ? '题' : 
                         rec.type === 'video' ? '视' : '资'}
                      </Avatar>
                    }
                    title={
                      <div>
                        <Text ellipsis style={{ width: 120 }}>{rec.title}</Text>
                        <Tag size="small" color="blue">{rec.difficulty}</Tag>
                      </div>
                    }
                    description={
                      <Text 
                        type="secondary" 
                        ellipsis 
                        style={{ fontSize: 12 }}
                        onClick={() => handleViewRecommendation(rec)}
                      >
                        {rec.reason}
                      </Text>
                    }
                  />
                </List.Item>
              )}
            />
            <Button 
              type="link" 
              block 
              onClick={() => window.location.href = '/student/recommendations'}
            >
              查看更多推荐
            </Button>
          </Card>

          {/* 学习日历 */}
          <Card title={<Space><CalendarOutlined />学习日历</Space>}>
            <Calendar
              fullscreen={false}
              value={selectedDate}
              onSelect={setSelectedDate}
              dateCellRender={getCalendarDateCellRender}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default StudentDashboard;