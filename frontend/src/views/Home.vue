<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { BookOpen, Play, Radio, ArrowRight, Sparkles, Flame, Eye } from 'lucide-vue-next'
import { getAlbums, getPopularAlbums, getTeachers } from '@/api/studio'
import { getPopularVideos, getSiteSettings, getVideos } from '@/api/videos'
import { getLiveSessions } from '@/api/live'
import type { LiveSession, SiteSettings, TeacherRecord, Video, VideoAlbum } from '@/api/types'
import { formatDuration } from '@/utils/format'
import defaultBanner from '@/assets/banner-default.svg'

const { t } = useI18n()

const latestVideos = ref<Video[]>([])
const popularVideos = ref<Video[]>([])
const popularAlbums = ref<VideoAlbum[]>([])
const liveSessions = ref<LiveSession[]>([])
const albums = ref<VideoAlbum[]>([])
const teachers = ref<TeacherRecord[]>([])
const site = ref<SiteSettings>({ id: 1, banner_image: null, site_name: '', footer_description: '', footer_copyright: '', updated_at: '' })

const liveList = computed(() => liveSessions.value.filter((session) => session.status === 'live'))

const bannerImage = computed(() => site.value?.banner_image || defaultBanner)

function formatViewCount(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return y + '-' + m + '-' + d + ' ' + h + ':' + min
}

onMounted(async () => {
  try {
    const [videos, sessions, albumPage, teacherList, settings, popular, popularAlbumList] = await Promise.all([
      getVideos({ page: 1 }),
      getLiveSessions({ status: 'live' }),
      getAlbums({ page: 1 }),
      getTeachers(),
      getSiteSettings(),
      getPopularVideos(),
      getPopularAlbums(),
    ])
    site.value = settings
    latestVideos.value = videos.results.slice(0, 8)
    liveSessions.value = sessions.results
    albums.value = albumPage.results.slice(0, 8)
    teachers.value = teacherList.slice(0, 6)
    popularVideos.value = popular.slice(0, 5)
    popularAlbums.value = popularAlbumList.slice(0, 5)
  } catch {
    // 鏈櫥褰曟垨鎺ュ彛寮傚父鏃剁敱鎷︽埅鍣ㄦ彁绀?
  }
})
</script>

