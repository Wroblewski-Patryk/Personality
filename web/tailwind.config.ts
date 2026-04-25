import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Manrope'", "sans-serif"],
      },
      colors: {
        base: {
          950: "#171412",
          900: "#241f1b",
          800: "#3d342f",
        },
        signal: {
          gold: "#e4b85d",
          coral: "#ef7f6d",
          mist: "#f2ece4",
        },
      },
      boxShadow: {
        halo: "0 24px 80px rgba(228, 184, 93, 0.18)",
      },
      backgroundImage: {
        "hero-glow":
          "radial-gradient(circle at top, rgba(228, 184, 93, 0.32), transparent 42%), radial-gradient(circle at 80% 20%, rgba(239, 127, 109, 0.22), transparent 28%)",
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        aion: {
          primary: "#e4b85d",
          secondary: "#ef7f6d",
          accent: "#8fc7b5",
          neutral: "#241f1b",
          "base-100": "#f7f1ea",
          "base-200": "#efe4d6",
          "base-300": "#dfcfbc",
          "base-content": "#1f1a17",
          info: "#4b8fd4",
          success: "#3d9d74",
          warning: "#c8892f",
          error: "#cf5a52",
        },
      },
    ],
  },
} satisfies Config;
