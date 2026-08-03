#!/bin/sh
set -e

# 执行数据库迁移
python manage.py migrate

# 自动创建管理员账号（如果不存在）
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created: admin / admin123')
else:
    print('Admin user already exists, skipped.')
"

# 启动 Django 开发服务器
exec python manage.py runserver 0.0.0.0:8000