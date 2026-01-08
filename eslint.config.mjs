import react from 'eslint-plugin-react';
import globals from 'globals';
import eslint from '@eslint/js';
import vitest from '@vitest/eslint-plugin';

export default [
  {
    ignores: [
      '**/.vscode/',
      '.github/',
      'media/',
      'static/',
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
      'pontoon/base/static/css/boilerplate.css',
      'pontoon/base/static/css/fontawesome-all.css',
      'pontoon/base/static/css/nprogress.css',
      'pontoon/base/static/js/lib/',
    ],
  },
  eslint.configs.recommended,
  react.configs.flat.recommended,
  {
    plugins: {
      react,
    },

    languageOptions: {
      globals: {
        ...globals.browser,
        ...vitest.environments.env.globals,
        gettext: 'readonly',
        ngettext: 'readonly',
        interpolate: 'readonly',
        l: 'readonly',
        expect: 'readonly',
        test: 'readonly',
        browser: 'readonly',
        Promise: 'readonly',
        Set: 'readonly',
        URLSearchParameters: 'readonly',
        FormData: 'readonly',
        require: 'readonly',
        shortcut: 'readonly',
        sorttable: 'readonly',
        $: 'readonly',
        Pontoon: 'readonly',
        jQuery: 'readonly',
        Clipboard: 'readonly',
        Chart: 'readonly',
        confetti: 'readonly',
        NProgress: 'readonly',
        diff_match_patch: 'readonly',
        Highcharts: 'readonly',
        Sideshow: 'readonly',
        editor: 'readonly',
        DIFF_INSERT: 'readonly',
        DIFF_EQUAL: 'readonly',
        DIFF_DELETE: 'readonly',
        ga: 'readonly',
        process: 'readonly',
        generalShortcutsHandler: 'writable',
        traversalShortcutsHandler: 'writable',
        editorShortcutsHandler: 'writable',
        showdown: 'writable',
      },

      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
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
