import os
from celery import Celery

# 设置 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_platform.settings')

app = Celery('video_platform')

# 从 Django settings 中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')