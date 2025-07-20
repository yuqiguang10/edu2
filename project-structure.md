# K12智能教育平台 - 完整项目结构

## 项目根目录结构

```
k12-edu-platform/
├── frontend/                          # 前端项目
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── api/                       # API接口层
│   │   │   ├── modules/               # 模块化API
│   │   │   │   ├── auth.ts
│   │   │   │   ├── user.ts
│   │   │   │   ├── exam.ts
│   │   │   │   ├── homework.ts
│   │   │   │   ├── question.ts
│   │   │   │   ├── ai.ts
│   │   │   │   └── analytics.ts
│   │   │   ├── request.ts             # Axios封装
│   │   │   └── types.ts               # API类型定义
│   │   ├── assets/                    # 静态资源
│   │   │   ├── images/
│   │   │   ├── icons/
│   │   │   └── styles/
│   │   ├── components/                # 公共组件
│   │   │   ├── common/                # 通用组件
│   │   │   │   ├── Button/
│   │   │   │   ├── Input/
│   │   │   │   ├── Modal/
│   │   │   │   ├── Table/
│   │   │   │   ├── Chart/
│   │   │   │   └── Loading/
│   │   │   ├── business/              # 业务组件
│   │   │   │   ├── QuestionCard/
│   │   │   │   ├── ExamCard/
│   │   │   │   ├── StudentCard/
│   │   │   │   ├── AIChat/
│   │   │   │   └── ProgressChart/
│   │   │   └── layout/                # 布局组件
│   │   │       ├── Header/
│   │   │       ├── Sidebar/
│   │   │       ├── Footer/
│   │   │       └── MainLayout/
│   │   ├── hooks/                     # 自定义Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useApi.ts
│   │   │   ├── useAI.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useLocalStorage.ts
│   │   ├── pages/                     # 页面组件
│   │   │   ├── auth/                  # 认证页面
│   │   │   │   ├── Login/
│   │   │   │   ├── Register/
│   │   │   │   └── ForgotPassword/
│   │   │   ├── student/               # 学生端页面
│   │   │   │   ├── Dashboard/
│   │   │   │   ├── Courses/
│   │   │   │   ├── Homework/
│   │   │   │   ├── Exams/
│   │   │   │   ├── Progress/
│   │   │   │   ├── Mistakes/
│   │   │   │   └── Resources/
│   │   │   ├── teacher/               # 教师端页面
│   │   │   │   ├── Dashboard/
│   │   │   │   ├── Classes/
│   │   │   │   ├── Homework/
│   │   │   │   ├── Exams/
│   │   │   │   ├── Analytics/
│   │   │   │   ├── Resources/
│   │   │   │   └── AIAssistant/
│   │   │   ├── parent/                # 家长端页面
│   │   │   │   ├── Dashboard/
│   │   │   │   ├── ChildProgress/
│   │   │   │   ├── Communication/
│   │   │   │   ├── Schedule/
│   │   │   │   └── Reports/
│   │   │   └── admin/                 # 管理端页面
│   │   │       ├── Dashboard/
│   │   │       ├── Users/
│   │   │       ├── System/
│   │   │       ├── Analytics/
│   │   │       └── Resources/
│   │   ├── router/                    # 路由配置
│   │   │   ├── modules/               # 模块化路由
│   │   │   │   ├── studentRoutes.ts
│   │   │   │   ├── teacherRoutes.ts
│   │   │   │   ├── parentRoutes.ts
│   │   │   │   └── adminRoutes.ts
│   │   │   ├── guards.ts              # 路由守卫
│   │   │   └── index.ts
│   │   ├── store/                     # 状态管理
│   │   │   ├── modules/               # 模块化Store
│   │   │   │   ├── auth.ts
│   │   │   │   ├── user.ts
│   │   │   │   ├── exam.ts
│   │   │   │   ├── homework.ts
│   │   │   │   ├── ai.ts
│   │   │   │   └── app.ts
│   │   │   ├── types.ts               # Store类型定义
│   │   │   └── index.ts
│   │   ├── styles/                    # 全局样式
│   │   │   ├── globals.css
│   │   │   ├── variables.css
│   │   │   ├── components.css
│   │   │   └── themes/
│   │   ├── utils/                     # 工具函数
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── storage.ts
│   │   │   ├── validation.ts
│   │   │   ├── formatters.ts
│   │   │   └── constants.ts
│   │   ├── types/                     # TypeScript类型定义
│   │   │   ├── api.ts
│   │   │   ├── user.ts
│   │   │   ├── exam.ts
│   │   │   ├── homework.ts
│   │   │   └── common.ts
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── vite-env.d.ts
│   ├── tests/                         # 测试文件
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── utils/
│   ├── .env.development               # 开发环境配置
│   ├── .env.production                # 生产环境配置
│   ├── .gitignore
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json                  # TypeScript配置
│   ├── vite.config.ts                 # Vite配置
│   └── README.md
├── backend/                           # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI应用入口
│   │   ├── api/                       # API路由层
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # 依赖注入
│   │   │   └── v1/                    # API版本v1
│   │   │       ├── __init__.py
│   │   │       ├── api.py             # 路由聚合
│   │   │       └── endpoints/         # API端点
│   │   │           ├── __init__.py
│   │   │           ├── auth.py        # 认证相关API
│   │   │           ├── users.py       # 用户管理API
│   │   │           ├── students.py    # 学生相关API
│   │   │           ├── teachers.py    # 教师相关API
│   │   │           ├── classes.py     # 班级管理API
│   │   │           ├── courses.py     # 课程管理API
│   │   │           ├── exams.py       # 考试相关API
│   │   │           ├── homeworks.py   # 作业相关API
│   │   │           ├── questions.py   # 题库管理API
│   │   │           ├── resources.py   # 资源管理API
│   │   │           ├── analytics.py   # 数据分析API
│   │   │           ├── ai_agent.py    # AI助手API
│   │   │           └── admin.py       # 管理相关API
│   │   ├── core/                      # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # 配置管理
│   │   │   ├── security.py            # 安全相关
│   │   │   ├── logging.py             # 日志配置
│   │   │   └── database.py            # 数据库配置
│   │   ├── models/                    # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 基础模型
│   │   │   ├── user.py                # 用户模型
│   │   │   ├── education.py           # 教育组织模型
│   │   │   ├── content.py             # 内容资源模型
│   │   │   ├── exam.py                # 考试模型
│   │   │   ├── homework.py            # 作业模型
│   │   │   ├── question.py            # 题库模型
│   │   │   ├── analytics.py           # 分析模型
│   │   │   └── system.py              # 系统配置模型
│   │   ├── schemas/                   # Pydantic模型
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # 认证相关Schema
│   │   │   ├── user.py                # 用户相关Schema
│   │   │   ├── exam.py                # 考试相关Schema
│   │   │   ├── homework.py            # 作业相关Schema
│   │   │   ├── question.py            # 题库相关Schema
│   │   │   ├── analytics.py           # 分析相关Schema
│   │   │   └── common.py              # 通用Schema
│   │   ├── services/                  # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py        # 认证服务
│   │   │   ├── user_service.py        # 用户服务
│   │   │   ├── exam_service.py        # 考试服务
│   │   │   ├── homework_service.py    # 作业服务
│   │   │   ├── question_service.py    # 题库服务
│   │   │   ├── ai_service.py          # AI服务
│   │   │   ├── analytics_service.py   # 分析服务
│   │   │   ├── notification_service.py # 通知服务
│   │   │   └── file_service.py        # 文件服务
│   │   ├── repository/                # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 基础仓储
│   │   │   ├── user_repo.py           # 用户仓储
│   │   │   ├── exam_repo.py           # 考试仓储
│   │   │   ├── homework_repo.py       # 作业仓储
│   │   │   ├── question_repo.py       # 题库仓储
│   │   │   └── analytics_repo.py      # 分析仓储
│   │   ├── db/                        # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 数据库基类
│   │   │   ├── session.py             # 会话管理
│   │   │   └── init_db.py             # 初始化脚本
│   │   ├── middleware/                # 中间件
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # 认证中间件
│   │   │   ├── cors.py                # CORS中间件
│   │   │   ├── logging.py             # 日志中间件
│   │   │   └── rate_limit.py          # 限流中间件
│   │   ├── utils/                     # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── cache.py               # 缓存工具
│   │   │   ├── validators.py          # 验证器
│   │   │   ├── helpers.py             # 辅助函数
│   │   │   ├── encryption.py          # 加密工具
│   │   │   └── file_utils.py          # 文件工具
│   │   ├── ai/                        # AI模块
│   │   │   ├── __init__.py
│   │   │   ├── agents/                # AI代理
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_agent.py      # 基础代理
│   │   │   │   ├── student_agent.py   # 学生代理
│   │   │   │   ├── teacher_agent.py   # 教师代理
│   │   │   │   ├── parent_agent.py    # 家长代理
│   │   │   │   └── admin_agent.py     # 管理代理
│   │   │   ├── models/                # AI模型
│   │   │   │   ├── __init__.py
│   │   │   │   ├── recommendation.py  # 推荐模型
│   │   │   │   ├── analysis.py        # 分析模型
│   │   │   │   └── generation.py      # 生成模型
│   │   │   ├── knowledge/             # 知识库
│   │   │   │   ├── __init__.py
│   │   │   │   ├── knowledge_base.py  # 知识库基类
│   │   │   │   ├── subject_knowledge.py # 学科知识
│   │   │   │   └── pedagogy_knowledge.py # 教学法知识
│   │   │   └── engines/               # AI引擎
│   │   │       ├── __init__.py
│   │   │       ├── llm_client.py      # LLM客户端
│   │   │       ├── recommendation_engine.py # 推荐引擎
│   │   │       └── analysis_engine.py # 分析引擎
│   │   ├── tasks/                     # 异步任务
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py          # Celery配置
│   │   │   ├── crawl_tasks.py         # 爬虫任务
│   │   │   ├── ai_tasks.py            # AI任务
│   │   │   ├── email_tasks.py         # 邮件任务
│   │   │   └── analysis_tasks.py      # 分析任务
│   │   └── tests/                     # 测试代码
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_api/
│   │       ├── test_services/
│   │       └── test_utils/
│   ├── alembic/                       # 数据库迁移
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── alembic.ini
│   ├── scripts/                       # 脚本工具
│   │   ├── init_data.py               # 初始化数据
│   │   ├── backup.sh                  # 备份脚本
│   │   └── deploy.sh                  # 部署脚本
│   ├── requirements/                  # 依赖文件
│   │   ├── base.txt                   # 基础依赖
│   │   ├── development.txt            # 开发依赖
│   │   ├── production.txt             # 生产依赖
│   │   └── testing.txt                # 测试依赖
│   ├── .env.example                   # 环境变量示例
│   ├── .gitignore
│   ├── Dockerfile                     # Docker镜像
│   ├── docker-compose.yml             # Docker编排
│   ├── pyproject.toml                 # Python项目配置
│   └── README.md
├── docs/                              # 项目文档
│   ├── api/                           # API文档
│   ├── deployment/                    # 部署文档
│   ├── development/                   # 开发文档
│   └── user_guide/                    # 用户指南
├── docker/                            # Docker配置
│   ├── nginx/
│   │   └── nginx.conf
│   ├── mysql/
│   │   └── init.sql
│   └── redis/
│       └── redis.conf
├── scripts/                           # 项目脚本
│   ├── install.sh                     # 安装脚本
│   ├── start.sh                       # 启动脚本
│   ├── stop.sh                        # 停止脚本
│   └── backup.sh                      # 备份脚本
├── .gitignore
├── .env.example                       # 环境变量示例
├── docker-compose.yml                 # 完整服务编排
├── Makefile                           # 项目命令
└── README.md                          # 项目说明

```

