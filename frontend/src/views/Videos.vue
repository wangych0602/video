<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Play, Search } from 'lucide-vue-next'
import { getSchools } from '@/api/schools'
import { getTeachers } from '@/api/studio'
import { getVideoCategories, getVideos } from '@/api/videos'
import type { School, TeacherRecord, Video, VideoCategory } from '@/api/types'
import { formatDuration } from '@/utils/format'

const { t } = useI18n()

const videos = ref<Video[]>([])
const categories = ref<VideoCategory[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const search = ref('')
const category = ref<number | undefined>()
const loading = ref(false)
const teacherMap = ref<Record<number, string>>({})
const schoolMap = ref<Record<number, string>>({})

const statusLabel = (key: string) => t('status.' + key)

async function load() {
  loading.value = true
  try {
    const data = await getVideos({
      page: page.value,
      search: search.value || undefined,
      category: category.value,
    })
    videos.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const data = await getVideoCategories()
  categories.value = data.results
}

async function loadMaps() {
  try {
    const [teachers, schools] = await Promise.all([getTeachers(), getSchools()])
    teacherMap.value = Object.fromEntries(teachers.map((t: TeacherRecord) => [t.id, t.username]))
    schoolMap.value = Object.fromEntries(schools.results.map((s: School) => [s.id, s.name]))
  } catch {
    // 地图加载失败不阻塞列表
  }
}

watch([search, category], () => {
  page.value = 1
  void load()
})

onMounted(() => {
  void loadCategories()
  void loadMaps()
  void load()
})
</script>

<template>
  <div class="page-block videos-page">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ t('videos.title') }}</h2>
        <p class="page-subtitle">{{ t('videos.subtitle', { count: total }) }}</p>
      </div>
      <div class="filters">
        <el-input v-model="search" :placeholder="t('videos.search')" clearable :prefix-icon="Search" class="search-input" />
        <el-select v-model="category" :placeholder="t('videos.allCategories')" clearable class="category-select">
          <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </div>
    </div>

    <div v-loading="loading" class="video-grid">
      <router-link
        v-for="row in videos"
        :key="row.id"
        :to="`/video/${row.id}`"
        class="video-card lift-card"
      >
        <div class="card-cover" :style="row.cover_image ? { backgroundImage: `url(${row.cover_image})` } : {}">
          <span class="play-badge"><Play :size="18" fill="currentColor" /></span>
          <span class="duration">{{ formatDuration(row.duration) }}</span>
        </div>
        <div class="card-body">
          <div class="card-title" :title="row.title">{{ row.title }}</div>
          <div class="card-meta">
            <span>{{ teacherMap[row.teacher ?? -1] || '-' }}</span>
            <span class="dot">·</span>
            <span>{{ schoolMap[row.school ?? -1] || '-' }}</span>
          </div>
          <div class="card-foot">
            <span class="category">{{ categories.find((item) => item.id === row.category)?.name || '-' }}</span>
            <el-tag size="small" :type="row.status === 'published' ? 'success' : 'info'" round>{{ statusLabel(row.status) }}</el-tag>
          </div>
        </div>
      </router-link>
    </div>

    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next, total"
      class="pagination"
      @current-change="load"
    />
  </div>
</template>

<style scoped>
.videos-page {
  min-height: 480px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.filters {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.category-select {
  width: 170px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(248px, 1fr));
  gap: 20px;
}

.video-card {
  display: block;
  overflow: hidden;
  color: var(--platform-text);
}

.card-cover {
  position: relative;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  background-size: cover;
  background-position: center;
  color: var(--platform-primary);
}

.play-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  color: var(--platform-primary);
  opacity: 0;
  transform: scale(0.8);
  transition: opacity 0.25s ease, transform 0.25s ease;
  box-shadow: var(--shadow-sm);
}

.video-card:hover .play-badge {
  opacity: 1;
  transform: scale(1);
}

.duration {
  position: absolute;
  right: 10px;
  bottom: 10px;
  padding: 3px 8px;
  border-radius: 7px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  line-height: 18px;
  backdrop-filter: blur(2px);
}

.card-body {
  padding: 14px 15px 16px;
}

.card-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
}

.card-meta {
  margin-top: 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--platform-muted);
  font-size: 13px;
}

.dot {
  margin: 0 6px;
  color: var(--platform-line);
}

.card-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 12px;
}

.category {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--platform-muted);
  font-size: 12px;
}

.pagination {
  margin-top: 28px;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .page-head {
    flex-direction: column;
  }

  .filters {
    width: 100%;
  }

  .search-input,
  .category-select {
    width: 100%;
  }
}
</style>
