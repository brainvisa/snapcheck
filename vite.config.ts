import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    preserveSymlinks: true,
    alias: {
      '@lepton/core': path.resolve(__dirname, 'node_modules/@lepton/core'),
      '@lepton/api-client': path.resolve(__dirname, 'snapcheck-front/src/api/types.ts'),
    },
  },
  optimizeDeps: {
    force: true,
    exclude: ['@lepton/core', '@lepton/api-client'],
    include: ['react-dom/client'],
  },
})
