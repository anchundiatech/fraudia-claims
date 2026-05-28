/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        verde:    { DEFAULT: "#16a34a", light: "#dcfce7", text: "#14532d" },
        amarillo: { DEFAULT: "#d97706", light: "#fef3c7", text: "#78350f" },
        rojo:     { DEFAULT: "#dc2626", light: "#fee2e2", text: "#7f1d1d" },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
