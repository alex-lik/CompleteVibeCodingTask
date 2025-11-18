import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3050,
    proxy: {
      '/api': {
        target: 'http://localhost:8050',
        changeOrigin: true,
      },
      '/webhook': {
        target: 'http://localhost:8050',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8050',
        ws: true,
      }
    }
  }
})