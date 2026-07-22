import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/status": "http://localhost:8000",
      "/models": "http://localhost:8000",
      "/config": "http://localhost:8000",
      "/chat": "http://localhost:8000",
      "/conversations": "http://localhost:8000",
      "/metrics": "http://localhost:8000",
    },
  },
});
