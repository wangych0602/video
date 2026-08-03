<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Languages } from 'lucide-vue-next'
import { setLocale, type SupportedLocale } from '@/i18n'

const { locale } = useI18n()

const languages: { value: SupportedLocale; label: string }[] = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-TW', label: '繁體中文' },
  { value: 'en-US', label: 'English' },
  { value: 'ko-KR', label: '한국어' },
  { value: 'vi-VN', label: 'Tiếng Việt' },
  { value: 'ru-RU', label: 'Русский' },
  { value: 'ms-MY', label: 'Bahasa Melayu' },
]

const currentLabel = computed(() => languages.find((item) => item.value === locale.value)?.label || '简体中文')

function handleLanguage(command: string | number | object) {
  setLocale(String(command) as SupportedLocale)
}
</script>

<template>
  <el-dropdown @command="handleLanguage">
    <button class="language-btn" type="button">
      <Languages :size="18" />
      <span>{{ currentLabel }}</span>
    </button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item v-for="item in languages" :key="item.value" :command="item.value">
          {{ item.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>
