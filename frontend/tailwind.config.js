/** @type {import('tailwindcss').Config} */
// Tokens visuales personalizados de la app
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Tipografías
      fontFamily: {
        sans: ['"Inter"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', '"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      // Paleta de colores de la marca (azul-noche + naranja-fuego)
      colors: {
        ink: {
          950: '#070a14',
          900: '#0b1020',
          850: '#0f1530',
          800: '#141a36',
          700: '#1c2348',
          600: '#272f5c',
        },
        ember: {
          50:  '#fff5ee',
          100: '#ffe6d2',
          200: '#ffc59c',
          300: '#ff9d61',
          400: '#ff7a36',
          500: '#ff5b14',
          600: '#ed3f00',
          700: '#c12f02',
          800: '#992708',
          900: '#7c220a',
        },
      },
      // Fondos con gradientes y patrones
      backgroundImage: {
        'grid-faint': "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
        'radial-ember': "radial-gradient(circle at 20% 0%, rgba(255,91,20,0.18), transparent 55%), radial-gradient(circle at 100% 100%, rgba(239,68,68,0.12), transparent 50%)",
        'gradient-ember': "linear-gradient(135deg, #ff7a36 0%, #ed3f00 60%, #b91c1c 100%)",
      },
      // Sombras: efecto fuego y glassmorphism
      boxShadow: {
        'ember':       '0 10px 40px -10px rgba(255,91,20,0.55), 0 0 0 1px rgba(255,91,20,0.25) inset',
        'ember-soft':  '0 8px 30px -10px rgba(255,91,20,0.35)',
        'glass':       '0 8px 32px 0 rgba(0,0,0,0.45), 0 0 0 1px rgba(255,255,255,0.06) inset',
        'glass-lg':    '0 20px 60px -10px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.08) inset',
      },
      // Animaciones reutilizables
      animation: {
        'pulse-soft':   'pulseSoft 2.4s ease-in-out infinite',
        'flicker':      'flicker 3s ease-in-out infinite',
        'float-slow':   'floatSlow 9s ease-in-out infinite',
        'shimmer':      'shimmer 2.2s linear infinite',
        'glow-pulse':   'glowPulse 2.8s ease-in-out infinite',
        'fade-in-up':   'fadeInUp .5s ease-out both',
      },
      // Definición de cada animación
      keyframes: {
        pulseSoft: {
          '0%,100%': { opacity: 1 },
          '50%':     { opacity: 0.55 },
        },
        flicker: {
          '0%,100%': { opacity: 0.95, transform: 'translateY(0)' },
          '20%':     { opacity: 0.7,  transform: 'translateY(-1px)' },
          '50%':     { opacity: 1,    transform: 'translateY(1px)' },
          '70%':     { opacity: 0.85, transform: 'translateY(0)' },
        },
        floatSlow: {
          '0%,100%': { transform: 'translateY(0) translateX(0)' },
          '50%':     { transform: 'translateY(-12px) translateX(6px)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        glowPulse: {
          '0%,100%': { boxShadow: '0 0 0 0 rgba(255,91,20,0.45)' },
          '50%':     { boxShadow: '0 0 0 14px rgba(255,91,20,0)' },
        },
        fadeInUp: {
          '0%':   { opacity: 0, transform: 'translateY(8px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
