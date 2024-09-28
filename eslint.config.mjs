import importPlugin from 'eslint-plugin-import';
import react from 'eslint-plugin-react';
import globals from 'globals';
import babelParser from '@babel/eslint-parser';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import js from '@eslint/js';
import { FlatCompat } from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default [
  {
    ignores: [
      '**/.vscode/',
      '.github/',
      'media/',
      '**/static/',
      '**/coverage/',
      'docs/_build/',
      '**/package-lock.json',
      '**/specs/',
      '**/.venv/',
      '**/venv/',
      'translate/dist/',
      // Jinja templates
      'translate/public/translate.html',
      '**/templates/**/*.html',
      // Vendored code
      'error_pages/css/blockrain.css',
      'error_pages/js/',
      'pontoon/base/static/css/boilerplate.css',
      'pontoon/base/static/css/fontawesome-all.css',
      'pontoon/base/static/css/nprogress.css',
      'pontoon/base/static/js/lib/',
    ],
  },
  ...compat.extends('eslint:recommended', 'plugin:react/recommended'),
  {
    plugins: {
      react,
      import: importPlugin,
    },

    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.jest,
        gettext: false,
        ngettext: false,
        interpolate: false,
        l: false,
        expect: false,
        test: false,
        browser: false,
        jest: false,
        Promise: false,
        Set: false,
        URLSearchParameters: false,
        FormData: false,
        require: false,
        shortcut: false,
        sorttable: false,
        $: false,
        Pontoon: false,
        jQuery: false,
        Clipboard: false,
        Chart: false,
        NProgress: false,
        diff_match_patch: false,
        Highcharts: false,
        Sideshow: false,
        editor: false,
        DIFF_INSERT: false,
        DIFF_EQUAL: false,
        DIFF_DELETE: false,
        ga: false,
        process: false,
        generalShortcutsHandler: true,
        traversalShortcutsHandler: true,
        editorShortcutsHandler: true,
        showdown: true,
      },

      parser: babelParser,
      ecmaVersion: 2017,
      sourceType: 'module',

      parserOptions: {
        ecmaFeatures: {
          jsx: true,
          experimentalObjectRestSpread: true,
        },

        babelOptions: {
          presets: ['@babel/preset-react'],
        },

        requireConfigFile: false,
      },
    },

    settings: {
      react: {
        version: 'detect',
      },
    },

    rules: {
      curly: 'error',
      'react/display-name': 0,
      'react/prefer-es6-class': 1,
      'react/prefer-stateless-function': 0,
      'react/prop-types': 0,
      'react/jsx-key': 0,
      'react/jsx-uses-react': 1,
      'react/jsx-uses-vars': 1,

      'no-unused-vars': [
        'error',
        {
          vars: 'all',
          args: 'after-used',
          ignoreRestSiblings: true,
        },
      ],

      'no-console': 1,
      'no-var': 'error',

      'prefer-const': [
        'error',
        {
          destructuring: 'any',
          ignoreReadBeforeAssign: false,
        },
      ],
    },
  },
];
