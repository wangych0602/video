import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('TranscriptViewer.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换文字稿相关文字
content = content.replace('课堂文字稿', "{{ t('ai.transcript.title') }}")
content = content.replace('关键词', "{{ t('ai.transcript.keywords') }}")
content = content.replace('暂无文字稿', "{{ t('ai.transcript.noData') }}")
content = content.replace('教师', "{{ t('ai.transcript.teacher') }}")
content = content.replace('学生', "{{ t('ai.transcript.student') }}")

with open('TranscriptViewer.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - TranscriptViewer.vue')
