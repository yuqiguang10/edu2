// frontend/src/pages/teacher/MyClasses.tsx
import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  Modal,
  Form,
  Input,
  DatePicker,
  Select,
  message,
  Tabs,
  Tag,
  Space,
  Progress,
  List,
  Avatar,
  Tooltip,
  Upload
} from 'antd';
import {
  TeamOutlined,
  BookOutlined,
  FileTextOutlined,
  PlusOutlined,
  EditOutlined,
  EyeOutlined,
  UploadOutlined,
  DownloadOutlined,
  UserOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import { useForm } from 'antd/es/form/Form';
import moment from 'moment';
import { classManagementAPI } from '@/api/classManagement';
import { homeworkAPI } from '@/api/homework';
import { examAPI } from '@/api/exam';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface TeacherClass {
  class_id: number;
  class_name: string;
  grade_name: string;
  subject_name: string;
  assignment_type: string;
  student_count: number;
  is_class_teacher: boolean;
}

interface Student {
  student_id: number;
  username: string;
  real_name: string;
  student_id_number: string;
  email: string;
  phone: string;
  join_date: string;
  learning_style?: string;
  last_login?: string;
}

interface Homework {
  id: number;
  title: string;
  description: string;
  due_date: string;
  status: string;
  score?: number;
  submitted: boolean;
  submit_time?: string;
}

interface Exam {
  id: number;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  duration: number;
  total_score: number;
  status: string;
  score?: number;
  submitted: boolean;
  submit_time?: string;
}

const MyClasses: React.FC = () => {
  const [myClasses, setMyClasses] = useState<TeacherClass[]>([]);
  const [selectedClass, setSelectedClass] = useState<TeacherClass | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [classStats, setClassStats] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // 作业相关状态
  const [homeworks, setHomeworks] = useState<Homework[]>([]);
  const [homeworkModalVisible, setHomeworkModalVisible] = useState(false);
  const [homeworkForm] = useForm();

  // 考试相关状态
  const [exams, setExams] = useState<Exam[]>([]);
  const [examModalVisible, setExamModalVisible] = useState(false);
  const [examForm] = useForm();

  // 学生管理状态
  const [importStudentVisible, setImportStudentVisible] = useState(false);

  useEffect(() => {
    fetchMyClasses();
  }, []);

  useEffect(() => {
    if (selectedClass) {
      fetchClassData(selectedClass.class_id);
    }
  }, [selectedClass]);

  const fetchMyClasses = async () => {
    setLoading(true);
    try {
      const response = await classManagementAPI.getMyTeachingClasses();
      setMyClasses(response.data);
      if (response.data.length > 0) {
        setSelectedClass(response.data[0]);
      }
    } catch (error) {
      message.error('获取我的班级失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchClassData = async (classId: number) => {
    try {
      const [studentsRes, statsRes, homeworksRes, examsRes] = await Promise.all([
        classManagementAPI.getClassStudents(classId),
        classManagementAPI.getClassStatistics(classId),
        homeworkAPI.getClassHomeworks(classId),
        examAPI.getClassExams(classId)
      ]);

      setStudents(studentsRes.data);
      setClassStats(statsRes.data);
      setHomeworks(homeworksRes.data);
      setExams(examsRes.data);
    } catch (error) {
      message.error('获取班级数据失败');
    }
  };

  const handleCreateHomework = async (values: any) => {
    try {
      await homeworkAPI.createHomework({
        ...values,
        class_id: selectedClass?.class_id,
        due_date: values.due_date.format('YYYY-MM-DD HH:mm:ss')
      });
      message.success('作业创建成功');
      setHomeworkModalVisible(false);
      homeworkForm.resetFields();
      fetchClassData(selectedClass!.class_id);
    } catch (error) {
      message.error('作业创建失败');
    }
  };

  const handleCreateExam = async (values: any) => {
    try {
      await examAPI.createExam({
        ...values,
        class_id: selectedClass?.class_id,
        start_time: values.exam_time[0].format('YYYY-MM-DD HH:mm:ss'),
        end_time: values.exam_time[1].format('YYYY-MM-DD HH:mm:ss')
      });
      message.success('考试创建成功');
      setExamModalVisible(false);
      examForm.resetFields();
      fetchClassData(selectedClass!.class_id);
    } catch (error) {
      message.error('考试创建失败');
    }
  };

  const handleImportStudents = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await classManagementAPI.importStudents(selectedClass!.class_id, formData);
      message.success('学生导入成功');
      setImportStudentVisible(false);
      fetchClassData(selectedClass!.class_id);
      return false;
    } catch (error) {
      message.error('学生导入失败');
      return false;
    }
  };

  const studentColumns: ColumnsType<Student> = [
    {
      title: '姓名',
      dataIndex: 'real_name',
      key: 'real_name',
      render: (text, record) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <div>
            <div>{text}</div>
            <div className="text-xs text-gray-500">{record.student_id_number}</div>
          </div>
        </Space>
      )
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username'
    },
    {
      title: '联系方式',
      key: 'contact',
      render: (_, record) => (
        <div>
          <div>{record.email}</div>
          <div className="text-sm text-gray-500">{record.phone}</div>
        </div>
      )
    },
    {
      title: '学习风格',
      dataIndex: 'learning_style',
      key: 'learning_style',
      render: (style) => style ? <Tag color="blue">{style}</Tag> : '-'
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      render: (time) => time ? moment(time).format('MM-DD HH:mm') : '-'
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              // 查看学生详情
              Modal.info({
                title: '学生详情',
                content: (
                  <div>
                    <p><strong>姓名：</strong>{record.real_name}</p>
                    <p><strong>学号：</strong>{record.student_id_number}</p>
                    <p><strong>邮箱：</strong>{record.email}</p>
                    <p><strong>电话：</strong>{record.phone}</p>
                    <p><strong>入班日期：</strong>{record.join_date}</p>
                  </div>
                ),
                width: 400
              });
            }}
          >
            详情
          </Button>
        </Space>
      )
    }
  ];

  const homeworkColumns: ColumnsType<Homework> = [
    {
      title: '作业标题',
      dataIndex: 'title',
      key: 'title'
    },
    {
      title: '截止时间',
      dataIndex: 'due_date',
      key: 'due_date',
      render: (date) => moment(date).format('YYYY-MM-DD HH:mm')
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          'assigned': { color: 'orange', text: '已布置' },
          'submitted': { color: 'blue', text: '已提交' },
          'graded': { color: 'green', text: '已批改' }
        };
        const statusInfo = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status };
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
      }
    },
    {
      title: '提交率',
      key: 'submit_rate',
      render: () => {
        // 这里应该计算实际的提交率
        const submitRate = Math.floor(Math.random() * 100);
        return (
          <div>
            <Progress percent={submitRate} size="small" />
            <span className="text-xs">{submitRate}%</span>
          </div>
        );
      }
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small">查看提交</Button>
          <Button type="link" size="small">批改</Button>
        </Space>
      )
    }
  ];

  const examColumns: ColumnsType<Exam> = [
    {
      title: '考试标题',
      dataIndex: 'title',
      key: 'title'
    },
    {
      title: '考试时间',
      key: 'exam_time',
      render: (_, record) => (
        <div>
          <div>{moment(record.start_time).format('YYYY-MM-DD HH:mm')}</div>
          <div className="text-xs text-gray-500">
            时长：{record.duration}分钟
          </div>
        </div>
      )
    },
    {
      title: '总分',
      dataIndex: 'total_score',
      key: 'total_score'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          'assigned': { color: 'orange', text: '已安排' },
          'ongoing': { color: 'blue', text: '进行中' },
          'completed': { color: 'green', text: '已完成' }
        };
        const statusInfo = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status };
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
      }
    },
    {
      title: '参与率',
      key: 'participate_rate',
      render: () => {
        const participateRate = Math.floor(Math.random() * 100);
        return (
          <div>
            <Progress percent={participateRate} size="small" />
            <span className="text-xs">{participateRate}%</span>
          </div>
        );
      }
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small">查看结果</Button>
          <Button type="link" size="small">批改</Button>
        </Space>
      )
    }
  ];

  return (
    <div className="my-classes">
      {/* 班级选择器 */}
      <Card style={{ marginBottom: 16 }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="font-medium">我的班级：</span>
            <Select
              value={selectedClass?.class_id}
              onChange={(classId) => {
                const classItem = myClasses.find(c => c.class_id === classId);
                setSelectedClass(classItem || null);
              }}
              style={{ width: 200 }}
            >
              {myClasses.map((classItem) => (
                <Option key={classItem.class_id} value={classItem.class_id}>
                  {classItem.class_name} - {classItem.subject_name}
                  {classItem.is_class_teacher && <Tag color="red" style={{ marginLeft: 8 }}>班主任</Tag>}
                </Option>
              ))}
            </Select>
          </div>
          {selectedClass?.is_class_teacher && (
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setImportStudentVisible(true)}
            >
              导入学生
            </Button>
          )}
        </div>
      </Card>

      {selectedClass && (
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          {/* 概览 */}
          <TabPane tab="班级概览" key="overview">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="学生人数"
                    value={students.length}
                    prefix={<TeamOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="作业数量"
                    value={homeworks.length}
                    prefix={<FileTextOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="考试数量"
                    value={exams.length}
                    prefix={<BookOutlined />}
                    valueStyle={{ color: '#faad14' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="平均分"
                    value={classStats.statistics?.avg_score || 0}
                    precision={1}
                    valueStyle={{ color: '#f5222d' }}
                    suffix="分"
                  />
                </Card>
              </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              <Col xs={24} lg={12}>
                <Card title="最近作业" size="small">
                  <List
                    size="small"
                    dataSource={homeworks.slice(0, 5)}
                    renderItem={(homework) => (
                      <List.Item>
                        <List.Item.Meta
                          title={homework.title}
                          description={`截止：${moment(homework.due_date).format('MM-DD HH:mm')}`}
                        />
                        <Tag color={homework.status === 'graded' ? 'green' : 'orange'}>
                          {homework.status === 'graded' ? '已批改' : '待批改'}
                        </Tag>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title="最近考试" size="small">
                  <List
                    size="small"
                    dataSource={exams.slice(0, 5)}
                    renderItem={(exam) => (
                      <List.Item>
                        <List.Item.Meta
                          title={exam.title}
                          description={`时间：${moment(exam.start_time).format('MM-DD HH:mm')}`}
                        />
                        <Tag color={exam.status === 'completed' ? 'green' : 'blue'}>
                          {exam.status === 'completed' ? '已完成' : '进行中'}
                        </Tag>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* 学生管理 */}
          <TabPane tab="学生管理" key="students">
            <Card
              title={`学生列表 (${students.length}人)`}
              extra={
                selectedClass.is_class_teacher && (
                  <Space>
                    <Button
                      icon={<UploadOutlined />}
                      onClick={() => setImportStudentVisible(true)}
                    >
                      导入学生
                    </Button>
                    <Button
                      icon={<DownloadOutlined />}
                      onClick={async () => {
                        try {
                          const response = await classManagementAPI.exportStudents(selectedClass.class_id);
                          // 处理文件下载
                          const url = window.URL.createObjectURL(new Blob([response.data]));
                          const link = document.createElement('a');
                          link.href = url;
                          link.download = `${selectedClass.class_name}_学生名单.xlsx`;
                          link.click();
                        } catch (error) {
                          message.error('导出失败');
                        }
                      }}
                    >
                      导出名单
                    </Button>
                  </Space>
                )
              }
            >
              <Table
                columns={studentColumns}
                dataSource={students}
                rowKey="student_id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 名学生`
                }}
              />
            </Card>
          </TabPane>

          {/* 作业管理 */}
          <TabPane tab="作业管理" key="homework">
            <Card
              title="作业列表"
              extra={
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setHomeworkModalVisible(true)}
                >
                  布置作业
                </Button>
              }
            >
              <Table
                columns={homeworkColumns}
                dataSource={homeworks}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true
                }}
              />
            </Card>
          </TabPane>

          {/* 考试管理 */}
          <TabPane tab="考试管理" key="exam">
            <Card
              title="考试列表"
              extra={
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setExamModalVisible(true)}
                >
                  创建考试
                </Button>
              }
            >
              <Table
                columns={examColumns}
                dataSource={exams}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true
                }}
              />
            </Card>
          </TabPane>
        </Tabs>
      )}

      {/* 布置作业模态框 */}
      <Modal
        title="布置作业"
        open={homeworkModalVisible}
        onCancel={() => setHomeworkModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={homeworkForm}
          layout="vertical"
          onFinish={handleCreateHomework}
        >
          <Form.Item
            name="title"
            label="作业标题"
            rules={[{ required: true, message: '请输入作业标题' }]}
          >
            <Input placeholder="请输入作业标题" />
          </Form.Item>
          <Form.Item
            name="description"
            label="作业描述"
            rules={[{ required: true, message: '请输入作业描述' }]}
          >
            <TextArea rows={4} placeholder="请详细描述作业要求" />
          </Form.Item>
          <Form.Item
            name="due_date"
            label="截止时间"
            rules={[{ required: true, message: '请选择截止时间' }]}
          >
            <DatePicker
              showTime
              format="YYYY-MM-DD HH:mm"
              placeholder="选择截止时间"
              style={{ width: '100%' }}
            />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                布置作业
              </Button>
              <Button onClick={() => setHomeworkModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 创建考试模态框 */}
      <Modal
        title="创建考试"
        open={examModalVisible}
        onCancel={() => setExamModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={examForm}
          layout="vertical"
          onFinish={handleCreateExam}
        >
          <Form.Item
            name="title"
            label="考试标题"
            rules={[{ required: true, message: '请输入考试标题' }]}
          >
            <Input placeholder="请输入考试标题" />
          </Form.Item>
          <Form.Item
            name="description"
            label="考试说明"
          >
            <TextArea rows={3} placeholder="考试相关说明" />
          </Form.Item>
          <Form.Item
            name="exam_time"
            label="考试时间"
            rules={[{ required: true, message: '请选择考试时间' }]}
          >
            <RangePicker
              showTime
              format="YYYY-MM-DD HH:mm"
              placeholder={['开始时间', '结束时间']}
              style={{ width: '100%' }}
            />
          </Form.Item>
          <Form.Item
            name="total_score"
            label="总分"
            rules={[{ required: true, message: '请输入总分' }]}
          >
            <Input type="number" placeholder="考试总分" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建考试
              </Button>
              <Button onClick={() => setExamModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 导入学生模态框 */}
      <Modal
        title="批量导入学生"
        open={importStudentVisible}
        onCancel={() => setImportStudentVisible(false)}
        footer={null}
      >
        <div>
          <p>请选择Excel文件进行批量导入：</p>
          <Upload
            beforeUpload={handleImportStudents}
            accept=".xlsx,.xls"
            showUploadList={false}
          >
            <Button icon={<UploadOutlined />}>选择文件</Button>
          </Upload>
          <div style={{ marginTop: 16 }}>
            <p>文件格式要求：</p>
            <ul>
              <li>支持 .xlsx 和 .xls 格式</li>
              <li>第一行为表头：姓名、用户名、邮箱、学号、电话</li>
              <li>每行一个学生信息</li>
            </ul>
            <Button 
              type="link" 
              onClick={() => {
                const link = document.createElement('a');
                link.href = '/templates/student_import_template.xlsx';
                link.download = '学生导入模板.xlsx';
                link.click();
              }}
            >
              下载模板文件
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default MyClasses;