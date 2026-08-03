<template>
  <footer class="site-footer">
    <div class="footer-content">
      <div v-if="config.footer_text" class="footer-text">
        {{ config.footer_text }}
      </div>
      <div class="footer-bottom">
        <span v-if="config.footer_copyright" class="copyright">
          {{ config.footer_copyright }}
        </span>
        <a v-if="config.footer_icp" :href="'https://beian.miit.gov.cn/'" target="_blank" class="icp">
          {{ config.footer_icp }}
        </a>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSiteConfig, type SiteConfig } from '../api/system'

const config = ref<SiteConfig>({
  site_name: '',
  site_description: '',
  default_language: 'zh-hans',
  contact_email: '',
  registration_enabled: true,
  footer_text: '',
  footer_copyright: '',
  footer_icp: '',
})

onMounted(async () => {
  try {
    const data = await getSiteConfig()
    config.value = data
  } catch (e) {
    console.error('Failed to load site config:', e)
  }
})
</script>

<style scoped>
.site-footer {
  background: var(--color-panel);
  border-top: 1px solid var(--color-border);
  padding: 32px 0 24px;
  margin-top: 48px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  text-align: center;
}

.footer-text {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
}

.footer-bottom {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.copyright {
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.icp {
  color: var(--color-text-tertiary);
  font-size: 13px;
  text-decoration: none;
  transition: color 0.2s ease;
}

.icp:hover {
  color: var(--color-primary);
}
</style>