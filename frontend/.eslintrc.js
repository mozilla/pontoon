/* eslint-env node */
module.exports = {
    extends: [
        '../.eslintrc.js',
        // TODO: enable recommended rules
        // "plugin:@typescript-eslint/recommended",
    ],
    parser: '@typescript-eslint/parser',
    plugins: [
        '@typescript-eslint',
    ],
    rules: {
        'no-unused-vars': 'off',
        '@typescript-eslint/no-unused-vars': 'error',
    },
};
