import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward /analyze to the FastAPI backend during local dev so the
      // frontend can call a relative path without CORS headaches.
      "/analyze": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
