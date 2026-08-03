<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getLiveSessions } from '@/api/live'
import type { LiveSession } from '@/api/types'
import LivePlayer from '@/components/LivePlayer.vue'
import { formatDateTime } from '@/utils/format'
import { Radio, Monitor, Clock, Video } from 'lucide-vue-next'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const sessions = ref<LiveSession[]>([])
const selectedId = ref<number | null>(null)
const loading = ref(false)

const selected = computed(() => sessions.value.find((s) => s.id === selectedId.value) || sessions.value[0] || null)

const statusLabel = (key: string) => t('status.' + key)

function switchSession(id: number) {
  if (id === selectedId.value) return
  selectedId.value = id
  router.replace({ query: { session: id } })
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await getLiveSessions({ status: 'live' })
    sessions.value = data.results
    const queryId = Number(route.query.session)
    selectedId.value = sessions.value.some((s) => s.id === queryId)
      ? queryId
      : sessions.value[0]?.id ?? null
  } catch {
    // handled by axios interceptor
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-block">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ t('live.title') }}</h2>
        <p class="page-subtitle">{{ t('live.subtitle') }}</p>
      </div>
    </div>

    <div v-loading="loading" class="live-content">
      <template v-if="selected">
        <div class="live-stage">
          <!-- 播放器面板 -->
          <div class="player-panel">
            <div class="player-head">
              <div class="live-badge">
                <span class="dot" />
                <Radio :size="14" />
                {{ statusLabel(selected.status) }}
              </div>
              <h3>{{ selected.title }}</h3>
              <div class="player-meta">
                <span v-if="selected.school_name" class="meta-item">
                  <Monitor :size="15" />
                  {{ selected.school_name }}
                </span>
                <span class="meta-item">
                  <Video :size="15" />
                  {{ selected.device_name }}
                </span>
                <span class="meta-item">
                  <Clock :size="15" />
                  {{ formatDateTime(selected.start_time) }}
                </span>
              </div>
            </div>
            <div v-if="selected.hls_url" class="player-wrap">
              <LivePlayer :key="selected.id" :src="selected.hls_url" />
            </div>
            <div v-else class="no-stream">
              <Video :size="48" :stroke-width="1.2" />
              <p>{{ t('live.noAddress') }}</p>
            </div>
          </div>

          <!-- 直播间列表 -->
          <div v-if="sessions.length" class="session-list">
            <h4 class="session-head">
              <Radio :size="16" />
              {{ t('live.rooms') }}
              <span class="session-count">{{ sessions.length }}</span>
            </h4>
            <div class="session-scroll">
              <button
                v-for="session in sessions"
                :key="session.id"
                class="session-item"
                :class="{ active: session.id === selected.id }"
                @click="switchSession(session.id)"
              >
                <span class="session-dot" :class="{ live: session.status === 'live' }" />
                <div class="session-text">
                  <strong>{{ session.title }}</strong>
                  <span>{{ session.school_name || '-' }} · {{ statusLabel(session.status) }}</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <div class="empty-icon">
          <Radio :size="56" :stroke-width="1" />
        </div>
        <h3>{{ t('live.empty') }}</h3>
        <p>{{ t('live.emptyDesc') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.live-content {
  min-height: 320px;
}

/* ===== 主舞台布局 ===== */
.live-stage {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.player-panel {
  flex: 1;
  min-width: 0;
  padding: 22px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 18px;
  box-shadow: var(--shadow-sm);
}

/* ===== 播放器头部 ===== */
.player-head {
  margin-bottom: 18px;
}

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  padding: 0 14px;
  border-radius: 999px;
  background: #fee2e2;
  color: #b91c1c;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 14px;
}

.live-badge .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #dc2626;
  animation: live-pulse 1.8s infinite;
}

.player-head h3 {
  margin: 0 0 12px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.3;
}

.player-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  color: var(--platform-muted);
  font-size: 13px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* ===== 播放器容器 ===== */
.player-wrap {
  overflow: hidden;
  border-radius: 14px;
  background: #0f172a;
  aspect-ratio: 16 / 9;
  min-height: 360px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.24);
}

.no-stream {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  aspect-ratio: 16 / 9;
  min-height: 360px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  color: var(--platform-muted);
}

.no-stream p {
  margin: 0;
  font-size: 14px;
}

/* ===== 直播间列表 ===== */
.session-list {
  width: 300px;
  flex: none;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 18px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.session-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 16px 18px;
  font-size: 15px;
  font-weight: 700;
  border-bottom: 1px solid var(--platform-line);
  color: var(--platform-text);
}

.session-count {
  margin-left: auto;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
  font-size: 12px;
  font-weight: 700;
}

.session-scroll {
  max-height: 540px;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
  color: var(--platform-text);
  text-align: left;
  cursor: pointer;
  transition: background 0.18s ease, border-color 0.18s ease;
}

.session-item:hover {
  background: var(--platform-primary-soft);
}

.session-item.active {
  background: var(--platform-primary-soft);
  border-color: var(--platform-primary);
}

.session-dot {
  width: 10px;
  height: 10px;
  flex: none;
  border-radius: 50%;
  background: #cbd5e1;
}

.session-dot.live {
  background: #dc2626;
  animation: live-pulse 1.8s infinite;
}

.session-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.session-text strong {
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-text span {
  font-size: 12px;
  color: var(--platform-muted);
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
  margin-bottom: 12px;
}

.empty-state h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.empty-state p {
  margin: 0;
  color: var(--platform-muted);
  font-size: 14px;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .live-stage {
    flex-direction: column;
  }

  .session-list {
    width: 100%;
  }

  .session-scroll {
    max-height: none;
  }
}
</style>
