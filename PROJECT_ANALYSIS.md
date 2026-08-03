# PROJECT_ANALYSIS.md

## 1. 项目现状概览

项目当前处于「工程骨架 + 演示前端」阶段：

- 后端：Django 6.0.7 + django-simpleui，SQLite 数据库，中文后台
- 前端：Vue 3.5 + Vite 6.4 + lucide-vue-next，纯静态演示页面
- 前后端尚未通过 API 真正联通
- 尚无任何业务模型、业务接口或业务数据

### 当前运行状态

- Vite 前端：`http://127.0.0.1:5173`，运行中，`GET /` 返回 200
- Django 后端：`http://127.0.0.1:8008`，当前有两个本项目 Django 进程同时监听
- 当前 `GET /admin/login/` 返回 SimpleUI 中文登录页（200）
- 当前 `GET /` 返回 Django 默认欢迎页（200），与代码中「302 跳转到 Vue」不一致

8008 端口存在重复监听进程，其中一个进程启动时间早于 `urls.py` 的跳转修改（22:17 启动，代码 22:23 修改），因此实际响应与当前代码不一致。这是此前后台界面「旧配置残留」问题的直接根因之一。

## 2. 当前已有功能

### 后端

- Django 6.0.7 项目骨架：`video_platform/`
- 应用骨架：`videos/`
- SimpleUI 后台主题，`LANGUAGE_CODE = 'zh-hans'`，`TIME_ZONE = 'Asia/Shanghai'`
- 超级管理员 `idste` 已创建
- 系统迁移已执行：admin、auth、contenttypes、sessions 共 18 个迁移
- 根路径代码配置为 302 跳转到 Vue 前端（尚未被运行中的旧进程正确加载）
- pip 已配置清华镜像

### 前端

- Vue 3 + Vite 6 项目：`frontend/`
- 首页演示：顶部导航、搜索框、直播/点播/热门/排行榜切换、精选内容区、视频卡片网格、热榜侧栏、管理后台入口
- 页面数据为本地 mock 数据，无真实接口调用
- Vite 已配置 `/api`、`/admin` 代理到 Django 8008

## 3. 缺少功能

### 后端

- 无业务模型：用户资料、教室、课程、直播、点播视频、分类、标签、评论、收藏、观看记录均为空
- 无 REST API：无序列化、无分页、无搜索、无鉴权接口
- 无媒体能力：上传、封面、转码、切片、播放地址均未实现
- 无直播能力：推流、拉流、在线状态、聊天、WebSocket 均未实现
- 无角色权限体系：教师、学生、管理员角色未建模
- 无通知、统计、报表模块
- 无生产配置：`DEBUG=True`、`SECRET_KEY` 明文、无 `.env`、无 CORS、无日志配置
- 无测试：`videos/tests.py` 为空

### 前端

- 无路由（vue-router）、无状态管理（Pinia）
- 无 HTTP 客户端封装、无环境变量配置
- 无登录注册、无角色路由守卫
- 无真实播放器（hls.js / video.js 等）
- 无视频详情页、直播观看页、个人中心、管理页面
- 无测试、无生产构建部署配置

### 工程化

- Git 仓库已存在，但尚无首次提交，全部文件处于未跟踪状态
- 无 CI/CD、无 Docker、无部署脚本
- 无统一的服务启停脚本，8008 出现重复 Django 监听进程
- 日志文件（`server.log`、`server-error.log`、`frontend/vite*.log`）已由 `.gitignore` 排除，但仍建议纳入统一日志管理

## 4. 数据库现状

数据库文件：`db.sqlite3`（SQLite）

已应用迁移：18 个

| 应用 | 迁移数 |
| --- | --- |
| admin | 3 |
| auth | 12 |
| contenttypes | 2 |
| sessions | 1 |
| videos | 0 |

当前表与数据：

| 表 | 行数 |
| --- | --- |
| auth_user | 1 |
| auth_permission | 24 |
| django_content_type | 6 |
| django_migrations | 18 |
| django_session | 2 |
| auth_group 等其余系统表 | 0 |

结论：

- 数据库中只有 Django 自带系统表，业务表数量为 0
- 唯一业务数据是超级管理员 `idste`
- SQLite 适合本地开发，生产环境需迁移到 PostgreSQL

## 5. 后端模块规划

建议按业务域拆分 Django 应用：

| 模块 | 职责 | 核心模型建议 |
| --- | --- | --- |
| accounts | 用户、角色、个人资料、认证 | User、Profile、Role |
| classrooms | 教室、班级、课程、排课 | Classroom、Course、Lesson |
| videos | 点播视频、分类、标签、上传、播放 | Video、Category、Tag、VideoFile |
| live | 直播场次、推流、拉流、状态 | LiveRoom、LiveSession、PushConfig |
| interactions | 评论、点赞、收藏、观看记录 | Comment、Favorite、WatchProgress |
| notifications | 站内通知 | Notification |
| stats | 观看统计、出勤、报表 | ViewStats、Attendance |
| api | API 聚合、权限、分页、文档 | DRF 路由与序列化 |

建议技术选型：

- Django REST Framework（API）
- djangorestframework-simplejwt（JWT 认证）
- Channels + Daphne（WebSocket，直播聊天、在线状态）
- Celery + Redis（异步转码、通知、统计）
- FFmpeg（转码、HLS 切片）
- MinIO / 对象存储（媒体文件）
- PostgreSQL（生产数据库）

## 6. 前端模块规划

基础层：

- vue-router：首页、直播、点播、详情、个人中心、登录注册
- Pinia：用户态、播放进度、观看历史、消息
- axios 封装：统一鉴权、错误处理、环境变量 API 地址

页面规划：

| 页面 | 核心内容 |
| --- | --- |
| 首页 | 直播大厅、点播推荐、热榜 |
| 点播列表 | 分类、标签、搜索、分页 |
| 视频详情 | 播放器、简介、评论、收藏、相关推荐 |
| 直播观看 | 播放器、聊天室、在线人数 |
| 教师开播 | 直播间配置、推流指引 |
| 个人中心 | 资料、观看记录、收藏、我的直播 |
| 管理后台 | 可继续使用 SimpleUI，或独立 Vue 管理端 |

播放技术建议：

- 点播：hls.js + video.js
- 直播初期：HLS；并发要求提高后再评估 WebRTC / SFU

## 7. 开发风险

### 高优先级

- 8008 端口重复 Django 进程：旧配置实例抢占请求，导致页面表现与代码不一致
- 直播流媒体复杂度：推拉流、转码、协议、带宽与延迟平衡
- 安全：视频防盗链、播放鉴权、上传文件校验、XSS/CSRF
- Django 6 较新，DRF、Channels、SimpleJWT 需先验证兼容版本

### 中优先级

- 无测试与无 CI，业务扩展后回归风险高
- 无生产配置：`DEBUG=True`、明文 `SECRET_KEY`、SQLite 不适合生产
- 媒体存储与异步任务未规划，点播上传后可能阻塞开发流程
- 前端无路由与状态管理，页面增多后会迅速失控

### 低优先级

- Git 尚无基线提交，协作与回滚困难
- 日志与进程管理依赖手动操作，容易产生残留进程
- 智慧教室需求边界较大，需要先明确 MVP 范围
