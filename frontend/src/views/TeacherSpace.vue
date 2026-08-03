<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { BookOpen, CalendarClock, CirclePlay, ImagePlus, MonitorPlay, Radio, Upload, User } from 'lucide-vue-next'
import { deletePersonalLive, getLiveSessions, startPersonalLive, stopPersonalLive, type PersonalLiveResult } from '@/api/live'
import { createAlbum, deleteAlbum, getAlbums, updateAlbum, getMyTeacherProfile, updateMyTeacherProfile } from '@/api/studio'
import { deleteVideo, getMyVideos, getVideoCategories, updateVideo, uploadVideo } from '@/api/videos'
import type { LiveSession, Video, VideoAlbum, VideoCategory } from '@/api/types'
import { formatDateTime, formatDuration, formatFileSize } from '@/utils/format'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()

const userStore = useUserStore()
const activeTab = ref<'courses' | 'upload' | 'live' | 'albums' | 'profile'>('courses')
const videos = ref<Video[]>([])
const categories = ref<VideoCategory[]>([])
const sessions = ref<LiveSession[]>([])
const albums = ref<VideoAlbum[]>([])
const loading = ref(false)
const loadingSessions = ref(false)
const loadingAlbums = ref(false)
const showAlbumDialog = ref(false)
const creatingAlbum = ref(false)
const albumForm = ref({ name: '', description: '' })
const albumCoverFile = ref<File | null>(null)
const albumCoverPreview = ref('')
const editingAlbumId = ref<number | null>(null)
const submitting = ref(false)
const showVideoDialog = ref(false)
const savingVideo = ref(false)
const editingVideoId = ref<number | null>(null)

const form = reactive({
  title: '',
  description: '',
  category: undefined as number | undefined,
  album_ids: [] as number[],
})
const videoForm = reactive({
  title: '',
  description: '',
  category: undefined as number | undefined,
  album_ids: [] as number[],
})
const file = ref<File | null>(null)
const cover = ref<File | null>(null)
const videoFileInput = ref<HTMLInputElement | null>(null)
const coverFileInput = ref<HTMLInputElement | null>(null)
const albumCoverInput = ref<HTMLInputElement | null>(null)
const videoCoverFile = ref<File | null>(null)
const videoCoverPreview = ref('')
const videoCoverInput = ref<HTMLInputElement | null>(null)

// 个人资料
const profileLoading = ref(false)
const profileSaving = ref(false)
const profile = ref<{ id: number; avatar: string; description: string; subject: string } | null>(null)
const profileAvatarFile = ref<File | null>(null)
const profileAvatarPreview = ref('')
const profileDescription = ref('')
const profileSubject = ref('')

const statusTagType: Record<string, string> = {
  draft: 'info',
  pending: 'warning',
  approved: 'success',
  published: 'success',
  rejected: 'danger',
}
const statusLabel = (key: string) => t('status.' + key)

const liveSessions = computed(() =>
  sessions.value.filter((s) => !userStore.school || s.school === Number(userStore.school)),
)
const currentLive = computed(() => liveSessions.value.filter((s) => s.status === 'live'))
const historyLive = computed(() => liveSessions.value.filter((s) => s.status !== 'live'))

const showLiveDialog = ref(false)
const startingLive = ref(false)
const liveTitle = ref('')
const liveResult = ref<PersonalLiveResult | null>(null)
const obsServer = computed(() => (liveResult.value ? liveResult.value.stream_url.replace('/' + liveResult.value.stream_key, '') : ''))
const pendingCount = computed(() => videos.value.filter((v) => v.status === 'pending').length)

function appendIds(data: FormData, key: string, ids: number[]) {
  ids.forEach((id) => data.append(key, String(id)))
}

