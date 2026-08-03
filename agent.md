# 视频平台项目工作记录

## 2026-08-03 工作记录

### 一、问题修复

#### 1. 专辑封面预览图不显示
**问题原因**：
DRF 的 ImageField 会自动构建绝对 URL（包含域名和端口）。由于前端通过代理访问后端，后端看到的 host 是 Docker 内部服务名 `backend:8000`，所以返回的图片 URL 是 `http://backend:8000/media/...`，浏览器无法解析这个地址，导致图片不显示。

**修复方案**：
- Django 配置：添加 `USE_X_FORWARDED_HOST = True`
  - 文件：`video_platform/settings.py`
  - 让 Django 使用 X-Forwarded-Host 头获取真实的客户端地址
- Vite 代理配置：添加 `xfwd: true` 选项
  - 文件：`frontend/vite.config.ts`
  - 让代理自动设置 X-Forwarded-* 头，传递真实的客户端地址

**验证结果**：
- 修复前：`http://backend:8000/media/album_covers/xxx.png` ❌
- 修复后：`http://localhost:5173/media/album_covers/xxx.png` ✅

---

#### 2. 视频时长不显示
**问题原因**：
视频时长探测依赖两个工具，但 backend 容器中都没有：
1. mutagen：Python 视频元数据库（纯 Python，无外部依赖）- 未安装
2. ffprobe：ffmpeg 工具集的一部分 - 未安装

两种方法都不可用，导致 duration 字段为 null。

**修复方案**：
- 安装 mutagen 库到 backend 容器
- 将 `mutagen==1.48.1` 添加到 `requirements.txt`
- 给所有已有视频重新计算并保存时长

**验证结果**：
- 视频时长正确返回：`00:00:40.378050`
- 文件大小正确返回：`4657419` 字节

---

### 二、功能优化

#### 1. 首页专辑封面显示优化
**需求**：首页专辑的图片封面与教师空间里面的专辑封面一致

**修改内容**：
- 文件：`frontend/src/views/Home.vue`
- 有封面图时：直接显示真实封面图片，去掉默认的 BookOpen 图标和半透明遮罩
- 无封面图时：保留默认渐变背景和图标
- 背景图显示方式：从 `cover`（覆盖填充）改为 `contain`（完整显示）

---

#### 2. 首页布局调整
**需求**：首页最新课程和课程专辑默认最大显示两排，8个卡片位置

**修改内容**：
- 文件：`frontend/src/views/Home.vue`
- 最新课程：从 4 个（1 排）增加到 8 个（2 排）
- 课程专辑：从 4 个（1 排）增加到 8 个（2 排）
- 网格布局：从自适应改为固定 4 列
  - 修改前：`grid-template-columns: repeat(auto-fill, minmax(230px, 1fr))`
  - 修改后：`grid-template-columns: repeat(4, 1fr)`

---

#### 3. 名师工作室专辑封面显示
**需求**：名师工作室的课程专辑的封面需要显示上传对应的图片

**修改内容**：
- 文件：`frontend/src/views/TeacherStudio.vue`
- 添加封面图显示：有上传封面图时，显示真实的封面图片
- 保留默认样式：没有封面图时，仍然显示默认的渐变背景 + 书本图标
- 优化显示效果：
  - `background-size: cover` - 图片覆盖整个封面区域
  - `background-position: center` - 图片居中显示
  - `overflow: hidden` - 保持圆角效果

---

#### 4. 首页最新课程添加观看次数和发布时间
**需求**：首页最新课程的视频显示观看次数和发布时间

**修改内容**：
- 文件：`frontend/src/views/Home.vue`
- 新增观看次数显示：带眼睛图标，自动格式化（1w / 1k / 具体数字）
- 新增发布时间显示：智能格式化
  - 今天发布 → "今天"
  - 昨天发布 → "昨天"
  - 7天内 → "N天前"
  - 更早 → "YYYY-MM-DD" 格式
- 添加 `formatDate` 函数
- 添加 `.video-meta` 和 `.meta-item` 样式

---

#### 5. 首页排行只显示前5名
**需求**：首页热门排行和专辑排行，默认只显示前5名

**修改内容**：
- 文件：`frontend/src/views/Home.vue`
- 热门排行：从 10 个改为 5 个
- 专辑排行：从 10 个改为 5 个

---

#### 6. 教师空间操作按钮一排显示
**需求**：教师空间的操作，查看，编辑，删除需要摆在一排

