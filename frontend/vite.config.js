import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',

      // Important for React Router (SPA)
      navigateFallback: '/',

      includeAssets: ['favicon.svg', 'favicon.ico', 'robots.txt'],

      manifest: {
        name: 'JalKosh',
        short_name: 'JalKosh',
        description: 'From groundwater information to the crop suggestions',
        theme_color: '#0f172a',
        background_color: '#0f172a',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },

      // Offline caching strategy
      workbox: {
        runtimeCaching: [
          // HTML pages
          {
            urlPattern: ({ request }) => request.destination === 'document',
            handler: 'NetworkFirst',
            options: {
              cacheName: 'html-cache',
            },
          },

          // JS & CSS
          {
            urlPattern: ({ request }) =>
              request.destination === 'script' ||
              request.destination === 'style',
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'assets-cache',
            },
          },

          // Images
          {
            urlPattern: ({ request }) => request.destination === 'image',
            handler: 'CacheFirst',
            options: {
              cacheName: 'images-cache',
              expiration: {
                maxEntries: 50,
              },
            },
          },
        ],
      },
    }),
  ],

  // Your existing dev server config (kept intact)
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['overweening-unmomentously-garfield.ngrok-free.dev'],
    proxy: {
      // Proxy /api and /users to the FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/users': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
