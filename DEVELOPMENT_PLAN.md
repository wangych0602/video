# DEVELOPMENT_PLAN.md

## 0. 目标

建设面向智慧教室场景的视频直播点播平台：

- 教师可创建教室、排课、开直播、上传点播视频
- 学生可观看直播与回放、参与聊天、记录学习进度
- 管理员可通过 SimpleUI 管理用户、内容、直播与统计
- 生产环境可安全部署、可扩展、可运维

## 1. 总体路线图

| 阶段 | 主题 | 周期 | 交付物 |
| --- | --- | --- | --- |
| Phase 0 | 工程化基础 | 第 1 周 | 干净基线、API 连通、前后端骨架 |
| Phase 1 | 用户与权限 | 第 2-3 周 | 登录注册、三角色、路由守卫 |
| Phase 2 | 点播核心 | 第 3-6 周 | 视频管理、上传、播放、进度 |
| Phase 3 | 直播核心 | 第 6-10 周 | 直播大厅、推拉流、聊天 |
| Phase 4 | 智慧教室场景 | 第 10-14 周 | 教室、课程、排课、统计闭环 |
| Phase 5 | 生产化 | 第 14 周起 | 部署、安全、测试、监控 |

## 2. Phase 0：工程化基础（第 1 周）

任务：

- 清理 8008 端口重复 Django 进程，建立统一启停脚本
- Git 首次提交，固定基线；明确分支规范
- 引入 `.env` 管理 `SECRET_KEY`、`DEBUG`、数据库配置
- 安装 Django REST Framework 并验证与 Django 6 的兼容性
- 新增 `/api/health/`，跑通「Vue -> 代理 -> Django API」链路
- 前端接入 vue-router、Pinia、axios 封装，搭建页面骨架
- 统一 API 响应格式、错误处理、日志

验收标准：

- `GET http://127.0.0.1:5173/api/health/` 返回 JSON
- 8008 端口只有一个 Django 进程
- 代码全部纳入 Git 首次提交

## 3. Phase 1：用户与权限（第 2-3 周）

任务：

- `accounts` 应用：User 扩展 Profile、角色（管理员/教师/学生）
- JWT 登录、注册、刷新、退出
- SimpleUI 用户管理：增删改查、角色分配
- 前端登录注册页、路由守卫、用户菜单

验收标准：

- 三种角色均可登录，并访问各自允许的页面
- 后端接口按角色做权限控制

## 4. Phase 2：点播核心（第 3-6 周）

任务：

- `videos` 应用模型：Video、Category、Tag、VideoFile
- 视频上传（本地或对象存储）、封面、转码状态机
- 播放地址 API、搜索、分类、分页
- 观看记录与进度、收藏
- 前端：点播列表、视频详情、hls.js 播放器、个人中心记录
- SimpleUI 后台：视频、分类、标签管理

验收标准：

- 学生可搜索并播放视频，断点续播进度可保存
- 教师可上传视频并看到转码状态

## 5. Phase 3：直播核心（第 6-10 周）

任务：

- `live` 应用模型：LiveRoom、LiveSession、PushConfig
- 推流密钥、拉流地址、直播状态切换
- Channels + Daphne：聊天室、在线人数、上下线事件
- 前端：直播大厅、直播观看页、聊天室、教师开播页
- 直播结束自动生成回放，归档到点播

验收标准：

- 教师可开播，学生可观看并发送聊天消息
- 直播中断与恢复状态可被感知
- 直播结束后回放可播放

## 6. Phase 4：智慧教室场景（第 10-14 周）

任务：

- `classrooms` 应用：Classroom、Course、Lesson、排课
- 课程与视频、直播绑定
- 学习数据：出勤、观看时长、互动统计
- 站内通知：开播提醒、作业/公告
- 教师端：教室管理、课程内容管理

验收标准：

- 完成「建教室 -> 排课 -> 直播/点播 -> 学习记录 -> 统计」闭环

## 7. Phase 5：生产化（第 14 周起）

任务：

- 迁移 PostgreSQL、Redis、Celery
- 媒体文件迁移到对象存储，接入 CDN
- HTTPS、CORS、播放鉴权、防盗链
- 测试补齐：后端 pytest、前端 Vitest、关键流程 E2E
- CI/CD、Docker Compose、日志与监控
- 性能优化：索引、缓存、直播并发压测

验收标准：

- 具备上线部署能力，关键路径有自动化测试

## 8. 里程碑

| 里程碑 | 定义 |
| --- | --- |
| M0 | 工程基线 + API 连通 |
| M1 | 角色权限可用 |
| M2 | 点播闭环可用 |
| M3 | 直播闭环可用 |
| M4 | 智慧教室闭环可用 |
| M5 | 生产上线 |

## 9. 推荐技术清单

后端：

- Django REST Framework、djangorestframework-simplejwt
- Channels、Daphne
- Celery、Redis
- FFmpeg、HLS
- MinIO / S3 兼容对象存储
- PostgreSQL
- drf-spectacular（OpenAPI 文档）

前端：

- vue-router、Pinia
- axios
- hls.js、video.js
- Vitest、Playwright

运维：

- Docker Compose
- Nginx
- Windows 下可用 NSSM / 计划任务管理常驻服务

## 10. 风险与对策

| 风险 | 对策 |
| --- | --- |
| 直播流媒体复杂度高 | 初期用 HLS 降低门槛，后续按需引入 WebRTC |
| Django 6 生态兼容性 | Phase 0 先做依赖兼容性验证 |
| 重复进程/环境混乱 | 统一启停脚本，端口与进程纳入文档 |
| 安全与防盗链 | 签名播放地址、临时 URL、上传校验 |
| 需求边界过大 | 以 M0-M4 里程碑锁定 MVP 范围 |

## 11. 下一步行动

1. 清理 8008 端口的两个 Django 残留进程，用新代码重启并验证 `/` 302 跳转
2. Git 首次提交，锁定当前基线
3. 安装 DRF，建立 `/api/health/` 并打通 Vue 代理
4. 创建 `accounts` 与 `videos` 业务模型并迁移
5. 前端引入 vue-router、Pinia、axios，替换 mock 数据