## 技术栈说明

### 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **状态管理**: Zustand/Redux Toolkit
- **路由**: React Router v6
- **UI组件**: Tailwind CSS + Headless UI
- **图表**: Recharts/Chart.js
- **HTTP客户端**: Axios
- **实时通信**: Socket.io
- **测试**: Vitest + React Testing Library

### 后端技术栈
- **框架**: FastAPI
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **缓存**: Redis
- **搜索**: Elasticsearch
- **消息队列**: RabbitMQ + Celery
- **对象存储**: MinIO
- **监控**: Prometheus + Grafana
- **文档**: OpenAPI/Swagger

### AI技术栈
- **LLM**: OpenAI GPT-4/Claude
- **向量数据库**: Chroma/Pinecone
- **机器学习**: scikit-learn
- **自然语言处理**: spaCy
- **推荐系统**: Surprise/LightFM

### 部署技术栈
- **容器化**: Docker + Docker Compose
- **编排**: Kubernetes (可选)
- **Web服务器**: Nginx
- **CI/CD**: GitHub Actions
- **监控**: ELK Stack
- **备份**: 自动化脚本

## 下一步计划

1. **第二步**: 初始化前端项目和基础配置
2. **第三步**: 实现用户认证系统
3. **第四步**: 构建核心业务组件
4. **第五步**: 实现AI Agent功能
5. **第六步**: 后端API开发
6. **第七步**: 数据库设计和实现
7. **第八步**: 部署和监控

您希望我继续进行哪一步？