<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { MonitorPlay } from 'lucide-vue-next'

const { t } = useI18n()
</script>

<template>
  <div class="app-logo">
    <MonitorPlay :size="26" />
    <span>{{ t('app.brandMain') }}<span>{{ t('app.brandAccent') }}</span></span>
  </div>
</template>
