import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  clearAuth,
  getToken,
  getUser,
  setToken,
  setUser,
  type StoredUser,
} from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(getToken())
  const username = ref('')
  const role = ref('guest')
  const school = ref('')

  const stored = getUser()
  if (stored) {
    username.value = stored.username
    role.value = stored.role
    school.value = stored.school
  }

  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => role.value === 'admin' || role.value === 'school_admin')
  const isTeacher = computed(() => role.value === 'teacher')

  function login(newToken: string, user: StoredUser) {
    token.value = newToken
    username.value = user.username
    role.value = user.role
    school.value = user.school
    setToken(newToken)
    setUser(user)
  }

  function logout() {
    token.value = null
    username.value = ''
    role.value = 'guest'
    school.value = ''
    clearAuth()
  }

  return {
    token,
    username,
    role,
    school,
    isAuthenticated,
    isAdmin,
    isTeacher,
    login,
    logout,
  }
})
