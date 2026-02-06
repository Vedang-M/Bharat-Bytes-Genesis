/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary & Brand
        primary: {
          green: '#2E7D32',
          blue: '#1976D2',
          brown: '#8D6E63',
        },
        // Status Colors
        status: {
          safe: '#43A047',
          warning: '#F9A825',
          critical: '#E53935',
        },
        // Background & Surface
        background: {
          app: '#FAFAF7',
          card: '#FFFFFF',
          border: '#E0E0E0',
        },
        // Text
        text: {
          primary: '#263238',
          secondary: '#546E7A',
          muted: '#90A4AE',
        },
        // Buttons
        button: {
          primary: '#2E7D32',
          secondary: '#1976D2',
          disabled: '#BDBDBD',
        },
      },
      fontFamily: {
        hindi: ['"Noto Sans Devanagari"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}