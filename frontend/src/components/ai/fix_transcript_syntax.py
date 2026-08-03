import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

with open('TranscriptViewer.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 script 部分
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
if script_match:
    script_content = script_match.group(1)
    fixed_script = re.sub(r'\{\{\s*t\(\'([^\']+)\'\)\s*\}\}', r"t('\1')", script_content)
    content = content.replace(script_content, fixed_script)
    print('Fixed TranscriptViewer.vue')

with open('TranscriptViewer.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
