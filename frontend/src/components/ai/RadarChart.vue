<template>
  <div class="radar-chart">
    <div class="chart-title">{{ title }}</div>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { use } from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

use([
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  CanvasRenderer
])

const { t } = useI18n()
const props = defineProps<{
  title: string
  indicators: { name: string; max: number }[]
  values: number[]
  seriesName?: string
}>()

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'item'
  },
  radar: {
    indicator: props.indicators,
    shape: 'polygon',
    splitNumber: 5,
    axisName: {
      color: '#606266',
      fontSize: 12
    },
    splitLine: {
      lineStyle: {
        color: ['#e4e7ed', '#dcdfe6', '#dcdfe6', '#dcdfe6', '#dcdfe6']
      }
    },
    splitArea: {
      show: true,
      areaStyle: {
        color: ['rgba(64, 158, 255, 0.02)', 'rgba(64, 158, 255, 0.04)', 
                'rgba(64, 158, 255, 0.06)', 'rgba(64, 158, 255, 0.08)', 
                'rgba(64, 158, 255, 0.1)']
      }
    },
    axisLine: {
      lineStyle: {
        color: '#dcdfe6'
      }
    }
  },
  series: [
    {
      name: props.seriesName || '评分',
      type: 'radar',
      data: [
        {
          value: props.values,
          name: props.seriesName || '评分',
          areaStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          },
          lineStyle: {
            color: '#409eff',
            width: 2
          },
          itemStyle: {
            color: '#409eff'
          },
          symbol: 'circle',
          symbolSize: 6
        }
      ]
    }
  ]
}))
</script>

<style scoped>
.radar-chart {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.chart {
  width: 100%;
  height: 350px;
}
</style>
