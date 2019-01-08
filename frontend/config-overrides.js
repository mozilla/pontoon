/*
 * This file is used by the react-app-rewired library to override
 * the default create-react-app configuration, without having to eject.
*/

const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');


module.exports = function override(config, env) {
    if (!config.plugins) {
        config.plugins = [];
    }
    config.plugins.push(
        // Inject a plugin to compile and include the needed resources for
        // the Monaco code editor to work correctly.
        new MonacoWebpackPlugin({
            languages: ['html'],
        }),
    );
    return config;
}
