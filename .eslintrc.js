module.exports = {
    "extends": [
        "eslint:recommended",
        "plugin:react/recommended"
    ],
    env: {
        es6: true,
        browser: true,
    },
    parserOptions: {
        ecmaVersion: 2017,
        ecmaFeatures: {
            jsx: true,
            experimentalObjectRestSpread: true
        },
        sourceType: 'module',
    },
    globals: {
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
        jQuery: false
    },
    plugins: [
        'react',
    ],
    rules: {
        'react/prefer-es6-class': 0,
        'react/prefer-stateless-function': 1,
        "react/prop-types": 0,
        "react/jsx-key": 0,
        "react/jsx-uses-react": 1,
        'react/jsx-uses-vars': 1,
        "no-unused-vars": ["error", { "vars": "all", "args": "after-used", "ignoreRestSiblings": true }],
        "react/prefer-stateless-function": [1, {"ignorePureComponents": true}]
    },
};
