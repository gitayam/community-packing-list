/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Orbitron', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        tactical: {
          bg: '#0A0E14',
          surface: '#12161D',
          elevated: '#1A1F29',
          border: '#2A3441',
          'border-light': '#3A4555',
        },
        accent: {
          cyan: '#00F0FF',
          'cyan-dim': '#00A5B0',
          'cyan-glow': '#00F0FF40',
          amber: '#FFB800',
          'amber-dim': '#B08000',
          'amber-glow': '#FFB80040',
        },
        status: {
          danger: '#FF3B3B',
          'danger-dim': '#CC2E2E',
          'danger-glow': '#FF3B3B40',
          success: '#00FF87',
          'success-dim': '#00CC6B',
          'success-glow': '#00FF8740',
          warning: '#FFB800',
        },
        text: {
          primary: '#E8EDF5',
          secondary: '#6B7A90',
          muted: '#4A5568',
          tactical: '#00F0FF',
        },
      },
      boxShadow: {
        'glow-cyan': '0 0 20px #00F0FF40, 0 0 40px #00F0FF20',
        'glow-amber': '0 0 20px #FFB80040, 0 0 40px #FFB80020',
        'glow-success': '0 0 20px #00FF8740, 0 0 40px #00FF8720',
        'glow-danger': '0 0 20px #FF3B3B40, 0 0 40px #FF3B3B20',
        'inner-glow': 'inset 0 1px 0 #ffffff10',
      },
      backgroundImage: {
        'grid-pattern': `
          linear-gradient(#00F0FF08 1px, transparent 1px),
          linear-gradient(90deg, #00F0FF08 1px, transparent 1px)
        `,
        'scanlines': 'repeating-linear-gradient(0deg, transparent, transparent 2px, #00000010 2px, #00000010 4px)',
        'radial-vignette': 'radial-gradient(ellipse at center, transparent 0%, #0A0E14 100%)',
      },
      keyframes: {
        'scan': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px #00F0FF40' },
          '50%': { opacity: '0.7', boxShadow: '0 0 30px #00F0FF60' },
        },
        'border-trace': {
          '0%': { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '200% 200%' },
        },
        'fadeInUp': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slideInRight': {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'scaleIn': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'spin-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        'scan': 'scan 4s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'border-trace': 'border-trace 4s linear infinite',
        'fadeInUp': 'fadeInUp 0.5s ease-out forwards',
        'slideInRight': 'slideInRight 0.4s ease-out forwards',
        'scaleIn': 'scaleIn 0.3s ease-out forwards',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin-slow 20s linear infinite',
      },
    },
  },
  plugins: [],
}
