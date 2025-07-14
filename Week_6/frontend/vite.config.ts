import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/songs': 'http://localhost:8000',
      '/albums': 'http://localhost:8000',
      '/playlists': 'http://localhost:8000',
      '/subscriptions': 'http://localhost:8000',
      '/analytics': 'http://localhost:8000',
      '/comments': 'http://localhost:8000',
    },
  },
})
