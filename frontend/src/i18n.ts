import { computed } from 'vue'
import { createI18n } from 'vue-i18n'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import zhTw from 'element-plus/es/locale/lang/zh-tw'
import en from 'element-plus/es/locale/lang/en'
import ko from 'element-plus/es/locale/lang/ko'
import vi from 'element-plus/es/locale/lang/vi'
import ru from 'element-plus/es/locale/lang/ru'
import ms from 'element-plus/es/locale/lang/ms'
import zhCN from './locales/zh-CN.json'
import zhTW from './locales/zh-TW.json'
import enUS from './locales/en-US.json'
import koKR from './locales/ko-KR.json'
import viVN from './locales/vi-VN.json'
import ruRU from './locales/ru-RU.json'
import msMY from './locales/ms-MY.json'

export const LOCALE_STORAGE_KEY = 'platform_locale'
export const SUPPORTED_LOCALES = ['zh-CN', 'zh-TW', 'en-US', 'ko-KR', 'vi-VN', 'ru-RU', 'ms-MY'] as const
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number]

const messages = {
  'zh-CN': zhCN,
  'zh-TW': zhTW,
  'en-US': enUS,
  'ko-KR': koKR,
  'vi-VN': viVN,
  'ru-RU': ruRU,
  'ms-MY': msMY,
}

function getInitialLocale(): string {
  const saved = localStorage.getItem(LOCALE_STORAGE_KEY)
  if (saved && SUPPORTED_LOCALES.includes(saved as SupportedLocale)) return saved
  return 'zh-CN'
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: getInitialLocale(),
  fallbackLocale: 'zh-CN',
  messages,
})

export function setLocale(locale: SupportedLocale) {
  i18n.global.locale.value = locale
  localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  document.documentElement.lang = locale
}

const elementLocales: Record<string, typeof zhCn> = {
  'zh-CN': zhCn,
  'zh-TW': zhTw,
  'en-US': en,
  'ko-KR': ko,
  'vi-VN': vi,
  'ru-RU': ru,
  'ms-MY': ms,
}

export const elementLocale = computed(() => elementLocales[i18n.global.locale.value] || zhCn)

export default i18n
