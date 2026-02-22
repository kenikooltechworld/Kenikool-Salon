import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
  build: {
    // Code splitting configuration
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          "vendor-react": ["react", "react-dom", "react-router-dom"],
          "vendor-query": ["@tanstack/react-query"],
          "vendor-ui": ["lucide-react", "sonner"],
          "vendor-charts": ["chart.js", "react-chartjs-2", "recharts"],
          "vendor-forms": ["axios"],
          "vendor-animations": ["framer-motion"],
          "vendor-maps": ["leaflet", "react-leaflet"],
          "vendor-carousel": ["swiper"],
          "vendor-utils": ["date-fns", "clsx", "tailwind-merge", "zustand"],
          "vendor-export": ["jspdf", "jspdf-autotable", "xlsx", "papaparse"],
          "vendor-qr": ["qrcode"],
          "vendor-other": ["idb", "leaflet-control-geocoder"],
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Enable minification
    minify: "terser",
    // Source maps for production debugging
    sourcemap: false,
    // CSS code splitting
    cssCodeSplit: true,
  },
  // Optimization for development
  optimizeDeps: {
    include: [
      "react",
      "react-dom",
      "react-router-dom",
      "@tanstack/react-query",
      "axios",
      "framer-motion",
      "swiper",
      "leaflet",
      "react-leaflet",
      "chart.js",
      "react-chartjs-2",
      "recharts",
      "date-fns",
      "zustand",
    ],
  },
});