**修改内容**：
- 文件：`frontend/src/views/TeacherSpace.vue`
- 视频操作列：宽度从 180px 增加到 220px
- 专辑操作列：宽度从 150px 增加到 180px
- 添加 `.action-btns` 样式，使用 flex 布局，确保按钮在同一行显示
- 添加 `.action-link` 样式，查看链接与按钮对齐

---

### 三、文件修改清单

| 文件 | 修改内容 |
|------|---------|
| `video_platform/settings.py` | 添加 USE_X_FORWARDED_HOST = True |
| `requirements.txt` | 添加 mutagen==1.48.1 |
| `frontend/vite.config.ts` | 代理添加 changeOrigin 和 xfwd 选项 |
| `frontend/src/views/Home.vue` | 首页布局、封面、排行、视频信息优化 |
| `frontend/src/views/TeacherStudio.vue` | 名师工作室专辑封面显示 |
| `frontend/src/views/TeacherSpace.vue` | 教师空间操作按钮布局 |

---

### 四、Docker 环境信息

#### 服务列表
| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| nginx-rtmp | video-nginx-rtmp | 1935, 8080 | 流媒体服务 |
| ffmpeg | video-ffmpeg | - | 视频处理工具 |
| redis | video-redis | 6379 | 缓存服务 |
| postgres | video-postgres | 5432 | 数据库 |
| backend | video-backend | 8008 | Django 后端 |
| frontend | video-frontend | 5173 | Vue 前端 |

#### 访问地址
- 前端页面：http://localhost:5173
- 后端 API：http://localhost:8008
- Django Admin：http://localhost:8008/admin
- PostgreSQL：localhost:5432（用户名: video / 密码: video123456）
- Redis：localhost:6379
- RTMP 流媒体：rtmp://localhost:1935
- HLS 流：http://localhost:8080

#### 默认账号
- 管理员：admin / admin123
- 教师：Teacher / teacher123
- 教师：teacher1 / teacher123

---

### 五、已知问题与注意事项

1. **Docker BuildKit 问题**：Windows 环境下 BuildKit 有权限问题，需要禁用（设置 DOCKER_BUILDKIT=0）
2. **镜像源问题**：国内网络需要配置 DaoCloud 镜像加速器
3. **换行符问题**：Windows 下创建的 shell 脚本需要转换为 LF 换行符
4. **Vite 热重载问题**：Docker 环境下 Vite 热重载可能不触发，需要重启容器或强制刷新浏览器
5. **CSRF 问题**：访问过 Django admin 后，前端登录会遇到 CSRF 问题，已通过设置 authentication_classes = [] 解决
6. **教师资料问题**：创建专辑需要用户有教师资料，管理员也需要，已添加自动创建逻辑
7. **媒体文件 URL 问题**：DRF 的 ImageField 会返回绝对 URL，需要配置 USE_X_FORWARDED_HOST 和代理 xfwd 选项
8. **视频时长问题**：需要 mutagen 库来探测视频时长，backend 容器默认没有安装，已添加到 requirements.txt

---

## Phase 10.6 - AI课堂分析前端系统（2026-08-03）

### 一、新增文件

**API 文件：**
- rontend/src/api/ai.ts - AI 分析 API 接口定义
  - 接口：getAITasks, getAITask, createAITask, getEvaluation, getScore, getReport, downloadReportPdf, getTranscript, getKeywords
  - 类型：AITask, TeachingEvaluation, AIReport, Transcript

**组件文件（components/ai/）：**
1. ScoreCard.vue - 评分卡片组件
   - 显示分数、等级、进度条
   - 颜色根据分数自动变化（优秀/良好/中等/及格/不及格）
   
2. RadarChart.vue - 雷达图组件
   - 使用 ECharts + vue-echarts
   - 五维评分可视化
   
3. ReportViewer.vue - 报告查看器组件
   - 课堂总结（时长、总分、等级、知识点）
   - 优势分析
   - 待改进
   - 改进建议
   - 知识点覆盖
   - PDF下载按钮
   
4. TranscriptViewer.vue - 文字稿查看器组件
   - 语音片段列表（教师/学生区分）
   - 关键词云
   - 语速统计
   - 时间戳显示

**页面文件（views/）：**
1. TeacherAI.vue - 教师 AI 分析页面
   - 课堂分析任务列表
   - 课堂评分卡片（overall_score）
   - 五维评价雷达图
   - AI优势分析
   - AI改进建议
   - 课堂文字稿查看
   - 完整报告查看（Tab切换）

