module.exports = {
  parser: 'typescript',
  printWidth: 100,
  singleQuote: true,
  trailingComma: 'all',
  arrowParens: 'avoid',
  overrides: [
    {
      files: ['.*', '*.json'],
      options: { parser: 'json' },
    },
    {
      files: ['*.js'],
      options: { parser: 'typescript' },
    },
  ],
};
