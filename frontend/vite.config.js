/*import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
//import tailwindcss from '@tailwindcss/vite'


// https://vite.dev/config/
export default defineConfig({
  plugins: [  
    react(),
  ],
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
*/ 


import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@features': path.resolve(__dirname, './src/features'),
      '@shared': path.resolve(__dirname, './src/shared'),
    },
  },
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
  }
})