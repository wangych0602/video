<template>
  <div class="ai-analytics-page">
    <div class="page-header">
      <h2 class="page-title">{{ t('ai.analytics') }}</h2>
      <p class="page-desc">{{ t('ai.analyticsDesc') }}</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><VideoCamera /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalTasks }}</div>
          <div class="stat-label">{{ t('ai.stats.totalTasks') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.teacherCount }}</div>
          <div class="stat-label">{{ t('ai.stats.teacherCount') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgScore }}</div>
          <div class="stat-label">{{ t('ai.stats.avgScore') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Trophy /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.excellentCount }}</div>
          <div class="stat-label">{{ t('ai.stats.excellentCount') }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <!-- {{ t('ai.charts.teacherRank') }} -->
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">{{ t('ai.charts.teacherRank') }}</span>
          <el-select v-model="rankPeriod" size="small" style="width: 120px">
            <el-option label="{{ t('ai.thisMonth') }}" value="month" />
            <el-option label="本季度" value="quarter" />
            <el-option label="本年" value="year" />
          </el-select>
        </div>
        <v-chart class="chart" :option="rankChartOption" autoresize />
      </div>

      <!-- {{ t('ai.charts.qualityTrend') }} -->
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">{{ t('ai.charts.qualityTrend') }}</span>
          <el-select v-model="trendPeriod" size="small" style="width: 120px">
            <el-option label="近7天" value="week" />
            <el-option label="{{ t('ai.last30Days') }}" value="month" />
            <el-option label="近90天" value="quarter" />
          </el-select>
        </div>
        <v-chart class="chart" :option="trendChartOption" autoresize />
      </div>
    </div>

    <!-- 五维能力对比 -->
    <div class="charts-row">
      <div class="chart-card full-width">
        <div class="chart-header">
          <span class="chart-title">{{ t('ai.charts.dimensionCompare') }}</span>
        </div>
        <div class="radar-comparison">
          <div class="radar-main">
            <v-chart class="chart" :option="comparisonRadarOption" autoresize />
          </div>
          <div class="dimension-stats">
            <div v-for="dim in dimensionStats" :key="dim.key" class="dim-stat-item">
              <div class="dim-stat-header">
                <span class="dim-stat-name">{{ dim.name }}</span>
                <span class="dim-stat-value" :style="{ color: dim.color }">
                  {{ dim.avg }}分
                </span>
              </div>
              <el-progress 
                :percentage="dim.avg" 
                :color="dim.color"
                :stroke-width="6"
                :show-text="false"
              />
              <div class="dim-stat-desc">
                最高: {{ dim.max }} / 最低: {{ dim.min }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- {{ t('ai.stats.excellentCount') }}列表 -->
    <div class="excellent-section">
      <div class="section-header">
        <span class="section-title">{{ t('ai.stats.excellentCount') }}</span>
        <el-button type="primary" link>{{ t('ai.excellent.viewAll') }}</el-button>
      </div>
      <div class="excellent-list">
        <div v-for="item in excellentClasses" :key="item.id" class="excellent-card">
          <div class="excellent-rank" :class="'rank-' + item.rank">
            {{ item.rank }}
          </div>
          <div class="excellent-info">
            <div class="excellent-title">{{ item.title }}</div>
            <div class="excellent-teacher">
              <el-icon><User /></el-icon>
              {{ item.teacher }}
            </div>
          </div>
          <div class="excellent-score">
            <span class="score-num">{{ item.score }}</span>
            <span class="score-label">分</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { use } from 'echarts/core'
import { BarChart, LineChart, RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { VideoCamera, User, Star, Trophy } from '@element-plus/icons-vue'

use([
  BarChart,
  LineChart,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  CanvasRenderer
])

const rankPeriod = ref('month')
const trendPeriod = ref('month')

// 模拟统计数据
const { t } = useI18n()
const stats = ref({
  totalTasks: 128,
  teacherCount: 24,
  avgScore: 82.5,
  excellentCount: 36
})

// 教师排行数据
const teacherRankData = ref([
  { name: '张老师', score: 94.5 },
  { name: '李老师', score: 91.2 },
  { name: '王老师', score: 89.8 },
  { name: '赵老师', score: 87.6 },
  { name: '刘老师', score: 85.3 },
  { name: '陈老师', score: 83.1 },
  { name: '杨老师', score: 80.7 },
  { name: '黄老师', score: 78.9 }
])

// 趋势数据
const trendData = ref({
  dates: ['07-28', '07-29', '07-30', '07-31', '08-01', '08-02', '08-03'],
  scores: [78.5, 80.2, 79.8, 82.1, 83.5, 84.2, 82.5],
  counts: [12, 15, 18, 14, 20, 16, 18]
})

// 五维统计
const dimensionStats = ref([
  { key: 'knowledge', name: t('ai.knowledge'), avg: 84.2, max: 95, min: 72, color: '#409eff' },
  { key: 'interaction', name: t('ai.interaction'), avg: 79.8, max: 92, min: 65, color: '#67c23a' },
  { key: 'expression', name: t('ai.expression'), avg: 85.6, max: 96, min: 74, color: '#e6a23c' },
  { key: 'classroom', name: t('ai.classroom'), avg: 81.3, max: 93, min: 68, color: '#f56c6c' },
  { key: 'structure', name: t('ai.structure'), avg: 82.7, max: 94, min: 70, color: '#909399' }
])

// t('ai.stats.excellentCount')
const excellentClasses = ref([
  { id: 1, rank: 1, title: '高中数学 - 函数与导数', teacher: '张老师', score: 94.5 },
  { id: 2, rank: 2, title: '初中英语 - 阅读理解技巧', teacher: '李老师', score: 91.2 },
  { id: 3, rank: 3, title: '小学语文 - 古诗词鉴赏', teacher: '王老师', score: 89.8 },
  { id: 4, rank: 4, title: '高中物理 - 力学综合', teacher: '赵老师', score: 87.6 },
  { id: 5, rank: 5, title: '初中化学 - 实验探究', teacher: '刘老师', score: 85.3 }
])

// 教师排行柱状图
const rankChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    max: 100,
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { type: 'dashed', color: '#ebeef5' } }
  },
  yAxis: {
    type: 'category',
    data: teacherRankData.value.map(d => d.name).reverse(),
    axisLine: { show: false },
    axisTick: { show: false }
  },
  series: [
    {
      type: 'bar',
      data: teacherRankData.value.map(d => d.score).reverse(),
      barWidth: 16,
      itemStyle: {
        borderRadius: [0, 8, 8, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        }
      },
      label: {
        show: true,
        position: 'right',
        formatter: '{c}分',
        color: '#606266',
        fontSize: 12
      }
    }
  ]
}))

