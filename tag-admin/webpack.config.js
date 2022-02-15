const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require('webpack-bundle-tracker');

/** @type {import('webpack').Configuration} */
module.exports = {
  mode: 'production',
  entry: {
      'tag_admin': path.resolve(__dirname, 'src/index.js')
  },
  output: {
    // This copies each source entry into the extension dist folder named
    // after its entry config key.
      path: path.resolve(__dirname, '../assets/webpack_bundles/'),
      filename: '[name].entry.chunk.js',
      chunkFilename: '[name].[chunkhash].js',
      publicPath: '/static/webpack_bundles/'
  },
  module: {
    // This transpiles all code (except for third party modules) using Babel.
    rules: [{
      exclude: /node_modules/,
      test: /\.js$/,
      loaders: ['babel-loader'],
    },{
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader"
        ]
    },{
	test: /\.json$/,
	loader: 'json-loader',
    }],
  },
  resolve: {
    // This allows you to import modules just like you would in a NodeJS app.
    extensions: ['.js', '.jsx'],
    modules: [
      'node_modules',
    ]
  },

  plugins: [
    // Read by django-webpack-loader
    new BundleTracker({ filename: '../webpack-stats.json' }),

    new MiniCssExtractPlugin({
      // Options similar to the same options in webpackOptions.output
      // both options are optional
      filename: "[name].css",
      chunkFilename: "[id].css"
    }),
  ],

  // This will expose source map files so that errors will point to your
  // original source files instead of the transpiled files.
  devtool: 'sourcemap'
};