2. AIAnalytics.vue - 学校管理 Dashboard 页面
   - 统计卡片（分析课堂数、参与教师数、平均评分、优秀课堂）
   - 教师评分排行（柱状图）
   - 课程质量趋势（折线图）
   - 五维教学能力对比（雷达图）
   - 优秀课堂列表

### 二、修改文件

1. rontend/src/router/index.ts - 添加路由配置
   - /teacher/ai - 教师AI分析页面（name: teacher-ai）
   - /admin/ai-analytics - AI分析总览页面（name: ai-analytics）

2. rontend/src/layouts/Layout.vue - 添加导航菜单项
   - 教师角色：添加 AI课堂分析 菜单（Cpu 图标）
   - 管理员/学校管理员角色：添加 AI分析总览 菜单（BarChart3 图标）

3. rontend/package.json - 添加依赖
   - echarts ^5.5.0
   - vue-echarts ^7.0.3

4. **7种语言翻译文件**（locales/）：
   - zh-CN.json（中文）
   - en-US.json（英文）
   - ko-KR.json（韩文）
   - vi-VN.json（越南语）
   - ru-RU.json（俄语）
   - ms-MY.json（马来语）
   - zh-TW.json（繁体中文）

### 三、页面功能

**TeacherAI.vue（教师端）：**
- 任务列表：展示教师所有的AI分析任务
- 评分展示：总体评分 + 五维评价雷达图
- 优势与建议：AI自动生成的教学优势和改进建议
- 完整报告：课堂总结、优势分析、待改进、改进建议、知识点覆盖
- 文字稿：课堂语音转文字结果，支持关键词云
- PDF下载：支持下载完整的PDF分析报告

**AIAnalytics.vue（学校管理端）：**
- 数据概览：分析课堂数、参与教师数、平均评分、优秀课堂数
- 教师排行：教师评分排行榜（柱状图）
- 质量趋势：课程质量变化趋势（折线图）
- 能力对比：五维教学能力对比（雷达图）
- 优秀课堂：优秀课堂列表

### 四、权限控制

- **教师角色**：只能查看自己的课堂分析（/teacher/ai）
- **管理员/学校管理员角色**：可以查看学校全部数据（/admin/ai-analytics）

### 五、技术栈

- Vue 3 + TypeScript
- Element Plus UI 组件库
- ECharts + vue-echarts（图表）
- vue-i18n（多语言）
- Pinia（状态管理）
- Vue Router（路由）

### 六、已修复的问题

1. **ai.ts 模板字符串语法错误**
   - 问题：反引号被 PowerShell 解析错误，导致模板字符串变成正则表达式
   - 修复：改用字符串拼接方式

2. **ScoreCard.vue 模板字符串语法错误**
   - 问题：linear-gradient 中的模板字符串解析错误
   - 修复：改用字符串拼接方式

3. **TranscriptViewer.vue 模板字符串语法错误**
   - 问题：formatTime 和 formatDuration 函数中的模板字符串解析错误
   - 修复：改用字符串拼接方式

4. **ReportViewer.vue Bulb 图标不存在**
   - 问题：element-plus 中没有 Bulb 图标
   - 修复：替换为 Star 图标

5. **ReportViewer.vue 类型错误**
   - 问题：index + 1 中 index 类型不确定
   - 修复：使用 Number(index) + 1

6. **package.json 格式错误**
   - 问题：PowerShell 替换时换行符变成字面字符串
   - 修复：替换为真正的换行符

### 七、待完成事项

1. **安装 ECharts 依赖**：
   cd frontend
   npm install
   （package.json 已添加依赖，但 node_modules 中尚未安装）

2. **多语言替换**：
   组件和页面中的部分文字还是硬编码中文，需要逐步替换为 vue-i18n 的 t() 函数调用

3. **测试构建**：
   npm run build

4. **提交代码**

### 八、注意事项

- 所有模板字符串已改为字符串拼接方式，避免 PowerShell 解析反引号导致的语法错误
- ReportViewer 中使用 Star 图标替代 Bulb 图标（element-plus 中无 Bulb 图标）
- AIAnalytics.vue 目前使用模拟数据，后续可接入真实 API



---

## Phase 10.R.2-A AI基础设施增强升级（2026-08-04）

### 一、目标
增强 AI 平台管理能力，为后续真实模型调用、SaaS 商业化、私有化部署做准备。

### 二、完成内容

