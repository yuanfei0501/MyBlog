# MyBlog - 博客系统

一个现代化的博客系统，支持前后端分离架构、Docker 一建部署。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | FastAPI + SQLAlchemy 2.0 (数据库 | PostgreSQL |
| 缓存 | Redis |
| 容器化 | Docker + Docker Compose |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yuanfei/MyBlog.git
cd MyBlog
```

### 2. 创建环境配置

```bash
cp .env.example .env
```

### 3. 启动服务

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up

# 生产环境
docker-compose up -d
```

访问：
- 博客前台: http://localhost
5173
- API 文档: http://localhost:8000/docs
- 后台管理: http://localhost:5173/admin

## 项目结构

```
myblog/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   └── main.py            # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── views/
│   │   │   ├── blog/          # 博客前台
│   │   │   └── admin/         # 后台管理
│   │   ├── components/
│   │   ├── stores/
│   │   ├── api/
│   │   ├── router/
│   │   └── assets/
│   ├── package.json
│   └── Dockerfile
│
├── nginx/                     # Nginx 配置
│   └── nginx.conf
│
├── docker-compose.yml        # 生产环境编排
├── docker-compose.dev.yml    # 开发环境编排
└── README.md
```

## 功能特性

- 用户系统：注册/登录、角色权限、个人资料管理
- 文章管理：Markdown 编辑、分类标签、草稿/发布、访问统计
- 评论系统：评论发布/回复、审核
- 媒体管理：图片上传、媒体库
- SEO 优化：Sitemap、RSS 订阅
- 深色模式：自动跟随系统/手动切换
- 响应式设计：完美适配移动端

- 后台管理：数据仪表盘、内容管理、用户管理

## API 文档

启动服务后访问 `/docs` 查看完整的 API 文档。

## 开发指南

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 本地开发

1. 安装依赖：
```bash
cd backend
pip install -r requirements.txt

cd frontend
npm install
```

2. 配置环境变量：
```bash
cp .env.example .env
```

3. 启动数据库：
```bash
docker-compose -f docker-compose.dev.yml up -d
```

4. 初始化数据库：
```bash
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
```

5. 访问应用：
- 后端: http://localhost:8000
- 前端: http://localhost:5173

### 生产部署

1. 一键启动：
```bash
docker-compose up -d
```

2. 访问博客
- 嚂址: http://localhost (你的域名)
- 后台: http://localhost/admin

3. 创建管理员账号
首次启动会访问后 API 注册接口创建管理员账号

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|---------------|
| `DATABASE_URL` | 数据库连接字符串 | `postgresql+asyncpg://blog:blog123@db:5432/blog` |
| `REDIS_URL` | Redis 连接字符串 | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT 密钥 | *必须修改* |
| `DEBUG` | 调试模式 | `true` |
| `CORS_ORIGINS` | 允许的前端地址 | `["http://localhost:5173", "http://localhost:3000"]` |

### 数据库配置

默认使用 PostgreSQL 15， 连接信息：
- 主机: `db:5432`
- 数据库名: `blog`
- 用户名: `blog`
- 密码: `blog123`

## 技术亮点

- 现代化技术栈：Vue 3 + FastAPI + PostgreSQL
- 完整的权限系统：JWT 认证 + 角色权限
- 精美的 UI 设计：Tailwind CSS + 深色模式
- Docker 化部署：一键启动
- 完善的 API 文档：Swagger/OpenAPI

- Markdown 支持：实时预览
- 代码高亮

## 默认账号

- 用户名: `admin`
- 邮箱: `admin@blog.com`
- 密码: `admin123456`

> ⚠️ **请立即修改默认密码！**

## License

MIT License

## 跔与 Star

欢迎 Star！

---

Made with ❤️ by [Your Name](https://github.com/yourname)
