/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core SetuX Design System Tokens
        navy: {
          900: "#0B2A4A",
          DEFAULT: "#0B2A4A",
        },
        govt: {
          blue: "#1769D2",
          light: "#EAF3FF",
          bg: "#F5F7FA",
        },
        setux: {
          navy: "#0B2A4A",
          blue: "#1769D2",
          lightBlue: "#EAF3FF",
          bgLight: "#F5F7FA",
          bgDark: "#07111F",
          surfaceDark: "#0B1B2D",
          surfaceDarkSec: "#10243A",
          textPrimaryLight: "#14213D",
          textSecondaryLight: "#64748B",
          textPrimaryDark: "#F8FAFC",
          textSecondaryDark: "#A8B3C2",
        },
        primary: {
          50:  "#EAF3FF",
          100: "#dbeafe",
          500: "#1769D2",
          600: "#1459b8",
          700: "#104899",
          800: "#0D377A",
          900: "#0B2A4A",
          DEFAULT: "#1769D2",
        },
        // Risk Status Semantics
        risk: {
          low: "#16A34A",
          medium: "#D97706",
          high: "#DC2626",
          critical: "#991B1B",
        },
        saffron: {
          50:  "#fff7ed",
          100: "#ffedd5",
          400: "#fb923c",
          500: "#f97316",
          600: "#ea580c",
          DEFAULT: "#f97316",
        },
        success: "#16A34A",
        warning: "#D97706",
        danger:  "#DC2626",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        devanagari: ["Noto Sans Devanagari", "serif"],
      },
      boxShadow: {
        xs: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
        card: "0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)",
        "card-dark": "0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.2)",
        "card-hover": "0 4px 12px 0 rgb(0 0 0 / 0.1)",
        "govt": "0 4px 20px -2px rgba(11, 42, 74, 0.08)",
      },
    },
  },
  plugins: [],
};


