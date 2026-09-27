/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Core Visual Identity: Dark Red + Liquid Glass
        background: "#0E0E0E",
        "background-deep": "#0A0A0B",
        "primary-red": "#EF2E4B",
        "bright-red": "#FF4964",
        "muted-text": "#B8B3B5",
        "gray-accent": "#4B4A4B",

        // Operational Status Colors
        "status-safe": "#35D07F",
        "status-moderate": "#FFB547",
        "status-high": "#FF7A45",
        "status-critical": "#EF2E4B",

        // Liquid Glass Tokens
        "glass-bg": "rgba(255, 255, 255, 0.055)",
        "glass-bg-subtle": "rgba(255, 255, 255, 0.035)",
        "glass-bg-elevated": "rgba(26, 22, 24, 0.65)",
        "glass-border": "rgba(255, 255, 255, 0.12)",
        "glass-border-subtle": "rgba(255, 255, 255, 0.08)",
        "glass-border-red": "rgba(239, 46, 75, 0.35)",

        // Legacy compatibility mappings
        surface: "#141416",
        "surface-container-lowest": "#0A0A0B",
        "surface-container-low": "#111113",
        "surface-container": "#18181B",
        "surface-container-high": "#222226",
        "surface-container-highest": "#2E2E33",
        "on-surface": "#FFFFFF",
        "on-surface-variant": "#B8B3B5",
        "primary-fixed": "#EF2E4B",
        "primary-fixed-dim": "#FF4964",
        "on-primary-fixed": "#FFFFFF",
        "secondary-fixed": "#FFB547",
        "secondary-fixed-dim": "#FFA01C",
        "tertiary-fixed-dim": "#FF7A45",
        error: "#EF2E4B",
        "error-container": "rgba(239, 46, 75, 0.15)",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        hud: ["Inter", "Space Grotesk", "monospace"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      borderRadius: {
        DEFAULT: "0.75rem",
        lg: "1.25rem",
        xl: "1.75rem",
        "2xl": "2.25rem",
        glass: "1rem",
      },
      boxShadow: {
        glass: "0 16px 36px rgba(0, 0, 0, 0.45)",
        "glass-elevated": "0 20px 48px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.15)",
        "red-glow": "0 0 25px rgba(239, 46, 75, 0.25)",
        "red-glow-lg": "0 0 45px rgba(239, 46, 75, 0.35)",
        radar: "0 0 24px rgba(239, 46, 75, 0.28)",
      },
      backdropBlur: {
        glass: "20px",
        "glass-lg": "24px",
      },
    },
  },
  plugins: [],
};
