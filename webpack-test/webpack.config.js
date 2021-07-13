module.exports = {
  entry: {
    'with-array': `${__dirname}/with-array.js`,
    'with-buffer': `${__dirname}/with-buffer.js`,
  },
  output: {
    path: __dirname,
    filename: 'output/[name].js',
  },
  mode: 'development',
  target: 'web',
};
