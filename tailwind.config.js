/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',  // Adjust this path if your templates are elsewhere
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