<template>
  <div class="home-page">
    <section class="home-banner">
      <img v-if="bannerImage" :src="bannerImage" alt="" class="banner-image" />
      <div class="banner-glow glow-a" />
      <div class="banner-glow glow-b" />
      <div class="banner-content">
        <span class="banner-tag"><Sparkles :size="14" /> {{ t('home.bannerTag') }}</span>
        <h1>{{ t('home.bannerTitle') }}</h1>
        <p>{{ t('home.bannerDesc') }}</p>
        <div class="banner-actions">
          <router-link to="/videos" class="banner-btn primary">
            {{ t('home.browseCourses') }} <ArrowRight :size="16" />
          </router-link>
          <router-link to="/live" class="banner-btn ghost">
            <Radio :size="16" /> {{ t('home.enterLive') }}
          </router-link>
        </div>
      </div>
    </section>

    <div class="top-row">
      <section class="home-section">
        <div class="section-head">
          <h2 class="section-title">{{ t('home.latestTitle') }}</h2>
          <router-link to="/videos" class="view-all">{{ t('home.viewAll') }} <ArrowRight :size="14" /></router-link>
        </div>
        <div v-if="latestVideos.length" class="video-grid">
          <router-link v-for="video in latestVideos" :key="video.id" :to="`/video/${video.id}`" class="video-card lift-card">
            <div
              class="video-thumb"
              :style="video.cover_image ? { backgroundImage: `url(${video.cover_image})` } : {}"
            >
              <span class="duration">{{ formatDuration(video.duration) }}</span>
              <div class="play-overlay"><Play :size="26" fill="currentColor" /></div>
            </div>
            <div class="video-body">
              <h3>{{ video.title }}</h3>
              <div class="video-meta">
                <span class="meta-item"><Eye :size="12" /> {{ formatViewCount(video.view_count) }}</span>
                <span class="meta-item">{{ formatDate(video.created_at) }}</span>
              </div>
            </div>
          </router-link>
        </div>
        <el-empty v-else :description="t('home.emptyCourses')" />
      </section>

      <aside v-if="popularVideos.length" class="home-section ranking-aside">
        <div class="section-head">
          <h2 class="section-title"><Flame :size="18" /> {{ t('home.rankingTitle') }}</h2>
        </div>
        <div class="ranking-list">
          <router-link
            v-for="(video, index) in popularVideos"
            :key="video.id"
            :to="`/video/${video.id}`"
            class="ranking-item"
          >
            <span class="ranking-no" :class="{ top3: index < 3 }">{{ index + 1 }}</span>
            <div class="ranking-info">
              <h3>{{ video.title }}</h3>
              <span class="ranking-views"><Eye :size="11" /> {{ formatViewCount(video.view_count) }}</span>
            </div>
          </router-link>
        </div>
      </aside>
    </div>

    <div class="top-row">
      <section class="home-section">
        <div class="section-head">
          <h2 class="section-title">{{ t('studio.albums') }}</h2>
          <router-link to="/studio" class="view-all">{{ t('home.viewAll') }} <ArrowRight :size="14" /></router-link>
        </div>
        <div v-if="albums.length" class="video-grid">
          <router-link v-for="album in albums" :key="album.id" :to="`/album/${album.id}`" class="video-card lift-card">
            <div
              class="video-thumb album-thumb"
              :style="album.cover_image ? { backgroundImage: `url(${album.cover_image})` } : {}"
            >
              <span v-if="!album.cover_image" class="album-icon"><BookOpen :size="26" /></span>
            </div>
            <div class="video-body">
              <h3>{{ album.name }}</h3>
              <p>{{ t('studio.videoCount', { count: album.videos.length }) }}</p>
            </div>
          </router-link>
        </div>
        <el-empty v-else :description="t('studio.emptyAlbums')" />
      </section>

      <aside v-if="popularAlbums.length" class="home-section ranking-aside">
        <div class="section-head">
          <h2 class="section-title"><Flame :size="18" /> {{ t('home.albumRankingTitle') }}</h2>
        </div>
        <div class="ranking-list">
          <router-link
            v-for="(album, index) in popularAlbums"
            :key="album.id"
            :to="`/album/${album.id}`"
            class="ranking-item"
          >
            <span class="ranking-no" :class="{ top3: index < 3 }">{{ index + 1 }}</span>
            <div class="ranking-info">
              <h3>{{ album.name }}</h3>
              <span class="ranking-views"><Eye :size="11" /> {{ formatViewCount(album.view_count) }}</span>
            </div>
          </router-link>
        </div>
      </aside>
    </div>

    <section class="home-section">
      <div class="section-head">
        <h2 class="section-title">{{ t('studio.teachers') }}</h2>
        <router-link to="/studio" class="view-all">{{ t('home.viewAll') }} <ArrowRight :size="14" /></router-link>
      </div>
      <div v-if="teachers.length" class="teacher-grid">
        <router-link v-for="teacher in teachers" :key="teacher.id" :to="`/teacher/${teacher.id}`" class="teacher-card lift-card">
          <div class="teacher-avatar">
            <img v-if="teacher.avatar" :src="teacher.avatar" :alt="teacher.username" />
            <span v-else>{{ (teacher.first_name || teacher.username).charAt(0).toUpperCase() }}</span>
          </div>
          <h3>{{ teacher.first_name || teacher.username }}</h3>
          <p>{{ teacher.subject || t('studio.noSubject') }}</p>
          <p class="teacher-school">{{ teacher.school_name || '-' }}</p>
        </router-link>
      </div>
      <el-empty v-else :description="t('studio.emptyTeachers')" />
    </section>

    <section class="home-section">
      <div class="section-head">
        <h2 class="section-title">{{ t('home.liveTitle') }}</h2>
        <router-link to="/live" class="view-all">{{ t('home.viewAll') }} <ArrowRight :size="14" /></router-link>
      </div>
      <div v-if="liveList.length" class="live-grid">
        <router-link
          v-for="session in liveList"
          :key="session.id"
          :to="{ path: '/live', query: { session: session.id } }"
          class="live-card lift-card"
        >
          <span class="live-dot" />
          <div>
            <h3>{{ session.title }}</h3>
            <p>{{ session.school_name || t('home.liveNow') }}</p>
          </div>
        </router-link>
      </div>
      <el-empty v-else :description="t('home.emptyLive')" />
    </section>

    <footer class="home-footer">
      <div class="footer-inner">
        <h3>{{ site.site_name || t('app.brand') }}</h3>
        <p>{{ site.footer_description || t('home.bannerDesc') }}</p>
        <span v-if="site.footer_copyright">{{ site.footer_copyright }}</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home-banner {
  position: relative;
  overflow: hidden;
  padding: 56px 44px;
  margin-bottom: 32px;
  background: var(--grad-hero);
  color: #f8fafc;
  border-radius: 22px;
  box-shadow: var(--shadow-lg);
}

.banner-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.banner-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(8px);
  opacity: 0.5;
  pointer-events: none;
  z-index: 1;
}

