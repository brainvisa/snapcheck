import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react()],
  resolve: {
    preserveSymlinks: true,
    alias: {
      '@lepton/core': path.resolve(__dirname, 'node_modules/@lepton/core'),
      // Temporarily keep stub API types until client is generated
      '@lepton/api-client': path.resolve(__dirname, 'snapcheck-front/src/api/types.ts'),
      '@lepton/api': path.resolve(__dirname, 'src/api/generated'),
      '@api': path.resolve(__dirname, 'src/api'),
    },
  },
  optimizeDeps: {
    force: true,
    exclude: ['@lepton/core'],
    include: ['react-dom/client'],
  },
})
