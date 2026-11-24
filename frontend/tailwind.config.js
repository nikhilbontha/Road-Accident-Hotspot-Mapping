/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        asphalt: '#1F2328',
        paper: '#F2F3EF',
        card: '#FFFFFF',
        line: '#DADCD5',
        ink: '#1D2125',
        muted: '#6A7077',
        lane: '#F5B800',
        crit: '#C62F2A',
        high: '#E2762B',
        med: '#E7B416',
        low: '#3E8E62',
        status: {
          identified: '#9AA0A6',
          review: '#F5B800',
          assigned: '#2F6FB5',
          progress: '#E2762B',
          implemented: '#3E8E62',
          closed: '#1F2328',
        },
        warn: {
          bg: '#FFF3C4',
          text: '#6B5200',
        },
      },
      fontFamily: {
        sans: ['Fira Sans', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '10px',
        btn: '8px',
        panel: '12px',
      },
    },
  },
  plugins: [],
};
