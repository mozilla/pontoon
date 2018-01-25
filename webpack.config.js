const path = require('path');
const webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');


module.exports = {
  entry: {
      'tag_admin': 'tags/admin'
  },
  output: {
    // This copies each source entry into the extension dist folder named
    // after its entry config key.
      path: path.resolve(__dirname, 'assets/webpack_bundles/'),
      filename: '[name].js'
  },
  module: {
    // This transpiles all code (except for third party modules) using Babel.
    loaders: [{
      exclude: /node_modules/,
      test: /\.js$/,
      loaders: ['babel-loader'],
    },{
        test: /\.css$/,
        loaders: [ 'style-loader', 'css-loader' ]
    },{
	test: /\.json$/,
	loader: 'json-loader',
    }],
  },
  resolve: {
    // This allows you to import modules just like you would in a NodeJS app.
    extensions: ['.js', '.jsx'],
    modules: [path.resolve(__dirname, 'pontoon/static/js/'), "node_modules"]
  },

  plugins: [
    // Since some NodeJS modules expect to be running in Node, it is helpful
    // to set this environment var to avoid reference errors.
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production'),
    }),
    new BundleTracker({filename: './webpack-stats.json'}),
  ],
  // This will expose source map files so that errors will point to your
  // original source files instead of the transpiled files.
  devtool: 'sourcemap',
};
