<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { BookOpen, ArrowRight, Video } from 'lucide-vue-next'
import { getAlbums } from '@/api/studio'
import type { VideoAlbum } from '@/api/types'
import { formatDateTime } from '@/utils/format'

const { t } = useI18n()
const albums = ref<VideoAlbum[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await getAlbums({ page: page.value })
    albums.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

onMounted(() => void load())
</script>

<template>
  <div class="page-block albums-page">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ t('studio.albums') }}</h2>
        <p class="page-subtitle">{{ t('videos.subtitle', { count: total }) }}</p>
      </div>
    </div>

    <div v-loading="loading" class="album-grid">
      <router-link v-for="a in albums" :key="a.id" :to="`/album/${a.id}`" class="album-card lift-card">
        <div class="album-cover" :style="a.cover_image ? { backgroundImage: `url(${a.cover_image})` } : {}">
          <BookOpen v-if="!a.cover_image" :size="30" />
          <span class="album-count"><Video :size="12" /> {{ a.videos.length }}</span>
        </div>
        <div class="album-info">
          <h3>{{ a.name }}</h3>
          <p>{{ a.description || t('studio.noDesc') }}</p>
          <span class="album-date">{{ formatDateTime(a.created_at) }}</span>
        </div>
        <span class="album-arrow"><ArrowRight :size="18" /></span>
      </router-link>
    </div>

    <el-empty v-if="!loading && !albums.length" :description="t('studio.emptyAlbums')" />

    <el-pagination
      v-if="total > pageSize"
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
.albums-page {
  min-height: 480px;
}

.page-head {
  margin-bottom: 24px;
}

.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 18px;
}

.album-card {
  position: relative;
  display: flex;
  gap: 16px;
  padding: 16px;
  color: inherit;
}

.album-cover {
  position: relative;
  width: 104px;
  height: 104px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: var(--grad-primary);
  background-size: cover;
  background-position: center;
  color: rgba(255, 255, 255, 0.95);
  box-shadow: var(--shadow-sm);
}

.album-count {
  position: absolute;
  right: 6px;
  bottom: 6px;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  height: 20px;
  padding: 0 6px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(2px);
}

.album-info {
  min-width: 0;
  flex: 1;
}

.album-info h3 {
  margin: 2px 0 6px;
  font-size: 16px;
  font-weight: 600;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.album-info p {
  margin: 0 0 8px;
  color: var(--platform-muted);
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.album-date {
  font-size: 12px;
  color: var(--platform-muted);
}

.album-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%) translateX(8px);
  color: var(--platform-primary);
  opacity: 0;
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.album-card:hover .album-arrow {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.pagination {
  margin-top: 28px;
  justify-content: flex-end;
}
</style>
