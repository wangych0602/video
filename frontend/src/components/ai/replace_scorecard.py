import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('ScoreCard.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# ScoreCard 主要通过 props 传入 title，所以内部硬编码不多
# 但可能有一些默认值或状态文字

with open('ScoreCard.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - ScoreCard.vue')

# RadarChart 也主要通过 props 传入
with open('RadarChart.vue', 'r', encoding='utf-8') as f:
    content = f.read()

with open('RadarChart.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - RadarChart.vue')
