<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { BarChart3, BookOpen, ChevronDown, Cpu, GraduationCap, Home, LayoutDashboard, MonitorPlay, Play, Radio, Search, Settings, Video } from 'lucide-vue-next'
import LanguageSwitch from '@/components/LanguageSwitch.vue'
import { searchStudio } from '@/api/studio'
import type { SearchResult } from '@/api/types'
import { useUserStore } from '@/stores/user'
import Footer from '@/components/Footer.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const userStore = useUserStore()

const menus = computed(() => {
  const role = userStore.role
  const items = [
    { path: '/', label: t('nav.home'), icon: Home },
    { path: '/videos', label: t('nav.videos'), icon: Video },
    { path: '/albums', label: t('nav.albums'), icon: BookOpen },
    { path: '/live', label: t('nav.live'), icon: Radio },
    { path: '/studio', label: t('nav.studio'), icon: GraduationCap },
  ]
  if (role === 'admin' || role === 'school_admin' || role === 'teacher') {
    items.push({ path: '/teacher', label: t('nav.teacher'), icon: LayoutDashboard })
  }
  if (role === 'teacher') {
      items.push({ path: '/teacher/ai', label: t('nav.aiAnalysis'), icon: Cpu })
  }
  if (role === 'admin' || role === 'school_admin') {
      items.push({ path: '/ai-analytics', label: t('nav.aiAnalytics'), icon: BarChart3 })
  }
  return items
})

const showUserMenu = ref(false)

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function goAdmin() {
  showUserMenu.value = false
  window.open('/admin/', '_blank')
}

const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/video/')) return '/videos'
  if (p.startsWith('/album')) return '/albums'
  if (p.startsWith('/teacher/ai')) return '/teacher/ai'
  if (p.startsWith('/teacher/')) return '/studio'
  if (p.startsWith('/teacher')) return '/teacher'
  return p
})

function handleLogout() {
  userStore.logout()
  void router.push('/login')
}

const searchQuery = ref('')
const searchResults = ref<SearchResult>({ videos: [], albums: [], teachers: [] })
const showSearch = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

async function doSearch() {
  const q = searchQuery.value.trim()
  if (!q) {
    searchResults.value = { videos: [], albums: [], teachers: [] }
    showSearch.value = false
    return
  }
  try {
    searchResults.value = await searchStudio(q)
    showSearch.value = true
  } catch {
    // ignore
  }
}

function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(doSearch, 300)
}

function goVideo(id: number) {
  showSearch.value = false
  searchQuery.value = ''
  void router.push(`/video/${id}`)
}

function goAlbum(id: number) {
  showSearch.value = false
  searchQuery.value = ''
  void router.push(`/album/${id}`)
}

function goTeacher(id: number) {
  showSearch.value = false
  searchQuery.value = ''
  void router.push(`/teacher/${id}`)
}

function goStudio() {
  showSearch.value = false
  searchQuery.value = ''
  void router.push('/studio')
}

onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer)
})

const showMobileMenu = ref(false)
</script>

<template>
  <div class="top-layout">
    <header class="top-nav">
      <div class="nav-inner">
        <router-link to="/" class="brand">
          <MonitorPlay :size="22" />
          <span>{{ t('app.brandMain') }}<span class="accent">{{ t('app.brandAccent') }}</span></span>
        </router-link>

        <button class="mobile-menu-btn" @click="showMobileMenu = !showMobileMenu" aria-label="Toggle menu">
          <span class="hamburger" />
        </button>

        <nav class="nav-links" :class="{ open: showMobileMenu }">
          <router-link
            v-for="m in menus"
            :key="m.path"
            :to="m.path"
            class="nav-link"
            :class="{ active: activeMenu === m.path }"
            @click="showMobileMenu = false"
          >
            {{ m.label }}
          </router-link>
        </nav>

        <div class="search-box" @focusin="showSearch = !!searchQuery">
          <Search :size="16" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="t('nav.search')"
            @input="onSearchInput"
            @keydown.enter="doSearch"
          />
          <div v-if="showSearch" class="search-dropdown">
            <div v-if="searchResults.videos.length" class="search-section">
              <h4>{{ t('nav.sectionVideos') }}</h4>
              <div
                v-for="v in searchResults.videos"
                :key="v.id"
                class="search-item"
                @click="goVideo(v.id)"
              >
                <Play :size="14" />
                <span>{{ v.title }}</span>
              </div>
            </div>
            <div v-if="searchResults.albums.length" class="search-section">
              <h4>{{ t('nav.sectionAlbums') }}</h4>
              <div
                v-for="a in searchResults.albums"
                :key="a.id"
                class="search-item"
                @click="goAlbum(a.id)"
              >
                <Video :size="14" />
                <span>{{ a.name }}</span>
              </div>
            </div>
            <div v-if="searchResults.teachers.length" class="search-section">
              <h4>{{ t('nav.sectionTeachers') }}</h4>
              <div
                v-for="tm in searchResults.teachers"
                :key="tm.id"
                class="search-item"
                @click="goTeacher(tm.id)"
              >
                <GraduationCap :size="14" />
                <span>{{ tm.first_name || tm.username }}</span>
              </div>
            </div>
            <p
              v-if="!searchResults.videos.length && !searchResults.albums.length && !searchResults.teachers.length"
              class="search-empty"
            >
              {{ t('nav.noResult') }}
            </p>
          </div>
        </div>

        <div class="nav-right">
          <LanguageSwitch />
          <template v-if="userStore.isAuthenticated">
            <div class="user-menu" @click="toggleUserMenu">
              <span class="user-label">{{ userStore.username }}</span>
              <ChevronDown :size="14" />
              <div v-if="showUserMenu" class="user-dropdown">
                <div v-if="userStore.role === 'admin'" class="user-dropdown-item" @click.stop="goAdmin">
                  <Settings :size="14" />
                  <span>{{ t('nav.admin') }}</span>
                </div>
                <div class="user-dropdown-item" @click.stop="handleLogout">
                  <span>{{ t('nav.logout') }}</span>
                </div>
              </div>
            </div>
          </template>
          <router-link v-else to="/login" class="login-link">{{ t('nav.login') }}</router-link>
        </div>
      </div>
    </header>
    <main class="top-main">
      <router-view />
    </main>
  

    <Footer />
