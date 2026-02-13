/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#1C1917',
          secondary: '#292524',
          tertiary: '#44403C',
        },
        primary: {
          DEFAULT: '#D97706',
          foreground: '#FFFFFF',
          hover: '#B45309',
        },
        accent: {
          DEFAULT: '#A3B18A',
          foreground: '#1C1917',
          gold: '#FCD34D',
        },
        tuner: {
          'in-tune': '#4ADE80',
          flat: '#FBBF24',
          sharp: '#F87171',
        }
      },
      fontFamily: {
        heading: ['Playfair Display', 'serif'],
        body: ['Manrope', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
