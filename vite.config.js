import { defineConfig } from "vite";

export default defineConfig({
  build: {
    assetsDir: ".",
    outdir: "dist",
    rollupOptions: {
      input: {
        "index.css": "./assets/css/index.scss",
        "index.js": "./assets/js/index.ts",
      },
      output: {
        assetFileNames: "[ext]/[name]",
        entryFileNames: "js/[name]",
        manualChunks: undefined,
      },
    },
    target: "es2015",
  },
});
