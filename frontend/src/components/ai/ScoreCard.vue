<template>
  <div class="score-card">
    <div class="score-header">
      <h3 class="score-title">{{ title }}</h3>
      <div class="score-grade" v-if="grade" :style="{ color: gradeColor }">
        {{ grade }}
      </div>
    </div>
    <div class="score-value" :style="{ color: scoreColor }">
      {{ score }}
      <span class="score-max">/100</span>
    </div>
    <div class="score-bar">
      <div 
        class="score-bar-fill" 
        :style="{ 
          width: score + '%', 
          background: 'linear-gradient(90deg, ' + gradeColor + '88, ' + gradeColor + ')'
        }"
      ></div>
    </div>
    <div class="score-desc">
      <slot name="desc"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{
  score: number
  title: string
  grade?: string
}>()

const scoreColor = computed(() => {
  if (props.score >= 90) return '#67c23a'
  if (props.score >= 80) return '#409eff'
  if (props.score >= 70) return '#e6a23c'
  if (props.score >= 60) return '#909399'
  return '#f56c6c'
})

const gradeColor = computed(() => {
  if (props.score >= 90) return '#67c23a'
  if (props.score >= 80) return '#409eff'
  if (props.score >= 70) return '#e6a23c'
  if (props.score >= 60) return '#909399'
  return '#f56c6c'
})
</script>

<style scoped>
.score-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.score-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(0, 0, 0, 0.12);
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.score-title {
  font-size: 15px;
  font-weight: 500;
  color: #606266;
  margin: 0;
}

.score-grade {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
  background: currentColor;
  opacity: 0.1;
  border-radius: 20px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 16px;
}

.score-max {
  font-size: 18px;
  font-weight: 400;
  color: #c0c4cc;
}

.score-bar {
  height: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.score-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}
</style>