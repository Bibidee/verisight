import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Document surfaces
        "audit-black": "#090B10",
        "graphite-blue": "#0F172A",
        "frost-grey": "#F3F6FA",
        "ledger-mist": "#F3F6FA", // alias retained for older usages
        "white-ledger": "#FFFFFF",
        "blue-steel": "#EAF0F8",
        // Brand + signal
        "exec-blue": "#2563EB",
        "grid-blue": "#2563EB",
        "data-cyan": "#06B6D4",
        amber: "#F59E0B",
        claim: "#DC2626",
        emerald: "#059669",
        consensus: "#7C3AED",
        // Text
        ink: "#0F172A",
        "ledger-white": "#F8FAFC",
        slate: "#64748B",
        // Borders
        auditline: "#E2E8F0",
        "ledger-line": "#E2E8F0",
        "glass-grid": "rgba(148,163,184,0.22)",
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "system-ui", "sans-serif"],
        body: ["var(--font-manrope)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: { btn: "8px", panel: "12px", stamp: "4px" },
      fontSize: {
        hero: ["64px", { lineHeight: "1.05", letterSpacing: "-0.025em" }],
        pagetitle: ["38px", { lineHeight: "1.08", letterSpacing: "-0.012em" }],
        section: ["24px", { lineHeight: "1.2" }],
        cardtitle: ["18px", { lineHeight: "1.3" }],
      },
      boxShadow: {
        doc: "0 1px 0 rgba(15,23,42,0.04), 0 8px 24px -18px rgba(15,23,42,0.18)",
        stamp: "0 0 0 1px rgba(124,58,237,0.35), 0 0 0 6px rgba(124,58,237,0.06)",
      },
      keyframes: {
        stampIn: {
          "0%":   { transform: "rotate(-2deg) scale(1.15)", opacity: "0" },
          "60%":  { transform: "rotate(-2deg) scale(0.98)", opacity: "1" },
          "100%": { transform: "rotate(-2deg) scale(1)",    opacity: "1" },
        },
        pulseDot: {
          "0%,100%": { opacity: "1", transform: "scale(1)" },
          "50%":     { opacity: "0.45", transform: "scale(0.85)" },
        },
      },
      animation: {
        stampIn: "stampIn .6s ease-out both",
        pulseDot: "pulseDot 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
