<template>
  <div class="report-viewer">
    <div class="report-header">
      <div class="report-title">
        <el-icon><Document /></el-icon>
        {{ report.title || t('ai.report.title') }}
      </div>
      <div class="report-actions">
        <el-button type="primary" :icon="Download" @click="handleDownloadPdf" v-if="report.pdf_url">
          {{ t('ai.downloadPdf') }}
        </el-button>
      </div>
    </div>
    
    <!-- {{ t('ai.report.summary') }} -->
    <div class="report-section" v-if="report.summary">
      <div class="section-header">
        <el-icon><InfoFilled /></el-icon>
        <span class="section-title">{{ t('ai.report.summary') }}</span>
      </div>
      <div class="summary-content">
        <div class="summary-grid">
          <div class="summary-item">
            <span class="label">{{ t('ai.report.duration') }}</span>
            <span class="value">{{ report.summary.duration || '-' }}</span>
          </div>
          <div class="summary-item">
            <span class="label">{{ t('ai.report.totalScore') }}</span>
            <span class="value score" :class="getScoreClass(report.summary.overall_score)">
              {{ report.summary.overall_score }}
            </span>
          </div>
          <div class="summary-item">
            <span class="label">{{ t('ai.report.grade') }}</span>
            <span class="value grade" :class="getGradeClass(report.summary.grade)">
              {{ report.summary.grade }}
            </span>
          </div>
          <div class="summary-item">
            <span class="label">{{ t('ai.report.knowledgePoints') }}</span>
            <span class="value">{{ report.summary.knowledge_points?.length || 0 }} 个</span>
          </div>
        </div>
      </div>
    </div>

    <!-- {{ t('ai.report.strengthsTitle') }} -->
    <div class="report-section" v-if="report.summary?.strengths?.length > 0">
      <div class="section-header">
        <el-icon type="success"><CircleCheck /></el-icon>
        <span class="section-title">{{ t('ai.report.strengthsTitle') }}</span>
      </div>
      <div class="strengths-list">
        <div v-for="(item, index) in report.summary.strengths" :key="index" class="strength-item">
          <span class="strength-num">{{ Number(index) + 1 }}</span>
          <span class="strength-text">{{ item }}</span>
        </div>
      </div>
    </div>

    <!-- {{ t('ai.report.weaknessesTitle') }} -->
    <div class="report-section" v-if="report.summary?.weaknesses?.length > 0">
      <div class="section-header">
        <el-icon type="warning"><Warning /></el-icon>
        <span class="section-title">{{ t('ai.report.weaknessesTitle') }}</span>
      </div>
      <div class="weaknesses-list">
        <div v-for="(item, index) in report.summary.weaknesses" :key="index" class="weakness-item">
          <span class="weakness-num">{{ Number(index) + 1 }}</span>
          <span class="weakness-text">{{ item }}</span>
        </div>
      </div>
    </div>

    <!-- {{ t('ai.report.suggestionsTitle') }} -->
    <div class="report-section" v-if="report.summary?.suggestions?.length > 0">
      <div class="section-header">
        <el-icon type="primary"><Star /></el-icon>
        <span class="section-title">{{ t('ai.report.suggestionsTitle') }}</span>
      </div>
      <div class="suggestions-list">
        <div v-for="(item, index) in report.summary.suggestions" :key="index" class="suggestion-item">
          <span class="suggestion-num">{{ Number(index) + 1 }}</span>
          <span class="suggestion-text">{{ item }}</span>
        </div>
      </div>
    </div>

    <!-- {{ t('ai.report.knowledgePoints') }}覆盖 -->
    <div class="report-section" v-if="report.summary?.knowledge_points?.length > 0">
      <div class="section-header">
        <el-icon><Collection /></el-icon>
        <span class="section-title">{{ t('ai.report.knowledgePoints') }}覆盖</span>
      </div>
      <div class="knowledge-list">
        <span
          v-for="(kp, index) in report.summary.knowledge_points"
          :key="index"
          class="knowledge-tag"
          :class="kp.importance"
        >
          {{ kp.name }}
        </span>
      </div>
    </div>

    <div v-if="!report.summary" class="empty-state">
      <el-empty description="{{ t('ai.report.noData') }}" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Document, Download, InfoFilled, CircleCheck, Warning, Star, Collection } from '@element-plus/icons-vue'

const { t } = useI18n()
const props = defineProps<{
  report: any
}>()

const emit = defineEmits(['download-pdf'])

const getScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'medium'
  if (score >= 60) return 'pass'
  return 'fail'
}

const getGradeClass = (grade: string) => {
  if (!grade) return ''
  const g = grade.toLowerCase()
  if (g === 'a' || g === 's') return 'excellent'
  if (g === 'b') return 'good'
  if (g === 'c') return 'medium'
  if (g === 'd') return 'pass'
  return 'fail'
}

const handleDownloadPdf = () => {
  emit('download-pdf')
}
</script>

<style scoped>
.report-viewer {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.report-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-item {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.summary-item .label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.summary-item .value.score.excellent { color: #67c23a; }
.summary-item .value.score.good { color: #409eff; }
.summary-item .value.score.medium { color: #e6a23c; }
.summary-item .value.score.pass { color: #909399; }
.summary-item .value.score.fail { color: #f56c6c; }

.summary-item .value.grade {
  font-size: 24px;
}

.summary-item .value.grade.excellent { color: #67c23a; }
.summary-item .value.grade.good { color: #409eff; }
.summary-item .value.grade.medium { color: #e6a23c; }
.summary-item .value.grade.pass { color: #909399; }
.summary-item .value.grade.fail { color: #f56c6c; }

.strengths-list, .weaknesses-list, .suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strength-item, .weakness-item, .suggestion-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
}

.strength-item {
  background: linear-gradient(135deg, #f0f9eb, #e1f3d8);
}

.weakness-item {
  background: linear-gradient(135deg, #fef0f0, #fde2e2);
}

.suggestion-item {
  background: linear-gradient(135deg, #ecf5ff, #d9ecff);
}

.strength-num, .weakness-num, .suggestion-num {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.strength-num { background: #67c23a; }
.weakness-num { background: #f56c6c; }
.suggestion-num { background: #409eff; }

.strength-text, .weakness-text, .suggestion-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.knowledge-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.knowledge-tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.knowledge-tag.high {
  background: #fef0f0;
  color: #f56c6c;
}

.knowledge-tag.medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.knowledge-tag.low {
  background: #ecf5ff;
  color: #409eff;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>