</div>
</template>

<style scoped>
.top-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: saturate(180%) blur(12px);
  -webkit-backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--platform-line);
  box-shadow: 0 1px 0 rgba(15, 23, 42, 0.02);
}

.nav-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
  height: 56px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--platform-text);
  font-weight: 800;
  font-size: 16px;
  white-space: nowrap;
  text-decoration: none;
}

.brand :deep(svg) {
  padding: 5px;
  width: 30px;
  height: 30px;
  border-radius: 9px;
  color: #fff;
  background: var(--grad-primary);
  box-shadow: var(--shadow-primary);
}

.brand .accent {
  color: var(--platform-accent);
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  padding: 4px;
}

.hamburger {
  display: block;
  width: 20px;
  height: 2px;
  background: var(--platform-text);
  position: relative;
}

.hamburger::before,
.hamburger::after {
  content: "";
  position: absolute;
  width: 20px;
  height: 2px;
  background: var(--platform-text);
}

.hamburger::before { top: -6px; }
.hamburger::after { top: 6px; }

.nav-links {
  display: flex;
  align-items: center;
  gap: 2px;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--platform-muted);
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.18s ease, color 0.18s ease;
}

.nav-link:hover {
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
}

.nav-link.active {
  background: var(--grad-primary);
  color: #fff;
  box-shadow: var(--shadow-primary);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 12px;
  margin-left: auto;
  border: 1px solid var(--platform-line);
  border-radius: 10px;
  background: var(--platform-bg);
  color: var(--platform-muted);
  width: 260px;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.search-box:focus-within {
  border-color: var(--platform-primary);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.12);
}

.search-box input {
  outline: none;
  border: none;
  background: transparent;
  width: 100%;
  color: var(--platform-text);
  font-size: 14px;
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 14px;
  box-shadow: var(--shadow-lg);
  max-height: 400px;
  overflow-y: auto;
  z-index: 200;
  padding: 6px;
}

.search-section h4 {
  margin: 0;
  padding: 10px 14px 4px;
  font-size: 12px;
  color: var(--platform-muted);
  font-weight: 600;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  font-size: 13px;
  color: var(--platform-text);
  cursor: pointer;
  border-radius: 9px;
}

.search-item:hover {
  background: var(--platform-primary-soft);
}

.search-empty {
  padding: 14px;
  text-align: center;
  color: var(--platform-muted);
  font-size: 13px;
  margin: 0;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--platform-muted);
}

.nav-right :deep(.language-btn) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  border: 1px solid var(--platform-line);
  border-radius: 10px;
  background: var(--platform-bg);
  color: var(--platform-muted);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
}

.nav-right :deep(.language-btn:hover) {
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
  border-color: var(--platform-primary);
}

.user-menu {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  cursor: pointer;
  color: var(--platform-muted);
  font-weight: 500;
  transition: background 0.18s ease, color 0.18s ease;
}

.user-menu:hover {
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 140px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  z-index: 200;
  padding: 6px;
}

.user-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--platform-text);
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.15s ease;
}

.user-dropdown-item:hover {
  background: var(--platform-primary-soft);
  color: var(--platform-primary);
}

.login-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  padding: 0 16px;
  border-radius: 10px;
  background: var(--grad-primary);
  color: #fff;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  box-shadow: var(--shadow-primary);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.login-link:hover {
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(15, 118, 110, 0.32);
}

.top-main {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 28px 20px 40px;
}

@media (max-width: 900px) {
  .mobile-menu-btn {
    display: block;
  }

  .nav-links {
    display: none;
    position: absolute;
    top: 52px;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: stretch;
    background: var(--platform-panel);
    border-bottom: 1px solid var(--platform-line);
    padding: 8px 12px;
    z-index: 99;
  }

  .nav-links.open {
    display: flex;
  }

  .search-box {
    max-width: 200px;
  }

  .top-main {
    padding: 16px 12px;
  }
}
</style>
