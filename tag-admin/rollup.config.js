import path from 'path';
import babel from '@rollup/plugin-babel';
import commonjs from '@rollup/plugin-commonjs';
import resolve from '@rollup/plugin-node-resolve';
import replace from '@rollup/plugin-replace';
import css from 'rollup-plugin-css-only';

/** @type {import('rollup').RollupOptions} */
export default {
    input: { tag_admin: 'src/index.js' },
    output: { dir: 'dist/' },
    plugins: [
        replace({
            preventAssignment: true,
            'process.env.NODE_ENV': JSON.stringify('production'),
        }),
        resolve(),
        babel({
            babelHelpers: 'runtime',
            configFile: path.resolve('.babelrc'),
        }),
        commonjs(),
        css({ output: 'tag_admin.css' }),
    ],
};
