// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Static site — resultat.astro reads query params client-side via JS
export default defineConfig({
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
  },
});