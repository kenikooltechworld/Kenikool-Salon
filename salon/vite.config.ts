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
    host: "0.0.0.0",
    middlewareMode: false,
    hmr: {
      host: "localhost",
      port: 3000,
      protocol: "ws",
    },
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path,
        configure: (proxy, options) => {
          proxy.on("proxyReq", (proxyReq, req, res) => {
            // Ensure X-Forwarded-Host is set to preserve subdomain
            const host = req.headers.host || "localhost:3000";
            proxyReq.setHeader("X-Forwarded-Host", host);
            proxyReq.setHeader("X-Forwarded-Proto", "http");

            // Forward cookies from the original request
            if (req.headers.cookie) {
              proxyReq.setHeader("Cookie", req.headers.cookie);
            }
          });

          proxy.on("proxyRes", (proxyRes, req, res) => {
            // Forward Set-Cookie headers from backend to client
            const setCookieHeaders = proxyRes.headers["set-cookie"];
            if (setCookieHeaders) {
              res.setHeader("Set-Cookie", setCookieHeaders);
            }
          });
        },
      },
      "/ws": {
        target: "http://localhost:8000",
        changeOrigin: true,
        ws: true,
      },
    },
    ...getSecurityHeadersConfig(),
  },
});
