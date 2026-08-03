import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

with open('ReportViewer.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Lines with nested {{:')
for i, line in enumerate(lines):
    if '{{' in line and line.count('{{') > 1:
        print(f'Line {i+1}: {line.rstrip()[:100]}')
