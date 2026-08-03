# STREAMING_ARCHITECTURE.md

## 1. 直播架构图

```mermaid
graph LR
    A[录播设备] -->|RTMP 推流| B[nginx-rtmp :1935]
    B -->|HLS 切片| C[/tmp/hls]
    B -->|on_publish 回调| D[Django :8000/api/live/callback/]
    D --> E[LiveSession 状态同步]
    C --> F[播放器]
    F -->|HTTP GET /hls/{key}.m3u8| B
    D --> G[Redis :6379]
    D --> H[PostgreSQL :5432]
```

## 2. RTMP 流程

1. 平台调用 `POST /api/devices/{device_id}/start-live/`
2. Django 检查设备在线，生成 `stream_key`
3. 返回 `stream_url`：`rtmp://服务器地址/live/{stream_key}`
4. 设备使用 OBS 或 SDK 向该地址推流
5. nginx-rtmp 收到推流，回调 `publish_started`
6. Django 将 `LiveSession.status` 更新为 `live`

## 3. HLS 流程

1. nginx-rtmp 将 RTMP 流转为 HLS 切片，写入 `/tmp/hls`
2. 播放地址：`http://服务器地址/hls/{stream_key}.m3u8`
3. 播放器请求 m3u8，浏览器通过 hls.js 播放
4. 推流结束，回调 `publish_stopped`，`LiveSession.status` 更新为 `stopped`

## 4. 设备配置方法

1. 设备注册：`POST /api/devices/register/`，保存返回的 `device_token`
2. 设备心跳：每 30 秒调用 `POST /api/devices/heartbeat/`，请求头带 `X-Device-Token`
3. 接收直播指令：平台调用 `start-live` 后，设备读取 `stream_url` 并推流
4. 录像上传：`POST /api/devices/upload-video/`，multipart 字段 `video_file`、`device_sn`、`record_time`

## 5. 服务器部署方法

### Docker Compose

```bash
docker compose up -d --build
```

服务：

- `nginx-rtmp`：RTMP 1935，HLS HTTP 8080
- `ffmpeg`：转码工具容器
- `redis`：6379
- `postgres`：5432
- `backend`：Django，映射 8008
- `frontend`：Vue 开发服务器，5173

### 直播检测

定时执行：

```bash
python manage.py check_live_streams
```

命令检查活跃 `LiveSession` 的 HLS 地址；断流时自动将状态改为 `error`。可配合系统计划任务或容器 cron 每 30 秒运行。

### 环境变量

- `RTMP_SERVER_URL`：推流服务器地址，默认 `rtmp://127.0.0.1:1935`
- `HLS_SERVER_URL`：HLS 服务器地址，默认 `http://127.0.0.1:8080`
- `DB_ENGINE=postgres` 时启用 PostgreSQL，配套 `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`
