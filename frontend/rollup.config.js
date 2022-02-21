/* eslint-env node */

import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import resolve from '@rollup/plugin-node-resolve';
import replace from '@rollup/plugin-replace';
import typescript from '@rollup/plugin-typescript';
import css from 'rollup-plugin-css-only';

/** @type {import('rollup').RollupOptions} */
export default {
    input: { frontend: 'src/index.tsx' },
    output: { dir: 'dist/' },
    treeshake: 'recommended',

    plugins: [
        json(),
        typescript(),
        replace({
            preventAssignment: true,
            'process.env.NODE_ENV': JSON.stringify(
                process.env.BUILD ?? 'development',
            ),
        }),
        resolve(),
        commonjs(),
        css({ output: 'frontend.css' }),
    ],

    onwarn(warning, warn) {
        // https://github.com/reduxjs/redux-toolkit/issues/1466
        if (warning.id?.includes('@reduxjs/toolkit')) {
            switch (warning.code) {
                case 'SOURCEMAP_ERROR':
                    return;
                case 'THIS_IS_UNDEFINED':
                    if (warning.frame?.includes('this && this')) return;
            }
        }

        warn(warning);
    },
};
