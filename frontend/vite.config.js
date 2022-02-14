/* eslint-env node */

import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
    base: '/static/',
    plugins: [react()],
    resolve: {
        alias: {
            '~': path.resolve(__dirname, 'src'),
            'react-infinite-scroller': 'react-infinite-scroller/index.js',
        },
    },
    server: {
        port: 3000,
    },
    build: {
        outDir: 'build',
        rollupOptions: {
            external: [
                '/css/boilerplate.css',
                '/css/fonts.css',
                '/css/fontawesome-all.css',
            ],
        },
    },
}));
