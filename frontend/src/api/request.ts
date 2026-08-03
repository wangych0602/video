import axios, {
  type AxiosError,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import i18n from '@/i18n'
import { clearAuth, getToken } from '@/utils/auth'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<{ message?: string }>) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.message || i18n.global.t('error.requestFailed')

    if (status === 401) {
      clearAuth()
      ElMessage.error(i18n.global.t('error.sessionExpired'))
      void router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
    } else if (status === 403) {
      ElMessage.error(i18n.global.t('error.forbidden'))
    } else {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  },
)

export default request
