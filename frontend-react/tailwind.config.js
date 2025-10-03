/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        military: {
          olive: '#4B5320',
          navy: '#1B365D',
          khaki: '#C3B091',
          sand: '#F4F1DE',
          dark: '#2C2C2C',
        },
        status: {
          required: '#DC3545',
          optional: '#FFC107',
          complete: '#28A745',
          pending: '#6C757D',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['Courier New', 'Monaco', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
