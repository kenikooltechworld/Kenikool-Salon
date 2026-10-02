import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import {
  securityHeadersPlugin,
  getSecurityHeadersConfig,
} from "./src/middleware/securityHeaders";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), securityHeadersPlugin()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    host: true,
    middlewareMode: false,
    proxy: {
      "/api": {
        target: "https://api.kenikoolsalon.com",
        changeOrigin: true,
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on("proxyReq", (proxyReq, req, _res) => {
            const host = req.headers.host || "localhost:3000";
            proxyReq.setHeader("X-Forwarded-Host", host);
            proxyReq.setHeader("X-Forwarded-Proto", "http");

            if (req.headers.cookie) {
              proxyReq.setHeader("Cookie", req.headers.cookie);
            }
          });

          proxy.on("proxyRes", (proxyRes, _req, res) => {
            const setCookieHeaders = proxyRes.headers["set-cookie"];
            if (setCookieHeaders) {
              res.setHeader("Set-Cookie", setCookieHeaders);
            }
          });
        },
      },
      "/socket.io": {
        target: "https://api.kenikoolsalon.com",
        changeOrigin: true,
        ws: true,
      },
    },
    ...getSecurityHeadersConfig(),
  },
  // Production build configuration
  build: {
    outDir: "dist",
    sourcemap: false, // Disable sourcemaps in production for security
    minify: "terser",
    target: "es2022",
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
          ui: ['motion', 'clsx', 'tailwind-merge'],
        }
      }
    }
  },
});