#### 1. AI 使用量和成本统计
- 新增模型：AIUsageLog
- 字段：user, organization, task_id, provider, model_name, task_type, input_tokens, output_tokens, total_tokens, estimated_cost, currency, request_time, response_time, status, error_message, model_config
- task_type 支持：video_analysis, speech_analysis, teaching_evaluation, report_generation, chat, embedding
- 自动计算 total_tokens = input_tokens + output_tokens

#### 2. AI Provider 健康状态管理
- AIModelConfig 新增字段：
  - health_status：active / degraded / offline
  - last_health_check_time：最后检查时间
  - last_error_message：最后错误信息
- 默认状态：active

#### 3. Provider 健康检查服务
- 新增文件：ai_analysis/services/provider_health.py
- 类：ProviderHealthChecker
- 功能：
  - check_all_providers() - 检查所有激活的 Provider
  - check_provider(config) - 检查单个 Provider
  - get_available_providers(capability) - 获取可用的 Provider 列表
  - get_provider_status_summary() - 获取状态汇总

#### 4. 增强 ProviderFactory
- 过滤不可用模型：排除 health_status="offline" 的配置
- 优先选择规则：is_active=True + status=True + health_status=active + priority 最低
- 失败自动降级：
  - chat_with_fallback() - 带自动降级的对话调用
  - analyze_image_with_fallback() - 带自动降级的图片分析
- 每次调用都记录 AIUsageLog（成功/失败）
- 所有 Provider 都失败时返回统一失败响应

#### 5. 任务级模型选择能力
- ClassAnalysisTask 新增字段：model_config (ForeignKey to AIModelConfig)
- 允许指定某一次视频分析使用特定模型
- 为空时使用 ProviderFactory 自动选择

#### 6. 组织级模型配置能力
- 新增模型：OrganizationAIConfig
- 字段：organization(School OneToOne), default_model(FK), allowed_models(M2M), monthly_token_limit, monthly_cost_limit, is_enabled, created_time, updated_time
- 方法：
  - get_monthly_usage() - 获取本月使用量
  - check_limit() - 检查是否超出限制

#### 7. 后台管理 Admin 升级
- AIModelConfigAdmin：
  - list_display 新增 health_status_display、last_health_check_time
  - list_filter 新增 health_status
- 新增 AIUsageLogAdmin：
  - 支持按用户、学校、模型、时间、任务类型查询统计
- 新增 OrganizationAIConfigAdmin：
  - 支持组织级 AI 配置管理

#### 8. 新增 API 接口
- GET /api/ai/providers/status/ - ProviderStatusView
  - 返回所有模型状态（summary + details）
- GET /api/ai/usage/statistics/ - UsageStatisticsView
  - 返回 Token 统计、成本统计（需管理员权限）
- GET /api/ai/models/available/ - AvailableModelsView
  - 返回当前可用模型列表（支持 capability 参数）

#### 9. Celery 定时任务
- 新增任务：provider_health_check_task
- 任务名：ai_analysis.tasks.provider_health_check_task
- 功能：检测所有 AI Provider 状态
- 装饰器：@shared_task
- 重试：max_retries=3，countdown=60

### 三、数据库 Migration
- 迁移文件：ai_analysis/migrations/0008_aimodelconfig_health_status_and_more.py
- 变更内容：
  - Add field health_status to aimodelconfig
  - Add field last_error_message to aimodelconfig
  - Add field last_health_check_time to aimodelconfig
  - Add field model_config to classanalysistask
  - Create model OrganizationAIConfig
  - Create model AIUsageLog

### 四、测试结果
所有测试通过：
1. ✅ AIModelConfig 健康状态字段
2. ✅ AIUsageLog 使用日志模型
3. ✅ ProviderFactory 离线过滤（OpenAI 设为 offline 后自动降级到 Qwen）
4. ✅ chat_with_fallback 自动降级（记录调用日志）
5. ✅ 可用模型列表
6. ✅ Provider 状态汇总
7. ✅ 任务级模型选择字段
8. ✅ 组织级模型配置

### 五、新增文件
- ai_analysis/services/provider_health.py

### 六、修改文件
- ai_analysis/models.py
- ai_analysis/providers/factory.py
- ai_analysis/admin.py
- ai_analysis/views.py
- ai_analysis/urls.py
- ai_analysis/tasks.py

### 七、注意事项
- 未接入真实 API Key
- 未开发前端页面
- 保持现有 Agent 代码不变
- 未修改 docker-compose
- 未修改 Celery 版本
- 未修改业务任务代码
