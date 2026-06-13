import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Puerto fijo: el backend solo permite CORS desde http://localhost:5173.
    // strictPort evita que Vite salte silenciosamente a 5174 si el puerto está ocupado.
    port: 5173,
    strictPort: true,
  },
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
