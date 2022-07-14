/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./*html'],
  theme: {
    screens:{
      sm: '480px',
      md: '768px',
      lg: '976px',
      xl: '1400px'
    },
    extend: {
      colors: {
        darkSlate: '#545F75',
        brightOrange: '#FF8C71',
        lightGray: '#BFBFBF',
        white: '#FFFFFF',
        }
    },
  },
  plugins: [],
}
