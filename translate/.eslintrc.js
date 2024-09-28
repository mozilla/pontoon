/* eslint-env node */

module.exports = {
  root: true,
  ignorePatterns: [
    '/dist/',
    '/public/translate.html',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'import'],
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  env: {
    browser: true,
    jest: true,
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
    '@typescript-eslint/no-unused-vars': ['error', { varsIgnorePattern: '^_' }],
    '@typescript-eslint/prefer-as-const': 0,
    'import/no-default-export': 'error',
  },
};
