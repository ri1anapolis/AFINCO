const path = require('path');

module.exports = [
  {
    entry: {
      cliente_pagamentos_new: path.resolve(
        __dirname,
        'js-src/cliente_pagamentos_new/index.js'
      ),
      despesas: path.resolve(__dirname, 'js-src/despesas/index.js'),
    },
    output: {
      path: path.resolve(__dirname, 'app/assets/js'),
      publicPath: '/static/',
      filename: '[name].js',
      chunkFilename: '[id]-[chunkhash].js',
    },
    devServer: {
      port: 8108,
      writeToDisk: true,
    },
  },
];
