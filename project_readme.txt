# K12智能教育平台

<div align="center">
  <h1>🎓 K12智能教育平台</h1>
  <p>现代化的K12教育管理系统，集成AI技术，为学生、教师、家长和管理员提供全方位的教育服务</p>
  
  ![React](https://img.shields.io/badge/React-18.2.0-blue)
  ![TypeScript](https://img.shields.io/badge/TypeScript-5.2.0-blue)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
  ![Python](https://img.shields.io/badge/Python-3.11-green)
  ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
  ![License](https://img.shields.io/badge/License-MIT-yellow)
</div>

## 📚 目录

- [项目概述](#项目概述)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [API文档](#api文档)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🎯 项目概述

K12智能教育平台是一个基于现代Web技术栈构建的教育管理系统，旨在为K12阶段的教育机构提供全面的数字化解决方案。

### 🌟 项目特色

- **🤖 AI驱动**: 集成GPT等大语言模型，提供智能对话、个性化推荐和学习分析
- **👥 多角色支持**: 支持学生、教师、家长、管理员四种角色，满足不同用户需求
- **📊 数据分析**: 全面的学习行为分析和教学效果评估
- **🎨 现代化UI**: 基于Tailwind CSS的响应式设计，支持深色模式
- **🔒 安全可靠**: 完善的权限管理和数据安全保障
- **🚀 高性能**: 采用现代化架构，支持高并发访问

## 🎯 核心功能

### 学生端功能
- 📈 **个性化学习仪表盘**: 展示学习进度、成绩趋势、任务提醒
- 🤖 **AI学习助手**: 智能答疑、学习建议、知识点推荐
- 📝 **在线考试**: 支持多种题型的在线考试和自动判题
- 📚 **作业管理**: 作业提交、成绩查看、错题分析
- 🎯 **学习路径**: AI生成个性化学习路径和推荐资源
- 📖 **错题本**: 智能错题收集和复习提醒
- 📊 **学习分析**: 详细的学习数据分析和进步报告

### 教师端功能
- 👨‍🏫 **班级管理**: 学生信息管理、班级统计、考勤记录
- 📋 **作业布置**: 灵活的作业创建和发布系统
- 🧪 **考试组织**: 智能组卷、考试监控、成绩分析
- 📊 **学情分析**: 班级成绩分析、学生画像、教学建议
- 🤖 **AI教学助手**: 备课建议、资源推荐、差异化教学方案
- 📚 **资源库**: 教学资源共享和管理

### 家长端功能
- 👪 **孩子监督**: 实时了解孩子的学习状态和进度
- 📱 **家校沟通**: 与教师的即时沟通和信息交流
- 📈 **成长报告**: 孩子的学习报告和发展建议
- 🔔 **消息通知**: 重要通知和提醒推送
- 🤖 **AI家教助手**: 家庭教育建议和亲子沟通指导

### 管理员功能
- 🏫 **学校管理**: 组织架构、用户管理、权限配置
- 📊 **数据统计**: 全校数据分析和经营决策支持
- ⚙️ **系统配置**: 系统参数设置和功能开关
- 🔧 **运维监控**: 系统性能监控和异常告警
- 📋 **审计日志**: 完整的操作记录和安全审计

## 🛠 技术栈

### 前端技术
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **状态管理**: Zustand
- **路由**: React Router v6
- **UI组件**: Tailwind CSS + Headless UI
- **图表**: Recharts
- **HTTP客户端**: Axios
- **表单**: React Hook Form + Zod
- **通知**: React Hot Toast

### 后端技术
- **框架**: FastAPI
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **缓存**: Redis
- **搜索**: Elasticsearch
- **消息队列**: RabbitMQ + Celery
- **对象存储**: MinIO
- **监控**: Prometheus + Grafana

### AI技术
- **大语言模型**: OpenAI GPT-4 / Anthropic Claude
- **向量数据库**: Chroma
- **机器学习**: scikit-learn
- **推荐系统**: 协同过滤算法

### 部署技术
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx
- **CI/CD**: GitHub Actions
- **监控**: ELK Stack

## 🏗 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (React)   │    │   API网关       │    │   后端 (FastAPI) │
│                 │◄──►│   (Nginx)       │◄──►│                 │
│ - 学生端        │    │                 │    │ - RESTful API   │
│ - 教师端        │    │ - 负载均衡      │    │ - WebSocket     │
│ - 家长端        │    │ - SSL终结       │    │ - 认证授权      │
│ - 管理端        │    │ - 静态资源      │    │ - 业务逻辑      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                        ┌─────────────────────────────────┼─────────────────┐
                        │                                 │                 │
                 ┌─────────────┐                 ┌─────────────┐    ┌─────────────┐
                 │   MySQL     │                 │   Redis     │    │ Elasticsearch│
                 │             │                 │             │    │             │
                 │ - 主数据库  │                 │ - 缓存      │    │ - 全文搜索  │
                 │ - 事务处理  │                 │ - 会话存储  │    │ - 日志分析  │
                 └─────────────┘                 └─────────────┘    └─────────────┘
                                                        │
                                               ┌─────────────┐
                                               │   AI服务    │
                                               │             │
                                               │ - OpenAI    │
                                               │ - Claude    │
                                               │ - 推荐引擎  │
                                               └─────────────┘
```

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.11+
- MySQL 8.0+
- Redis 6.0+
- Docker & Docker Compose (推荐)

### 使用Docker快速部署

```bash
# 克隆项目
git clone https://github.com/your-org/k12-edu-platform.git
cd k12-edu-platform

# 配置环境变量
cp .env.example .env.production
# 编辑 .env.production 文件，配置数据库密码等

# 启动所有服务
make start

# 初始化数据库（仅首次部署）
make init-db
```

访问应用：
- 前端：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 本地开发环境

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements/development.txt

# 配置环境变量
cp .env.example .env

# 启动数据库（使用Docker）
docker-compose up -d mysql redis

# 初始化数据库
python -m app.db.init_db

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.development

# 启动开发服务器
npm run dev
```

## 💻 开发指南

### 项目结构

```
k12-edu-platform/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── api/                # API接口层
│   │   ├── components/         # 组件库
│   │   ├── pages/              # 页面组件
│   │   ├── hooks/              # 自定义Hooks
│   │   ├── store/              # 状态管理
│   │   ├── types/              # 类型定义
│   │   └── utils/              # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── backend/                     # 后端项目
│   ├── app/
│   │   ├── api/                # API路由
│   │   ├── core/               # 核心配置
│   │   ├── models/             # 数据模型
│   │   ├── services/           # 业务逻辑
│   │   ├── schemas/            # 数据验证
│   │   └── db/                 # 数据库相关
│   ├── requirements/           # 依赖文件
│   └── alembic/               # 数据库迁移
├── docker/                     # Docker配置
├── docs/                       # 项目文档
└── scripts/                    # 部署脚本
```

### 代码规范

#### 前端代码规范

```typescript
// 组件命名：PascalCase
const StudentDashboard: React.FC = () => {
  // Hook在组件顶部
  const [loading, setLoading] = useState(false);
  const { user } = useStore();
  
  // 事件处理函数：handle开头
  const handleSubmit = async () => {
    // 实现逻辑
  };
  
  // 条件渲染
  if (loading) {
    return <Loading />;
  }
  
  return (
    <div className="space-y-6">
      {/* 组件内容 */}
    </div>
  );
};
```

#### 后端代码规范

```python
# 路由命名：snake_case
@router.post("/create_exam", response_model=APIResponse[ExamResponse])
async def create_exam(
    exam_data: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """创建考试"""
    try:
        # 业务逻辑
        exam_service = ExamService(db)
        exam = exam_service.create_exam(exam_data, current_user.id)
        
        return APIResponse(
            data=ExamResponse.from_orm(exam),
            message="考试创建成功"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Git工作流

```bash
# 功能开发
git checkout -b feature/student-dashboard
git add .
git commit -m "feat: 实现学生仪表盘基础功能"
git push origin feature/student-dashboard

# 创建Pull Request进行代码审查
```

提交信息规范：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建工具等

## 🚀 部署指南

### 生产环境部署

#### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt install docker-compose-plugin

# 配置防火墙
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

#### 2. 部署应用

```bash
# 克隆代码
git clone https://github.com/your-org/k12-edu-platform.git
cd k12-edu-platform

# 配置生产环境变量
cp .env.example .env.production
# 编辑配置文件，设置强密码和API密钥

# 执行部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh --init-db
```

#### 3. SSL证书配置

```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

### 监控和维护

#### 日志查看

```bash
# 查看所有服务日志
make logs

# 查看特定服务日志
make logs-backend
make logs-frontend

# 实时监控
docker-compose logs -f
```

#### 备份策略

```bash
# 数据库备份
make backup-db

# 定期备份脚本
cat > /etc/cron.daily/k12-backup << 'EOF'
#!/bin/bash
cd /path/to/k12-edu-platform
make backup-db
# 上传到云存储
EOF
chmod +x /etc/cron.daily/k12-backup
```

#### 健康检查

```bash
# 服务状态检查
make health

# 性能监控
docker stats

# 资源使用情况
df -h
free -h
```

## 📖 API文档

### 认证接口

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "student001",
  "password": "password123"
}
```

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "student001",
      "real_name": "张三",
      "roles": ["student"]
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

### AI对话接口

```http
POST /api/v1/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "我的数学成绩怎么样？",
  "role": "student",
  "context": {
    "current_subject": "数学",
    "recent_scores": [85, 92, 78]
  }
}
```

```json
{
  "success": true,
  "data": {
    "content": "根据你最近的数学成绩...",
    "suggestions": [
      "查看错题分析",
      "制定学习计划",
      "推荐练习题"
    ],
    "resources": [
      {
        "title": "数学基础练习",
        "url": "/resources/math-basics"
      }
    ]
  }
}
```

### 完整API文档

部署后访问：`http://your-domain/docs`

## 🧪 测试

### 前端测试

```bash
cd frontend

# 运行单元测试
npm run test

# 运行测试覆盖率
npm run test:coverage

# 运行E2E测试
npm run test:e2e
```

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式

1. **提交Issue**: 报告bug、建议新功能
2. **提交PR**: 修复bug、实现新功能
3. **完善文档**: 改进文档和示例
4. **分享经验**: 撰写教程和最佳实践

### 贡献流程

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 开发规范

- 遵循代码规范和ESLint配置
- 为新功能添加测试用例
- 更新相关文档
- 保持提交信息清晰明确

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

## 🙏 致谢

感谢以下开源项目：

- [React](https://reactjs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架
- 以及所有其他依赖的优秀开源项目

## 📞 联系我们

- 📧 邮箱：support@k12edu.com
- 🌐 官网：https://k12edu.com
- 📱 微信群：扫描二维码加入开发者交流群

---

<div align="center">
  <p>⭐ 如果这个项目对你有帮助，请给我们一个星标！</p>
  <p>Made with ❤️ by K12 Education Team</p>
</div>