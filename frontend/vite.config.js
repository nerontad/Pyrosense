import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Sin sourcemaps en prod (evita filtrar nombres / paths del proyecto)
    sourcemap: false,
    // Minificado por defecto
    minify: true,
  },
  oxc: {
    // Quita comentarios del bundle (mitiga "Information Disclosure - Suspicious Comments")
    legalComments: 'none',
    // Quita console.* y debugger en producción
    drop: ['console', 'debugger'],
  },
})
