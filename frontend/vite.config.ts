import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        xfwd: true,
      },
      '/admin': {
        target: 'http://backend:8000',
        changeOrigin: true,
        xfwd: true,
      },
      '/media': {
        target: 'http://backend:8000',
        changeOrigin: true,
        xfwd: true,
      },
      '/static': {
        target: 'http://backend:8000',
        changeOrigin: true,
        xfwd: true,
      },
      '/i18n': {
        target: 'http://backend:8000',
        changeOrigin: true,
        xfwd: true,
      },
    },
  },
})
