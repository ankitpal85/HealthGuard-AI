/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0a0f1e',
          800: '#0d1929',
          700: '#1e293b',
          600: '#334155',
        },
        brand: {
          500: '#4f8ef7',
          600: '#3b82f6',
          700: '#2563eb',
          purple: '#a855f7',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
