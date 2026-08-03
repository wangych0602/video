<template>
  <div class="transcript-viewer">
    <div class="viewer-header">
      <h3 class="viewer-title">{{ title }}</h3>
      <div class="viewer-stats" v-if="speakingRate || duration">
        <span v-if="speakingRate" class="stat-item">
          <el-icon><Microphone /></el-icon>
          语速: {{ speakingRate }} 字/分
        </span>
        <span v-if="duration" class="stat-item">
          <el-icon><Clock /></el-icon>
          时长: {{ formatDuration(duration) }}
        </span>
      </div>
    </div>

    <!-- {{ t('ai.transcript.keywords') }} -->
    <div v-if="keywords && keywords.length > 0" class="keywords-section">
      <div class="section-label">{{ t('ai.transcript.keywords') }}</div>
      <div class="keywords-cloud">
        <span 
          v-for="(kw, index) in keywords" 
          :key="index" 
          class="keyword-tag"
          :style="{ fontSize: getKeywordSize(kw.weight) + 'px' }"
        >
          {{ kw.text || kw }}
        </span>
      </div>
    </div>

    <!-- 文字稿列表 -->
    <div class="transcript-list" v-if="segments && segments.length > 0">
      <div 
        v-for="(segment, index) in segments" 
        :key="index" 
        class="transcript-item"
        :class="segment.speaker"
      >
        <div class="segment-time">{{ formatTime(segment.start_time || 0) }}</div>
        <div class="segment-content">
          <div class="segment-speaker">{{ getSpeakerName(segment.speaker) }}</div>
          <div class="segment-text">{{ segment.text }}</div>
        </div>
      </div>
    </div>

    <el-empty v-else description="{{ t('ai.transcript.noData') }}" />
  </div>
</template>

<script setup lang="ts">
import { Microphone, Clock } from '@element-plus/icons-vue'

defineProps<{
  title?: string
  segments?: any[]
  keywords?: any[]
  speakingRate?: any
  duration?: number
}>()

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return mins.toString().padStart(2, '0') + ':' + secs.toString().padStart(2, '0')
}

const formatDuration = (seconds?: number) => {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return mins + '分' + secs + '秒'
}

const getSpeakerName = (speaker: string) => {
  if (speaker === 'teacher') return t('ai.transcript.teacher')
  if (speaker === 'student') return t('ai.transcript.student')
  return speaker
}

const getKeywordSize = (weight: number) => {
  if (!weight) return 14
  const baseSize = 12
  const maxSize = 24
  return Math.min(baseSize + weight * 2, maxSize)
}
</script>

<style scoped>
.transcript-viewer {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.viewer-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.viewer-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.keywords-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.section-label {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 12px;
}

.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}

.keyword-tag {
  color: #409eff;
  font-weight: 500;
  cursor: default;
  transition: all 0.3s;
}

.keyword-tag:hover {
  color: #66b1ff;
  transform: scale(1.1);
}

.transcript-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.transcript-item {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f5f7fa;
}

.transcript-item:last-child {
  border-bottom: none;
}

.segment-time {
  flex-shrink: 0;
  width: 60px;
  font-size: 12px;
  color: #909399;
  font-family: monospace;
  padding-top: 2px;
}

.segment-content {
  flex: 1;
  min-width: 0;
}

.segment-speaker {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

.transcript-item.teacher .segment-speaker {
  color: #409eff;
}

.transcript-item.student .segment-speaker {
  color: #67c23a;
}

.segment-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.7;
}

.transcript-list::-webkit-scrollbar {
  width: 6px;
}

.transcript-list::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 3px;
}

.transcript-list::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.transcript-list::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}
</style>