async function loadMine() {
  loading.value = true
  try {
    const data = await getMyVideos(1)
    videos.value = data.results
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const data = await getVideoCategories()
  categories.value = data.results
}

async function loadSessions() {
  loadingSessions.value = true
  try {
    const data = await getLiveSessions({ mine: '1' })
    sessions.value = data.results
  } finally {
    loadingSessions.value = false
  }
}

async function loadAlbums() {
  loadingAlbums.value = true
  try {
    const data = await getAlbums({ mine: '1' })
    albums.value = data.results
  } finally {
    loadingAlbums.value = false
  }
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  file.value = input.files?.[0] || null
}

function handleCoverChange(event: Event) {
  const input = event.target as HTMLInputElement
  cover.value = input.files?.[0] || null
}

function handleAlbumCoverChange(event: Event) {
  const input = event.target as HTMLInputElement
  albumCoverFile.value = input.files?.[0] || null
  albumCoverPreview.value = albumCoverFile.value ? URL.createObjectURL(albumCoverFile.value) : ''
}

function handleVideoCoverChange(event: Event) {
  const input = event.target as HTMLInputElement
  videoCoverFile.value = input.files?.[0] || null
  videoCoverPreview.value = videoCoverFile.value ? URL.createObjectURL(videoCoverFile.value) : ''
}

// 个人资料相关方法
async function loadProfile() {
  profileLoading.value = true
  try {
    const data = await getMyTeacherProfile()
    profile.value = data
    profileDescription.value = data.description || ''
    profileSubject.value = data.subject || ''
    profileAvatarPreview.value = data.avatar || ''
  } catch (e) {
    // 没有教师资料时不报错，显示空表单
    profile.value = null
  } finally {
    profileLoading.value = false
  }
}

function handleProfileAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement
  profileAvatarFile.value = input.files?.[0] || null
  profileAvatarPreview.value = profileAvatarFile.value ? URL.createObjectURL(profileAvatarFile.value) : ''
}

async function saveProfile() {
  profileSaving.value = true
  try {
    const formData = new FormData()
    formData.append('description', profileDescription.value)
    formData.append('subject', profileSubject.value)
    if (profileAvatarFile.value) {
      formData.append('avatar', profileAvatarFile.value)
    }
    const data = await updateMyTeacherProfile(formData)
    profile.value = data
    profileAvatarFile.value = null
    ElMessage.success('个人资料保存成功')
  } catch (e) {
    ElMessage.error('保存失败，请重试')
  } finally {
    profileSaving.value = false
  }
}

async function handleUpload() {
  if (!form.title.trim()) {
    ElMessage.warning(t('teacher.uploadWarnTitle'))
    return
  }
  if (!file.value) {
    ElMessage.warning(t('teacher.uploadWarnFile'))
    return
  }

  submitting.value = true
  try {
    const data = new FormData()
    data.append('title', form.title.trim())
    data.append('description', form.description.trim())
    if (form.category) data.append('category', String(form.category))
    appendIds(data, 'album_ids', form.album_ids)
    data.append('file', file.value)
    if (cover.value) data.append('cover_image', cover.value)
    await uploadVideo(data)
    ElMessage.success(t('teacher.uploadSuccess'))
    form.title = ''
    form.description = ''
    form.category = undefined
    form.album_ids = []
    file.value = null
    cover.value = null
    if (videoFileInput.value) videoFileInput.value.value = ''
    if (coverFileInput.value) coverFileInput.value.value = ''
    void loadMine()
    activeTab.value = 'courses'
  } finally {
    submitting.value = false
  }
}

function openVideoEdit(video: Video) {
  editingVideoId.value = video.id
  videoForm.title = video.title
  videoForm.description = video.description
  videoForm.category = video.category || undefined
  videoForm.album_ids = (video.albums || []).map((item) => item.id)
  videoCoverFile.value = null
  videoCoverPreview.value = video.cover_image || ''
  if (videoCoverInput.value) videoCoverInput.value.value = ''
  showVideoDialog.value = true
}

async function saveVideo() {
  if (!videoForm.title.trim()) {
    ElMessage.warning(t('teacher.uploadWarnTitle'))
    return
  }
  if (!editingVideoId.value) return
  savingVideo.value = true
  try {
    const data = new FormData()
    data.append('title', videoForm.title.trim())
    data.append('description', videoForm.description.trim())
    if (videoForm.category) data.append('category', String(videoForm.category))
    appendIds(data, 'album_ids', videoForm.album_ids)
    if (videoCoverFile.value) data.append('cover_image', videoCoverFile.value)
    await updateVideo(editingVideoId.value, data)
    ElMessage.success(t('teacher.videoUpdated'))
    showVideoDialog.value = false
    videoCoverFile.value = null
    videoCoverPreview.value = ''
    if (videoCoverInput.value) videoCoverInput.value.value = ''
    void loadMine()
  } finally {
    savingVideo.value = false
  }
}

