<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { getTeachers, getAlbums } from '@/api/studio'
import type { TeacherRecord, VideoAlbum } from '@/api/types'
import { BookOpen, GraduationCap, School, Video, ArrowRight } from 'lucide-vue-next'
import { formatDateTime } from '@/utils/format'

const { t } = useI18n()

const teachers = ref<TeacherRecord[]>([])
const albums = ref<VideoAlbum[]>([])

onMounted(async () => {
  try {
    const [tData, aData] = await Promise.all([getTeachers(), getAlbums()])
    teachers.value = tData
    albums.value = aData.results
  } catch {
    // ignore
  }
})
</script>

<template>
  <div class="page-block">
    <!-- Hero -->
    <section class="studio-hero">
      <div class="hero-glow glow-1" />
      <div class="hero-glow glow-2" />
      <div class="hero-content">
        <div class="hero-badge">
          <GraduationCap :size="16" />
          <span>名师风采</span>
        </div>
        <h1>{{ t('studio.title') }}</h1>
        <p>{{ t('studio.subtitle') }}</p>
      </div>
    </section>

    <!-- 名师列表 -->
    <section class="studio-section">
      <h2 class="section-title">{{ t('studio.teachers') }}</h2>
      <div v-if="teachers.length" class="teacher-grid">
        <router-link
          v-for="teacher in teachers"
          :key="teacher.id"
          :to="`/teacher/${teacher.id}`"
          class="teacher-card lift-card"
        >
          <div class="teacher-avatar">
            <img v-if="teacher.avatar" :src="teacher.avatar" :alt="teacher.username" />
            <span v-else>{{ (teacher.first_name || teacher.username).charAt(0).toUpperCase() }}</span>
          </div>
          <h3>{{ teacher.first_name || teacher.username }}</h3>
          <p class="subject">{{ teacher.subject || t('studio.noSubject') }}</p>
          <p class="school">
            <School :size="13" />
            {{ teacher.school_name || '-' }}
          </p>
          <div class="card-arrow">
            <ArrowRight :size="18" />
          </div>
        </router-link>
      </div>
      <el-empty v-else :description="t('studio.emptyTeachers')" />
    </section>

    <!-- 专辑列表 -->
    <section class="studio-section">
      <h2 class="section-title">{{ t('studio.albums') }}</h2>
      <div v-if="albums.length" class="album-grid">
        <router-link
          v-for="a in albums"
          :key="a.id"
          :to="`/album/${a.id}`"
          class="album-card lift-card"
        >
          <div
            class="album-cover"
            :style="a.cover_image ? { backgroundImage: `url(${a.cover_image})` } : {}"
          >
            <BookOpen v-if="!a.cover_image" :size="28" />
            <span class="album-count">{{ a.videos.length }}</span>
          </div>
          <div class="album-info">
            <h3>{{ a.name }}</h3>
            <p class="album-desc">{{ a.description || t('studio.noDesc') }}</p>
            <div class="album-foot">
              <span class="album-videos">
                <Video :size="13" />
                {{ t('studio.videoCount', { count: a.videos.length }) }}
              </span>
              <span class="album-date">{{ formatDateTime(a.created_at) }}</span>
            </div>
          </div>
        </router-link>
      </div>
      <el-empty v-else :description="t('studio.emptyAlbums')" />
    </section>
  </div>
</template>

<style scoped>
/* ===== Hero ===== */
.studio-hero {
  position: relative;
  overflow: hidden;
  padding: 40px 36px;
  margin-bottom: 32px;
  background: var(--grad-hero);
  border-radius: 20px;
  box-shadow: var(--shadow-md);
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  pointer-events: none;
}

.glow-1 {
  width: 280px;
  height: 280px;
  right: -40px;
  top: -80px;
  background: rgba(20, 184, 166, 0.35);
}

.glow-2 {
  width: 200px;
  height: 200px;
  right: 120px;
  bottom: -80px;
  background: rgba(217, 119, 6, 0.2);
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  color: #2dd4bf;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 14px;
}

.studio-hero h1 {
  margin: 0 0 8px;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: 0;
  color: #f8fafc;
}

.studio-hero p {
  margin: 0;
  color: #94a3b8;
  font-size: 15px;
}

/* ===== Section ===== */
.studio-section {
  margin-bottom: 36px;
}

.studio-section .section-title {
  margin-bottom: 20px;
}

/* ===== 名师卡片 ===== */
.teacher-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 20px;
}

.teacher-card {
  position: relative;
  display: block;
  padding: 30px 20px 24px;
  text-align: center;
  text-decoration: none;
  color: inherit;
}

.teacher-avatar {
  width: 84px;
  height: 84px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--grad-primary);
  color: #fff;
  font-size: 30px;
  font-weight: 700;
  overflow: hidden;
  box-shadow: var(--shadow-primary);
}

.teacher-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.teacher-card h3 {
  margin: 0 0 6px;
  font-size: 17px;
  font-weight: 600;
}

.teacher-card .subject {
  margin: 0 0 6px;
  color: var(--platform-primary);
  font-size: 13px;
  font-weight: 500;
}

.teacher-card .school {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin: 0;
  color: var(--platform-muted);
  font-size: 13px;
}

.card-arrow {
  position: absolute;
  right: 16px;
  top: 16px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.teacher-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* ===== 专辑卡片 ===== */
.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.album-card {
  display: flex;
  gap: 18px;
  padding: 18px;
  text-decoration: none;
  color: inherit;
}

.album-cover {
  position: relative;
  width: 84px;
  height: 84px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: var(--grad-primary);
  background-size: cover;
  background-position: center;
  color: #fff;
  box-shadow: var(--shadow-primary);
  overflow: hidden;
}

.album-count {
  position: absolute;
  right: -6px;
  bottom: -6px;
  min-width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 7px;
  border-radius: 999px;
  background: var(--platform-accent);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  border: 2px solid var(--platform-panel);
}

.album-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.album-info h3 {
  margin: 2px 0 6px;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.album-desc {
  margin: 0;
  flex: 1;
  color: var(--platform-muted);
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.album-foot {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
}

.album-videos {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--platform-primary);
  font-weight: 500;
}

.album-date {
  font-size: 12px;
  color: var(--platform-muted);
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .studio-hero {
    padding: 28px 20px;
  }

  .studio-hero h1 {
    font-size: 24px;
  }
}
</style>
