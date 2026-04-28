import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        muted: "#687286",
        line: "#d8dee9",
        panel: "#ffffff",
        canvas: "#f6f7f9",
        success: "#15803d",
        danger: "#b42318",
        amber: "#b7791f"
      },
      boxShadow: {
        soft: "0 10px 24px rgba(23, 32, 51, 0.07)"
      }
    }
  },
  plugins: []
};

export default config;
