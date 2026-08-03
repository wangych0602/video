<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, BookOpen } from 'lucide-vue-next'
import { getTeachers } from '@/api/studio'
import { getAlbums } from '@/api/studio'
import type { TeacherRecord, VideoAlbum } from '@/api/types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const teacher = ref<TeacherRecord | null>(null)
const albums = ref<VideoAlbum[]>([])

const initial = computed(() => ((teacher.value?.first_name || teacher.value?.username || '')).charAt(0).toUpperCase())

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    const [teachers, albumData] = await Promise.all([getTeachers(), getAlbums()])
    teacher.value = teachers.find((te: TeacherRecord) => te.id === id) ?? null
    albums.value = albumData.results.filter((a: VideoAlbum) => a.teacher === id)
  } catch {
    // ignore
  }
})
</script>

<template>
  <div v-if="teacher" class="teacher-profile">
    <div class="profile-header">
      <div class="profile-inner">
        <button class="back-btn" @click="router.push('/studio')">
          <ArrowLeft :size="16" />
          {{ t('teacherProfile.back') }}
        </button>
        <div class="profile-container">
          <div class="avatar">
          <img v-if="teacher.avatar" :src="teacher.avatar" :alt="teacher.first_name || teacher.username" />
            <span v-else>{{ initial }}</span>
          </div>
          <div class="info">
            <h1>{{ teacher.first_name || teacher.username }}</h1>
            <p class="school-subject">{{ teacher.school_name || t('studio.noSubject') }} <template v-if="teacher.subject">- {{ teacher.subject }}</template></p>
            <p class="bio">{{ teacher.description || t('teacherProfile.noBio') }}</p>
            <p class="stats">{{ albums.length }} {{ t('teacherProfile.courses') }}</p>
          </div>
        </div>
      </div>
    </div>

    <section class="profile-section">
      <h2>{{ t('teacherProfile.courses') }} ({{ albums.length }})</h2>
      <div v-if="albums.length" class="album-grid">
        <router-link v-for="a in albums" :key="a.id" :to="`/album/${a.id}`" class="album-card">
          <div class="album-cover" :style="a.cover_image ? { backgroundImage: `url(${a.cover_image})` } : {}">
            <BookOpen v-if="!a.cover_image" :size="32" />
          </div>
          <div class="album-info">
            <h3>{{ a.name }}</h3>
            <p>{{ a.description || t('studio.noDesc') }}</p>
            <span>{{ t('studio.videoCount', { count: a.videos.length }) }}</span>
          </div>
        </router-link>
      </div>
      <el-empty v-else :description="t('teacherProfile.noCourses')" />
    </section>
  </div>
  <el-empty v-else :description="t('teacherProfile.notFound')" />
</template>

<style scoped>
.profile-header {
  padding: 40px 0 32px;
  background: linear-gradient(135deg, #1d976c 0%, #27ae60 100%);
  color: #fff;
}

.profile-inner {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.back-btn {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.16);
  border: none;
  color: #fff;
  font-size: 14px;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
}

.back-btn:hover {
  background: rgba(255,255,255,0.28);
}

.profile-container {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  overflow: hidden;
  flex: none;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info h1 {
  margin: 0 0 6px;
  font-size: 28px;
}

.school-subject {
  margin: 0 0 6px;
  color: rgba(255,255,255,0.85);
  font-size: 15px;
}

.bio {
  margin: 0 0 6px;
  color: rgba(255,255,255,0.9);
  font-size: 14px;
  line-height: 1.6;
  max-width: 720px;
}

.stats {
  margin: 0;
  font-size: 14px;
}

.profile-section {
  margin-top: 28px;
}

.profile-section h2 {
  margin: 0 0 16px;
  font-size: 20px;
}

.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.album-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s;
}

.album-card:hover {
  border-color: var(--platform-primary);
}

.album-cover {
  width: 96px;
  height: 96px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--platform-primary-soft);
  background-size: cover;
  background-position: center;
  color: var(--platform-primary);
}

.album-info h3 {
  margin: 0 0 4px;
  font-size: 16px;
}

.album-info p {
  margin: 0 0 6px;
  color: var(--platform-muted);
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.album-info span {
  font-size: 12px;
  color: var(--platform-muted);
}
</style>