async function handleDeleteVideo(video: Video) {
  await ElMessageBox.confirm(t('teacher.videoConfirmDelete', { title: video.title }), t('common.delete'), {
    confirmButtonText: t('common.delete'),
    cancelButtonText: t('common.cancel'),
  })
  await deleteVideo(video.id)
  ElMessage.success(t('teacher.videoDeleted'))
  void loadMine()
}

function openCreateAlbum() {
  editingAlbumId.value = null
  albumForm.value = { name: '', description: '' }
  albumCoverFile.value = null
  albumCoverPreview.value = ''
  if (albumCoverInput.value) albumCoverInput.value.value = ''
  showAlbumDialog.value = true
}

function handleEditAlbum(album: VideoAlbum) {
  editingAlbumId.value = album.id
  albumForm.value = { name: album.name, description: album.description }
  albumCoverFile.value = null
  albumCoverPreview.value = album.cover_image || ''
  if (albumCoverInput.value) albumCoverInput.value.value = ''
  showAlbumDialog.value = true
}

async function submitAlbum() {
  if (!albumForm.value.name.trim()) {
    ElMessage.warning(t('teacher.albumWarnName'))
    return
  }
  creatingAlbum.value = true
  try {
    const data = new FormData()
    data.append('name', albumForm.value.name.trim())
    data.append('description', albumForm.value.description.trim())
    if (albumCoverFile.value) data.append('cover_image', albumCoverFile.value)
    if (editingAlbumId.value) {
      await updateAlbum(editingAlbumId.value, data)
      ElMessage.success(t('teacher.albumSaved'))
    } else {
      await createAlbum(data)
      ElMessage.success(t('teacher.albumSuccess'))
    }
    showAlbumDialog.value = false
    editingAlbumId.value = null
    albumForm.value = { name: '', description: '' }
    albumCoverFile.value = null
    albumCoverPreview.value = ''
    if (albumCoverInput.value) albumCoverInput.value.value = ''
    void loadAlbums()
  } finally {
    creatingAlbum.value = false
  }
}

async function handleDeleteAlbum(album: VideoAlbum) {
  await ElMessageBox.confirm(t('teacher.albumConfirmDelete', { name: album.name }), t('teacher.albumDeleteTitle'), {
    confirmButtonText: t('common.delete'),
    cancelButtonText: t('common.cancel'),
  })
  await deleteAlbum(album.id)
  ElMessage.success(t('teacher.albumDeleted'))
  void loadAlbums()
}

function openLiveDialog() {
  liveTitle.value = ''
  liveResult.value = null
  showLiveDialog.value = true
}

async function handleStartPersonalLive() {
  if (!liveTitle.value.trim()) {
    ElMessage.warning(t('teacher.livePersonalPlaceholder'))
    return
  }
  startingLive.value = true
  try {
    liveResult.value = await startPersonalLive(liveTitle.value.trim())
    void loadSessions()
  } finally {
    startingLive.value = false
  }
}

async function copyText(text: string) {
  await navigator.clipboard.writeText(text)
  ElMessage.success(t('teacher.liveCopied'))
}

const stoppingLive = ref(false)

async function handleStopLive(id: number) {
  await ElMessageBox.confirm(t('teacher.liveStopConfirm'), t('teacher.liveStopBtn'), {
    confirmButtonText: t('common.ok'),
    cancelButtonText: t('common.cancel'),
    type: 'warning',
  })
  stoppingLive.value = true
  try {
    await stopPersonalLive(id)
    ElMessage.success(t('teacher.liveStopped'))
    void loadSessions()
  } finally {
    stoppingLive.value = false
  }
}

async function handleDeleteLive(id: number) {
  await ElMessageBox.confirm(t('teacher.liveDeleteConfirm'), t('teacher.liveDeleteBtn'), {
    confirmButtonText: t('common.delete'),
    cancelButtonText: t('common.cancel'),
    type: 'warning',
  })
  await deletePersonalLive(id)
  ElMessage.success(t('teacher.liveDeleted'))
  void loadSessions()
}

