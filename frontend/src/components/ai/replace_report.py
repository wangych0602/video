import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('ReportViewer.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换报告相关文字
content = content.replace('课堂分析报告', "{{ t('ai.report.title') }}")
content = content.replace('课堂总结', "{{ t('ai.report.summary') }}")
content = content.replace('课堂时长', "{{ t('ai.report.duration') }}")
content = content.replace('总分', "{{ t('ai.report.totalScore') }}")
content = content.replace('等级', "{{ t('ai.report.grade') }}")
content = content.replace('知识点', "{{ t('ai.report.knowledgePoints') }}")
content = content.replace('优势分析', "{{ t('ai.report.strengthsTitle') }}")
content = content.replace('待改进', "{{ t('ai.report.weaknessesTitle') }}")
content = content.replace('改进建议', "{{ t('ai.report.suggestionsTitle') }}")
content = content.replace('知识点覆盖', "{{ t('ai.report.knowledgeCoverage') }}")
content = content.replace('暂无报告数据', "{{ t('ai.report.noData') }}")
content = content.replace('下载PDF', "{{ t('ai.downloadPdf') }}")

with open('ReportViewer.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - ReportViewer.vue')
