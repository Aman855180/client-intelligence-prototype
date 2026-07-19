/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#F7F8FA",
        surface: "#FFFFFF",
        line: "#E4E7EC",
        ink: "#131B29",
        muted: "#5B6472",
        faint: "#8A94A6",
        brand: {
          DEFAULT: "#2F6F5E",
          dark: "#20493D",
          soft: "#E7F0EC",
        },
        confirmed: { DEFAULT: "#2F6F5E", soft: "#E7F0EC" },
        reported: { DEFAULT: "#3E63DD", soft: "#EAEFFD" },
        inference: { DEFAULT: "#B7791F", soft: "#FBF1DF" },
        missing: { DEFAULT: "#8A94A6", soft: "#F0F1F3" },
        conflict: { DEFAULT: "#C1440E", soft: "#FBEAE1" },
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(19, 27, 41, 0.04), 0 1px 0 rgba(19, 27, 41, 0.03)",
        raised: "0 4px 16px rgba(19, 27, 41, 0.08)",
      },
    },
  },
  plugins: [],
};