// 趋势折线图
const trendChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: [t('ai.stats.avgScore'), t('ai.charts.analysisCount')],
    top: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: trendData.value.dates,
    axisLine: { lineStyle: { color: '#dcdfe6' } },
    axisTick: { show: false }
  },
  yAxis: [
    {
      type: 'value',
      name: '评分',
      min: 70,
      max: 100,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { type: 'dashed', color: '#ebeef5' } }
    },
    {
      type: 'value',
      name: '数量',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false }
    }
  ],
  series: [
    {
      name: t('ai.stats.avgScore'),
      type: 'line',
      smooth: true,
      data: trendData.value.scores,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { width: 3, color: '#409eff' },
      itemStyle: { color: '#409eff' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ]
        }
      }
    },
    {
      name: t('ai.charts.analysisCount'),
      type: 'bar',
      yAxisIndex: 1,
      data: trendData.value.counts,
      barWidth: 20,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(103, 194, 58, 0.8)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.2)' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      }
    }
  ]
}))

// 五维对比雷达图
const comparisonRadarOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: {
    data: [t('ai.charts.avgLevel'), t('ai.charts.excellentTeacher')],
    bottom: 0
  },
  radar: {
    indicator: dimensionStats.value.map(d => ({ name: d.name, max: 100 })),
    shape: 'polygon',
    splitNumber: 5,
    axisName: {
      color: '#606266',
      fontSize: 13
    },
    splitArea: {
      show: true,
      areaStyle: {
        color: ['rgba(0,0,0,0.02)', 'rgba(0,0,0,0.04)', 
                'rgba(0,0,0,0.06)', 'rgba(0,0,0,0.08)', 
                'rgba(0,0,0,0.1)']
      }
    }
  },
  series: [
    {
      type: 'radar',
      data: [
        {
          value: dimensionStats.value.map(d => d.avg),
          name: t('ai.charts.avgLevel'),
          areaStyle: { color: 'rgba(64, 158, 255, 0.3)' },
          lineStyle: { color: '#409eff', width: 2 },
          itemStyle: { color: '#409eff' }
        },
        {
          value: dimensionStats.value.map(d => d.max),
          name: t('ai.charts.excellentTeacher'),
          areaStyle: { color: 'rgba(103, 194, 58, 0.3)' },
          lineStyle: { color: '#67c23a', width: 2 },
          itemStyle: { color: '#67c23a' }
        }
      ]
    }
  ]
}))

onMounted(() => {
  // TODO: 加载真实数据
})
</script>

<style scoped>
.ai-analytics-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-icon.green {
  background: linear-gradient(135deg, #11998e, #38ef7d);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #fa709a, #fee140);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart {
  width: 100%;
  height: 320px;
}

.radar-comparison {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
  align-items: center;
}

.radar-main .chart {
  height: 380px;
}

.dimension-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dim-stat-item {
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.dim-stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.dim-stat-name {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.dim-stat-value {
  font-size: 18px;
  font-weight: 700;
}

.dim-stat-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.excellent-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.excellent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.excellent-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  transition: all 0.3s;
}

.excellent-card:hover {
  background: #f5f7fa;
}

.excellent-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  background: #909399;
}

.excellent-rank.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffb700);
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

.excellent-rank.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.4);
}

.excellent-rank.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #b87333);
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.4);
}

.excellent-info {
  flex: 1;
}

.excellent-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.excellent-teacher {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.excellent-score {
  text-align: right;
}

.score-num {
  font-size: 24px;
  font-weight: 700;
  color: #67c23a;
}

.score-label {
  font-size: 12px;
  color: #909399;
  margin-left: 2px;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .radar-comparison {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
