<template>
  <div class="teacher-ai-page">
    <div class="page-header">
      <h2 class="page-title">{{ t('ai.teacherAI') }}</h2>
      <p class="page-desc">{{ t('ai.teacherAIDesc') }}</p>
    </div>

    <!-- 任务列表 -->
    <div class="task-list-section">
      <div class="section-header">
        <h3 class="section-title">{{ t('ai.tasks') }}</h3>
      </div>
      <div v-if="tasks.length > 0" class="task-list">
        <div 
          v-for="task in tasks" 
          :key="task.id" 
          class="task-item"
          :class="{ active: selectedTaskId === task.id }"
          @click="selectTask(task)"
        >
          <div class="task-info">
            <div class="task-name">{{ task.video?.title || t('ai.classroomVideo') + ' ' + task.id }}</div>
            <div class="task-meta">
              <span class="task-date">{{ formatDate(task.created_time) }}</span>
              <el-tag :type="getStatusType(task.status)" size="small">
                {{ getStatusText(task.status) }}
              </el-tag>
            </div>
          </div>
          <div v-if="task.status === 'completed' && task.progress === 100" class="task-score">
            <span class="score-label">{{ t('ai.score') }}</span>
            <span class="score-value">-</span>
          </div>
          <el-progress 
            v-else-if="task.status === 'processing'"
            :percentage="task.progress" 
            :stroke-width="6"
            :show-text="false"
            style="width: 100px"
          />
        </div>
      </div>
      <el-empty v-else :description="t('ai.noTasks')" />
    </div>

    <!-- 分析详情 -->
    <div v-if="selectedTask" class="analysis-detail">
      <!-- 加载中 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>{{ t('ai.loading') }}</p>
      </div>

      <!-- 已完成 -->
      <template v-else-if="selectedTask.status === 'completed'">
        <!-- 评分卡片和雷达图 -->
        <div class="score-section">
          <ScoreCard 
            :score="evaluation?.overall_score || 0" 
            :title="t('ai.overallScore')"
            :grade="evaluation?.grade"
          >
            <template #desc>
              {{ t('ai.overallScoreDesc') }}
            </template>
          </ScoreCard>
          <div class="radar-card">
            <RadarChart
              :title="t('ai.radarTitle')"
              :indicators="radarIndicators"
              :values="radarValues"
              :series-name="t('ai.teachingScore')"
            />
          </div>
        </div>

        <!-- 优势和建议 -->
        <div class="insights-section">
          <div class="insight-card strengths">
            <div class="insight-header">
              <el-icon><CircleCheck /></el-icon>
              <span>{{ t('ai.strengths') }}</span>
            </div>
            <ul class="insight-list">
              <li v-for="(item, index) in evaluation?.strengths || []" :key="index">
                {{ item }}
              </li>
            </ul>
          </div>
          <div class="insight-card suggestions">
            <div class="insight-header">
              <el-icon><Star /></el-icon>
              <span>{{ t('ai.suggestions') }}</span>
            </div>
            <ul class="insight-list">
              <li v-for="(item, index) in evaluation?.suggestions || []" :key="index">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Tab切换 -->
        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="{{ t('ai.fullReport') }}" name="report">
            <ReportViewer 
              :report="report || {}" 
              @download-pdf="handleDownloadPdf"
            />
          </el-tab-pane>
          <el-tab-pane label="{{ t('ai.transcript') }}" name="transcript">
            <TranscriptViewer
              title="{{ t('ai.transcript') }}"
              :segments="transcript?.speech_segments || []"
              :keywords="transcript?.keywords || []"
              :speaking-rate="transcript?.speaking_rate"
              :duration="selectedTask.video?.duration"
            />
          </el-tab-pane>
        </el-tabs>
      </template>

      <!-- 处理中 -->
      <div v-else-if="selectedTask.status === 'processing'" class="processing-state">
        <el-progress :percentage="selectedTask.progress" :stroke-width="10" />
        <p class="progress-text">{{ selectedTask.current_step || t('ai.status.processing') }}</p>
      </div>

      <!-- 失败 -->
      <div v-else-if="selectedTask.status === 'failed'" class="failed-state">
        <el-icon color="#f56c6c" size="48"><Warning /></el-icon>
        <p>{{ t('ai.status.failed') }}</p>
        <p class="error-message">{{ selectedTask.error_message }}</p>
      </div>
    </div>

    <!-- 未选择任务 -->
    <div v-else class="empty-detail">
      <el-empty description="请选择一个{{ t('ai.tasks') }}查看详情" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loading, CircleCheck, Star, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ScoreCard from '../components/ai/ScoreCard.vue'
