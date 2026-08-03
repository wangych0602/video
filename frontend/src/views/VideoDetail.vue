<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import videojs from 'video.js'
import { ArrowLeft, PlayCircle, MessageSquare, Star, Send, ListVideo, Film } from 'lucide-vue-next'
import { getSchools } from '@/api/schools'
import { getTeachers } from '@/api/studio'
import { getVideo, getVideoCategories } from '@/api/videos'
import { getAlbum } from '@/api/studio'
import { getReviews, createReview } from '@/api/reviews'
import { useUserStore } from '@/stores/user'
import type { School, TeacherRecord, Video, VideoCategory, VideoMini, Review } from '@/api/types'
import { formatDateTime, formatDuration, formatFileSize } from '@/utils/format'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const props = defineProps<{ id: string }>()

const video = ref<Video | null>(null)
const albumVideos = ref<VideoMini[]>([])
const albumName = ref('')
const reviews = ref<Review[]>([])
const teacherName = ref('')
const schoolName = ref('')
const categoryName = ref('')
const playerElement = ref<HTMLVideoElement | null>(null)
const loading = ref(true)
const reviewLoading = ref(false)
const submitting = ref(false)
let player: ReturnType<typeof videojs> | null = null

// 评论表单
const commentText = ref('')
const commentRating = ref(5)

const isLoggedIn = computed(() => userStore.isAuthenticated)

function statusLabel(key: string) {
  return t('status.' + key)
}

function sourceType(url: string): string {
  return /.m3u8/i.test(url) ? 'application/x-mpegURL' : 'video/mp4'
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/videos')
  }
}

async function loadMaps() {
  try {
    const [teachers, schools, categories] = await Promise.all([
      getTeachers(),
      getSchools(),
      getVideoCategories(),
    ])
    const teacher = teachers.find((item: TeacherRecord) => item.id === video.value?.teacher)
    const school = schools.results.find((s: School) => s.id === video.value?.school)
    const category = categories.results.find((c: VideoCategory) => c.id === video.value?.category)
    teacherName.value = teacher?.first_name || teacher?.username || ''
    schoolName.value = school?.name || ''
    categoryName.value = category?.name || ''
  } catch {
    // ignore
  }
}

async function loadAlbumVideos() {
  if (!video.value?.albums?.length) return
  try {
    const albumId = video.value.albums[0].id
    const album = await getAlbum(albumId)
    albumName.value = album.name
    albumVideos.value = album.videos.filter((v) => v.id !== video.value?.id)
  } catch {
    // ignore
  }
}

async function loadReviews() {
  if (!video.value) return
  reviewLoading.value = true
  try {
    const data = await getReviews({ video: video.value.id })
    reviews.value = data.results
  } catch {
    reviews.value = []
  } finally {
    reviewLoading.value = false
  }
}

