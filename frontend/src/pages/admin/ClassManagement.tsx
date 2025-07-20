// frontend/src/pages/admin/ClassManagement.tsx
import React, { useState, useEffect } from 'react';
import {
  Button,
  Input,
  Modal,
  Table,
  Card,
  Select,
  Form,
  Upload,
  message,
  Tabs,
  Space,
  Tag,
  Tooltip,
  Popconfirm,
  Progress,
  Drawer
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserAddOutlined,
  ImportOutlined,
  ExportOutlined,
  EyeOutlined,
  TeamOutlined,
  BookOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import { useForm } from 'antd/es/form/Form';
import { ColumnsType } from 'antd/es/table';
import { classManagementAPI } from '@/api/classManagement';
import { userAPI } from '@/api/user';
import { educationAPI } from '@/api/education';

const { Option } = Select;
const { TabPane } = Tabs;
const { TextArea } = Input;

interface Class {
  id: number;
  name: string;
  grade_name: string;
  student_count: number;
  max_students: number;
  class_teacher?: {
    id: number;
    name: string;
  };
  academic_year?: string;
  created_at: string;
}

interface Teacher {
  id: number;
  name: string;
  subject_name?: string;
  assignment_type?: string;
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

const ClassManagement: React.FC = () => {
  const [classes, setClasses] = useState<Class[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingClass, setEditingClass] = useState<Class | null>(null);
  const [classDetailVisible, setClassDetailVisible] = useState(false);
  const [selectedClass, setSelectedClass] = useState<Class | null>(null);
  const [assignTeacherVisible, setAssignTeacherVisible] = useState(false);
  const [importStudentVisible, setImportStudentVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('list');
  
  const [form] = useForm();
  const [assignForm] = useForm();

  // 数据状态
  const [studyLevels, setStudyLevels] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [classStudents, setClassStudents] = useState<Student[]>([]);
  const [classTeachers, setClassTeachers] = useState<Teacher[]>([]);
  const [classStats, setClassStats] = useState<any>({});

  // 分页状态
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  useEffect(() => {
    fetchClasses();
    fetchStudyLevels();
    fetchTeachers();
    fetchSubjects();
  }, [pagination.current, pagination.pageSize]);

  const fetchClasses = async () => {
    setLoading(true);
    try {
      const response = await classManagementAPI.getClasses({
        page: pagination.current,
        page_size: pagination.pageSize
      });
      setClasses(response.data.items);
      setPagination(prev => ({
        ...prev,
        total: response.data.total
      }));
    } catch (error) {
      message.error('获取班级列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchStudyLevels = async () => {
    try {
      const response = await educationAPI.getStudyLevels();
      setStudyLevels(response.data);
    } catch (error) {
      console.error('获取学段失败:', error);
    }
  };

  const fetchTeachers = async () => {
    try {
      const response = await userAPI.getTeachers();
      setTeachers(response.data);
    } catch (error) {
      console.error('获取教师列表失败:', error);
    }
  };

  const fetchSubjects = async () => {
    try {
      const response = await educationAPI.getSubjects();
      setSubjects(response.data);
    } catch (error) {
      console.error('获取学科列表失败:', error);
    }
  };

  const fetchClassDetail = async (classId: number) => {
    try {
      const [detailRes, studentsRes, statsRes] = await Promise.all([
        classManagementAPI.getClassDetail(classId),
        classManagementAPI.getClassStudents(classId),
        classManagementAPI.getClassStatistics(classId)
      ]);
      
      setSelectedClass(detailRes.data);
      setClassStudents(studentsRes.data);
      setClassTeachers(detailRes.data.teachers || []);
      setClassStats(statsRes.data);
    } catch (error) {
      message.error('获取班级详情失败');
    }
  };

  const handleCreateClass = () => {
    setEditingClass(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEditClass = (record: Class) => {
    setEditingClass(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingClass) {
        await classManagementAPI.updateClass(editingClass.id, values);
        message.success('班级更新成功');
      } else {
        await classManagementAPI.createClass(values);
        message.success('班级创建成功');
      }
      setIsModalVisible(false);
      fetchClasses();
    } catch (error) {
      message.error(editingClass ? '更新失败' : '创建失败');
    }
  };

  const handleDeleteClass = async (id: number) => {
    try {
      await classManagementAPI.deleteClass(id);
      message.success('班级删除成功');
      fetchClasses();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleViewDetail = (record: Class) => {
    setSelectedClass(record);
    fetchClassDetail(record.id);
    setClassDetailVisible(true);
  };

  const handleAssignTeacher = (record: Class) => {
    setSelectedClass(record);
    assignForm.resetFields();
    setAssignTeacherVisible(true);
  };

  const handleSubmitAssignment = async (values: any) => {
    try {
      await classManagementAPI.assignTeacher(selectedClass!.id, values);
      message.success('教师分配成功');
      setAssignTeacherVisible(false);
      fetchClasses();
    } catch (error) {
      message.error('分配失败');
    }
  };

  const handleImportStudents = (record: Class) => {
    setSelectedClass(record);
    setImportStudentVisible(true);
  };

  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await classManagementAPI.importStudents(selectedClass!.id, formData);
      message.success('学生导入任务创建成功');
      setImportStudentVisible(false);
      // 可以显示导入进度
      return false; // 阻止默认上传行为
    } catch (error) {
      message.error('导入失败');
      return false;
    }
  };

  const columns: ColumnsType<Class> = [
    {
      title: '班级名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <strong>{text}</strong>
          <Tag color="blue">{record.grade_name}</Tag>
        </Space>
      )
    },
    {
      title: '班主任',
      key: 'class_teacher',
      render: (_, record) => record.class_teacher?.name || '-'
    },
    {
      title: '学生人数',
      key: 'student_count',
      render: (_, record) => (
        <Space>
          <span>{record.student_count}/{record.max_students}</span>
          <Progress
            percent={(record.student_count / record.max_students) * 100}
            size="small"
            style={{ width: 60 }}
          />
        </Space>
      )
    },
    {
      title: '学年',
      dataIndex: 'academic_year',
      key: 'academic_year'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => new Date(text).toLocaleDateString()
    },
    {
      title: '操作',
      key: 'actions',
      width: 300,
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          <Tooltip title="编辑班级">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEditClass(record)}
            />
          </Tooltip>
          <Tooltip title="分配教师">
            <Button
              type="link"
              icon={<UserAddOutlined />}
              onClick={() => handleAssignTeacher(record)}
            />
          </Tooltip>
          <Tooltip title="导入学生">
            <Button
              type="link"
              icon={<ImportOutlined />}
              onClick={() => handleImportStudents(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除这个班级吗？"
            onConfirm={() => handleDeleteClass(record.id)}
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            />
          </Popconfirm>
        </Space>
      )
    }
  ];

  const studentColumns: ColumnsType<Student> = [
    {
      title: '姓名',
      dataIndex: 'real_name',
      key: 'real_name'
    },
    {
      title: '学号',
      dataIndex: 'student_id_number',
      key: 'student_id_number'
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username'
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email'
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone'
    },
    {
      title: '入班日期',
      dataIndex: 'join_date',
      key: 'join_date'
    },
    {
      title: '学习风格',
      dataIndex: 'learning_style',
      key: 'learning_style',
      render: (style) => style ? <Tag>{style}</Tag> : '-'
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      render: (time) => time ? new Date(time).toLocaleString() : '-'
    }
  ];

  return (
    <div className="class-management">
      <Card
        title="班级管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateClass}
          >
            创建班级
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={classes}
          loading={loading}
          rowKey="id"
          pagination={{
            ...pagination,
            onChange: (page, pageSize) => {
              setPagination(prev => ({
                ...prev,
                current: page,
                pageSize: pageSize || 10
              }));
            }
          }}
        />
      </Card>

      {/* 创建/编辑班级对话框 */}
      <Modal
        title={editingClass ? '编辑班级' : '创建班级'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="assignment_type"
            label="分配类型"
            rules={[{ required: true, message: '请选择分配类型' }]}
          >
            <Select placeholder="请选择分配类型">
              <Option value="class_teacher">班主任</Option>
              <Option value="subject_teacher">科任教师</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                分配
              </Button>
              <Button onClick={() => setAssignTeacherVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 导入学生对话框 */}
      <Modal
        title="批量导入学生"
        open={importStudentVisible}
        onCancel={() => setImportStudentVisible(false)}
        footer={null}
      >
        <div>
          <p>请选择Excel文件进行批量导入：</p>
          <Upload
            beforeUpload={handleFileUpload}
            accept=".xlsx,.xls"
            showUploadList={false}
          >
            <Button icon={<ImportOutlined />}>选择文件</Button>
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
                // 下载模板文件
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

      {/* 班级详情抽屉 */}
      <Drawer
        title={`${selectedClass?.name} - 班级详情`}
        placement="right"
        onClose={() => setClassDetailVisible(false)}
        open={classDetailVisible}
        width={800}
      >
        {selectedClass && (
          <Tabs defaultActiveKey="overview">
            <TabPane tab="概览" key="overview">
              <Card title="基本信息" style={{ marginBottom: 16 }}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <strong>班级名称：</strong>{selectedClass.name}
                  </div>
                  <div>
                    <strong>年级：</strong>{selectedClass.grade_name}
                  </div>
                  <div>
                    <strong>学年：</strong>{classStats.class_info?.academic_year}
                  </div>
                  <div>
                    <strong>学生人数：</strong>{classStats.statistics?.student_count}/{classStats.class_info?.max_students}
                  </div>
                  <div>
                    <strong>平均分：</strong>{classStats.statistics?.avg_score?.toFixed(2) || 0}
                  </div>
                  <div>
                    <strong>出勤率：</strong>{classStats.statistics?.attendance_rate?.toFixed(1) || 100}%
                  </div>
                </div>
              </Card>

              <Card title="统计数据" style={{ marginBottom: 16 }}>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {classStats.statistics?.homework_count || 0}
                    </div>
                    <div>作业数量</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {classStats.statistics?.exam_count || 0}
                    </div>
                    <div>考试数量</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {classStats.statistics?.student_count || 0}
                    </div>
                    <div>学生人数</div>
                  </div>
                </div>
              </Card>

              <Card title="最近活动">
                <Tabs size="small">
                  <TabPane tab="最近作业" key="homework">
                    {classStats.recent_activities?.homeworks?.map((homework: any) => (
                      <div key={homework.id} className="border-b py-2">
                        <div className="font-medium">{homework.title}</div>
                        <div className="text-sm text-gray-500">
                          {new Date(homework.created_at).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </TabPane>
                  <TabPane tab="最近考试" key="exam">
                    {classStats.recent_activities?.exams?.map((exam: any) => (
                      <div key={exam.id} className="border-b py-2">
                        <div className="font-medium">{exam.title}</div>
                        <div className="text-sm text-gray-500">
                          {new Date(exam.created_at).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </TabPane>
                </Tabs>
              </Card>
            </TabPane>

            <TabPane tab="教师" key="teachers">
              <Card
                title="任课教师"
                extra={
                  <Button 
                    type="primary" 
                    size="small"
                    onClick={() => handleAssignTeacher(selectedClass)}
                  >
                    添加教师
                  </Button>
                }
              >
                {classTeachers.map((teacher, index) => (
                  <div key={index} className="border-b py-3 flex justify-between items-center">
                    <div>
                      <div className="font-medium">{teacher.name}</div>
                      <div className="text-sm text-gray-500">
                        {teacher.subject_name} - {teacher.assignment_type === 'class_teacher' ? '班主任' : '科任教师'}
                      </div>
                    </div>
                    <Tag color={teacher.assignment_type === 'class_teacher' ? 'red' : 'blue'}>
                      {teacher.assignment_type === 'class_teacher' ? '班主任' : '科任教师'}
                    </Tag>
                  </div>
                ))}
              </Card>
            </TabPane>

            <TabPane tab="学生" key="students">
              <Card
                title="学生列表"
                extra={
                  <Space>
                    <Button 
                      size="small"
                      icon={<ImportOutlined />}
                      onClick={() => handleImportStudents(selectedClass)}
                    >
                      批量导入
                    </Button>
                    <Button 
                      size="small"
                      icon={<ExportOutlined />}
                      onClick={async () => {
                        try {
                          const response = await classManagementAPI.exportStudents(selectedClass.id);
                          // 处理文件下载
                          const url = window.URL.createObjectURL(new Blob([response.data]));
                          const link = document.createElement('a');
                          link.href = url;
                          link.download = `${selectedClass.name}_学生名单.xlsx`;
                          link.click();
                        } catch (error) {
                          message.error('导出失败');
                        }
                      }}
                    >
                      导出名单
                    </Button>
                  </Space>
                }
              >
                <Table
                  columns={studentColumns}
                  dataSource={classStudents}
                  rowKey="student_id"
                  size="small"
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: false
                  }}
                />
              </Card>
            </TabPane>
          </Tabs>
        )}
      </Drawer>
    </div>
  );
};

export default ClassManagement;
            name="name"
            label="班级名称"
            rules={[{ required: true, message: '请输入班级名称' }]}
          >
            <Input placeholder="如：三年级1班" />
          </Form.Item>
          <Form.Item
            name="grade_name"
            label="年级名称"
            rules={[{ required: true, message: '请输入年级名称' }]}
          >
            <Input placeholder="如：三年级" />
          </Form.Item>
          <Form.Item
            name="study_level_id"
            label="学段"
            rules={[{ required: true, message: '请选择学段' }]}
          >
            <Select placeholder="请选择学段">
              {studyLevels.map((level: any) => (
                <Option key={level.id} value={level.id}>
                  {level.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="academic_year"
            label="学年"
            initialValue="2023-2024"
          >
            <Input placeholder="如：2023-2024" />
          </Form.Item>
          <Form.Item
            name="semester"
            label="学期"
            initialValue="上学期"
          >
            <Select>
              <Option value="上学期">上学期</Option>
              <Option value="下学期">下学期</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="max_students"
            label="最大学生数"
            initialValue={50}
          >
            <Input type="number" min={1} max={100} />
          </Form.Item>
          <Form.Item
            name="class_motto"
            label="班级口号"
          >
            <Input placeholder="班级口号或目标" />
          </Form.Item>
          <Form.Item
            name="class_rules"
            label="班级规则"
          >
            <TextArea rows={4} placeholder="班级规章制度" />
          </Form.Item>
          <Form.Item
            name="description"
            label="班级描述"
          >
            <TextArea rows={3} placeholder="班级详细描述" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingClass ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setIsModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 分配教师对话框 */}
      <Modal
        title="分配教师"
        open={assignTeacherVisible}
        onCancel={() => setAssignTeacherVisible(false)}
        footer={null}
      >
        <Form
          form={assignForm}
          layout="vertical"
          onFinish={handleSubmitAssignment}
        >
          <Form.Item
            name="teacher_id"
            label="选择教师"
            rules={[{ required: true, message: '请选择教师' }]}
          >
            <Select placeholder="请选择教师">
              {teachers.map((teacher: any) => (
                <Option key={teacher.id} value={teacher.id}>
                  {teacher.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="subject_id"
            label="任教学科"
            rules={[{ required: true, message: '请选择学科' }]}
          >
            <Select placeholder="请选择学科">
              {subjects.map((subject: any) => (
                <Option key={subject.id} value={subject.id}>
                  {subject.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item