/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: "jit",
  content: ["./templates/**/*.{html,js}"],
  theme: {
    colors: {
      'primary-white': '#FFFFFF', // bg
      'secondary-navy': '#545F75',
      'tertiary-orange': '#FF8C71',
      'orange-500': '#BF6D59', // border color orange buttons
      'green-col': '#7BBF7D',
      'green-col-500': '#66A668', // border color of green buttons
      'red-col': '#F16969',
      'red-col-500:': '#BA0505' // border color of red buttons
    },
    extend: {

    },
    container: {
        center: true
    }
  },
  plugins: [],
}
