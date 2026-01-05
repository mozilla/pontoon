import path from 'path';
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    coverage: {
      reportOnFailure: true,
      include: ['src/**/*.{js,jsx,ts,tsx}'],
    },
    setupFiles: ['./src/setupTests.ts'],
    mockReset: true,
    testTimeout: 10000,
    environment: 'jsdom',
    environmentOptions: {
      jsdom: {
        url: 'http://localhost',
      },
    },
  },
  resolve: {
    alias: [
      {
        find: /^~(.*)$/,
        replacement: path.resolve(import.meta.dirname, 'src/$1'),
      },
      {
        find: /\.svg$/,
        replacement: path.resolve(import.meta.dirname, '__mocks__/svg.js'),
      },
    ],
  },
});