async function submitComment() {
  if (!commentText.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  if (!video.value) return
  submitting.value = true
  try {
    await createReview({
      video: video.value.id,
      rating: commentRating.value,
      comment: commentText.value.trim(),
    })
    ElMessage.success(t('detail.commentPending'))
    commentText.value = ''
    commentRating.value = 5
    // Refresh reviews (the new one won't appear since it's pending)
    void loadReviews()
  } catch {
    // Error handled by interceptor
  } finally {
    submitting.value = false
  }
}

function goToLogin() {
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

function initPlayer() {
  if (video.value?.file && playerElement.value) {
    player = videojs(playerElement.value, {
      controls: true,
      autoplay: false,
      fluid: true,
      sources: [{ src: video.value.file, type: sourceType(video.value.file) }],
    })
  }
}

async function loadAll() {
  loading.value = true
  try {
    video.value = await getVideo(props.id)
    await nextTick()
    initPlayer()
    void loadMaps()
    void loadAlbumVideos()
    void loadReviews()
  } finally {
    loading.value = false
  }
}

// Watch for route param changes (navigating between videos)
watch(() => props.id, async (newId) => {
  if (player) {
    player.dispose()
    player = null
  }
  video.value = null
  albumVideos.value = []
  reviews.value = []
  await loadAll()
})

onMounted(loadAll)

onBeforeUnmount(() => {
  if (player) {
    player.dispose()
    player = null
  }
})
</script>

<template>
  <div v-loading="loading" class="min-h-[400px]">
    <template v-if="video">
      <!-- 返回按钮 -->
      <button class="back-btn" @click="goBack">
        <ArrowLeft :size="18" />
        {{ t('detail.back') }}
      </button>

      <!-- 标题区（无背景图、无状态标签） -->
      <div class="video-header">
        <h1 class="video-title">{{ video.title }}</h1>
        <div class="video-meta">
          <span v-if="teacherName" class="meta-item">
            <strong>{{ t('detail.teacher') }}</strong> {{ teacherName }}
          </span>
          <span v-if="schoolName" class="meta-item">
            <strong>{{ t('detail.room') }}</strong> {{ schoolName }}
          </span>
          <span v-if="categoryName" class="meta-item">
            <strong>{{ t('detail.category') }}</strong> {{ categoryName }}
          </span>
          <span class="meta-item">
            <strong>{{ t('detail.duration') }}</strong> {{ formatDuration(video.duration) }}
          </span>
          <span class="meta-item">
            <strong>{{ t('detail.size') }}</strong> {{ formatFileSize(video.file_size) }}
          </span>
          <span class="meta-item">
            <strong>{{ t('detail.upload') }}</strong> {{ formatDateTime(video.created_at) }}
          </span>
          <span v-if="video.resolution" class="meta-item">
            <strong>{{ t('detail.resolution') }}</strong> {{ video.resolution }}
          </span>
        </div>
      </div>

      <!-- 播放器 + 侧边栏 -->
      <div class="player-layout">
        <!-- 播放器 -->
        <div class="player-main">
          <div class="player-container">
            <video v-if="video.file" ref="playerElement" class="video-js vjs-big-play-centered" />
            <div v-else class="no-file">
              <Film :size="48" :stroke-width="1.2" />
              <p>{{ t('detail.noFile') }}</p>
            </div>
          </div>

          <!-- 简介 -->
          <div class="video-desc-section">
            <p class="video-desc">{{ video.description || t('detail.noDesc') }}</p>
          </div>
        </div>

        <!-- 侧边栏 -->
        <div class="player-sidebar">
          <!-- 正在播放 -->
          <div class="sidebar-card now-playing">
            <div class="sidebar-head">
              <PlayCircle :size="16" />
              {{ t('detail.nowPlaying') }}
            </div>
            <div class="now-playing-body">
              <div class="np-thumb">
                <div v-if="video.cover_image" class="np-cover" :style="{ backgroundImage: 'url(' + video.cover_image + ')' }" />
                <PlayCircle v-else :size="28" />
              </div>
              <div class="np-info">
                <strong>{{ video.title }}</strong>
                <span>{{ formatDuration(video.duration) }} · {{ formatFileSize(video.file_size) }}</span>
              </div>
            </div>
          </div>

          <!-- 同专辑视频 -->
          <div v-if="albumVideos.length" class="sidebar-card">
            <div class="sidebar-head">
              <ListVideo :size="16" />
              {{ t('detail.sameAlbum') }}
              <span v-if="albumName" class="album-badge">{{ albumName }}</span>
            </div>
            <div class="album-list">
              <router-link
                v-for="item in albumVideos"
                :key="item.id"
                :to="'/video/' + item.id"
                class="album-item"
              >
                <div class="album-thumb">
                  <div v-if="item.cover_image" class="thumb-bg" :style="{ backgroundImage: 'url(' + item.cover_image + ')' }" />
                  <Film v-else :size="18" />
                  <span class="thumb-duration">{{ formatDuration(item.duration) }}</span>
                </div>
                <div class="album-item-info">
                  <strong>{{ item.title }}</strong>
                  <span>{{ formatFileSize(item.file_size) }}</span>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 评论区 -->
      <div class="comment-section">
        <div class="comment-head">
          <h2>
            <MessageSquare :size="20" />
            {{ t('detail.comments') }}
            <span v-if="reviews.length" class="comment-count">{{ t('detail.commentCount', { count: reviews.length }) }}</span>
          </h2>
        </div>

        <!-- 评论输入 -->
        <div class="comment-form-area">
          <template v-if="isLoggedIn">
            <div class="comment-rating">
              <span class="rating-label">{{ t('detail.commentRating') }}</span>
              <el-rate v-model="commentRating" :max="5" />
            </div>
            <div class="comment-input-wrap">
              <el-input
                v-model="commentText"
                type="textarea"
                :rows="3"
                :placeholder="t('detail.commentPlaceholder')"
                maxlength="500"
                show-word-limit
                resize="none"
              />
              <div class="comment-submit-row">
                <span class="comment-user">{{ userStore.username }}</span>
                <el-button
                  type="primary"
                  :loading="submitting"
                  :disabled="!commentText.trim()"
                  @click="submitComment"
                >
                  <Send :size="15" />
                  {{ submitting ? t('detail.commentSubmitting') : t('detail.commentSubmit') }}
                </el-button>
              </div>
            </div>
          </template>
          <div v-else class="comment-login-prompt">
            <MessageSquare :size="28" :stroke-width="1.3" />
            <p>{{ t('detail.commentLoginRequired') }}</p>
            <el-button type="primary" @click="goToLogin">{{ t('detail.commentLogin') }}</el-button>
          </div>
        </div>

        <!-- 评论列表 -->
        <div v-loading="reviewLoading" class="comment-list">
          <div v-for="review in reviews" :key="review.id" class="comment-item">
            <div class="comment-avatar">
              {{ (review.user_first_name || review.user_username).charAt(0).toUpperCase() }}
            </div>
            <div class="comment-body">
              <div class="comment-top">
                <strong>{{ review.user_first_name || review.user_username || t('detail.commentAnonymous') }}</strong>
                <el-rate :model-value="review.rating" :max="5" disabled size="small" />
              </div>
              <p class="comment-text">{{ review.comment }}</p>
              <span class="comment-time">{{ formatDateTime(review.created_at) }}</span>
            </div>
          </div>
          <div v-if="!reviews.length && !reviewLoading" class="comment-empty">
            <MessageSquare :size="36" :stroke-width="1" />
            <p>{{ t('detail.commentEmpty') }}</p>
          </div>
        </div>
      </div>
    </template>
    <el-empty v-else-if="!loading" :description="t('detail.notFound')" />
  </div>
</template>

<style scoped>
/* ===== 返回按钮 ===== */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 16px;
  margin-bottom: 18px;
  border: 1px solid var(--platform-line);
  border-radius: 10px;
  background: var(--platform-panel);
  color: var(--platform-muted);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
}

.back-btn:hover {
  border-color: var(--platform-primary);
  color: var(--platform-primary);
  background: var(--platform-primary-soft);
}

/* ===== 标题区 ===== */
.video-header {
  margin-bottom: 20px;
}

.video-title {
  margin: 0 0 12px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.3;
  color: var(--platform-text);
}

.video-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
  font-size: 13px;
  color: var(--platform-muted);
}