.glow-a {
  width: 320px;
  height: 320px;
  right: -80px;
  top: -120px;
  background: radial-gradient(circle, rgba(45, 212, 191, 0.55), transparent 70%);
  animation: float-slow 7s ease-in-out infinite;
}

.glow-b {
  width: 260px;
  height: 260px;
  left: -60px;
  bottom: -120px;
  background: radial-gradient(circle, rgba(217, 119, 6, 0.35), transparent 70%);
  animation: float-slow 9s ease-in-out infinite reverse;
}

.banner-content {
  position: relative;
  z-index: 2;
}

.banner-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #99f6e4;
  font-size: 13px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.home-banner h1 {
  margin: 18px 0 10px;
  font-size: 38px;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.2;
}

.home-banner p {
  margin: 0 0 24px;
  color: #cbd5e1;
  font-size: 15px;
  max-width: 560px;
  line-height: 1.6;
}

.banner-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.banner-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 42px;
  padding: 0 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.banner-btn.primary {
  background: var(--grad-accent);
  color: #fff;
  box-shadow: 0 8px 20px rgba(217, 119, 6, 0.35);
}

.banner-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(217, 119, 6, 0.45);
}

.banner-btn.ghost {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #f8fafc;
  backdrop-filter: blur(4px);
}

.banner-btn.ghost:hover {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-2px);
}

.home-section {
  margin-bottom: 36px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.view-all {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--platform-primary);
  font-size: 14px;
  font-weight: 600;
  transition: gap 0.2s ease;
}

.view-all:hover {
  gap: 8px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.video-card {
  overflow: hidden;
}

.video-thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  background-size: cover;
  background-position: center;
}

.album-thumb {
  background: var(--grad-primary);
  background-size: contain;
  background-repeat: no-repeat;
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

.video-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
  color: var(--platform-muted);
  font-size: 12px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.album-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.92);
  background: rgba(0, 0, 0, 0.12);
}

.live-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

.live-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
}

.live-card h3 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0;
}

.live-card p {
  margin: 0;
  color: var(--platform-muted);
  font-size: 13px;
}

.live-dot {
  width: 12px;
  height: 12px;
  flex: none;
  border-radius: 50%;
  background: #dc2626;
  animation: live-pulse 1.8s infinite;
}

.teacher-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 18px;
}

.teacher-card {
  display: block;
  padding: 26px 20px 22px;
  text-align: center;
}

.teacher-avatar {
  width: 72px;
  height: 72px;
  margin: 0 auto 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--grad-primary);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  overflow: hidden;
  padding: 3px;
  box-shadow: var(--shadow-primary);
}

.teacher-avatar img,
.teacher-avatar span {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.teacher-card h3 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
}

.teacher-card p {
  margin: 0;
  color: var(--platform-muted);
  font-size: 13px;
}

.teacher-school {
  margin-top: 4px;
}

.section-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.top-row {
  display: flex;
  gap: 22px;
  margin-bottom: 36px;
  align-items: stretch;
  width: 100%;
}

.top-row > section,
.top-row > aside {
  margin-bottom: 0;
  min-width: 0;
}

.top-row .video-grid {
  grid-template-columns: repeat(4, minmax(220px, 1fr));
  gap: 18px;
}

.ranking-aside {
  flex: none;
  width: 260px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--platform-card, #fff);
  border-radius: 16px;
  padding: 6px;
  box-shadow: var(--shadow-sm);
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  transition: background 0.18s ease, transform 0.18s ease;
}

.ranking-item:hover {
  background: var(--platform-primary-soft, #f0f7ff);
  transform: translateX(3px);
}

.ranking-no {
  flex: none;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: var(--platform-muted-soft, #f1f5f9);
  color: var(--platform-muted, #64748b);
  font-size: 12px;
  font-weight: 700;
}

.ranking-no.top3 {
  background: var(--grad-accent);
  color: #fff;
  box-shadow: 0 3px 8px rgba(217, 119, 6, 0.35);
}

.ranking-info {
  flex: 1;
  min-width: 0;
}

.ranking-info h3 {
  margin: 0 0 2px;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ranking-views {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  color: var(--platform-muted, #64748b);
  font-size: 11px;
}

.ranking-aside .section-head {
  margin-bottom: 12px;
}

.home-footer {
  margin-top: 44px;
  padding: 38px 0;
  background: var(--grad-hero);
  color: #cbd5e1;
  border-radius: 22px;
  box-shadow: var(--shadow-md);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 28px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-inner h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0;
}

.footer-inner p {
  margin: 0;
  font-size: 13px;
  max-width: 720px;
  line-height: 1.6;
}

.footer-inner span {
  color: #94a3b8;
  font-size: 12px;
}
</style>
