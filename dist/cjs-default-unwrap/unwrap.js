module.exports = function unwrap(module, path) {
  const results = module.require(path).default;
  module.exports = results;
  module.exports.default = results;
};
