import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // React core
          'react-vendor': ['react', 'react-dom', 'react/jsx-runtime'],
          // React Router
          'router': ['react-router-dom'],
          // TanStack Query and devtools
          'react-query': ['@tanstack/react-query', '@tanstack/react-query-devtools'],
          // Form libraries
          'forms': ['react-hook-form', '@hookform/resolvers', 'zod'],
          // UI utilities
          'ui-utils': ['react-hot-toast', 'lucide-react', 'clsx'],
          // HTTP client
          'http': ['axios'],
        },
      },
    },
    // Increase chunk size warning limit to 600kb (from default 500kb)
    chunkSizeWarningLimit: 600,
    // Enable source maps for production debugging (optional, can disable for smaller builds)
    sourcemap: false,
  },
})
