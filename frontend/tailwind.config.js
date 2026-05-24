module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "sans-serif"] },
      colors: {
        sidebar: { DEFAULT: "#0F1117", surface: "#1E2433" },
        brand:   { DEFAULT: "#6366F1", light: "#818CF8", dark: "#4F46E5" },
        surface: { DEFAULT: "#F8F9FC", card: "rgba(255,255,255,0.85)" },
        success: "#22C55E",
        warning: "#F59E0B",
        danger:  "#EF4444",
        slate:   { 400: "#94A3B8", 600: "#475569", 700: "#334155", 800: "#1E293B" }
      },
      borderRadius: { xl: "16px", "2xl": "20px" },
      boxShadow: {
        glass: "0 4px 24px rgba(0,0,0,0.06)",
        "glass-hover": "0 8px 32px rgba(0,0,0,0.10)",
        brand: "0 4px 12px rgba(99,102,241,0.30)"
      },
      backdropBlur: { glass: "12px" }
    }
  },
  plugins: []
}
