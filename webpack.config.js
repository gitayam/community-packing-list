const path = require('path');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      'packing-list-detail': './src/packing-list-detail.ts',
      'store-list': './src/store-list.ts',
      'packing-list-form': './src/packing-list-form.ts',
      'price-form-modal': './src/price-form-modal.ts',
      'common': './src/common.ts'
    },
    output: {
      path: path.resolve(__dirname, 'packing_lists/static/packing_lists/js'),
      filename: '[name].js',
      clean: true
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: 'ts-loader',
          exclude: /node_modules/
        }
      ]
    },
    resolve: {
      extensions: ['.tsx', '.ts', '.js']
    },
    devtool: isProduction ? 'source-map' : 'eval-source-map',
    optimization: {
      minimize: isProduction
    }
  };
}; 