# 视频平台 (Video Platform)

一个功能完整的在线视频教育平台，支持视频点播、直播、名师工作室、教师空间等功能。

## 技术栈

### 后端
- **Django 6.0** - Python Web 框架
- **Django REST Framework** - REST API 框架
- **PostgreSQL 16** - 关系型数据库
- **Redis 7** - 缓存服务
- **SimpleUI** - Django Admin 美化

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite 6** - 下一代前端构建工具
- **TypeScript** - 类型安全
- **Element Plus** - Vue 3 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Video.js** - 视频播放器
- **Tailwind CSS** - 原子化 CSS 框架
- **Vue I18n** - 国际化

### 流媒体
- **Nginx-RTMP** - RTMP 流媒体服务器
- **FFmpeg** - 视频处理工具
- **HLS** - HTTP 直播流

### 部署
- **Docker** - 容器化
- **Docker Compose** - 多容器编排
- **Gunicorn** - Python WSGI HTTP 服务器

## 功能特性

### 🎬 视频点播
- 视频上传与管理
- 视频分类
- 视频专辑（系列课程）
- 视频时长自动探测
- 观看次数统计
- 封面图上传

### 📺 直播功能
- RTMP 推流支持
- HLS 播放
- 直播状态管理
- 个人直播间

### 👨‍🏫 名师工作室
- 教师名录
- 教师个人主页
- 教师专辑展示
- 搜索功能

### 💼 教师空间
- 我的视频管理
- 视频上传
- 专辑管理
- 直播管理
- 个人资料（头像、简介、科目）

### 💬 评论系统
- 视频评论
- 评论审核
- 评论管理

### 🌐 多语言支持
- 简体中文
- 繁体中文
- 英语
- 韩语
- 越南语
- 马来语
- 俄语

### 🔐 用户系统
- 多角色支持（管理员、学校管理员、教师、学生）
- Token 认证
- 权限管理

## 快速开始

### 环境要求
- Docker & Docker Compose
- 4GB+ 内存
- 10GB+ 磁盘空间

### 开发环境启动

1. **克隆项目**
```bash
git clone https://github.com/wangych0602/video.git
cd video
```

2. **配置环境变量**
```bash
cp .env.example .env
```

3. **启动所有服务**
```bash
docker compose up -d
```

4. **访问应用**
- 前端页面：http://localhost:5173
- Django Admin：http://localhost:8008/admin
- API 文档：http://localhost:8008/api/

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 教师 | Teacher | teacher123 |
| 教师 | teacher1 | teacher123 |

## 项目结构

```
.
├── docker/                    # Docker 配置
│   └── backend/
│       ├── Dockerfile         # 开发环境 Dockerfile
│       ├── Dockerfile.prod    # 生产环境 Dockerfile
│       └── entrypoint.sh      # 启动脚本
├── frontend/                  # Vue 前端项目
│   ├── src/
│   │   ├── api/               # API 接口
│   │   ├── components/        # 组件
│   │   ├── layouts/           # 布局
│   │   ├── views/             # 页面
│   │   ├── stores/            # 状态管理
│   │   ├── router/            # 路由
│   │   ├── utils/             # 工具函数
│   │   ├── locales/           # 国际化
│   │   └── assets/            # 静态资源
│   ├── vite.config.ts
│   └── package.json
├── nginx/                     # Nginx 配置
│   ├── nginx.conf             # RTMP 配置
│   └── prod-gateway.conf      # 生产环境网关
├── video_platform/            # Django 项目配置
│   ├── settings.py            # 开发配置
│   ├── settings_prod.py       # 生产配置
│   └── urls.py                # 主路由
├── users/                     # 用户模块
├── videos/                    # 视频模块
├── live/                      # 直播模块
├── devices/                   # 设备模块
├── schools/                   # 学校模块
├── reviews/                   # 评论模块
├── system/                    # 系统模块
├── templates/                 # 模板文件
├── media/                     # 媒体文件（运行时生成）
├── docker-compose.yml         # 开发环境 Compose
├── docker-compose.prod.yml    # 生产环境 Compose
├── requirements.txt           # Python 依赖
└── manage.py                  # Django 管理脚本
```

## 生产环境部署

### 1. 准备服务器
- Linux 服务器（推荐 Ubuntu 22.04+）
- 安装 Docker & Docker Compose
- 配置域名解析

### 2. 上传代码
```bash
git clone https://github.com/wangych0602/video.git
cd video
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，修改以下配置：
# - DEBUG=False
# - SECRET_KEY=你的随机密钥
# - ALLOWED_HOSTS=你的域名
# - 数据库密码
```

### 4. 启动生产环境
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 5. 创建管理员
```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## 服务端口

| 服务 | 开发环境端口 | 说明 |
|------|-------------|------|
| 前端 | 5173 | Vue 开发服务器 |
| 后端 API | 8008 | Django 开发服务器 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| RTMP | 1935 | 直播推流 |
| HLS | 8080 | HLS 播放 |

## API 接口

### 认证
- `POST /api/auth/login/` - 登录

### 用户
- `GET /api/users/` - 用户列表（管理员）
- `GET /api/teacher-profiles/me/` - 获取我的教师资料
- `PUT /api/teacher-profiles/me/` - 更新我的教师资料
- `GET /api/teachers/` - 教师名录

### 视频
- `GET /api/videos/` - 视频列表
- `GET /api/videos/{id}/` - 视频详情
- `POST /api/videos/` - 上传视频
- `PUT /api/videos/{id}/` - 更新视频
- `DELETE /api/videos/{id}/` - 删除视频

### 专辑
- `GET /api/video-albums/` - 专辑列表
- `GET /api/video-albums/{id}/` - 专辑详情
- `POST /api/video-albums/` - 创建专辑
- `PUT /api/video-albums/{id}/` - 更新专辑
- `DELETE /api/video-albums/{id}/` - 删除专辑

### 直播
- `GET /api/live/sessions/` - 直播列表
- `POST /api/live/personal/start/` - 开启个人直播
- `POST /api/live/personal/stop/` - 停止个人直播

### 评论
- `GET /api/reviews/` - 评论列表
- `POST /api/reviews/` - 发表评论

## 开发说明

### 热重载
- 前端：Vite 热重载（修改代码自动刷新）
- 后端：Django 开发服务器自动重载

### 数据库迁移
```bash
# 创建迁移
docker compose exec backend python manage.py makemigrations

# 执行迁移
docker compose exec backend python manage.py migrate
```

### 进入容器
```bash
# 后端容器
docker compose exec backend sh

# 数据库容器
docker compose exec postgres psql -U video -d video_platform
```

### 查看日志
```bash
# 所有服务
docker compose logs -f

# 单个服务
docker compose logs -f backend
docker compose logs -f frontend
```

## 注意事项

1. **媒体文件**：`media/` 目录存储上传的视频和图片，生产环境建议挂载持久化存储
2. **数据库备份**：定期备份 PostgreSQL 数据
3. **大文件**：GitHub 不支持 100MB 以上的文件，大视频文件不要提交到代码仓库
4. **安全**：生产环境务必修改默认密码和 SECRET_KEY
5. **HTTPS**：生产环境建议配置 HTTPS（可使用 Let'\''s Encrypt）

## License

MIT
