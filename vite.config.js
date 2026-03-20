import { fileURLToPath, URL } from 'node:url'
import { execSync } from 'node:child_process'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

const commitDate = execSync('git log -1 --format=%cd --date=short').toString().trim()

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  define: {
    __COMMIT_DATE__: JSON.stringify(commitDate),
  },
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
