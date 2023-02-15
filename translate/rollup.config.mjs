/* eslint-env node */

import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import replace from '@rollup/plugin-replace';
import typescript from '@rollup/plugin-typescript';
import css from 'rollup-plugin-css-only';

/** @type {import('rollup').RollupOptions} */
const config = {
  input: 'src/index.tsx',
  output: { file: 'dist/translate.js' },

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
    nodeResolve(),
    commonjs(),
    css({ output: 'translate.css' }),
  ],

  onwarn(warning, warn) {
    // https://github.com/reduxjs/redux-toolkit/issues/1466
    if (warning.id?.includes('@reduxjs/toolkit')) {
      switch (warning.code) {
        case 'SOURCEMAP_ERROR':
          return;
        case 'THIS_IS_UNDEFINED':
          if (warning.frame?.includes('this && this')) {
            return;
          }
      }
    }

    warn(warning);
  },
};

// eslint-disable-next-line import/no-default-export
export default config;
