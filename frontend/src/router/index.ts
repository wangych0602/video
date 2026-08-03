import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'
import Layout from '@/layouts/Layout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/Home.vue'),
          meta: { public: true },
        },
        {
          path: 'videos',
          name: 'videos',
          component: () => import('@/views/Videos.vue'),
          meta: { public: true },
        },
        {
          path: 'video/:id',
          name: 'video-detail',
          component: () => import('@/views/VideoDetail.vue'),
          props: true,
          meta: { public: true },
        },
        {
          path: 'teacher/ai',
          name: 'teacher-ai',
          component: () => import('@/views/TeacherAI.vue'),
        },
        {
          path: 'teacher/:id',
          name: 'teacher-profile',
          component: () => import('@/views/TeacherProfile.vue'),
          props: true,
          meta: { public: true },
        },
        {
          path: 'teacher',
          name: 'teacher',
          component: () => import('@/views/Teacher.vue'),
        },
        {
          path: 'live',
          name: 'live',
          component: () => import('@/views/Live.vue'),
          meta: { public: true },
        },
        {
          path: 'albums',
          name: 'albums',
          component: () => import('@/views/Albums.vue'),
          meta: { public: true },
        },
        {
          path: 'studio',
          name: 'studio',
          component: () => import('@/views/TeacherStudio.vue'),
          meta: { public: true },
        },
        {
          path: 'album/:id',
          name: 'album-detail',
          component: () => import('@/views/AlbumDetail.vue'),
          props: true,
          meta: { public: true },
        },
        
        {
          path: 'ai-analytics',
          name: 'ai-analytics',
          component: () => import('@/views/AIAnalytics.vue'),
        },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('@/views/Admin.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach((to) => {
  if (!to.meta.public && !getToken()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
