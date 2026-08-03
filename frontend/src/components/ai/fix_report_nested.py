import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

with open('ReportViewer.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 || '{{ t('xxx') }}' 模式
content = re.sub(
    r"\|\| '\{\{ t\('([^']+)'\) \}\}'",
    r"|| t('\1')",
    content
)

# 修复嵌套的 {{ {{
# 查找所有 {{ ... {{ ... }} ... }} 模式
# 这个比较复杂，先看看具体是什么情况

with open('ReportViewer.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - fixed ReportViewer.vue')
