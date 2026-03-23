import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',    // permite acceso desde fuera del contenedor
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://web:8000',   // redirige llamadas /api al backend Django
        changeOrigin: true,
      }
    }
  }
})
