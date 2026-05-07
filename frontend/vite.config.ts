import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // En dev, redirige les appels /auth et /game vers le backend
      "/auth": { target: "http://localhost:8000", changeOrigin: true },
      "/game": { target: "http://localhost:8000", changeOrigin: true },
      "/assets": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
