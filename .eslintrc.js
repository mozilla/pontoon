module.exports = {
    "extends": [
        "eslint:recommended",
        "plugin:react/recommended"
    ],
    env: {
        es6: true,
        browser: true,
        jest: true,
    },
    parser: "@babel/eslint-parser",
    parserOptions: {
        ecmaVersion: 2017,
        ecmaFeatures: {
            jsx: true,
            experimentalObjectRestSpread: true
        },
        sourceType: 'module',
        babelOptions: {
          configFile: __dirname + "/.babelrc",
        },
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
        // Flow specific things
        CredentialsType: true,
        SyntheticEvent: false,
        SyntheticFocusEvent: false,
        SyntheticInputEvent: false,
        SyntheticKeyboardEvent: false,
        SyntheticMouseEvent: false,
        TimeoutID: false,
        "$Diff": false,
        "$ReadOnly": false,
        "$ReadOnlyArray": false,
        "React$Element": false,
    },
    plugins: [
        'react',
    ],
    rules: {
        'react/display-name': 0,
        'react/prefer-es6-class': 1,
        'react/prefer-stateless-function': 0,
        "react/prop-types": 0,
        "react/jsx-key": 0,
        "react/jsx-uses-react": 1,
        'react/jsx-uses-vars': 1,
        "no-unused-vars": ["error", { "vars": "all", "args": "after-used", "ignoreRestSiblings": true }],
        "no-console": 1,
    },
    settings: {
        'react': {
            'version': 'detect'
        }
    }
};