import RadarChart from '../components/ai/RadarChart.vue'
import ReportViewer from '../components/ai/ReportViewer.vue'
import TranscriptViewer from '../components/ai/TranscriptViewer.vue'
import { getAITasks, getEvaluation, getReport, getTranscript, downloadReportPdf } from '../api/ai'
import type { AITask, TeachingEvaluation, AIReport, Transcript } from '../api/ai'

const tasks = ref<AITask[]>([])
const selectedTaskId = ref<number | null>(null)
const selectedTask = ref<AITask | null>(null)
const evaluation = ref<TeachingEvaluation | null>(null)
const report = ref<AIReport | null>(null)
const transcript = ref<Transcript | null>(null)
const { t } = useI18n()
const loading = ref(false)
const activeTab = ref('report')

const radarIndicators = computed(() => [
  { name: '知识掌握度', max: 100 },
  { name: '互动参与度', max: 100 },
  { name: '表达清晰度', max: 100 },
  { name: '课堂管理', max: 100 },
  { name: '教学结构', max: 100 }
])

const radarValues = computed(() => {
  if (!evaluation.value) return [0, 0, 0, 0, 0]
  return [
    evaluation.value.knowledge_score || 0,
    evaluation.value.interaction_score || 0,
    evaluation.value.expression_score || 0,
    evaluation.value.classroom_management_score || 0,
    evaluation.value.teaching_structure_score || 0
  ]
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'primary'
    case 'pending': return 'info'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return t('ai.status.completed')
    case 'processing': return t('ai.status.processing')
    case 'pending': return t('ai.status.pending')
    case 'failed': return t('ai.status.failed')
    default: return status
  }
}

const loadTasks = async () => {
  try {
    const res = await getAITasks()
    tasks.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load tasks:', e)
  }
}

const selectTask = async (task: AITask) => {
  selectedTaskId.value = task.id
  selectedTask.value = task
  
  if (task.status === 'completed') {
    loading.value = true
    try {
      // 并行加载评价、报告、文字稿
      const [evalRes, reportRes, transcriptRes] = await Promise.all([
        getEvaluation(task.id).catch(() => null),
        getReport(task.id).catch(() => null),
        getTranscript(task.id).catch(() => null)
      ])
      
      evaluation.value = evalRes?.data || null
      report.value = reportRes?.data || null
      transcript.value = transcriptRes?.data || null
    } catch (e) {
      console.error('Failed to load task details:', e)
    } finally {
      loading.value = false
    }
  }
}

const handleDownloadPdf = async () => {
  if (!selectedTask.value) return
  try {
    const res = await downloadReportPdf(selectedTask.value.id)
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'analysis-report.pdf'
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success(t('ai.pdfSuccess'))
  } catch (e) {
    ElMessage.error(t('ai.pdfFailed'))
  }
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.teacher-ai-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-desc {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.task-list-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.task-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.task-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-date {
  font-size: 13px;
  color: #909399;
}

.task-score {
  text-align: right;
}

.score-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.score-value {
  font-size: 20px;
  font-weight: 600;
  color: #67c23a;
}

.analysis-detail {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.loading-state, .processing-state, .failed-state, .empty-detail {
  padding: 60px 20px;
  text-align: center;
  color: #909399;
}

.loading-state .el-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 16px;
}

.progress-text {
  margin-top: 16px;
  font-size: 14px;
  color: #606266;
}

.failed-state .error-message {
  font-size: 13px;
  color: #f56c6c;
  margin-top: 8px;
}

.score-section {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.radar-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.insights-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.insight-card {
  border-radius: 12px;
  padding: 20px;
}

.insight-card.strengths {
  background: linear-gradient(135deg, #f0f9eb, #e1f3d8);
}

.insight-card.suggestions {
  background: linear-gradient(135deg, #ecf5ff, #d9ecff);
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.insight-list {
  margin: 0;
  padding-left: 20px;
}

.insight-list li {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 8px;
}

.detail-tabs {
  margin-top: 24px;
}

@media (max-width: 1024px) {
  .score-section {
    grid-template-columns: 1fr;
  }
  
  .insights-section {
    grid-template-columns: 1fr;
  }
}
</style>