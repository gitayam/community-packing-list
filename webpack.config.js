const path = require('path');

module.exports = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  entry: {
    'packing-list-detail': './src/packing-list-detail.ts',
    'packing-list-form': './src/packing-list-form.ts',
    'price-form-modal': './src/price-form-modal.ts',
    'store-list': './src/store-list.ts'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'packing_lists/static/packing_lists/js')
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },
  resolve: {
    extensions: ['.ts', '.js']
  },
  devtool: 'source-map'
}; 