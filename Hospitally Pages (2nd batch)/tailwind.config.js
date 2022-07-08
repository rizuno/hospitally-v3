/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    screens:{
      sm: '480px',
      md: '768px',
      lg: '976px',
      xl: '1400px'
    },
    lineHeight: {
      'extra-loose': '2.5',
      '12': '3rem',
    },
    extend: {
      colors: {
      darkSlate: '#545F75',
      brightOrange: '#FF8C71',
      lightGray: '#BFBFBF',
      lighterGray: '#F4F4F4',
      white: '#FFFFFF',
      blue: '#562BF7',
      light: '#F5F5F5',
      lightBlue: '#F3F0FF',
      grey: '#eee',
      darkGrey: '#666',
      black: '#222',
      orange: '#FFA500',
      green: '#4CAF50',
      
      }
    },
  },
  plugins: [],
}
