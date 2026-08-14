import eslintReact from '@eslint-react/eslint-plugin';
import js from '@eslint/js';
import vitest from '@vitest/eslint-plugin';
import { defineConfig } from 'eslint/config';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default defineConfig(
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
      'documentation/site/',

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

  {
    files: ['pontoon/**/*.js'],

    extends: [js.configs.recommended],

    languageOptions: {
      globals: {
        ...globals.browser,
        $: 'readonly',
        Chart: 'readonly',
        Pontoon: 'readonly',
      },
    },

    rules: {
      curly: 'error',
      'no-console': 1,
      'no-unused-vars': [
        'error',
        {
          vars: 'all',
          args: 'after-used',
          ignoreRestSiblings: true,
        },
      ],
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

  {
    files: ['translate/*.mjs'],

    languageOptions: { globals: { ...globals.node } },
  },

  {
    files: ['**/*.{ts,tsx}', 'translate/**/*.{js,jsx}'],

    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      eslintReact.configs['recommended-typescript'],
    ],

    languageOptions: {
      globals: {
        ...globals.browser,
        ...vitest.environments.env.globals,
      },
    },

    rules: {
      curly: 'error',
      'no-console': ['error', { allow: ['warn', 'error'] }],
      'no-restricted-exports': [
        'error',
        { restrictedNamedExports: ['default'] },
      ],

      // TODO: Review these eslint-react errors
      '@eslint-react/static-components': 0,
      '@eslint-react/no-nested-component-definitions': 0,
      '@eslint-react/rules-of-hooks': 0,

      // TODO: Review these eslint-react warnings
      '@eslint-react/exhaustive-deps': 0,
      '@eslint-react/naming-convention-ref-name': 0,
      '@eslint-react/no-array-index-key': 0,
      '@eslint-react/use-state': 0,
      '@eslint-react/dom-no-dangerously-set-innerhtml': 0,
      '@eslint-react/purity': 0,
      '@eslint-react/set-state-in-effect': 0,
      '@eslint-react/naming-convention-context-name': 0,
      '@eslint-react/no-unnecessary-use-prefix': 0,

      '@typescript-eslint/ban-ts-comment': 0,
      '@typescript-eslint/no-explicit-any': 0,
      '@typescript-eslint/no-unused-vars': [
        'error',
        { varsIgnorePattern: '^_' },
      ],
    },
  },
);
