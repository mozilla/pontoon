import typescriptEslint from '@typescript-eslint/eslint-plugin';
import globals from 'globals';
import tsParser from '@typescript-eslint/parser';
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import vitest from '@vitest/eslint-plugin';

export default [
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },

    languageOptions: {
      globals: {
        ...globals.browser,
        ...vitest.environments.env.globals,
      },

      parser: tsParser,
    },

    rules: {
      curly: 'error',
      'prefer-const': 0,
      'no-var': 0,
      '@typescript-eslint/ban-ts-comment': 0,
      '@typescript-eslint/ban-types': 0,
      '@typescript-eslint/explicit-module-boundary-types': 0,
      '@typescript-eslint/no-empty-function': 0,
      '@typescript-eslint/no-explicit-any': 0,
      '@typescript-eslint/no-inferrable-types': 0,

      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          varsIgnorePattern: '^_',
        },
      ],

      '@typescript-eslint/prefer-as-const': 0,

      'no-restricted-exports': [
        'error',
        {
          restrictedNamedExports: ['default'],
        },
      ],
    },
  },
];
