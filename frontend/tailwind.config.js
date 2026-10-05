/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070A11',
          900: '#0B0F19',
          850: '#0F1626',
          800: '#141D33',
          700: '#1E293B',
          600: '#334155',
        },
        brand: {
          blue: '#3B82F6',
          indigo: '#6366F1',
          purple: '#8B5CF6',
          cyan: '#06B6D4',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#F43F5E',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glow-blue': '0 0 25px -5px rgba(59, 130, 246, 0.25)',
        'glow-purple': '0 0 25px -5px rgba(139, 92, 246, 0.25)',
        'inner-light': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.07)',
      }
    },
  },
  plugins: [],
}
