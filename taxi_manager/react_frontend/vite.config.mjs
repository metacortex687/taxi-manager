import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import path from "node:path"

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    cors: {
      origin: "http://172.27.79.57:8000",
    },
  },
  build: {
    manifest: true,
    outDir: path.resolve(__dirname, "static/react_frontend/dist"),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, "react_src/index.jsx"),
    },
  },
})