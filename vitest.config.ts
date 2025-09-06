import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,           // allows describe/it/test without imports
    environment: 'jsdom',    // for DOM-related tests
    setupFiles: './src/setupTests.ts', // similar to jest.setup.js
    coverage: {
      reporter: ['text', 'json', 'html'],
    },
  },
});
