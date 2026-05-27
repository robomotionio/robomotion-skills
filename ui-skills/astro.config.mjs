import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";

// https://astro.build/config
export default defineConfig({
  site: "https://www.ui-skills.com",
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()],
    assetsInclude: ["**/*.sh"],
    resolve: {
      dedupe: ["react", "react-dom"],
    },
  },
});
