import path from 'path';
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    coverage: {
      enabled: true,
      reportOnFailure: true,
      include: ['src/**/*.{js,jsx,ts,tsx}'],
      exclude: ['src/**/*.d.ts', 'node_modules/**'],
    },
    setupFiles: ['./src/setupTests.ts'],
    mockReset: true,
    testTimeout: 10000,
  },
  resolve: {
    alias: [
      { find: /^~(.*)$/, replacement: path.resolve(__dirname, 'src/$1') },
      {
        find: /\.svg$/,
        replacement: path.resolve(__dirname, '__mocks__/svg.js'),
      },
    ],
  },
});
