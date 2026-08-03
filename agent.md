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
