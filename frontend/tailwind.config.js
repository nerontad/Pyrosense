/** @type {import('tailwindcss').Config} */
// Tokens del sistema visual "estación de vigilancia": carbón cálido, ceniza, hueso,
// brasa como luz emisiva y musgo para "sistema sano"
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Tipografías: Archivo (display expandido), Inter (cuerpo), JetBrains Mono (telemetría)
      fontFamily: {
        sans: ['"Inter"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Archivo"', '"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      // Paleta: negro carbón con temperatura (subtono quemado), neutros ceniza,
      // hueso para texto, brasa para acción/peligro, flare para humo, musgo para OK
      colors: {
        char: {
          950: '#0B0805',
          900: '#0F0B07',
          850: '#16100A',
          800: '#1D150C',
          700: '#2B1E10',
        },
        bone: '#F4EDDF',
        ash: {
          300: '#CCC1B2',
          400: '#ADA193',
          500: '#8D8173',
          600: '#6B6055',
        },
        ember: {
          200: '#FFB088',
          300: '#FF8A50',
          400: '#FF6A26',
          500: '#FF4D00',
          600: '#D63E00',
          700: '#A93200',
        },
        moss: {
          300: '#BAC49A',
          400: '#97A567',
          500: '#76863F',
        },
        flare: {
          300: '#EFC183',
          400: '#E0A458',
          500: '#C98A2E',
        },
        // Hairlines cálidas: la estructura del sistema es la línea
        line: 'rgba(244, 237, 223, 0.16)',
        'line-strong': 'rgba(244, 237, 223, 0.36)',
        'line-ember': 'rgba(255, 77, 0, 0.4)',
      },
      letterSpacing: {
        mega: '0.35em',
      },
      // Easings con carácter (los nativos son débiles)
      transitionTimingFunction: {
        'out-strong': 'cubic-bezier(0.23, 1, 0.32, 1)',
        'in-out-strong': 'cubic-bezier(0.77, 0, 0.175, 1)',
      },
      // Luz emisiva: la única sombra permitida es el resplandor de la brasa
      boxShadow: {
        'ember-glow': '0 0 32px -6px rgba(255, 77, 0, 0.45)',
        'ember-glow-lg': '0 0 60px -10px rgba(255, 77, 0, 0.55)',
        'moss-glow': '0 0 24px -6px rgba(151, 165, 103, 0.35)',
      },
      backgroundImage: {
        // Gradiente de fuego para botones y acentos
        'fire-grad': 'linear-gradient(135deg, #FF6A26 0%, #FF4D00 55%, #D63E00 100%)',
        // Lavado de calor para módulos destacados
        'heat-wash': 'radial-gradient(120% 90% at 85% 0%, rgba(255,77,0,0.17), transparent 60%)',
        'moss-wash': 'radial-gradient(120% 90% at 85% 0%, rgba(151,165,103,0.14), transparent 60%)',
      },
      // Animaciones: parpadeo tipo cursor, entradas con easing fuerte, shimmer de carga
      animation: {
        'blink':    'blink 1.2s steps(1) infinite',
        'fade-up':  'fadeUp .5s cubic-bezier(0.23, 1, 0.32, 1) both',
        'rise':     'rise .6s cubic-bezier(0.23, 1, 0.32, 1) both',
        'shimmer':  'shimmer 2.2s linear infinite',
        'flicker':  'flicker 3.2s ease-in-out infinite',
        'breathe':  'breathe 3s ease-in-out infinite',
      },
      keyframes: {
        blink: {
          '0%, 60%': { opacity: 1 },
          '61%, 100%': { opacity: 0.15 },
        },
        fadeUp: {
          '0%':   { opacity: 0, transform: 'translateY(8px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        rise: {
          '0%':   { opacity: 0, transform: 'translateY(16px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        flicker: {
          '0%, 100%': { opacity: 1 },
          '42%':      { opacity: 0.82 },
          '58%':      { opacity: 0.94 },
          '72%':      { opacity: 0.78 },
        },
        breathe: {
          '0%, 100%': { boxShadow: '0 0 24px -8px rgba(255,77,0,0.35)' },
          '50%':      { boxShadow: '0 0 44px -8px rgba(255,77,0,0.6)' },
        },
      },
    },
  },
  plugins: [],
}
