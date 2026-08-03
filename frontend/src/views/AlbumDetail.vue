<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { getAlbum } from '@/api/studio'
import type { VideoAlbum } from '@/api/types'
import { formatDuration } from '@/utils/format'

const { t } = useI18n()
import { Play, BookOpen, ArrowLeft } from 'lucide-vue-next'

const props = defineProps<{ id: string }>()
const album = ref<VideoAlbum | null>(null)

onMounted(async () => {
  try {
    album.value = await getAlbum(props.id)
  } catch {
    // ignore
  }
})
</script>

<template>
  <div v-if="album">
    <router-link to="/albums" class="back-link">
      <ArrowLeft :size="16" /> {{ t('album.backToAlbums') }}
    </router-link>

    <div class="album-header">
      <div
        class="album-cover"
        :style="album.cover_image ? { backgroundImage: `url(${album.cover_image})` } : {}"
      >
        <BookOpen v-if="!album.cover_image" :size="36" />
      </div>
      <div class="album-headinfo">
        <span class="album-eyebrow">{{ t('studio.albums') }}</span>
        <h1>{{ album.name }}</h1>
        <p>{{ album.description || t('album.noDesc') }}</p>
        <span class="album-meta">{{ t('studio.videoCount', { count: album.videos.length }) }}</span>
      </div>
    </div>

    <div v-if="album.videos.length" class="video-grid">
      <router-link v-for="video in album.videos" :key="video.id" :to="`/video/${video.id}`" class="video-card lift-card">
        <div
          class="video-thumb"
          :style="video.cover_image ? { backgroundImage: `url(${video.cover_image})` } : {}"
        >
          <span class="duration">{{ formatDuration(video.duration) }}</span>
          <div class="play-overlay"><Play :size="26" fill="currentColor" /></div>
        </div>
        <div class="video-body">
          <h3>{{ video.title }}</h3>
          <p>{{ video.status === 'published' ? t('status.published') : t('status.unpublished') }}</p>
        </div>
      </router-link>
    </div>
    <el-empty v-else :description="t('album.emptyVideos')" />
  </div>
  <el-empty v-else :description="t('album.notFound')" />
</template>

<style scoped>
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 18px;
  padding: 6px 14px 6px 10px;
  border-radius: 10px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  color: var(--platform-muted);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}

.back-link:hover {
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
  border-color: var(--platform-primary);
  transform: translateX(-2px);
}

.album-header {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  padding: 24px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 18px;
  box-shadow: var(--shadow-sm);
}

.album-cover {
  width: 120px;
  height: 120px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: var(--grad-primary);
  background-size: cover;
  background-position: center;
  color: rgba(255, 255, 255, 0.95);
  box-shadow: var(--shadow-primary);
}

.album-headinfo {
  min-width: 0;
}

.album-eyebrow {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: var(--platform-primary);
  background: var(--platform-primary-soft);
  padding: 2px 10px;
  border-radius: 999px;
  margin-bottom: 10px;
}

.album-header h1 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 800;
}

.album-header p {
  margin: 0 0 12px;
  color: var(--platform-muted);
  font-size: 14px;
  line-height: 1.6;
}

.album-meta {
  font-size: 13px;
  color: var(--platform-muted);
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 20px;
}

.video-card {
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 16px;
  box-shadow: var(--shadow-xs);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.video-card:hover {
  border-color: var(--platform-primary-soft);
}

.video-thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  background-size: cover;
  background-position: center;
}

.duration {
  position: absolute;
  right: 10px;
  bottom: 10px;
  height: 24px;
  padding: 0 8px;
  display: inline-flex;
  align-items: center;
  border-radius: 7px;
  background: rgba(0, 0, 0, 0.72);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(2px);
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.15));
  color: #fff;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.play-overlay :deep(svg) {
  width: 52px;
  height: 52px;
  padding: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.video-card:hover .play-overlay {
  opacity: 1;
}

.video-body {
  padding: 14px 14px 16px;
}

.video-body h3 {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-body p {
  margin: 0;
  color: var(--platform-muted);
  font-size: 13px;
}
</style>