onMounted(() => {
  void loadMine()
  void loadCategories()
  void loadSessions()
  void loadAlbums()
  void loadProfile()
})
</script>

<template>
  <div class="teacher-space">
    <div class="space-head">
      <div>
        <h2 class="page-title">{{ t('teacher.title') }}</h2>
        <p class="page-subtitle">{{ t('teacher.subtitle', { username: userStore.username }) }}</p>
      </div>
      <el-button type="primary" @click="activeTab = 'upload'">
        <Upload :size="16" />
        {{ t('teacher.uploadBtn') }}
      </el-button>
    </div>

    <div class="stat-grid">
      <div class="stat-card">
        <BookOpen :size="20" />
        <div><strong>{{ videos.length }}</strong><span>{{ t('teacher.statCourses') }}</span></div>
      </div>
      <div class="stat-card">
        <CalendarClock :size="20" />
        <div><strong>{{ pendingCount }}</strong><span>{{ t('teacher.statPending') }}</span></div>
      </div>
      <div class="stat-card">
        <CirclePlay :size="20" />
        <div><strong>{{ currentLive.length }}</strong><span>{{ t('teacher.statLive') }}</span></div>
      </div>
      <div class="stat-card">
        <MonitorPlay :size="20" />
        <div><strong>{{ albums.length }}</strong><span>{{ t('teacher.statAlbums') }}</span></div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="space-tabs">
      <el-tab-pane :label="t('teacher.tabCourses')" name="courses">
        <div class="page-block">
          <el-table v-loading="loading" :data="videos">
            <el-table-column :label="t('teacher.colCourse')" min-width="260">
              <template #default="{ row }">
                <router-link :to="'/video/' + row.id" class="course-cell">
                  <div class="thumb" :style="row.cover_image ? { backgroundImage: 'url(' + row.cover_image + ')' } : {}" />
                  <div>
                    <span class="course-title">{{ row.title }}</span>
                    <span class="course-sub">{{ categories.find((item) => item.id === row.category)?.name || t('teacher.unclassified') }}</span>
                  </div>
                </router-link>
              </template>
            </el-table-column>
            <el-table-column :label="t('teacher.colStatus')" width="110">
              <template #default="{ row }">
                <el-tag :type="statusTagType[row.status] || 'info'">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('teacher.colDuration')" width="100">
              <template #default="{ row }">{{ formatDuration(row.duration) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.colSize')" width="110">
              <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.colTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.colAction')" width="220">
              <template #default="{ row }">
                <div class="action-btns">
                  <router-link :to="'/video/' + row.id" class="action-link">{{ t('teacher.view') }}</router-link>
                  <el-button type="primary" size="small" @click="openVideoEdit(row)">{{ t('common.edit') }}</el-button>
                  <el-button type="danger" size="small" @click="handleDeleteVideo(row)">{{ t('common.delete') }}</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && videos.length === 0" :description="t('teacher.emptyCourses')" />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('teacher.tabUpload')" name="upload">
        <div class="page-block upload-block">
          <el-form label-position="top">
            <el-form-item :label="t('teacher.uploadTitle')">
              <el-input v-model="form.title" :placeholder="t('teacher.uploadTitle')" />
            </el-form-item>
            <el-form-item :label="t('teacher.uploadCategory')">
              <el-select v-model="form.category" :placeholder="t('teacher.uploadCategory')" clearable>
                <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('teacher.videoAlbumLabel')">
              <el-select v-model="form.album_ids" multiple :placeholder="t('teacher.videoAlbumPlaceholder')">
                <el-option v-for="item in albums" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('teacher.uploadDesc')">
              <el-input v-model="form.description" type="textarea" :rows="4" :placeholder="t('teacher.uploadDesc')" />
            </el-form-item>
            <el-form-item :label="t('teacher.uploadFile')">
              <label class="file-picker">
                <Upload :size="20" />
                <span>{{ file?.name || t('teacher.uploadPick') }}</span>
                <input ref="videoFileInput" type="file" accept=".mp4,.mkv,.mov" hidden @change="handleFileChange" />
              </label>
            </el-form-item>
            <el-form-item :label="t('teacher.uploadCover')">
              <label class="file-picker">
                <ImagePlus :size="20" />
                <span>{{ cover?.name || t('teacher.uploadCoverPick') }}</span>
                <input ref="coverFileInput" type="file" accept=".jpg,.jpeg,.png,.webp" hidden @change="handleCoverChange" />
              </label>
            </el-form-item>
            <el-button type="primary" :loading="submitting" @click="handleUpload">{{ t('teacher.uploadSubmit') }}</el-button>
          </el-form>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('teacher.tabLive')" name="live">
        <div class="page-block">
          <div class="tab-toolbar">
            <el-button type="primary" @click="openLiveDialog">
              <Radio :size="16" />
              {{ t('teacher.livePersonalStart') }}
            </el-button>
          </div>
          <h3 class="section-title">{{ t('teacher.liveCurrent') }}</h3>
          <el-table v-loading="loadingSessions" :data="currentLive">
            <el-table-column prop="title" :label="t('teacher.liveColTitle')" min-width="220" />
            <el-table-column :label="t('teacher.liveColRoom')" width="160">
              <template #default="{ row }">{{ row.school_name || '-' }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.colStatus')" width="110">
              <template #default="{ row }"><el-tag type="danger">{{ t('status.live') }}</el-tag></template>
            </el-table-column>
            <el-table-column :label="t('teacher.liveColStart')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.start_time) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.colAction')" width="180">
              <template #default="{ row }">
                <router-link v-if="row.hls_url" to="/live">{{ t('teacher.liveWatch') }}</router-link>
                <el-button size="small" type="danger" link :loading="stoppingLive" @click="handleStopLive(row.id)">{{ t('teacher.liveStopBtn') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingSessions && currentLive.length === 0" :description="t('teacher.liveEmptyCurrent')" />

          <h3 class="section-title history-title">{{ t('teacher.liveHistory') }}</h3>
          <el-table :data="historyLive">
            <el-table-column prop="title" :label="t('teacher.liveColTitle')" min-width="220" />
            <el-table-column :label="t('teacher.liveColRoom')" width="160">
              <template #default="{ row }">{{ row.school_name || '-' }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.colStatus')" width="110">
              <template #default="{ row }">
                <el-tag :type="row.status === 'stopped' || row.status === 'error' ? 'info' : 'warning'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('teacher.liveColStart')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.start_time) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.liveColEnd')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.end_time) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.colAction')" width="100">
              <template #default="{ row }">
                <el-button size="small" type="danger" link @click="handleDeleteLive(row.id)">{{ t('teacher.liveDeleteBtn') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="historyLive.length === 0" :description="t('teacher.liveEmptyHistory')" />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('teacher.tabAlbums')" name="albums">
        <div class="page-block">
          <div class="tab-toolbar">
            <el-button type="primary" @click="openCreateAlbum">{{ t('teacher.albumCreate') }}</el-button>
          </div>
          <el-table v-loading="loadingAlbums" :data="albums">
            <el-table-column :label="t('teacher.albumCoverColumn')" width="110">
              <template #default="{ row }">
                <div class="album-cover" :style="row.cover_image ? { backgroundImage: 'url(' + row.cover_image + ')' } : {}" />
              </template>
            </el-table-column>
            <el-table-column prop="name" :label="t('teacher.albumName')" min-width="180" />
            <el-table-column prop="description" :label="t('teacher.albumDesc')" min-width="220" show-overflow-tooltip />
            <el-table-column :label="t('teacher.albumCount')" width="90">
              <template #default="{ row }">{{ row.videos?.length || 0 }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.albumTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column :label="t('teacher.albumAction')" width="180">
              <template #default="{ row }">
                <div class="action-btns">
                  <el-button type="primary" size="small" @click="handleEditAlbum(row)">{{ t('common.edit') }}</el-button>
                  <el-button type="danger" size="small" @click="handleDeleteAlbum(row)">{{ t('common.delete') }}</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingAlbums && albums.length === 0" :description="t('teacher.albumEmpty')" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="个人资料" name="profile">
        <div class="page-block profile-block" v-loading="profileLoading">
          <div class="profile-form">
            <div class="profile-avatar-section">
              <div class="avatar-wrapper">
                <img v-if="profileAvatarPreview" :src="profileAvatarPreview" class="profile-avatar" alt="头像" />
                <div v-else class="profile-avatar-placeholder">
                  <User :size="48" />
                </div>
              </div>
              <div class="avatar-actions">
                <label class="upload-avatar-btn">
                  <ImagePlus :size="16" />
                  <span>上传头像</span>
                  <input type="file" accept=".jpg,.jpeg,.png,.webp" hidden @change="handleProfileAvatarChange" />
                </label>
                <p class="avatar-tip">支持 JPG、PNG 格式，建议尺寸 200×200</p>
              </div>
            </div>

            <el-form label-position="top" class="profile-info-form">
              <el-form-item label="任教科目">
                <el-input v-model="profileSubject" placeholder="请输入任教科目" />
              </el-form-item>
              <el-form-item label="个人简介">
                <el-input
                  v-model="profileDescription"
                  type="textarea"
                  :rows="6"
                  placeholder="请输入个人简介，介绍您的教学经历、专业领域等"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="profileSaving" @click="saveProfile">
                  保存资料
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showVideoDialog" :title="t('teacher.videoEditTitle')" width="560px">
      <el-form label-position="top">
        <el-form-item :label="t('teacher.uploadTitle')">
          <el-input v-model="videoForm.title" :placeholder="t('teacher.uploadTitle')" />
        </el-form-item>
        <el-form-item :label="t('teacher.uploadCategory')">
          <el-select v-model="videoForm.category" :placeholder="t('teacher.uploadCategory')" clearable>
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('teacher.videoAlbumLabel')">
          <el-select v-model="videoForm.album_ids" multiple :placeholder="t('teacher.videoAlbumPlaceholder')" class="album-select">
            <el-option v-for="item in albums" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('teacher.uploadCover')">
          <label class="file-picker cover-picker">
            <img v-if="videoCoverPreview" :src="videoCoverPreview" class="cover-preview" alt="" />
            <template v-else>
              <ImagePlus :size="20" />
              <span>{{ videoCoverFile?.name || t('teacher.uploadCoverPick') }}</span>
            </template>
            <input ref="videoCoverInput" type="file" accept=".jpg,.jpeg,.png,.webp" hidden @change="handleVideoCoverChange" />
          </label>
        </el-form-item>
        <el-form-item :label="t('teacher.uploadDesc')">
          <el-input v-model="videoForm.description" type="textarea" :rows="4" :placeholder="t('teacher.uploadDesc')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showVideoDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="savingVideo" @click="saveVideo">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showLiveDialog" :title="t('teacher.livePersonalStart')" width="760px">
      <div v-if="!liveResult">
        <el-form label-position="top">
          <el-form-item :label="t('teacher.livePersonalTitle')">
            <el-input v-model="liveTitle" :placeholder="t('teacher.livePersonalPlaceholder')" />
          </el-form-item>
        </el-form>
      </div>
      <div v-else class="push-info">
        <p class="obs-hint">{{ t('teacher.liveObsHint', { server: obsServer }) }}</p>
        <div class="push-row">
          <span>{{ t('teacher.livePushUrl') }}</span>
          <code>{{ liveResult.stream_url }}</code>
          <el-button size="small" @click="copyText(liveResult.stream_url)">{{ t('teacher.liveCopy') }}</el-button>
        </div>
        <div class="push-row">
          <span>{{ t('teacher.livePushKey') }}</span>
          <code>{{ liveResult.stream_key }}</code>
          <el-button size="small" @click="copyText(liveResult.stream_key)">{{ t('teacher.liveCopy') }}</el-button>
        </div>
        <div class="push-row">
          <span>{{ t('teacher.liveWatchUrl') }}</span>
          <code>{{ liveResult.hls_url }}</code>
          <el-button size="small" @click="copyText(liveResult.hls_url)">{{ t('teacher.liveCopy') }}</el-button>
        </div>
      </div>
      <template #footer>
        <el-button v-if="!liveResult" @click="showLiveDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="!liveResult" type="primary" :loading="startingLive" @click="handleStartPersonalLive">{{ t('teacher.livePersonalBtn') }}</el-button>
        <el-button v-else type="primary" @click="showLiveDialog = false">{{ t('common.ok') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAlbumDialog" :title="editingAlbumId ? t('teacher.albumDialogEditTitle') : t('teacher.albumDialogTitle')" width="480px">
      <el-form label-position="top">
        <el-form-item :label="t('teacher.albumNameLabel')">
          <el-input v-model="albumForm.name" :placeholder="t('teacher.albumName')" />
        </el-form-item>
        <el-form-item :label="t('teacher.albumDescLabel')">
          <el-input v-model="albumForm.description" type="textarea" :rows="3" :placeholder="t('teacher.albumDesc')" />
        </el-form-item>
        <el-form-item :label="t('teacher.albumCoverLabel')">
          <label class="file-picker cover-picker">
            <img v-if="albumCoverPreview" :src="albumCoverPreview" class="cover-preview" alt="" />
            <template v-else>
              <ImagePlus :size="20" />
              <span>{{ albumCoverFile?.name || t('teacher.albumCoverPick') }}</span>
            </template>
            <input ref="albumCoverInput" type="file" accept=".jpg,.jpeg,.png,.webp" hidden @change="handleAlbumCoverChange" />
          </label>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAlbumDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="creatingAlbum" @click="submitAlbum">{{ editingAlbumId ? t('common.save') : t('common.create') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.space-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 8px;
  color: var(--platform-primary);
}

.stat-card div {
  display: flex;
  flex-direction: column;
}

.stat-card strong {
  font-size: 20px;
  color: var(--platform-text);
  line-height: 1.2;
}

.stat-card span {
  font-size: 13px;
  color: var(--platform-muted);
}

.space-tabs .page-block {
  padding-top: 20px;
}

.section-title {
  margin: 0 0 12px;
  font-size: 16px;
  letter-spacing: 0;
}

.history-title {
  margin-top: 26px;
}

.course-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.thumb {
  width: 96px;
  height: 54px;
  flex: none;
  border-radius: 6px;
  background: #dbe5e3;
  background-size: cover;
  background-position: center;
}

.album-cover {
  width: 80px;
  height: 46px;
  border-radius: 6px;
  background: #dbe5e3;
  background-size: cover;
  background-position: center;
}

.course-cell .course-title,
.course-cell .course-sub {
  display: block;
}

.course-title {
  font-weight: 600;
  color: var(--platform-text);
}

.course-sub {
  margin-top: 4px;
  font-size: 13px;
  color: var(--platform-muted);
}

.tab-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 14px;
}

.upload-block {
  max-width: 640px;
}

.upload-block .el-select,
.album-select {
  width: 100%;
}

.file-picker {
  width: 100%;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px dashed var(--platform-line);
  border-radius: 8px;
  color: var(--platform-muted);
  cursor: pointer;
}

.file-picker:hover {
  border-color: var(--platform-primary);
  color: var(--platform-primary);
}

.cover-preview {
  max-height: 120px;
  max-width: 100%;
  border-radius: 6px;
}

.action-btns {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.action-link {
  color: var(--platform-primary);
  font-size: 13px;
  text-decoration: none;
}

.action-link:hover {
  text-decoration: underline;
}

@media (max-width: 900px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* 个人资料 */
.profile-block {
  max-width: 600px;
}

.profile-form {
  padding: 20px 0;
}

.profile-avatar-section {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--platform-line);
}

.avatar-wrapper {
  flex-shrink: 0;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--platform-panel);
  box-shadow: var(--shadow-sm);
}

.profile-avatar-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--grad-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.avatar-actions {
  padding-top: 8px;
}

.upload-avatar-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--platform-primary);
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.upload-avatar-btn:hover {
  opacity: 0.9;
}

.avatar-tip {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--platform-muted);
}

.profile-info-form {
  margin-top: 24px;
}
</style>

.push-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.obs-hint {
  margin: 0 0 4px;
  font-size: 12px;
  color: var(--platform-muted);
}

.push-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.push-row span {
  width: 84px;
  flex: none;
  font-size: 13px;
  color: var(--platform-muted);
}

.push-row code {
  flex: 1;
  min-width: 0;
  overflow-wrap: anywhere;
  font-size: 12px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 6px;
  padding: 6px 8px;
}

.push-row .el-button {
  flex: none;
}
