module.exports = {
    "extends": [
        "eslint:recommended",
        "plugin:react/recommended"
    ],
    env: {
        browser: true,
    },
    parserOptions: {
        ecmaVersion: 6,
        ecmaFeatures: {
            jsx: true,
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
    },
};
