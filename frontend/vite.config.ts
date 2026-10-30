import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";
export default defineConfig({
  plugins: [react(), tailwind()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          charts: ["recharts"],
          forms: ["react-hook-form", "zod", "@hookform/resolvers"],
          react: ["react", "react-dom", "react-router-dom"],
        },
      },
    },
  },
});
