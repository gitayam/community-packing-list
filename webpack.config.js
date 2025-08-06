const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      'packing-list-detail': './src/packing-list-detail.ts',
      'store-list': './src/store-list.ts',
      'packing-list-form': './src/packing-list-form.ts',
      'price-form-modal': './src/price-form-modal.ts',
      'items': './src/items.ts'
    },
    output: {
      path: path.resolve(__dirname, 'packing_lists/static/packing_lists/js'),
      filename: isProduction ? '[name].[contenthash].js' : '[name].js',
      clean: true,
      publicPath: '/static/packing_lists/js/'
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: [
            {
              loader: 'ts-loader',
              options: {
                transpileOnly: true,
                configFile: 'tsconfig.json'
              }
            }
          ],
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        }
      ]
    },
    resolve: {
      extensions: ['.tsx', '.ts', '.js'],
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@types': path.resolve(__dirname, 'src/types'),
        '@utils': path.resolve(__dirname, 'src/utils'),
        '@components': path.resolve(__dirname, 'src/components')
      }
    },
    devtool: isProduction ? 'source-map' : 'eval-source-map',
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction,
              drop_debugger: isProduction,
              pure_funcs: isProduction ? ['console.log', 'console.info'] : [],
            },
            mangle: {
              safari10: true, // Fix for Safari 10/11
            },
          },
          extractComments: false,
        }),
      ],
      splitChunks: {
        chunks: 'all',
        maxInitialRequests: 6,
        maxAsyncRequests: 4,
        cacheGroups: {
          // Services and utilities (most likely to be shared)
          services: {
            name: 'services',
            test: /[\\/]src[\\/]services[\\/]/,
            chunks: 'all',
            priority: 20,
            enforce: true,
          },
          
          // Components
          components: {
            name: 'components', 
            test: /[\\/]src[\\/]components[\\/]/,
            chunks: 'all',
            priority: 15,
          },
          
          // Common utilities
          utils: {
            name: 'utils',
            test: /[\\/]src[\\/](utils|common)[\\/]/,
            chunks: 'all',
            priority: 10,
          },
          
          // Vendor libraries
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 30,
          },
          
          // Shared code across multiple entry points
          shared: {
            name: 'shared',
            minChunks: 2,
            chunks: 'all',
            priority: 5,
            enforce: true,
          }
        }
      },
      runtimeChunk: 'single', // Better caching
    },
    performance: {
      hints: isProduction ? 'warning' : false,
      maxEntrypointSize: 250000,
      maxAssetSize: 250000
    },
    stats: {
      preset: 'minimal',
      moduleTrace: true,
      errorDetails: true
    }
  };
}; 