.meta-item strong {
  color: var(--platform-text);
  font-weight: 600;
  margin-right: 4px;
}

/* ===== 播放器布局 ===== */
.player-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 28px;
}

.player-main {
  flex: 1;
  min-width: 0;
}

.player-container {
  overflow: hidden;
  border-radius: 16px;
  background: #0f172a;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.no-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 360px;
  color: var(--platform-muted);
}

.no-file p {
  margin: 0;
  font-size: 14px;
}

/* ===== 简介 ===== */
.video-desc-section {
  margin-top: 16px;
  padding: 16px 18px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 14px;
}

.video-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--platform-text);
  white-space: pre-wrap;
}

/* ===== 侧边栏 ===== */
.player-sidebar {
  width: 320px;
  flex: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-card {
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 14px;
  overflow: hidden;
}

.sidebar-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 700;
  color: var(--platform-text);
  border-bottom: 1px solid var(--platform-line);
}

.album-badge {
  margin-left: auto;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
  font-size: 11px;
  font-weight: 600;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== 正在播放 ===== */
.now-playing-body {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
}

.np-thumb {
  width: 72px;
  height: 44px;
  flex: none;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  color: #fff;
}

.np-cover {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.np-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.np-info strong {
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.np-info span {
  font-size: 12px;
  color: var(--platform-muted);
}

/* ===== 同专辑列表 ===== */
.album-list {
  max-height: 420px;
  overflow-y: auto;
  padding: 8px;
}

.album-item {
  display: flex;
  gap: 10px;
  padding: 8px;
  border-radius: 10px;
  text-decoration: none;
  color: inherit;
  transition: background 0.15s ease;
}

.album-item:hover {
  background: var(--platform-primary-soft);
}

.album-thumb {
  position: relative;
  width: 96px;
  height: 56px;
  flex: none;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  color: #fff;
}

.thumb-bg {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.thumb-duration {
  position: absolute;
  right: 4px;
  bottom: 4px;
  padding: 1px 6px;
  border-radius: 5px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  line-height: 16px;
}

.album-item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
  padding-top: 2px;
}

.album-item-info strong {
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.album-item-info span {
  font-size: 12px;
  color: var(--platform-muted);
}

/* ===== 评论区 ===== */
.comment-section {
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-xs);
}

.comment-head {
  margin-bottom: 20px;
}

.comment-head h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--platform-text);
}

.comment-count {
  font-size: 13px;
  font-weight: 500;
  color: var(--platform-muted);
}

/* ===== 评论输入 ===== */
.comment-form-area {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--platform-line);
}

.comment-rating {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.rating-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--platform-text);
}

.comment-input-wrap {
  background: var(--platform-bg);
  border: 1px solid var(--platform-line);
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.18s ease;
}

.comment-input-wrap:focus-within {
  border-color: var(--platform-primary);
}

.comment-input-wrap :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  box-shadow: none;
  padding: 12px 14px;
  font-size: 14px;
  line-height: 1.6;
}

.comment-submit-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-top: 1px solid var(--platform-line);
}

.comment-user {
  font-size: 13px;
  color: var(--platform-muted);
}

.comment-submit-row :deep(.el-button) {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

/* 未登录提示 */
.comment-login-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px 20px;
  text-align: center;
  color: var(--platform-muted);
}

.comment-login-prompt p {
  margin: 0;
  font-size: 14px;
}

/* ===== 评论列表 ===== */
.comment-list {
  min-height: 80px;
}

.comment-item {
  display: flex;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid var(--platform-line);
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--grad-primary);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  box-shadow: var(--shadow-primary);
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.comment-top strong {
  font-size: 14px;
  font-weight: 600;
  color: var(--platform-text);
}

.comment-text {
  margin: 0 0 6px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--platform-text);
  word-break: break-word;
}

.comment-time {
  font-size: 12px;
  color: var(--platform-muted);
}

.comment-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px 20px;
  color: var(--platform-muted);
}

.comment-empty p {
  margin: 0;
  font-size: 14px;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .player-layout {
    flex-direction: column;
  }

  .player-sidebar {
    width: 100%;
  }
}
</style>
